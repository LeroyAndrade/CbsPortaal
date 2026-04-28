from app.extensions.db import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from datetime import datetime

# User tabel
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column('user_id', db.Integer, unique=True,primary_key=True, autoincrement=True, nullable=False,)
    username = db.Column('username', db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column("password_hash", db.String(300), nullable=False)
    email = db.Column('email', db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)

    # Constructor
    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        self.password = password

        if password:  # als password
            self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Logging tabel
class userlogging(db.Model, UserMixin):
    __tablename__ = 'userlogging'
    id = db.Column('userlogging_id', db.Integer, unique=True,primary_key=True, autoincrement=True, nullable=False,)
    inlogtijden = db.column('inlogtijden', db.Integer, unique=True, nullable=True)
    useracties = db.column('useracties', db.String(100))