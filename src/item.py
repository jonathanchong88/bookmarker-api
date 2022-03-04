from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import db, Person, Item, Image, images_schema, Language, languages_schema
from flasgger import swag_from
from src.google_storage import generate_download_signed_url_v4, generate_upload_signed_url_v4, cors_configuration, bucket_metadata

item = Blueprint("item", __name__, url_prefix="/api/v1/item")

@item.get("/")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_items():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        group_id = request.args.get('group')
        menu_id = request.args.get('menu')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        item_list = Item.query.join(
            Image, Item.item_id == Image.item_id, isouter=True)\
            .filter(Item.group_id == group_id, Item.menu_id == menu_id)\
            .paginate(page=page, per_page=per_page)

        
        if item_list:
            data = []

            for item in item_list.items:
                print(item.created_date)
                image = []
                for image_item in item.image:
                    bucket_name = cors_configuration(image_item.bucket_name)
                    image_url = generate_download_signed_url_v4(
                        bucket_name, image_item.file_name)
                    image.append({
                        'image_url': image_url
                        # 'image_url': 'https://d626yq9e83zk1.cloudfront.net/files/share-odb-2020-01-01.jpg'
                    })

                data.append({
                    'item_id': item.item_id,
                    'title': item.title,
                    'content': item.content,
                    'created_date': item.created_date.isoformat(),
                    'images': image
                })

            meta = {
                "page": item_list.page,
                'pages': item_list.pages,
                'total_count': item_list.total,
                'prev_page': item_list.prev_num,
                'next_page': item_list.next_num,
                'has_next': item_list.has_next,
                'has_prev': item_list.has_prev,
            }

            return jsonify({'items': data, "meta": meta}), HTTP_200_OK
        else:
            return jsonify({'error': 'list not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@item.get("/detail")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_item():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        item_id = request.args.get('id')
        item = Item.query.join(
            Image, Item.item_id == Image.item_id, isouter=True)\
            .filter(Item.item_id == item_id).first()

        if item:
            # print(item.created_date)
            image = []
            for image_item in item.image:
                bucket_name=cors_configuration(image_item.bucket_name)
                image_url = generate_download_signed_url_v4(bucket_name, image_item.file_name)
                image.append({
                    
                    'image_url': image_url
                    # 'image_url': 'https://d626yq9e83zk1.cloudfront.net/files/share-odb-2020-01-01.jpg'
                })

            #generate deep link url for
            deep_link = "https://lcms.com/path/portion/?path={}&id={}".format(
                item.menu_id, item_id)

            return jsonify({'item': {
                'item_id': item.item_id,
                'title': item.title,
                'content': item.content,
                'deep_link': deep_link,
                'created_date': item.created_date.isoformat(),
                'images': image
            }}), HTTP_200_OK
        else:
            return jsonify({'error': 'item not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@item.post("/upload")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_upload_item():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    file_name = request.get_json().get('file_name', '')

    if person:
    #     url = generate_download_signed_url_v4('jonathan_bucket_1', 'hello')
    #     print(url)
    #     return jsonify({'data': url}), HTTP_200_OK
    # else:
    #     return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
    # data = []
        bucket_name = cors_configuration('jonathan_bucket_1')
        url3 = generate_upload_signed_url_v4(bucket_name, file_name)
    # url4 = generate_upload_signed_url_v4('jonathan_bucket_1', 'zhouxun4')

    
    # print(url)
        return jsonify({'data': {
            'upload_url': url3,
        }}), HTTP_200_OK
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@item.get("/language")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_language():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        # group_id = request.args.get('group')
        # menu_id = request.args.get('menu')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        print(page)
        language_list = Language.query.paginate(
            page=page, per_page=per_page, error_out=True)
        
        if language_list:
           
            # data = []

            # for item in language_list.items:
              
            #     image = []

                # data.append({
                #     'item_id': item.item_id,
                #     'title': item.title,
                #     'content': item.content,
                #     'created_date': item.created_date.isoformat(),
                #     'images': image
                # })

            meta = {
                "page": language_list.page,
                'pages': language_list.pages,
                'total_count': language_list.total,
                'prev_page': language_list.prev_num,
                'next_page': language_list.next_num,
                'has_next': language_list.has_next,
                'has_prev': language_list.has_prev,
            }

            return jsonify({'language_list': languages_schema.dump(language_list.items), "meta": meta}), HTTP_200_OK
        else:
            return jsonify({'error': 'language_list not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@item.get("/images")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_images():
    bucket_name = cors_configuration('jonathan_bucket_1')
    # bucket = bucket_metadata('jonathan_bucket_1')
    url = generate_download_signed_url_v4(bucket_name, 'zhouxun1')
    return jsonify({'data': url}), HTTP_200_OK
