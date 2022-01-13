from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import db, Person, Duty, duty_schema, dutys_schema, Image
from flasgger import swag_from

duty = Blueprint("duty", __name__, url_prefix="/api/v1/duty")


@duty.get("/")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_duty():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        duty_list = Duty.query.join(Image, Duty.duty_id == Image.duty_id)\
            .paginate(page=page, per_page=per_page)

        # print(song_list)

        if duty_list:
            data = []

            for duty in duty_list.items:

                # print()

                image = []
                for image_item in duty.image:
                    print(image_item.bucket_name)
                    image.append({
                        # generate_download_signed_url_v4(image_item.bucket_name, image_item.file_name)
                        'image_url':  'https://img2.baidu.com/it/u=3891121913,1329352522&fm=26'
                    })

                data.append({
                    'duty_id': duty.duty_id,
                    'images': image,
                    'created_date': duty.created_date.isoformat()
                })

            meta = {
                "page": duty_list.page,
                'pages': duty_list.pages,
                'total_count': duty_list.total,
                'prev_page': duty_list.prev_num,
                'next_page': duty_list.next_num,
                'has_next': duty_list.has_next,
                'has_prev': duty_list.has_prev,
            }

            return jsonify({'duty': data, "meta": meta}), HTTP_200_OK
        else:
            return jsonify({'error': 'song not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
