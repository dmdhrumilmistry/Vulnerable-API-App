from faker import Faker
from flask import Flask, jsonify, make_response, redirect, render_template, request
from flask_jwt_extended import JWTManager, create_access_token, current_user, jwt_required, verify_jwt_in_request
from flask_restful import Api
from models import UserModel, db
from random import randint
from views import AdminView, UsersView, UserView

import json

app = Flask(
    import_name=__name__,
    static_url_path='/static',
    static_folder='./static',
)

# configure flask app
app.debug = False
app.config.from_file('config.json', load=json.load)

# init db
db.init_app(app)

# init jwt
jwt = JWTManager(app)


@ jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(email=identity).one_or_none()


# init api
api = Api(app)


@ app.before_first_request
def configure_app():
    max_users = randint(20, 50)
    # init db
    db.create_all()
    total_users = len(UserModel.query.all())

    # dump fake data into database if database is empty
    if total_users == 0:
        fake = Faker()
        for _ in range(max_users):
            first_name: str = fake.first_name()
            last_name: str = fake.last_name()

            # create unique email and token
            email = f'{first_name.lower()}.{last_name.lower()}.{randint(0,99999)}@vuln-api-app.com'
            password = fake.password(length=randint(20, 64))
            token = create_access_token(identity=email, expires_delta=False)

            # create user and update database
            new_user = UserModel(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                jwt_token=token,
                is_admin=False
            )
            db.session.add(new_user)
            db.session.commit()

        # create admin user
        # from /api/users endpoint get admin
        # bruteforce /api/user/:id endpoint to get admin userid
        admin = UserModel(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email='admin@vuln-api-app.com',
            password=fake.password(length=randint(50, 64)),
            jwt_token=create_access_token(identity='admin@vuln-api-app.com', expires_delta=False),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

        # comment during production
        if app.debug:
            print(admin.json(hide_sensitive_info=False))




# web app endpoints
@app.route('/')
def root():
    # if jwt totken is present redirect user to dashboard else
    verify_jwt_in_request(optional=True)

    # get token
    token = request.args.get('token', None)

    # get jwt token if present
    if current_user:
        token = current_user.jwt_token

    # redirect to login page if token is available
    if token:
        return redirect(f'/home?token={token}')
    else:
        return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html', title='Login Page')

@app.route('/home', methods=['GET'])
def home():
    verify_jwt_in_request(optional=True)

    # get token
    # vulnerable: any account can be hijacked by passing user's token
    # which can be received from api endpoint
    token = request.args.get('token', None)

    # get jwt token if present
    if current_user and token is None:
        token = current_user.jwt_token

    if token:
        return render_template(
            'home.html',
            title='Home',
            token=token,
        )
    else:
        return redirect('/login')


@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    # get jwt token if present
    if current_user:
        return render_template(
            'admin.html',
            title='Admin Page',
            token=current_user.jwt_token,
        )
    else:
        return redirect('/login')
# api endpoints


@app.route("/api")
def flask_main():
    return jsonify({
        "message": "Vulnerable-API-APP",
        "author": "dmdhrumilmistry",
        "github": "https://github.com/dmdhrumilmistry"
    })

# to login user use `/api/user/login` [POST](email, password)
# to create user use `/api/users` [POST](email, password, first_name, last_name, )


@app.route('/api/user/login', methods=['POST'])
def api_login():
    message = {'message': 'email or password is invalid'}
    status_code = 401

    # get post data
    if request.is_json:
        data = dict(request.get_json())
        email = data.get('email', '')
        password = data.get('password', '')
    else:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

    # authenticate user
    user: UserModel = UserModel.query.filter_by(email=email).one_or_none()
    if user and user.email == email and user.password == password:
        message = {'token': user.jwt_token}
        status_code = 200

    # return repsone
    return make_response(jsonify(message), status_code)

# get user details from token
@app.route('/api/user/getDetails')
@jwt_required()
def get_user_details():
    message = {'message': 'invalid token'}
    status_code = 401

    # check if token belongs to the user
    if current_user:
        message = current_user.json(hide_sensitive_info=False)
        status_code = 200
        
    return make_response(jsonify(message), status_code)


# add resources to the flask application using api
api.add_resource(UsersView, '/api/users')
api.add_resource(UserView, '/api/user/<int:id>')  # vulnerable
api.add_resource(AdminView, '/api/admin')

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
