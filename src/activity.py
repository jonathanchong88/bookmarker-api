from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import validators
from src.database2 import Person, db, Item, Image, Churchgroup
from flask_login import login_user, login_required, logout_user, current_user
from src.webform import ActivityForm
from src.ustil import solve
import os
from src.google_storage import generate_download_signed_url_v4, generate_upload_signed_url_v4, cors_configuration, bucket_metadata, upload_blob, delete_blob
import uuid
# import urllib.parse
# import random

from datetime import datetime
from src.ustil import ROWS_PER_PAGE


webactivity = Blueprint("webactivity", __name__)

# filenames = []

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
basedir = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@webactivity.route('/activities/delete/<int:id>')
@login_required
def delete_activity(id):
    activity_to_delete = Item.query.get_or_404(id)
    # id = current_user.person_id
    # if id == post_to_delete.poster.id:
    try:
        db.session.delete(activity_to_delete)
        db.session.commit()

        # Return a message
        flash("Activity Was Deleted!")

        # Grab all the posts from the database
        activities = Item.query.join(
            Image, Item.item_id == Image.item_id, isouter=True)\
            .filter(Item.menu_id == 3).order_by(Item.updated_date.desc()).paginate(
            page=1, per_page=ROWS_PER_PAGE)
        return render_template("activities.html", activities=activities)

    except:
        # Return an error message
        flash("Whoops! There was a problem deleting activty, try again...")

        # Grab all the posts from the database
        activities = Item.query.join(
            Image, Item.item_id == Image.item_id, isouter=True)\
            .filter(Item.menu_id == 3).order_by(Item.updated_date.desc()).paginate(
            page=1, per_page=ROWS_PER_PAGE)
        return render_template("activities.html", activities=activities)
    # else:
    #     # Return a message
    #     flash("You Aren't Authorized To Delete That Post!")

    #     # Grab all the posts from the database
    #     posts = Posts.query.order_by(Posts.date_posted)
    #     return render_template("posts.html", posts=posts)


@webactivity.route('/activities')
@login_required
def activities():
    page = request.args.get('page', 1, type=int)
    # Grab all the activities from the database
    activities = Item.query.join(
        Image, Item.item_id == Image.item_id, isouter=True)\
        .filter(Item.menu_id == 3).order_by(Item.updated_date.desc()).paginate(
        page=page, per_page=ROWS_PER_PAGE)

    return render_template("activities.html", activities=activities)

    # .paginate(page=page, per_page=per_page)
    # activities = Item.query.order_by(Posts.date_posted)


@webactivity.route('/activities/<int:id>')
@login_required
def activity(id):
    activity = Item.query.join(
        Churchgroup, Item.group_id == Churchgroup.group_id, isouter=True)\
        .filter(Item.item_id == id).first()
    if activity.created_date:
        activity.created_date = activity.created_date.strftime(
            "%m/%d/%Y, %H:%M:%S")
    return render_template('activity.html', activity=activity)


@webactivity.route('/activities/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    print('edit_activity')

    if 'filenames' in session:
        filenames = session['filenames']
    else:
        filenames = []
    activity = Item.query.get_or_404(id)
    form = ActivityForm()
    form.group_id.choices = [(g.group_id, g.name)
                             for g in Churchgroup.query.all()]

    if request.method == 'POST' and form.validate_on_submit():

        activity.title = form.title.data
        activity.content = form.content.data
        activity.group_id = form.group_id.data

        #remove record from db
        for image_item in activity.image:
            # print(image_item.file_name)
            print(filenames)
            index = solve('name', image_item.file_name, filenames)
            if index is None:
                # print(image_item.file_name)
                imageItem = Image.query.filter_by(
                    file_name=image_item.file_name).first()  # dont have image id
                
                print('remove record' +image_item.file_name)
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
                activity.image.append(Image(
                    file_name=image['name'], bucket_name='jonathan_bucket_1', item_id=id, created_date=datetime.now(), updated_date=datetime.now()))

        # Update Database
        db.session.add(activity)
        # db.session.flush()
        db.session.commit()
        session.pop('filenames', None)
        flash("Activity Has Been Updated!")
        return redirect(url_for('webactivity.activity', id=activity.item_id))

    # if current_user.person_id == post.person_id:
   
    form.item_id.data = activity.item_id
    form.title.data = activity.title
    form.content.data = activity.content
    form.group_id.data = activity.group_id
    

    image = []
    for image_item in activity.image:
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

    return render_template('edit_activity.html', form=form)
    # else:
    # 	flash("You Aren't Authorized To Edit This Post...")
    # 	posts = Posts.query.order_by(Posts.date_posted)
    # 	return render_template("webpost.posts.html", posts=posts)


# Add Post Page
@webactivity.route('/add-activity', methods=['GET', 'POST'])
@login_required
def add_activity():
    form = ActivityForm()
    form.group_id.choices = [(g.group_id, g.name)
                             for g in Churchgroup.query.all()]

    if 'filenames' in session:
        filenames = session['filenames']
    else:
        filenames = []

    if request.method == 'POST' and form.validate_on_submit():
        # person_id = current_user.person_id

        # print(form.group_id.data)
        activity = Item(title=form.title.data, content=form.content.data,
                        menu_id=3, group_id=form.group_id.data)
        db.session.add(activity)
        db.session.commit()
        # print(activity.item_id)

        # Clear The Form
        activity.title = form.title.data
        activity.content = form.content.data
        activity.group_id = form.group_id.data

        #upload local image to google storage if path dont have http
        for image in filenames:
            if "http" not in image['dataURL']:
                bucket_name = cors_configuration('jonathan_bucket_1')
                upload_blob(bucket_name, image['dataURL'], image['name'])
                #update to db
                activity.image.append(Image(
                    file_name=image['name'], bucket_name='jonathan_bucket_1', item_id=activity.item_id, created_date=datetime.now(), updated_date=datetime.now()))


        # # Add post data to database
        db.session.add(activity)
        db.session.commit()

        # Return a Message
        flash("Activity Submitted Successfully!")
        return redirect(url_for('webactivity.activities'))

    form.images.data = []
    filenames.clear()
    session['filenames'] = filenames
    session.permanent = True
    # Redirect to the webpage
    return render_template("add_activity.html", form=form)


# @webactivity.route('/activity/upload', methods=['POST', 'GET'])
# def upload():
    
#     if request.method == 'POST':
#         file = request.files['file']
#         filename = str(uuid.uuid4())+ secure_filename(file.filename)
#         now = datetime.now()
#         if file and allowed_file(file.filename):
#             # session['filenames'] = filenames
           
#             # print(session['filenames'])
#             file_dir = os.path.join(basedir,
#                                     current_app.config['UPLOAD_FOLDER'])
#             # if not os.path.exists(file_dir):
#             #     os.mkdir(file_dir)
#             file_path = os.path.join(file_dir, filename)
#             # print(file_path)
#             file.save(file_path)

#             file.seek(0, os.SEEK_END)
#             file_length = file.tell()
#             # print(filenames)
#             session['filenames'].append(
#                 {'name': filename, 'size': file_length, 'dataURL': file_path})
#             # print(len(filenames))
#             return filename
    
#     msg = 'success calling'
#     return jsonify(msg)


# @webactivity.route('/activity/delete', methods=['POST', 'GET'])
# def delete_image():

#     if request.method == 'POST':
#         filename = request.json['filename']
#         filePath = request.json['filePath']
#         # print(filename)
#         # print(filePath)
#         if 'filenames' in session:
#             filenames = session['filenames']
#         else:
#             filenames = []

#         # #delete filename is not contain http
#         if "http" not in filePath:
#             index = solve('name', filePath, filenames)
#             # print(index)
#             file_dir = os.path.join(basedir,
#                                 current_app.config['UPLOAD_FOLDER'])
#             file_path = os.path.join(file_dir, filePath)
#             os.remove(file_path)
#         else:
#             index = solve('name', filename, filenames)
#         print(index)
#         # print(len(filenames))
#         filenames.pop(index)
#         session['filenames'] = filenames
#         print(len(session['filenames']))
#         # print(filenames)
#     msg = 'success calling'
#     return jsonify(msg)


@webactivity.route('/activity/confirm/images', methods=['POST'])
def confirm_image():
    print('confirm image')
    
    # session['image'] = filename
    return render_template('edit_activity.html', form=form)

    # if request.method == 'POST':
    #     # print(request.json)
    #     group_id = request.json['group_id']
    #     title = request.json['title']
    #     content = request.json['content']
    #     item_id = request.json['item_id']
        
    #     form.group_id.data = group_id
    #     form.title.data = title 
    #     form.content.data = content
    #     form.item_id.data = item_id
    #     # return jsonify('msg')
    #     print(session['filenames'])
    #     # return redirect(request.referrer)
    #     return redirect(url_for('webactivity.edit_activity', id=item_id))
        # return render_template('edit_activity.html', form=form)

