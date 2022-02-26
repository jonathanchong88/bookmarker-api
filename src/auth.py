from flask import Blueprint, request, jsonify, url_for, render_template, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database2 import Person, db, person_schema, persons_schema, PersonDetail
# from src.database import User, db, user_schema, users_schema
from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flasgger import swag_from
# from src.google_storage import generate_upload_signed_url_v4
from src.security import ts
from src.email import send_email
import pyotp 
# import time
import datetime
from src.firebase_send_msg import send_to_token
from src.test_send import test_send, test_send_invalid_token

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post("/register")
@swag_from('./docs/auth/register.yaml')
def register():
    # first_name = request.json['first_name']
    # last_name = request.json['last_name']
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

    person = Person(password=pwd_hash, email=email,
                    person_status_id=2, confirmed=False)
    db.session.add(person)
    db.session.commit()

    # Now we'll send the email confirmation link
    subject = "Confirm your email"

    token = ts.dumps(person.email, salt='email-confirm-key')

    confirm_url = url_for(
        'auth.confirm_email',
        token=token,
        _external=True)

    html = render_template(
        'email/activate.html',
        confirm_url=confirm_url)

    # We'll assume that send_email has been defined in myapp/util.py
    status = send_email(person.email, subject, html)

    if status is False:
        db.session.delete(person)
        db.session.commit()
        return jsonify({
            'error': 'Unable to create account. Please contact your administrator.'

        }), HTTP_409_CONFLICT
    # flash('A confirmation email has been sent via email.', 'success')

    return jsonify({
        'status': 0,
        'message': "User created",
        'data': {
             "email": email
        }

    }), HTTP_201_CREATED


@auth.post("/login")
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')
    fcmToken = request.json.get('fcm_token', '')

    person = Person.query.filter_by(email=email).first()

    if person:
        print(person.email)
        
        is_pass_correct = check_password_hash(person.password, password)

        if is_pass_correct:

            print(person.confirmed)

            if person.confirmed is False:
                return jsonify({'error': 'Account not email comfirmed yet.'}), HTTP_401_UNAUTHORIZED

            # person_detail = PersonDetail.query.filter_by(PersonDetail.person_id=person.persson_id).first()

            # if person_detail is None:
            #     return jsonify({'error': 'Account not approved by administrator yet.'}), HTTP_401_UNAUTHORIZED

            expires = datetime.timedelta(minutes=60)
            refresh = create_refresh_token(identity=person.person_id)
            access = create_access_token(
                identity=person.person_id, expires_delta=expires)

            #assign fcm token
            if fcmToken:
                print(fcmToken)
                person.fcm_token = fcmToken
                db.session.commit()

            test_send_invalid_token("LCMS APP", "Successfully login", {'score':'850'},
                                    person.fcm_token)

            return jsonify({
                'status': 0,
                'message': "Successfully login",
                'data': {
                    'refresh': refresh,
                    'access': access,
                    'email': person.email,
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.post("/social/login")
# @swag_from('./docs/auth/register.yaml')
def social_login():
    # first_name = request.json['first_name']
    # last_name = request.json['last_name']
    password = request.json['password']
    email = request.json['email']
    fcmToken = request.json['fcm_token']

    pwd_hash = generate_password_hash(password)

    person = Person(password=pwd_hash, email=email,
                    person_status_id=2,fcm_token=fcmToken, confirmed=true)
    db.session.add(person)
    db.session.commit()

    expires = datetime.timedelta(minutes=60)
    refresh = create_refresh_token(identity=person.person_id)
    access = create_access_token(
        identity=person.person_id, expires_delta=expires)

    return jsonify({
        'status': 0,
        'message': "Successfully login",
        'data': {
            'refresh': refresh,
            'access': access,
            'email': person.email
        }

    }), HTTP_200_OK


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
        'data': {
             'access': access
        }
       
    }), HTTP_200_OK


@auth.get('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    person = Person.query.filter_by(email=email).first_or_404()

    if person.confirmed:
        return render_template(
            'email/invalid_activate.html')

    person.confirmed = True

    db.session.add(person)
    db.session.commit()

    return render_template(
        'email/success_activate.html')


@auth.post('/forgot')
def forgot_password():

    email = request.json['email']

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    person = Person.query.filter_by(email=email).first()

    if person:
        ram_base32 = pyotp.random_base32()
        print('person.otp_secret before ' + ram_base32)
        totp = pyotp.TOTP(s=ram_base32, interval=900)
        otp = totp.now()
        person.otp_secret = ram_base32
        db.session.add(person)
        db.session.commit()

        # Now we'll send the otp to email
        subject = "Your OTP for reset password"


        html = render_template(
            'forgot.html',
            otp=otp)

        send_email(person.email, subject, html)
    else:
        return jsonify({'error': "Email is invalid."}), HTTP_409_CONFLICT


    return jsonify({
        'status': 0,
        'message': "Successfully set new password",

    }), HTTP_200_OK


@auth.post('/forgot/new')
def forgot_password_new():

    new_password = request.json['password']
    otp = request.json['otp']
    email = request.json['email']

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    person = Person.query.filter_by(email=email).first()
   
    if person:
        if not person.otp_secret:
            return jsonify({'error': "Otp is not valid"}), HTTP_400_BAD_REQUEST
        totp = pyotp.TOTP(s=person.otp_secret, interval=900)
        isOtpValid = totp.verify(otp)

        if isOtpValid:
            pwd_hash = generate_password_hash(new_password)
            person.password = pwd_hash
            person.otp_secret = None
            db.session.add(person)
            db.session.commit()
        else:
            return jsonify({'error': "OTP is expired."}), HTTP_409_CONFLICT
    else:
        return jsonify({'error': "Email is invalid."}), HTTP_409_CONFLICT

    return jsonify({
        'status': 0,
        'message': "Successfully create new password",

    }), HTTP_200_OK


@auth.post('/changepassword')
@jwt_required()
def change_password():

    current_password = request.json['current_password']
    new_password = request.json['new_password']

    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        is_pass_correct = check_password_hash(
            person.password, current_password)

        if is_pass_correct:
            pwd_hash = generate_password_hash(new_password)
            person.password = pwd_hash
            db.session.commit()
        else:
            return jsonify({'error': "Current password is incorrect."}), HTTP_401_UNAUTHORIZED
    else:
        return jsonify({'error': "Person is not found."}), HTTP_401_UNAUTHORIZED

    return jsonify({
        'status': 0,
        'message': "Successfully create new password",

    }), HTTP_200_OK
