from flask import Blueprint, jsonify, make_response, request
from models.image import Image
from models.user import User

images_api_blueprint = Blueprint('images_api', __name__)

@images_api_blueprint.route('/', methods=['GET'])
def index():
    if request.args.get('userId'):
        images = Image.select().where(Image.user_id == int(request.args['userId']))
    else:
        images = Image.select()

    images = [image.image_url for image in images]

    return jsonify(images)

@images_api_blueprint.route('/me', methods=['GET'])
def show():
    auth_header = request.headers.get('Authorization')

    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        responseObject = {
            'status': 'failed',
            'message': 'No authorization header found'
        }

        return make_response(jsonify(responseObject)), 401

    user_id = User.decode_auth_token(auth_token)

    user = User.get_or_none(id=user_id)

    if user:
        images = Image.select().where(Image.user_id == user.id)
        images = [image.image_url for image in images]

        return jsonify(images)
    else:
        responseObject = {
            'status': 'failed',
            'message': 'Authentication failed'
        }

        return make_response(jsonify(responseObject)), 401
