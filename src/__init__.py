from flask import Flask, redirect, jsonify
import os
from src.auth import auth
from src.menu import menus
from src.item import item
from src.song import song
from src.duty import duty
from src.database2 import db, ma
# from src.database import db, Bookmark, ma
from flask_jwt_extended import JWTManager
from src.constant.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from flask_migrate import Migrate
from src.email import mail
from src.member import member
from src.profile import profile


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"), 
            # SQLALCHEMY_DATABASE_URI=os.environ.get(
            #     "DATABASE_URL").replace("://", "ql://", 1),
            # SQLALCHEMY_DATABASE_URI="postgresql://postgres:As5201314@localhost/postgres",
            SQLALCHEMY_DATABASE_URI="postgresql://nvaqwtbctrvhcd:2dcaef125c2cff007a7a0ab237dff2d891ead044e7ebc7c4c99e6994b5d7b724@ec2-35-169-49-157.compute-1.amazonaws.com:5432/drddv61fm0c69",
            SQLALCHEMY_TRACK_MODIFICATIONS=False, 
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'), 
            SWAGGER={
                'title': "Bookmarks API",
                'uiversion': 3
            })
    else:
        app.config.from_mapping(test_config)

    JWTManager(app)

    db.app = app
    db.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(menus)
    app.register_blueprint(item)
    app.register_blueprint(song)
    app.register_blueprint(duty)
    app.register_blueprint(member)
    app.register_blueprint(profile)
    # ma.app = app
    ma.init_app(app)
   
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'fyneos88@gmail.com'
    app.config['MAIL_PASSWORD'] = 'As5201314!@#$'
    app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@fyneos88.gmail.com'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.app = app
    mail.init_app(app)

    migrate = Migrate(app, db)

    # with app.app_context():
    #     db.create_all()

    Swagger(app, config=swagger_config, template=template)

    # @app.get('/<short_url>')
    # @swag_from('./docs/short_url.yaml')
    # def redirect_to_url(short_url):
    #     bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

    #     if bookmark:
    #         bookmark.visits = bookmark.visits+1
    #         db.session.commit()
    #         return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    
    return app
