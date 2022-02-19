from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import validators
from src.database2 import Person, db, Song, Image, Video
from flask_login import login_user, login_required, logout_user, current_user
from src.webform import SongForm
from src.ustil import solve
import os
from src.google_storage import generate_download_signed_url_v4, generate_upload_signed_url_v4, cors_configuration, bucket_metadata, upload_blob, delete_blob
import uuid
from urllib.parse import urlparse

from datetime import datetime

from src.ustil import ROWS_PER_PAGE

websong = Blueprint("websong", __name__)


@websong.route('/song/delete/<int:id>')
@login_required
def delete_song(id):
    song_to_delete = Song.query.get_or_404(id)
    # id = current_user.person_id
    # if id == post_to_delete.poster.id:
    try:
        db.session.delete(song_to_delete)
        db.session.commit()

        # Return a message
        flash("Song Was Deleted!")

        # Grab all the posts from the database
        songs = Song.query.join(
            Image, Song.song_id == Image.song_id, isouter=True)\
            .join(Video, Song.song_id == Video.song_id, isouter=True)\
            .order_by(Song.song_name).all()
        return render_template("song/songs.html", songs=songs)

    except:
        # Return an error message
        flash("Whoops! There was a problem deleting song, try again...")

        # Grab all the posts from the database
        songs = Song.query.join(
            Image, Song.song_id == Image.song_id, isouter=True)\
            .join(Video, Song.song_id == Video.song_id, isouter=True)\
            .order_by(Song.song_name).all()
        return render_template("song/songs.html", songs=songs)
    # else:
    #     # Return a message
    #     flash("You Aren't Authorized To Delete That Post!")

    #     # Grab all the posts from the database
    #     posts = Posts.query.order_by(Posts.date_posted)
    #     return render_template("posts.html", posts=posts)


@websong.route('/songs')
@login_required
def songs():
    page = request.args.get('page', 1, type=int)
    # Grab all the programmes from the database
    songs = Song.query.join(
        Image, Song.song_id == Image.song_id, isouter=True)\
        .join(Video, Song.song_id == Video.song_id, isouter=True)\
        .order_by(Song.song_name).paginate(
        page=page, per_page=ROWS_PER_PAGE)


    return render_template("/song/songs.html", songs=songs)


@websong.route('/song/<int:id>')
@login_required
def song(id):
    song = Song.query.join(
        Image, Song.song_id == Image.song_id, isouter=True)\
        .join(Video, Song.song_id == Video.song_id, isouter=True)\
        .filter(Song.song_id == id).first()
    if song.created_date:
        song.created_date = song.created_date.strftime(
            "%m/%d/%Y, %H:%M:%S")

    return render_template('song/song.html', song=song)


@websong.route('/song/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_song(id):
    print('edit_song')

    song = Song.query.get_or_404(id)
    form = SongForm()

    if 'filenames' in session:
        filenames = session['filenames']
    else:
        filenames = []

    if request.method == 'POST' and form.validate_on_submit():

        song.song_name = form.song_name.data
        song.song_lyric = form.song_lyric.data

        if form.video.data:
            for video_item in song.video:
                videoItem = Video.query.filter_by(
                    song_id=video_item.song_id).first()
                db.session.delete(videoItem)
                db.session.commit()
            song.video.append(Video(url=form.video.data,song_id=song.song_id))

        #remove record from db
        for image_item in song.image:
            # print(image_item.file_name)
            # print(filenames)
            index = solve('name', image_item.file_name, filenames)
            if index is None:
                # print(image_item.file_name)
                imageItem = Image.query.filter_by(
                    file_name=image_item.file_name).first()  # dont have image id

                print('remove record' + image_item.file_name)
                db.session.delete(imageItem)
                db.session.commit()
                bucket_name = cors_configuration('jonathan_bucket_1')
                delete_blob(bucket_name, image_item.file_name)

        #upload local image to google storage if path dont have http
        for image in filenames:
            if "http" not in image['dataURL']:
                bucket_name = cors_configuration('jonathan_bucket_1')
                upload_blob(bucket_name, image['dataURL'], image['name'])
                #update to db
                song.image.append(Image(
                    file_name=image['name'], bucket_name='jonathan_bucket_1', item_id=id, created_date=datetime.now(), updated_date=datetime.now()))

        # Update Database
        db.session.add(song)
        # db.session.flush()
        db.session.commit()
        flash("Song Has Been Updated!")
        return redirect(url_for('websong.song', id=song.song_id))

    # if current_user.person_id == post.person_id:

    form.song_id.data = song.song_id
    form.song_name.data = song.song_name
    form.song_lyric.data = song.song_lyric
    form.video.data = song.video[0].url

    image = []
    for image_item in song.image:
        # print(image_item.file_name)
        # print(image_item.item_id)
        # bucket_name = cors_configuration(image_item.bucket_name)
        # url = generate_download_signed_url_v4(
        #     bucket_name, image_item.file_name)
        image.append({
            # bucket_name=cors_configuration(image_item.bucket_name)
            # generate_download_signed_url_v4(bucket_name, image_item.file_name)
            'name': image_item.file_name,
            'size': 12345678,
            'dataURL': 'https://images.unsplash.com/photo-1471879832106-c7ab9e0cee23?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8Mnx8fGVufDB8fHx8&w=1000&q=80'
        })

    form.images.data = image
    filenames.clear()
    session['filenames'] = []
    filenames.extend(image)
    session['filenames'] = filenames
    session.permanent = True

    print(session['filenames'])

    return render_template('song/edit_song.html', form=form)
    # else:
    # 	flash("You Aren't Authorized To Edit This Post...")
    # 	posts = Posts.query.order_by(Posts.date_posted)
    # 	return render_template("webpost.posts.html", posts=posts)


# Add Post Page
@websong.route('/add-song', methods=['GET', 'POST'])
@login_required
def add_song():
    form = SongForm()

    if 'filenames' in session:
        filenames = session['filenames']
    else:
        filenames = []

    if request.method == 'POST' and form.validate_on_submit():
        # person_id = current_user.person_id

        # print(form.group_id.data)
        song = Song(song_name=form.song_name.data, song_lyric=form.song_lyric.data)
        db.session.add(song)
        db.session.commit()

        # Clear The Form
        song.song_name = form.song_name.data
        song.song_lyric = form.song_lyric.data

        if form.video.data:
            song.video.append(Video(url=form.video.data, song_id=song.song_id))

        #upload local image to google storage if path dont have http
        for image in filenames:
            if "http" not in image['dataURL']:
                bucket_name = cors_configuration('jonathan_bucket_1')
                upload_blob(bucket_name, image['dataURL'], image['name'])
                #update to db
                song.image.append(Image(
                    file_name=image['name'], bucket_name='jonathan_bucket_1', song_id=song.song_id, created_date=datetime.now(), updated_date=datetime.now()))

        # # Add post data to database
        db.session.add(song)
        db.session.commit()

        # Return a Message
        flash("Song Submitted Successfully!")
        return redirect(url_for('websong.songs'))

    form.images.data = []
    form.video.data = ''
    filenames.clear()
    session['filenames'] = filenames
    session.permanent = True
    # Redirect to the webpage
    return render_template("song/add_song.html", form=form)
