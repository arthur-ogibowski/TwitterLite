from twitter import database
from datetime import datetime
from twitter import login_manager
from flask_login import UserMixin
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(database.Model, UserMixin):
    __tablename__ = 'user'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False, unique=True)
    email = database.Column(database.String, nullable=False, unique=True)
    password = database.Column(database.String, nullable=False)
    posts = relationship('Posts', foreign_keys='Posts.user_id', backref='user')
    reposts = relationship('Posts', foreign_keys='Posts.original_posted_by_id', backref='original_posted_by')


class Posts(database.Model):
    __tablename__ = 'posts'
    id = database.Column(database.Integer, primary_key=True)
    post_text = database.Column(database.String, default='')
    post_img = database.Column(database.String, default='default.png')
    creation_date = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    likes = database.Column(database.Integer, default=0)
    reposted = database.Column(database.Boolean, default=False)
    original_posted_by_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=True)
    original_posted_date = database.Column(database.DateTime, nullable=True, default=datetime.utcnow())


class Like(database.Model):
    __tablename__ = 'like'
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), primary_key=True)
    post_id = database.Column(database.Integer, database.ForeignKey('posts.id'), primary_key=True)


