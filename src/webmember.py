from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import validators
from src.database2 import PersonDetail, db, Image, Churchgroup, DutyRole, person_duty_role, PersonStatus, person_group
from flask_login import login_user, login_required, logout_user, current_user
from src.webform import MemberForm
from src.ustil import solve
import os
from src.google_storage import generate_download_signed_url_v4, generate_upload_signed_url_v4, cors_configuration, bucket_metadata, upload_blob_stream, delete_blob
import uuid
from urllib.parse import urlparse
from src.ustil import GENDER_CHOICES

from src.ustil import ROWS_PER_PAGE
from datetime import datetime


webmember = Blueprint("webmember", __name__)


@webmember.route('/member/delete/<int:id>')
@login_required
def delete_member(id):
    member_to_delete = PersonDetail.query.get_or_404(id)
    # id = current_user.person_id
    # if id == post_to_delete.poster.id:
    try:
        db.session.delete(member_to_delete)
        db.session.commit()

        # Return a message
        flash("Member Was Deleted!")

        # Grab all the posts from the database
        return redirect(url_for('webmember.members'))

    except:
        # Return an error message
        flash("Whoops! There was a problem deleting member, try again...")

        # Grab all the posts from the database
        return redirect(url_for('webmember.members'))
    # else:
    #     # Return a message
    #     flash("You Aren't Authorized To Delete That Post!")

    #     # Grab all the posts from the database
    #     posts = Posts.query.order_by(Posts.date_posted)
    #     return render_template("posts.html", posts=posts)


@webmember.route('/members')
@login_required
def members():
    page = request.args.get('page', 1, type=int)
    # Grab all the programmes from the database
    members = PersonDetail.query.join(
        Image, Image.person_detail_id == PersonDetail.person_detail_id, isouter=True)\
        .order_by(PersonDetail.last_name).paginate(
        page=page, per_page=ROWS_PER_PAGE)

    return render_template("/member/members.html", members=members)


@webmember.route('/member/<int:id>')
@login_required
def member(id):
    member = PersonDetail.query.join(
        Image, Image.person_detail_id == PersonDetail.person_detail_id, isouter=True)\
        .filter(PersonDetail.person_detail_id == id).first()
    
    if member.created_date:
        member.created_date = member.created_date.strftime(
            "%m/%d/%Y, %H:%M:%S")

    person_status=''
    if member.person:
        _person_status = PersonStatus.query.filter_by(person_status_id=member.person.person_status_id).first()
        person_status = _person_status.status_type
        # print(person_status.status_type)

    image_url = ''
    if len(member.image) > 0:
        bucket_name = cors_configuration(member.image[0].bucket_name)
        image_url = generate_download_signed_url_v4(bucket_name, member.image[0].file_name)
        
    return render_template('member/member.html', member=member, image_url=image_url, status=person_status)


@webmember.route('/member/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    print('edit_member')

    member = PersonDetail.query.get_or_404(id)
    form = MemberForm()

    form.gender.choices = GENDER_CHOICES
    form.duty_roles.choices = [(g.duty_role_id, g.duty_role_type)
                               for g in DutyRole.query.all()]
    form.status.choices = [(g.person_status_id, g.status_type)
                               for g in PersonStatus.query.all()]
    form.groups.choices = [(g.group_id, g.name)
                           for g in Churchgroup.query.all()]

    isRegisted = False
    print('edit_member->'+str(form.validate_on_submit()))

    if request.method == 'POST' and form.validate_on_submit():
        # print('edit_member->'+str(form.duty_roles.data))
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.gender = form.gender.data
        member.address = form.address.data
        member.nickname = form.nickname.data
        member.phone_number = form.phone_number.data
        member.nationality = form.nationality.data
        member.date_of_birth = form.date_of_birth.data
        member.person.person_status_id = form.status.data
        
        #delete duty role record and assign new records
        if form.duty_roles.data:
            for memberroleid in member.dutyroles:
                db.session.execute(person_duty_role.delete().where(
                    person_duty_role.c.duty_role_id == memberroleid.duty_role_id))
            for role_id in form.duty_roles.data:
                db.session.execute(person_duty_role.insert().values(
                    person_detail_id=member.person_detail_id, duty_role_id=role_id))
                db.session.commit()

        if form.groups.data:
            for groupid in member.group:
                db.session.execute(person_group.delete().where(
                    person_group.c.group_id == groupid.group_id))
            for group_id in form.groups.data:
                db.session.execute(person_group.insert().values(
                    person_detail_id=member.person_detail_id, group_id=group_id))
                db.session.commit()
        
                
        if form.image.data:
            print(form.image.data)
            bucket_name = cors_configuration('jonathan_bucket_1')
            if len(member.image) > 0:
                delete_blob(bucket_name, member.image[0].file_name)
                imageItem = Image.query.filter_by(
                    file_name=member.image[0].file_name).first()
                
                db.session.delete(imageItem)
                db.session.commit()

            filename = str(uuid.uuid4()) + \
                secure_filename(form.image.data.filename)
            upload_blob_stream(bucket_name, form.image.data, filename)
            member.image.append(Image(file_name=filename, bucket_name='jonathan_bucket_1',
                                person_detail_id=member.person_detail_id))
            
                
        # Update Database
        db.session.add(member)
        db.session.flush()
        db.session.commit()
        flash("Member Has Been Updated!")
        return redirect(url_for('webmember.member', id=member.person_detail_id))

    # if current_user.person_id == post.person_id:

    form.last_name.data = member.last_name
    form.first_name.data = member.first_name
    form.nickname.data = member.nickname
    form.gender.data = member.gender
    form.address.data = member.address
    form.phone_number.data = member.phone_number
    form.nationality.data = member.nationality
    if member.person:
        isRegisted = True
        member.person.person_status_id = form.status.data
    cr_date = ''
    if member.date_of_birth:
        cr_date = str(member.date_of_birth)
        cr_date = datetime.strptime(cr_date, '%Y-%m-%d')
    form.date_of_birth.data = cr_date
    form.person_detail_id.data = member.person_detail_id
    duty_role_id = []
    if member.dutyroles:
        for dutyroleid in member.dutyroles:
            duty_role_id.append(dutyroleid.duty_role_id)
        print(duty_role_id)
    form.duty_roles.data = duty_role_id
    group_id = []
    if member.group:
        for groupid in member.group:
            group_id.append(groupid.group_id)
        print(group_id)
    form.groups.data = group_id

    return render_template('member/edit_member.html', form=form, isRegisted=isRegisted)
    # else:
    # 	flash("You Aren't Authorized To Edit This Post...")
    # 	posts = Posts.query.order_by(Posts.date_posted)
    # 	return render_template("webpost.posts.html", posts=posts)


# Add Post Page
@webmember.route('/add-member', methods=['GET', 'POST'])
@login_required
def add_member():
    form = MemberForm()

    form.gender.choices = GENDER_CHOICES
    form.duty_roles.choices = [(g.duty_role_id, g.duty_role_type)
                               for g in DutyRole.query.all()]
    form.status.choices = [(g.person_status_id, g.status_type)
                           for g in PersonStatus.query.all()]

    isRegisted = False
    if request.method == 'POST' and form.validate_on_submit():

        member = PersonDetail(first_name=form.first_name.data)
        db.session.add(member)
        db.session.commit()

        # Clear The Form
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.gender = form.gender.data
        member.address = form.address.data
        member.nickname = form.nickname.data
        member.phone_number = form.phone_number.data
        member.nationality = form.nationality.data
        member.date_of_birth = form.date_of_birth.data
        
        if member.person:
            isRegisted = True
            member.person.person_status_id = form.status.data
        # upload local image to google storage if path dont have http
        #delete duty role record and assign new records
        if form.duty_roles.data:
            for memberroleid in member.dutyroles:
                db.session.execute(person_duty_role.delete().where(
                    person_duty_role.c.duty_role_id == memberroleid.duty_role_id))
            for role_id in form.duty_roles.data:
                db.session.execute(person_duty_role.insert().values(
                    person_detail_id=member.person_detail_id, duty_role_id=role_id))
                db.session.commit()

        if form.image.data:
            print(form.image.data)
            bucket_name = cors_configuration('jonathan_bucket_1')
            if len(member.image) > 0:
                delete_blob(bucket_name, member.image[0].file_name)
                imageItem = Image.query.filter_by(
                    file_name=member.image[0].file_name).first()

                db.session.delete(imageItem)
                db.session.commit()

            filename = str(uuid.uuid4()) + \
                secure_filename(form.image.data.filename)
            upload_blob_stream(bucket_name, form.image.data, filename)
            member.image.append(Image(file_name=filename, bucket_name='jonathan_bucket_1',
                                person_detail_id=member.person_detail_id))

        # Update Database
        db.session.add(member)
        db.session.flush()
        db.session.commit()

        # Return a Message
        flash("Member Submitted Successfully!")
        return redirect(url_for('webmember.members'))

    form.date_of_birth.data = ''
    # Redirect to the webpage
    return render_template("member/add_member.html", form=form, isRegisted=isRegisted)
