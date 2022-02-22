from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import db, Person, DutyRole, Image, PhoneNumber, Location, PersonDetail
from flasgger import swag_from
from sqlalchemy.orm import aliased
from datetime import datetime
from src.google_storage import delete_blob, generate_download_signed_url_v4

profile = Blueprint("profile", __name__, url_prefix="/api/v1/profile")

@profile.get("/")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_profile():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
            # .join(PhoneNumber, Person.person_id == PhoneNumber.person_id, isouter=True)\
            # .join(Location, Person.person_id == Location.person_id, isouter=True)\
        member = PersonDetail.query.join(
            Image, Image.person_detail_id == PersonDetail.person_detail_id, isouter=True)\
            .filter(PersonDetail.person_id == person.person_id).first()

        if member:
            duties = []
            # numbers = []
            # locations = []
            image_url = ''

            if member.dutyroles:
                for duty in member.dutyroles:
                    duties.append({
                        'duty': duty.duty_role_type,
                        # 'created_date': duty.created_date.isoformat(),
                    })

            # if member.phonenumber:
            #     for _phonenumber in member.phonenumber:
            #         numbers.append({
            #             'number': _phonenumber.number,
            #         })

            # if member.location:
            #     for _location in member.location:
            #         locations.append({
            #             'address_line_1': _location.address_line_1,
            #             'address_line_2':  _location.address_line_2,
            #             'postcode':  _location.postcode,
            #             'city': _location.city,
            #             'state': _location.state,
            #             'country': _location.country
            #         })

            if member.image:
                    image_url =  'https://d626yq9e83zk1.cloudfront.net/files/share-odb-2020-01-01.jpg'
                 
                # generate_download_signed_url_v4(
                #     member.image[0].bucket_name, member.image[0].file_name)

            return jsonify({'person_id': member.person_id,
                            "name": member.first_name + ' ' + member.last_name,
                            'nickname': member.nickname,
                            'first_name': member.first_name,
                            'last_name': member.last_name,
                            'gender': member.gender,
                            'email': member.email,
                            'date_of_birth': member.date_of_birth.isoformat(),
                            'created_date': member.created_date.isoformat(),
                            "duties": duties,
                            'profile_image': image_url,
                            'phone_number': member.phone_number,
                            'nationality': member.nationality,
                            'address': member.address,
                            # 'numbers': numbers,
                            # 'locations': locations,
                            }), HTTP_200_OK
        else:
            return jsonify({'person_id': person.person_id,
                            "name": None,
                            'nickname': None,
                            'first_name': None,
                            'last_name': None,
                            'gender': None,
                            'email': person.email,
                            'date_of_birth': None,
                            'created_date': person.created_date.isoformat(),
                            "duties": [],
                            'profile_image': None,
                            'phone_number': None,
                            'nationality': None,
                            'address': None,
                            # 'numbers': numbers,
                            # 'locations': locations,
                            }), HTTP_200_OK
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


# @profile.post('/delete')
# @jwt_required()
# def delete_file():

#     result = delete_blob('jonathan_bucket_1', 'old_image')

#     if not result:
#         return jsonify({
#             'status': 0,
#             'message': "file not deleted {}".format(result),
#         }), HTTP_200_OK
#     else:
#         return jsonify({
#             'status': 0,
#             'message': "file deleted {}".format(result),
#         }), HTTP_200_OK

@profile.post('/update')
@jwt_required()
def update_profile():

    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if not person:
            return jsonify({'message': 'Person not found'}), HTTP_404_NOT_FOUND

    if person:
        first_name = request.get_json().get('first_name', '')
        last_name = request.get_json().get('last_name', '')
        nickname = request.get_json().get('nickname', '')
        gender = request.get_json().get('gender', '')
        dob = request.get_json().get('date_of_birth', '')
        phone_number = request.get_json().get('phone_number', '')
        nationality = request.get_json().get('nationality', '')
        address = request.get_json().get('address', '')
        bucket_name = 'jonathan_bucket_1'
        file_name = request.get_json().get('file_name', '')

        person.first_name = first_name
        person.last_name = last_name
        person.nickname = nickname
        person.genders = gender
        person.date_of_birth = dob
        person.phone_number = phone_number
        person.nationality = nationality
        person.address = address
        person.updated_date = datetime.now()
        db.session.commit()

        if file_name:

            image = Image.query.filter_by(person_id=person_id).first()

            if image:
                old_image = image.file_name
                image.file_name = file_name
                image.updated_date = datetime.now()
                db.session.commit()
                #delete image
                delete_blob(bucket_name, old_image)
                
            else:
                person_new = Person(file_name=file_name, bucket_name=bucket_name, person_id=person_id,)
                db.session.add(person_new)
                db.session.commit()

        return jsonify({
            'status': 0,
            'message': "Profile updated",
        }), HTTP_200_OK
    else:
        return jsonify({'message': 'Person not found'}), HTTP_404_NOT_FOUND


   