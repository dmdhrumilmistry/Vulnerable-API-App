from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column('id', db.Integer, primary_key=True)
    first_name = db.Column('first_name', db.String(20))
    last_name = db.Column('last_name', db.String(20))
    email = db.Column('email', db.String(200), unique=True)
    jwt_token = db.Column('jwt_token', db.String(300), unique=True)
    # password = db.Column(''db.String(200))

    def __init__(self, first_name, last_name, email, jwt_token) -> None:
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.email: str = email
        self.jwt_token: str = jwt_token

    def json(self, hide_sensitive_info: bool = True):
        data = dict()
        data['userid'] = self.id
        data['first_name'] = self.first_name
        data['last_name'] = self.last_name

        if not hide_sensitive_info:
            data['token'] = self.jwt_token
            data['email'] = self.email
        return data

    def __str__(self):
        return f'{self.id}-{self.first_name.capitalize()}{self.last_name.capitalize()}'
