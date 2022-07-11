from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column('id', db.Integer, primary_key=True)
    first_name = db.Column('first_name', db.String(20))
    last_name = db.Column('last_name', db.String(20))
    email = db.Column('email', db.String(200), unique=True)
    password = db.Column('password', db.String(100))
    jwt_token = db.Column('token', db.String(300), unique=True)
    is_admin = db.Column('admin', db.Boolean, default=False)

    def __init__(self, first_name, last_name, email, password, jwt_token, is_admin) -> None:
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.email: str = email
        self.password: str = password
        self.jwt_token: str = jwt_token
        self.is_admin: bool = is_admin

    def json(self, hide_sensitive_info: bool = True):
        data = dict()
        data['userid'] = self.id
        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['admin'] = self.is_admin

        if not hide_sensitive_info:
            data['token'] = self.jwt_token
            data['email'] = self.email
            
        return data

    def __str__(self):
        return f'{self.id}-{self.first_name.capitalize()}{self.last_name.capitalize()}'
