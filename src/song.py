from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import db, Person, Song, song_schema, songs_schema, Image, Video, video_schema
from flasgger import swag_from

song = Blueprint("song", __name__, url_prefix="/api/v1/song")


@song.get("/")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_song():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        song_list = Song.query.join(Image, Song.song_id == Image.song_id)\
                    .join(Video, Song.song_id == Video.song_id)\
                    .paginate(page=page, per_page=per_page)

        # print(song_list)

        if song_list:
            data = []

            for song in song_list.items:

                # print()

                image = []
                for image_item in song.image:
                    print(image_item.bucket_name)
                    image.append({
                        # generate_download_signed_url_v4(image_item.bucket_name, image_item.file_name)
                        'image_url':  'https://img2.baidu.com/it/u=3891121913,1329352522&fm=26'
                    })
               
                data.append({
                    'song_id': song.song_id,
                    'song_name': song.song_name,
                    'song_lyric': song.song_lyric,
                    'images' : image,
                    'video_url': song.video[0].url
                    # 'created_date': song.created_date.isoformat()
                })

            meta = {
                "page": song_list.page,
                'pages': song_list.pages,
                'total_count': song_list.total,
                'prev_page': song_list.prev_num,
                'next_page': song_list.next_num,
                'has_next': song_list.has_next,
                'has_prev': song_list.has_prev,
            }

            return jsonify({'songs': data, "meta": meta}), HTTP_200_OK
        else:
            return jsonify({'error': 'song not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
