from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# app/models.py
from app.extensions import db

# User tabel
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, unique=True,primary_key=True, autoincrement=True, nullable=False,)
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


# Artikel tabel
# class Article(db.Model):
#     __tablename__ = 'articles'
#     unique_id = db.Column(db.String(100), primary_key=True)
#     title = db.Column(db.Text, nullable=False)
#     release_time = db.Column(db.DateTime, index=True)
#     url = db.Column(db.String(500))
#     meta_description = db.Column(db.Text)
#     lead_text = db.Column(db.Text)
#     body = db.Column(db.Text)
#     language = db.Column(db.String(10), index=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     __table_args__ = (
#         db.Index('idx_article_release_time', 'release_time'),
#         db.Index('idx_article_language', 'language'),
#     )
#
# # Category tabel
# class Category(db.Model):
#     __tablename__ = 'categories'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), unique=True, nullable=False, index=True)
#
# # Koppeltabel
# class ArticleCategory(db.Model):
#     __tablename__ = 'article_categories'
#     article_id = db.Column(db.String(100), db.ForeignKey('articles.unique_id', ondelete='CASCADE'), primary_key=True)
#     category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
#
# # RunLog tabel
# class RunLog(db.Model):
#     __tablename__ = 'run_logs'
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
#     dataset_name = db.Column(db.String(100), index=True)
#     records_count = db.Column(db.Integer)
#     duration_seconds = db.Column(db.Float)
#     status = db.Column(db.String(20), index=True)
#
# # LoginAttempts tabel (uitgecommentarieerd was, nu actief)
# class LoginAttempts(db.Model):
#     __tablename__ = 'loginpogingen'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     pogingen = db.Column(db.Integer)