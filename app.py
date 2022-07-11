from faker import Faker
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_restful import Api
from models import UserModel, db
from views import UsersView, UserView
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
    # init db
    db.create_all()
    total_users = len(UserModel.query.all())

    # dump fake data into database if database is empty
    if total_users == 0:
        fake = Faker()
        for _ in range(500):
            first_name: str = fake.first_name()
            last_name: str = fake.last_name()

            # create unique email and token
            email = f'{first_name.lower()}.{last_name.lower()}.{randint(0,99999)}@vuln-api-app.com'
            token = create_access_token(identity=email, expires_delta=False)

            # create user and update database
            new_user = UserModel(
                first_name=first_name,
                last_name=last_name,
                email=email,
                jwt_token=token
            )
            db.session.add(new_user)
            db.session.commit()


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
api.add_resource(UserView, '/api/user/<int:id>')

if __name__ == '__main__':
    app.run('localhost', 3000)
