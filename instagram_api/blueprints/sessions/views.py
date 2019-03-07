from flask import jsonify, Blueprint, request, make_response
from models.user import User
from werkzeug.security import check_password_hash

sessions_api_blueprint = Blueprint('sessions_api', __name__)

@sessions_api_blueprint.route('/login', methods=['POST'])
def sign_in():
    # get the post data
    post_data = request.get_json()
    # check if user already exists
    user = User.get_or_none(email=post_data.get('email'))
    if user and check_password_hash(user.password, post_data.get('password')):
        auth_token = user.encode_auth_token(user.id)

        responseObject = {
            'status': 'success',
            'message': 'Successfully signed in.',
            'auth_token': auth_token.decode(),
            'user': {"id": int(user.id), "username": user.username,
              "profileImage": user.profile_image_url}
        }

        return make_response(jsonify(responseObject)), 201

    else:
        responseObject = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }

        return make_response(jsonify(responseObject)), 401
