from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database2 import Person, db, person_schema, persons_schema
# from src.database import User, db, user_schema, users_schema
from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flasgger import swag_from
# from src.google_storage import generate_upload_signed_url_v4

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post("/register")
@swag_from('./docs/auth/register.yaml')
def register():
    # username=request.json['username']
    password = request.json['password']
    email = request.json['email']

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    # if len(username) < 3:
    #     return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

    # if not username.isalnum() or " " in username:
    #     return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if Person.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is takens"}), HTTP_409_CONFLICT

    # if User.query.filter_by(username=username).first() is not None:
    #     return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    person = Person( password=pwd_hash, email=email, status='active')
    db.session.add(person)
    db.session.commit()

    return person_schema.jsonify(person), HTTP_201_CREATED

    # return jsonify({
    #     'message': "User created",
    #     'user': {
    #         'username': username, "email": email
    #     }

    # }), HTTP_201_CREATED


@auth.post("/login")
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    person = Person.query.filter_by(email=email).first()

    if person:
        is_pass_correct = check_password_hash(person.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=person.person_id)
            access = create_access_token(identity=person.person_id)

            return jsonify({
                'person': {
                    'refresh': refresh,
                    'access': access,
                    'email': person.email
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required()
def me():
    # if 'x-access-tokens' in request.headers:
    # print(request.headers['x-access-tokens'])
    person_id = get_jwt_identity()
    person = Person.query.filter_by(person_id=person_id).first()
    # url = generate_upload_signed_url_v4('jonathan_bucket_1', 'hello')
    # print(url)

    if not person.date_of_birth:
        test = ''
    else:
        test = person.date_of_birth

    return jsonify({
        'data': {
            'first_name': person.first_name,
            'last_name': person.last_name,
            'nickname': person.nickname,
            'email': person.email,
            'status': person.status,
            'created_date': person.created_date,
            'date_of_birth': person.date_of_birth,
            'age': test
        }

    }), HTTP_200_OK


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK
