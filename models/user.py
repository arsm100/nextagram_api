from app import app
import peewee as pw
from models.base_model import BaseModel
from playhouse.hybrid import hybrid_property
from models.following import Following
from models.image import Image
from flask import flash
import datetime
import jwt


class User(BaseModel):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField()
    profile_image = pw.CharField(null=True)
    is_private = pw.BooleanField(default=False)


    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username)

        if duplicate_username and duplicate_username.id != self.id:
            self.errors.append('username not unique')

        duplicate_email = User.get_or_none(User.email == self.email)

        if duplicate_email and duplicate_email.id != self.id:
            self.errors.append('email not unique')

        

    @hybrid_property
    def profile_image_url(self):
        if self.profile_image:
            return app.config['S3_LOCATION'] + self.profile_image
        else:
            return app.config['S3_LOCATION'] + "person-placeholder-image-3.jpg"

    @hybrid_property
    def images(self): # used to replace the backref
        images = Image.select().join(User, on=(User.id == Image.user_id)).where(Image.user_id==self.id)
        return images
    
    @hybrid_property
    def idols(self):
        idols = User.select().join(Following, on=(User.id == Following.idol_id)).where(Following.fan_id==self.id, Following.is_approved==True)
        return idols
    
    @hybrid_property
    def fans(self):
        fans = User.select().join(Following, on=(User.id == Following.fan_id)).where(Following.idol_id==self.id, Following.is_approved==True)
        return fans
    
    def follow(self, idol_id):
        idol = User.get(id=idol_id)
        Following.create(fan_id=self.id, idol_id=idol_id)
        if not idol.is_private:
            Following.update(is_approved=True).where(Following.fan_id==self.id, Following.idol_id==idol_id).execute()
            flash(f'Successfully followed {idol.username}', 'success')
        else:
            flash(f'follow request sent to {idol.username}. Pending approval', 'info')
            
    def unfollow(self, idol_id):
        Following.delete().where(Following.fan_id==self.id, Following.idol_id==idol_id).execute()

    def feed(self):
        idols_ids = list(idol.id for idol in self.idols)
        feed = Image.select(Image, User).join(User, on=(Image.user_id == User.id)).where(Image.user_id << idols_ids).order_by(Image.created_at.desc())
        return feed

    @hybrid_property
    def pending_idols(self):
        pending_idols = User.select().join(Following, on=(User.id == Following.idol_id)).where(Following.fan_id==self.id, Following.is_approved==False)
        return pending_idols
    
    @hybrid_property
    def pending_fans(self):
        pending_fans = User.select().join(Following, on=(User.id == Following.fan_id)).where(Following.idol_id==self.id, Following.is_approved==False)
        return pending_fans
    
    def approve(self, fan_id):
        Following.update(is_approved=True).where(Following.fan_id==fan_id, Following.idol_id==self.id).execute()
        

    # Login through apis (creating JWT) 

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 0
        except jwt.InvalidTokenError:
            return 0
