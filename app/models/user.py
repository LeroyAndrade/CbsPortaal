from app.extensions.db import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from datetime import datetime, UTC


# User tabel
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    last_logged_in = db.Column(db.DateTime, nullable=True)

    logs = db.relationship('UserLogging', back_populates='user', lazy=True)

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email

        if password:
            self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class UserLogging(db.Model):
    __tablename__ = 'userlogging'

    userlogging_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    logged_at = db.Column(db.DateTime, nullable=False)
    useracties = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', back_populates='logs')
