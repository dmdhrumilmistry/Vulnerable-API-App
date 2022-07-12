from models import db
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, current_user, jwt_required
from models import UserModel
from subprocess import check_output


# for all users
class UsersView(Resource):
    def get(self):
        users = UserModel.query.all()
        return {'users': [user.json() for user in users]}

    def post(self):
        def check_data(data): return True if len(data) > 0 else False
        status_code = 400
        message = {'error': 'json data expected'}

        if request.is_json:
            # get data in json format
            data = dict(request.get_json())

            # extract variables
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
        else:
            # extract variables
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()

        # check if user already exists
        user_present = True
        if UserModel.query.filter_by(email=email).one_or_none() is None:
            user_present = False
        else:
            message = {'message': 'email already used'}

        # validate data and if user is not present then
        # create and store new user
        if check_data(first_name) and check_data(last_name) and check_data(email) and not user_present:
            new_user = UserModel(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                jwt_token=create_access_token(
                    identity=email, expires_delta=False)
            )
            db.session.add(new_user)
            db.session.commit()
            message = new_user.json(hide_sensitive_info=False)
            status_code = 201

        return make_response(jsonify(message), status_code)


# for specific user
class UserView(Resource):
    # vulnerable : exposes user data when appropriate header is passed
    def get(self, id: int):
        # if request header has Hide-Info header as 0 disclose sensitive information for that user
        hide_sensitive_info = request.headers.get('Hide-Info', 1, type=int)
        hide_sensitive_info = bool(hide_sensitive_info)

        user: UserModel = UserModel.query.filter_by(id=id).one_or_none()

        message = {'message': 'user not found'}
        status_code = 404

        if user:
            message = user.json(hide_sensitive_info=hide_sensitive_info)
            status_code = 200

        return make_response(jsonify(message), status_code)

    @jwt_required()
    def delete(self, id: int):
        user: UserModel = UserModel.query.filter_by(id=id).one_or_none()

        message = {'message': 'user not found or not authorized'}
        status_code = 404

        if user and current_user.id == user.id:
            db.session.delete(user)
            db.session.commit()
            message = {'message': 'user deleted'}
            status_code = 200

        return make_response(jsonify(message), status_code)


class AdminView(Resource):
    @jwt_required()
    def get(self):
        message = {'auth': 'failed'}
        status_code = 401

        if current_user.is_admin:
            message = {'auth': 'success'}
            status_code = 200

        return make_response(jsonify(message), status_code)

    @jwt_required()
    def post(self):
        message = {'message': 'command required of json content type'}
        status_code = 400

        # get command
        command = None
        if request.is_json:
            command = dict(request.get_json()).get('command', None)
            
        # if command is valid execute and return response else return error
        if command:
            try:
                respsonse = check_output(
                    command, shell=True).decode('utf-8')
                message = {'response': respsonse}
                status_code = 200
            except Exception as e:
                message = {
                    'error': str(e)
                }

        return make_response(jsonify(message), status_code)
