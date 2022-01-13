from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.google_storage import generate_download_signed_url_v4

import string
import random
db = SQLAlchemy()
ma = Marshmallow()


person_duty_role = db.Table('person_duty_role',
                                   db.Column('person_id', db.Integer,
                                             db.ForeignKey('person.person_id')),
                                   db.Column('duty_role_id', db.Integer, db.ForeignKey('duty_role.duty_role_id')))


class Person(db.Model):
    __tablename__ = 'person'
    person_id = db.Column(UUID(as_uuid=True), primary_key=True,
                          nullable=False, default=uuid.uuid4)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(1))
    phone_number = db.Column(db.String(50))
    nationality = db.Column(db.String(20))
    fcm_token = db.Column(db.Text())
    address = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    date_of_birth = db.Column(db.DATE)
    confirmed = db.Column(db.Boolean)
    otp_secret = db.Column(db.String(50))
    image = db.relationship("Image", backref="person")
    # phonenumber = db.relationship("PhoneNumber", backref="person")
    # location = db.relationship("Location", backref="person")
    dutyroles = db.relationship('DutyRole', secondary=person_duty_role,
                                backref=db.backref('dutyroles',
                                                    lazy='dynamic'))

    def __repr__(self) -> str:
        return 'User>>> {self.dutyrole.duty_role_id}'


# create Person schema
class PersonSchema(ma.Schema):
    class Meta:
        fields = ['first_name','last_name','nickname','status','email', 'created_date','confirmed']


# create instance of schema
person_schema = PersonSchema(many=False)
persons_schema = PersonSchema(many=True)


class PhoneNumber(db.Model):
    __tablename__ = 'phone_number'
    phone_number_id = db.Column(db.Integer, primary_key=True,
                        nullable=False)
    number = db.Column(db.String(50))
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))

    def __repr__(self) -> str:
        return '<PhoneNumber %r>' % self.number


class Location(db.Model):
    __tablename__ = 'location'
    location_id = db.Column(db.Integer, primary_key=True,
                                nullable=False)
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(20))
    postcode = db.Column(db.String(20))
    country = db.Column(db.String(20))
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))

    def __repr__(self) -> str:
        return '<PhoneNumber %r>' % self.number


# create Menu schema
class DutySchema(ma.Schema):
    class Meta:
        fields = ['duty_id', 'created_date']


# create instance of schema
duty_schema = DutySchema(many=False)
dutys_schema = DutySchema(many=True)

class DutyRole(db.Model):
    __tablename__ = 'duty_role'
    duty_role_id = db.Column(db.Integer, primary_key=True,
                             nullable=False)
    duty_role_type = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    _person = db.relationship('Person', secondary=person_duty_role, backref=db.backref(
        'person_duty_role_backref', lazy='dynamic'))

    def __repr__(self) -> str:
        return '<DutyRole %r>' % self.duty_role_type



class Menu(db.Model):
    menu_id = db.Column(db.Integer, primary_key=True,
                          nullable=False)
    type = db.Column(db.String(50))
    group_menu = db.relationship("Group_menu", backref='menu')
    item = db.relationship("Item", backref='menu')


    def __repr__(self) -> str:
        return '<Menu %r>' % self.type
        # return 'Menu>>> {self.type}'


# create Menu schema
class MenuSchema(ma.Schema):
    class Meta:
        fields = ['menu_id','type']


# create instance of schema
menu_schema = MenuSchema(many=False)
menus_schema = MenuSchema(many=True)


class Churchgroup(db.Model):
    __tablename__ = 'church_group'
    group_id = db.Column(db.Integer, primary_key=True,
                        nullable=False)
    name = db.Column(db.String(50))
    group_menu = db.relationship("Group_menu", backref='church_group')
    item = db.relationship("Item", backref='church_group')


    def __repr__(self) -> str:
        return '<churchGroup %r>' % self.name


# create Menu schema
class Church_groupSchema(ma.Schema):
    class Meta:
        fields = ['group_id', 'name']


# create instance of schema
group_schema = Church_groupSchema(many=False)
groups_schema = Church_groupSchema(many=True)

class Group_menu(db.Model):
    group_menu_id = db.Column(db.Integer, primary_key=True,
                        nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('church_group.group_id'))
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.menu_id'),)
   

    def __repr__(self) -> str:
        return '<Group_menu %r>' % self.menu_id
        # return 'Group_menu>>> {self.menu_id}'




# create Menu schema
class Group_menuSchema(ma.Schema):
    class Meta:
        fields = ['group_id', 'menu_id']


# create instance of schema
group_menu_schema = Group_menuSchema(many=False)
groups_menu_schema = Group_menuSchema(many=True)


# get item list
class Item(db.Model):
    __tablename__ = 'item'
    item_id = db.Column(db.Integer, primary_key=True,
                              nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    group_id = db.Column(db.Integer, db.ForeignKey('church_group.group_id'))
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.menu_id'))
    image = db.relationship("Image", backref="item")

    def __repr__(self) -> str:
        return '<Item %r>' % self.created_date


# create Menu schema
class ItemSchema(ma.Schema):
    class Meta:
        fields = ['item_id', 'title', 'content', 'name',
                  'created_date', 'group_id', 'menu_id']


# create instance of schema
item_schema = ItemSchema(many=False)
items_schema = ItemSchema(many=True)


# get image list
class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(db.Integer, primary_key=True,
                        nullable=False)
    file_name = db.Column(db.String(255))
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    bucket_name = db.Column(db.String(50), default='jonathan_bucket_1')
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'))
    song_id = db.Column(db.Integer, db.ForeignKey('song.song_id'))
    duty_id = db.Column(db.Integer, db.ForeignKey('duty.duty_id'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))

    def __repr__(self) -> str:
        return '<Image %r>' % self.image_id


# create Menu schema
class ImageSchema(ma.Schema):
    class Meta:
        fields = ['image_id', 'file_name', 'created_date',
                  'item_id', 'bucket_name']


# create instance of schema
image_schema = ImageSchema(many=False)
images_schema = ImageSchema(many=True)



# get language list
class Language(db.Model):
    __tablename__ = 'language'
    language_id = db.Column(db.Integer, primary_key=True,
                        nullable=False)
    language_type = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return '<Language %r>' % self.language_type


# create Menu schema
class LanguageSchema(ma.Schema):
    class Meta:
        fields = ['language_id', 'language_type']


# create instance of schema
language_schema = LanguageSchema(many=False)
languages_schema = LanguageSchema(many=True)

# get language list


class Song(db.Model):
    __tablename__ = 'song'
    song_id = db.Column(db.Integer, primary_key=True,
                            nullable=False)
    song_name = db.Column(db.String(255))
    song_lyric = db.Column(db.Text())
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    image = db.relationship("Image", backref="song")
    video = db.relationship("Video", backref="song")
    # video = db.relationship('Video', foreign_keys='song.song_id')

    def __repr__(self) -> str:
        return '<Song %r>' % self.video


# create Menu schema
class SongSchema(ma.Schema):
    class Meta:
        fields = ['song_id', 'song_name', 'song_lyric', 'created_date']


# create instance of schema
song_schema = SongSchema(many=False)
songs_schema = SongSchema(many=True)


class Video(db.Model):
    __tablename__ = 'video'
    video_id = db.Column(db.Integer, primary_key=True,
                        nullable=False)
    url = db.Column(db.Text())
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'))
    song_id = db.Column(db.Integer, db.ForeignKey('song.song_id'))

    def __repr__(self) -> str:
        return '<Video %r>' % self.url


# create Menu schema
class VideoSchema(ma.Schema):
    class Meta:
        fields = ['video_id', 'url', 'created_date']


# create instance of schema
video_schema = VideoSchema(many=False)
videos_schema = VideoSchema(many=True)


class Duty(db.Model):
    __tablename__ = 'duty'
    duty_id = db.Column(db.Integer, primary_key=True,
                         nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    image = db.relationship("Image", backref="duty")

    def __repr__(self) -> str:
        return '<Duty %r>' % self.duty_id


# create Menu schema
class DutySchema(ma.Schema):
    class Meta:
        fields = ['duty_id', 'created_date']


# create instance of schema
duty_schema = DutySchema(many=False)
dutys_schema = DutySchema(many=True)