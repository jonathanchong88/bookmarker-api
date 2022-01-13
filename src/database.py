from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

import string
import random
db = SQLAlchemy()
ma = Marshmallow()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship('Bookmark', backref="user")

    def __repr__(self) -> str:
        return 'User>>> {self.username}'


# create user schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ['username', 'email']


# create instance of schema
user_schema = UserSchema(many=False)
users_schema = UserSchema(many=True)


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
   

    def generate_short_characters(self):
        characters = string.digits+string.ascii_letters
        picked_chars = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=picked_chars).first()

        if link:
            self.generate_short_characters()
        else:
            return picked_chars

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url = self.generate_short_characters()

    def __repr__(self) -> str:
        return 'Boomark>>> {self.url}'


# create Bookmarks schema
class BookmarksSchema(ma.Schema):
    class Meta:
        fields = ['id', 'body', 'url', 'short_url',
                  'visits', 'user_id', 'created_at', 'updated_at', 'testbookmark']


# create instance of schema
bookmark_schema = BookmarksSchema(many=False)
bookmarks_schema = BookmarksSchema(many=True)
