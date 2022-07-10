from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from flask_restful import Api
from models import db
from views import UsersView

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

    # TODO: dump fake data into database

@app.route('/home')
@jwt_required()
def home():
    return jsonify({'message':'success'})

@app.route("/api")
def flask_main():
    return jsonify({
        "message": "Vulnerable-API-APP",
        "author": "dmdhrumilmistry",
        "github": "https://github.com/dmdhrumilmistry"
    })


# add resources to the flask application using api
api.add_resource(UsersView, '/api/users')

if __name__ == '__main__':
    app.run('localhost', 3000)
