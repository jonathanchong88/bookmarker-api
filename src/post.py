from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database2 import Person, db, Posts
from flask_login import login_user, login_required, logout_user, current_user
from src.webform import  PostForm

webpost = Blueprint("webpost", __name__)


@webpost.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if id == post_to_delete.poster.id:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()

			# Return a message
			flash("Blog Post Was Deleted!")

			# Grab all the posts from the database
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)

		except:
			# Return an error message
			flash("Whoops! There was a problem deleting post, try again...")

			# Grab all the posts from the database
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)
	else:
		# Return a message
		flash("You Aren't Authorized To Delete That Post!")

		# Grab all the posts from the database
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)


@webpost.route('/posts')
def posts():
	# Grab all the posts from the database
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


@webpost.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post=post)

@webpost.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		#post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update Database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated!")
		return redirect(url_for('webpost.post', id=post.id))

	if current_user.person_id == post.person_id:
		form.title.data = post.title
		#form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form=form)
	else:
		flash("You Aren't Authorized To Edit This Post...")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("webpost.posts.html", posts=posts)


# Add Post Page
@webpost.route('/add-post', methods=['GET', 'POST'])
#@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		person_id = current_user.person_id
		post = Posts(title=form.title.data, content=form.content.data,
		             person_id=person_id, slug=form.slug.data)
		# Clear The Form
		form.title.data = ''
		form.content.data = ''
		#form.author.data = ''
		form.slug.data = ''

		# Add post data to database
		db.session.add(post)
		db.session.commit()

		# Return a Message
		flash("Blog Post Submitted Successfully!")

	# Redirect to the webpage
	return render_template("add_post.html", form=form)
