from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, SelectField, HiddenField, IntegerField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

from datetime import datetime
from pytz import timezone
from src.database2 import db, Item, Image, Menu

# Create A Search Form


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])

    #author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Posts Form


class DutyRoleForm(FlaskForm):
    type = StringField("Duty Role", validators=[DataRequired()])
    submit = SubmitField("Add New")

class ActivityForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[
                            DataRequired()])
    # content = CKEditorField('Content', validators=[DataRequired()])
    group_id = SelectField(u'Group', choices=[], coerce=int)
    item_id = HiddenField('Item_id')
    images = HiddenField('Images')
    video = StringField("Video")
    submit = SubmitField("Submit")


class ProgramForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[
                            DataRequired()])
    group_id = SelectField(u'Group', choices=[], coerce=int)
    item_id = HiddenField('Item_id')
    images = HiddenField('Images')
    submit = SubmitField("Submit")


class SongForm(FlaskForm):
    song_name = StringField("Song Name", validators=[DataRequired()])
    song_lyric = TextAreaField("Song Lyric", validators=[
                            DataRequired()])
    song_id = HiddenField('Song_id')
    images = HiddenField('Images')
    video = StringField("Video")
    submit = SubmitField("Submit")


class ZhouxunForm(FlaskForm):
    item_id = HiddenField('Item_id')
    images = HiddenField('Images')
    submit = SubmitField("Submit")


class DutyForm(FlaskForm):
    item_id = HiddenField('Item_id')
    group_id = SelectField(u'Group', choices=[], coerce=int)
    images = HiddenField('Images')
    submit = SubmitField("Submit")


format = "%Y-%m-%d %H:%M:%S %Z%z"
class MemberForm(FlaskForm):
    person_detail_id = HiddenField('Person Detail Id')
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    nickname = StringField("Nickname")
    phone_number = StringField("Phone Number")
    gender = SelectField(u'Gender', choices=[])
    status = SelectField(u'Status', choices=[])
    duty_roles = SelectMultipleField(
        u'Duty Roles', choices=[], coerce=int, default=[1])
    groups = SelectMultipleField(
        u'Groups', choices=[], coerce=int, default=[1])
    nationality = StringField("Nationality", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    date_of_birth = DateField(
        "Date of Birth", format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now(timezone('UTC')).strftime(format))
    image = FileField("Profile Picture")

    submit = SubmitField("Submit")


# Create a Form Class


class UserForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    nickname = StringField("Nickname", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Password', validators=[DataRequired(
    ), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField(
        "What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Form Class


class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

    # BooleanField
    # DateField
    # DateTimeField
    # DecimalField
    # FileField
    # HiddenField
    # MultipleField
    # FieldList
    # FloatField
    # FormField
    # IntegerField
    # PasswordField
    # RadioField
    # SelectField
    # SelectMultipleField
    # SubmitField
    # StringField
    # TextAreaField

    # Validators
    # DataRequired
    # Email
    # EqualTo
    # InputRequired
    # IPAddress
    # Length
    # MacAddress
    # NumberRange
    # Optional
    # Regexp
    # URL
    # UUID
    # AnyOf
    # NoneOf
