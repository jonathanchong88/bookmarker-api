from flask import Flask, redirect, jsonify, request, session
import os
from src.auth import auth
from src.menu import menus
from src.item import item
from src.song import song
# from src.duty import duty
from src.database2 import db, ma, Person
# from src.database import db, Bookmark, ma
from flask_jwt_extended import JWTManager
from src.constant.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from flask_migrate import Migrate
from src.email import mail
from src.member import member
from src.profile import profile
from src.website.webAuth import webAuth
from src.website.views import views
from flask_login import LoginManager
from src.post import webpost
from src.activity import webactivity
from src.webprogram import webprogram
from src.zhouxun import webzhouxun
from src.webduty import webduty
from src.websong import websong
from src.webmember import webmember
from src.webdutyrole import webdutyrole
from src.loadprivacy import webprivacy
from src.ustil import solve, allowed_file, basedir
from flask_ckeditor import CKEditor
import uuid
from werkzeug.utils import secure_filename
from src.appScedular import scheduler

from urllib.parse import urlparse
from datetime import datetime


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # print('csdcsdc' + os.environ.get("TEST"))
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"), 
            SQLALCHEMY_DATABASE_URI=os.environ.get(
                "DATABASE_URL").replace("://", "ql://", 1),
            SQLALCHEMY_TRACK_MODIFICATIONS=False, 
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'), 
            SWAGGER={
                'title': "Bookmarks API",
                'uiversion': 3
            })
        UPLOAD_FOLDER = 'static/uploads'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    else:
        app.config.from_mapping(test_config)

    JWTManager(app)

    db.app = app
    db.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(webAuth)
    app.register_blueprint(menus)
    app.register_blueprint(item)
    app.register_blueprint(song)
    # app.register_blueprint(duty)
    app.register_blueprint(member)
    app.register_blueprint(profile)
    app.register_blueprint(views)
    app.register_blueprint(webpost)
    app.register_blueprint(webactivity)
    app.register_blueprint(webprogram)
    app.register_blueprint(webzhouxun)
    app.register_blueprint(webduty)
    app.register_blueprint(websong)
    app.register_blueprint(webmember)
    app.register_blueprint(webdutyrole)
    app.register_blueprint(webprivacy)
    # ma.app = app
    ma.init_app(app)
    ckeditor = CKEditor(app)

    login_manager = LoginManager()
    login_manager.login_view = 'webauth.loginPage'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Person.query.get(id)

    print(os.environ.get('APP_MAIL_USERNAME'))
    print(os.environ.get('APP_MAIL_PASSWORD'))

   
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get('APP_MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('APP_MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@fyneos88.gmail.com'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.app = app
    mail.init_app(app)

    migrate = Migrate(app, db)

    # with app.app_context():
    #     db.create_all()

    Swagger(app, config=swagger_config, template=template)

    # delete_upload_dir2()

    # @app.get('/<short_url>')
    # @swag_from('./docs/short_url.yaml')
    # def redirect_to_url(short_url):
    #     bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

    #     if bookmark:
    #         bookmark.visits = bookmark.visits+1
    #         db.session.commit()
    #         return redirect(bookmark.url)


    @app.route('/delete_upload_dir')
    def delete_upload_dir():
        folder = os.path.join(basedir,
                              app.config['UPLOAD_FOLDER'])

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        
        return jsonify({'success': 'clear'}), HTTP_200_OK


    @app.route('/upload', methods=['POST', 'GET'])
    def upload():

        if request.method == 'POST':
            file = request.files['file']
            filename = str(uuid.uuid4()) + secure_filename(file.filename)
            now = datetime.now()
            if file and allowed_file(file.filename):
                # session['filenames'] = filenames

                # print(session['filenames'])
                file_dir = os.path.join(basedir,
                                        app.config['UPLOAD_FOLDER'])
                # if not os.path.exists(file_dir):
                #     os.mkdir(file_dir)
                file_path = os.path.join(file_dir, filename)
                # print(file_path)
                file.save(file_path)

                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                # print(filenames)
                session['filenames'].append(
                    {'name': filename, 'size': file_length, 'dataURL': file_path})
                print(session['filenames'])
                return filename

        msg = 'success calling'
        return jsonify(msg)


    @app.route('/delete', methods=['POST', 'GET'])
    def delete_image():

        if request.method == 'POST':
            filename = request.json['filename']
            filePath = request.json['filePath']
            # print(filename)
            # print(filePath)
            if 'filenames' in session:
                filenames = session['filenames']
            else:
                filenames = []

            print(filenames)

            # #delete filename is not contain http
            if "http" not in filePath:
                index = solve('name', filePath, filenames)
                # print(index)
                file_dir = os.path.join(basedir,
                                        app.config['UPLOAD_FOLDER'])
                file_path = os.path.join(file_dir, filePath)
                os.remove(file_path)
            else:
                index = solve('name', filename, filenames)
            print(index)
            # print(len(filenames))
            filenames.pop(index)
            session['filenames'] = filenames
            print(len(session['filenames']))
            # print(filenames)
        msg = 'success calling'
        return jsonify(msg)


    @app.route('/video/id', methods=['POST'])
    def getvideo_id():
        if request.method == 'POST':
            video_url = request.json['video_url']

            print(video_id(video_url))
            return jsonify({'data': video_id(video_url)})


    def video_id(value):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        query = urlparse(value)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    
    return app
