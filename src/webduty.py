from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import validators
from src.database2 import Person, db, Item, Image, Churchgroup
from flask_login import login_user, login_required, logout_user, current_user
from src.webform import DutyForm
from src.ustil import solve
import os
from src.google_storage import generate_download_signed_url_v4, generate_upload_signed_url_v4, cors_configuration, bucket_metadata, upload_blob, delete_blob
import uuid
from urllib.parse import urlparse

from src.ustil import ROWS_PER_PAGE
from datetime import datetime


webduty = Blueprint("webduty", __name__)


@webduty.route('/duty/delete/<int:id>')
@login_required
def delete_duty(id):

    duty_to_delete = Item.query.get_or_404(id)
    # id = current_user.person_id
    # if id == post_to_delete.poster.id:
    try:
        db.session.delete(duty_to_delete)
        db.session.commit()

        # Return a message
        flash("Duty Was Deleted!")

        
        # Grab all the posts from the database
        duties = Item.query.join(
            Image, Item.item_id == Image.item_id, isouter=True)\
            .filter(Item.menu_id == 11).all()
        return render_template("duty/duties.html", duties=duties)

    except:
        # Return an error message
        flash("Whoops! There was a problem deleting duty, try again...")

        # Grab all the posts from the database
        duties = Item.query.join(
            Image, Item.item_id == Image.item_id, isouter=True)\
            .filter(Item.menu_id == 11).all()
        return render_template("duty/duties.html", duties=duties)
    # else:
    #     # Return a message
    #     flash("You Aren't Authorized To Delete That Post!")

    #     # Grab all the posts from the database
    #     posts = Posts.query.order_by(Posts.date_posted)
    #     return render_template("posts.html", posts=posts)


@webduty.route('/duties')
@login_required
def duties():
    page = request.args.get('page', 1, type=int)
    # Grab all the programmes from the database
    duties = Item.query.join(
        Image, Item.item_id == Image.item_id, isouter=True)\
        .filter(Item.menu_id == 11).order_by(Item.updated_date.desc()).paginate(
        page=page, per_page=ROWS_PER_PAGE)

    if duties.items:
        for duty in duties.items:
            duty.created_date = duty.created_date.strftime(
                "%m/%d/%Y, %H:%M:%S")

    return render_template("/duty/duties.html", duties=duties)


@webduty.route('/duty/<int:id>')
@login_required
def duty(id):
    duty = Item.query.join(
        Churchgroup, Item.group_id == Churchgroup.group_id, isouter=True)\
        .filter(Item.item_id == id).first()

    if duty.created_date:
        duty.created_date = duty.created_date.strftime(
            "%m/%d/%Y, %H:%M:%S")
    return render_template('duty/duty.html', duty=duty)


@webduty.route('/duty/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_duty(id):
    print('edit_duty')

    duty = Item.query.get_or_404(id)
    form = DutyForm()
    form.group_id.choices = [(g.group_id, g.name)
                             for g in Churchgroup.query.all()]

    if 'filenames' in session:
        filenames = session['filenames']
    else:
        filenames = []

    if request.method == 'POST' and form.validate_on_submit():

        duty.group_id = form.group_id.data

        #remove record from db
        for image_item in duty.image:
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
                duty.image.append(Image(
                    file_name=image['name'], bucket_name='jonathan_bucket_1', item_id=id, created_date=datetime.now(), updated_date=datetime.now()))

        # Update Database
        db.session.add(duty)
        # db.session.flush()
        db.session.commit()
        flash("Duty Has Been Updated!")
        return redirect(url_for('webduty.duty', id=duty.item_id))

    # if current_user.person_id == post.person_id:

    form.item_id.data = duty.item_id
    form.group_id.data = duty.group_id

    image = []
    for image_item in duty.image:
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

    return render_template('duty/edit_duty.html', form=form)
    # else:
    # 	flash("You Aren't Authorized To Edit This Post...")
    # 	posts = Posts.query.order_by(Posts.date_posted)
    # 	return render_template("webpost.posts.html", posts=posts)


# Add Post Page
@webduty.route('/add-duty', methods=['GET', 'POST'])
@login_required
def add_duty():
    form = DutyForm()
    form.group_id.choices = [(g.group_id, g.name)
                             for g in Churchgroup.query.all()]

    if 'filenames' in session:
        filenames = session['filenames']
    else:
        filenames = []

    if request.method == 'POST' and form.validate_on_submit():
        # person_id = current_user.person_id

        # print(form.group_id.data)
        duty = Item(menu_id=11, group_id=form.group_id.data)
        db.session.add(duty)
        db.session.commit()
        # print(program.item_id)

        # Clear The Form
        duty.group_id = form.group_id.data

        #upload local image to google storage if path dont have http
        for image in filenames:
            if "http" not in image['dataURL']:
                bucket_name = cors_configuration('jonathan_bucket_1')
                upload_blob(bucket_name, image['dataURL'], image['name'])
                #update to db
                duty.image.append(Image(
                    file_name=image['name'], bucket_name='jonathan_bucket_1', item_id=duty.item_id, created_date=datetime.now(), updated_date=datetime.now()))

        # # Add post data to database
        db.session.add(duty)
        db.session.commit()

        # Return a Message
        flash("Duty Submitted Successfully!")
        return redirect(url_for('webduty.duties'))

    form.images.data = []
    filenames.clear()
    session['filenames'] = filenames
    session.permanent = True
    # Redirect to the webpage
    return render_template("duty/add_duty.html", form=form)
