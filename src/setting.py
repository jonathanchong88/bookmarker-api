from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import db, Person
from flasgger import swag_from

setting = Blueprint("setting", __name__, url_prefix="/api/v1/setting")

@setting.post("/language")
@jwt_required()
def set_language():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        language_code = request.get_json().get('language_code', '')

        # print(language_code)

        if language_code == 'en':
            person.language = 1
        else:
            person.language = 2

        db.session.add(person)
        db.session.commit()

        return jsonify({
            'status': 0,
            'message': "Successfully updated language",
        }), HTTP_200_OK

    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
