from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import validators
from src.database2 import db, DutyRole
from flask_login import login_user, login_required, logout_user, current_user
from src.webform import DutyRoleForm
from src.ustil import ROWS_PER_PAGE
import os
from src.google_storage import generate_download_signed_url_v4, generate_upload_signed_url_v4, cors_configuration, bucket_metadata, upload_blob_stream, delete_blob

from datetime import datetime


webdutyrole = Blueprint("webdutyrole", __name__)

@webdutyrole.route('/dutyrole/delete/<int:id>')
@login_required
def delete_dutyrole(id):
   
    dutyrole_to_delete = DutyRole.query.get_or_404(id)
    # id = current_user.person_id
    # if id == post_to_delete.poster.id:
    try:
        db.session.delete(dutyrole_to_delete)
        db.session.commit()

        # Return a message
        flash("Duty Role Was Deleted!")

        # Grab all the posts from the database
        return redirect(url_for('webdutyrole.dutyroles'))

    except:
        # Return an error message
        flash("Whoops! There was a problem deleting duty role, try again...")

        # Grab all the posts from the database
        return redirect(url_for('webdutyrole.dutyroles'))
    # else:
    #     # Return a message
    #     flash("You Aren't Authorized To Delete That Post!")

    #     # Grab all the posts from the database
    #     posts = Posts.query.order_by(Posts.date_posted)
    #     return render_template("posts.html", posts=posts)



@webdutyrole.route('/dutyroles')
@login_required
def dutyroles():
    # Grab all the programmes from the database
    page = request.args.get('page', 1, type=int)
    dutyroles = DutyRole.query.order_by(DutyRole.duty_role_type).paginate(
        page=page, per_page=ROWS_PER_PAGE)
    form = DutyRoleForm()

    return render_template("/duty_role/duty_roles.html", dutyroles=dutyroles, form=form)


# @webdutyrole.route('/dutyrole/<int:id>')
# def dutyrole(id):
#     member = DutyRole.query.filter(PersonDetail.person_detail_id == id).first()

#     return render_template('member/member.html', member=member, image_url=image_url, status=person_status)


# @webdutyrole.route('/dutyrole/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_dutyrole(id):
#     print('edit_member')

#     if request.method == 'POST' and form.validate_on_submit():
      
#         # Update Database
#         db.session.add(member)
#         db.session.flush()
#         db.session.commit()
#         flash("Member Has Been Updated!")
#         return redirect(url_for('webmember.member', id=member.person_detail_id))

#     # if current_user.person_id == post.person_id:

#     return render_template('member/edit_member.html', form=form, isRegisted=isRegisted)
#     # else:
#     # 	flash("You Aren't Authorized To Edit This Post...")
#     # 	posts = Posts.query.order_by(Posts.date_posted)
#     # 	return render_template("webpost.posts.html", posts=posts)


# Add Post Page
@webdutyrole.route('/add-dutyrole', methods=['GET', 'POST'])
@login_required
def add_dutyrole():
    form = DutyRoleForm()

    print(str(form.validate_on_submit()))
   
    if request.method == 'POST' and form.validate_on_submit():

        print(form.type.data)

        dutyrole = DutyRole(duty_role_type=form.type.data)

        # Update Database
        db.session.add(dutyrole)
        db.session.flush()
        db.session.commit()

        # Return a Message
        flash("Duty role Submitted Successfully!")
        return redirect(url_for('webdutyrole.dutyroles'))

    # Redirect to the webpage
    flash(form.errors)
    return redirect(url_for('webdutyrole.dutyroles'))
