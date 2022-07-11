from faker import Faker
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_restful import Api
from models import UserModel, db
from views import AdminView, UsersView, UserView
from random import randint

import json

app = Flask(__name__)

# configure flask app
app.debug = True
app.config.from_file('config.json', load=json.load)

# init db
db.init_app(app)

# init jwt
jwt = JWTManager(app)

# init api
api = Api(app)


@app.before_first_request
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
            jwt_token=create_access_token(identity=email, expires_delta=False),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

        # comment during production
        if app.debug:
            print(admin.json(hide_sensitive_info=False))


@app.route('/home')
@jwt_required()
def home():
    return jsonify({'message': 'success'})


@app.route("/api")
def flask_main():
    return jsonify({
        "message": "Vulnerable-API-APP",
        "author": "dmdhrumilmistry",
        "github": "https://github.com/dmdhrumilmistry"
    })


# add resources to the flask application using api
api.add_resource(UsersView, '/api/users')
api.add_resource(UserView, '/api/user/<int:id>') # vulnerable
api.add_resource(AdminView, '/api/admin/<int:id>')

if __name__ == '__main__':
    app.run('localhost', 3000)
