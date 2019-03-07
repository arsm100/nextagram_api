import peewee as pw
from models.base_model import BaseModel
from app import app
from playhouse.hybrid import hybrid_property
# from models.user import User


class Image(BaseModel):
    user_id = pw.IntegerField() #IntegerField was used instead of ForeignKeyField to prevent circular import errors
    image_path = pw.CharField()

    @hybrid_property
    def image_url(self):
        return app.config['S3_LOCATION'] + self.image_path
        