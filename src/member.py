from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import PersonDetail, db, Image, Churchgroup, DutyRole, person_duty_role, PersonStatus, person_group, Person
from flasgger import swag_from
from sqlalchemy.orm import aliased

member = Blueprint("member", __name__, url_prefix="/api/v1/member")


@member.get("/")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_members():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()
    group_id = request.args.get('id', 4, type=int)
    

    if person:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        member_list = PersonDetail.query.join(
            Image, Image.person_detail_id == PersonDetail.person_detail_id, isouter=True)\
            .join(Person)\
            .filter(Person.person_status_id==1)\
            .filter(PersonDetail.group.any(Churchgroup.group_id ==group_id))\
            .order_by(PersonDetail.last_name).paginate(
            page=page, per_page=per_page)
        if member_list:
            data = []
            for member in member_list.items:
                print(member.person.person_status_id)

                data.append({
                    'person_detail_id' : str(member.person_detail_id),
                    'name': member.first_name + ' ' + member.last_name
                })

            meta = {
                "page": member_list.page,
                'pages': member_list.pages,
                'total_count': member_list.total,
                'prev_page': member_list.prev_num,
                'next_page': member_list.next_num,
                'has_next': member_list.has_next,
                'has_prev': member_list.has_prev,
            }

            return jsonify({'member': data, "meta": meta}), HTTP_200_OK
        else:
            return jsonify({'error': 'member not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@member.get("/detail")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_member_detail():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()
    person_detail_id = request.args.get('id', type=str)

    if person:
        member = PersonDetail.query.join(
            Image, Image.person_detail_id == PersonDetail.person_detail_id, isouter=True)\
            .filter(PersonDetail.person_detail_id == person_detail_id).first()
            

        # ml = PersonDutyRole.query.join(
        #     DutyRole, DutyRole.duty_role_id == PersonDutyRole.duty_role_id).subquery().alias('anon_1')

        if member:
            duties = []
            numbers = []
            locations = []
            image_url = ''

            if member.dutyroles:
                for duty in member.dutyroles:
                    duties.append({
                        'duty': duty.duty_role_type,
                        # 'created_date': duty.created_date.isoformat(),
                    })

            # if member.location:
            #     for _location in member.location:
            #         locations.append({
            #             'address_line_1': _location.address_line_1,
            #             'address_line_2':  _location.address_line_2,
            #             'postcode':  _location.postcode,
            #             'city': _location.city,
            #             'state': _location.state,
            #             'country': _location.country
            #             })

            # person_status = ''
            # if member.person:
            #     _person_status = PersonStatus.query.filter_by(
            #         person_status_id=member.person.person_status_id).first()


            if member.image:
                image_url = 'https://d626yq9e83zk1.cloudfront.net/files/share-odb-2020-01-01.jpg'

            return jsonify({'person_id': member.person_id, 
                            "name": member.first_name + ' ' + member.last_name,
                            'nickname': member.nickname,
                            'gender': member.gender,
                            'email': member.person.email,
                            'date_of_birth': member.date_of_birth.isoformat(),
                            'created_date': member.created_date.isoformat(),
                            "duties": duties,
                            'profile_image': image_url,
                            'phone_number': member.phone_number,
                            'address': member.address,
                            # 'status': _person_status.status_type,
                            }), HTTP_200_OK
        else:
            return jsonify({'error': 'member not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
