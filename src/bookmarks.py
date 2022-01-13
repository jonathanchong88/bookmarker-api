# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relation, scoped_session, sessionmaker, eagerload
# from sqlalchemy import create_engine, Column, Integer, DateTime, String, ForeignKey, Table
# from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
# from flask import Blueprint, request
# from flask.json import jsonify
# import validators
# from flask_jwt_extended import get_jwt_identity, jwt_required
# from src.database import Bookmark, db, bookmark_schema, bookmarks_schema
# from flasgger import swag_from

# bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


# @bookmarks.route('/', methods=['POST', 'GET'])
# @jwt_required()
# def handle_bookmarks():
#     current_user = get_jwt_identity()

#     if request.method == 'POST':

#         body = request.get_json().get('body', '')
#         url = request.get_json().get('url', '')

#         if not validators.url(url):
#             return jsonify({
#                 'error': 'Enter a valid url'
#             }), HTTP_400_BAD_REQUEST

#         if Bookmark.query.filter_by(url=url).first():
#             return jsonify({
#                 'error': 'URL already exists'
#             }), HTTP_409_CONFLICT

#         bookmark = Bookmark(url=url, body=body, user_id=current_user)
#         db.session.add(bookmark)
#         db.session.commit()

#         return jsonify({
#             'id': bookmark.id,
#             'url': bookmark.url,
#             'short_url': bookmark.short_url,
#             'visit': bookmark.visits,
#             'body': bookmark.body,
#             'created_at': bookmark.created_at,
#             'updated_at': bookmark.updated_at,
#         }), HTTP_201_CREATED

#     else:
#         page = request.args.get('page', 1, type=int)
#         per_page = request.args.get('per_page', 5, type=int)
#         bookmarks = Bookmark.query.filter_by(
#             user_id=current_user).paginate(page=page, per_page=per_page)

#         data = []

#         for bookmark in bookmarks.items:
#             data.append({
#                 'id': bookmark.id,
#                 'url': bookmark.url,
#                 'short_url': bookmark.short_url,
#                 'visit': bookmark.visits,
#                 'body': bookmark.body,
#                 'created_at': bookmark.created_at,
#                 'updated_at': bookmark.updated_at,
#             })

#         meta = {
#             "page": bookmarks.page,
#             'pages': bookmarks.pages,
#             'total_count': bookmarks.total,
#             'prev_page': bookmarks.prev_num,
#             'next_page': bookmarks.next_num,
#             'has_next': bookmarks.has_next,
#             'has_prev': bookmarks.has_prev,

#         }

#         return jsonify({'data': data,"meta": meta}), HTTP_200_OK


# @bookmarks.get("/<int:id>")
# @jwt_required()
# def get_bookmark(id):
#     current_user = get_jwt_identity()

#     bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

#     if not bookmark:
#         return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

#     return jsonify({
#         'id': bookmark.id,
#         'url': bookmark.url,
#         'short_url': bookmark.short_url,
#         'visit': bookmark.visits,
#         'body': bookmark.body,
#         'created_at': bookmark.created_at,
#         'updated_at': bookmark.updated_at,
#     }), HTTP_200_OK


# @bookmarks.delete("/<int:id>")
# @jwt_required()
# def delete_bookmark(id):
#     current_user = get_jwt_identity()

#     bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

#     if not bookmark:
#         return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

#     db.session.delete(bookmark)
#     db.session.commit()

#     return jsonify({}), HTTP_204_NO_CONTENT


# @bookmarks.put('/<int:id>')
# @bookmarks.patch('/<int:id>')
# @jwt_required()
# def editbookmark(id):
#     current_user = get_jwt_identity()

#     bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

#     if not bookmark:
#         return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

#     body = request.get_json().get('body', '')
#     url = request.get_json().get('url', '')

#     if not validators.url(url):
#         return jsonify({
#             'error': 'Enter a valid url'
#         }), HTTP_400_BAD_REQUEST

#     bookmark.url = url
#     bookmark.body = body

#     db.session.commit()

#     return jsonify({
#         'id': bookmark.id,
#         'url': bookmark.url,
#         'short_url': bookmark.short_url,
#         'visit': bookmark.visits,
#         'body': bookmark.body,
#         'created_at': bookmark.created_at,
#         'updated_at': bookmark.updated_at,
#     }), HTTP_200_OK


# @bookmarks.get("/stats")
# @jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
# def get_stats():
#     current_user = get_jwt_identity()
   

#     # data = []
#     items = Bookmark.query.filter_by(user_id=current_user).all()

#     return jsonify({'data': bookmarks_schema.dump(items)}), HTTP_200_OK

#     # for item in items:
#     #     new_link = {
#     #         'visits': item.visits,
#     #         'url': item.url,
#     #         'id': item.id,
#     #         'short_url': item.short_url,
#     #     }

#     #     data.append(new_link)

#     # return jsonify({'data': data}), HTTP_200_OK


# engine = create_engine('sqlite:///:memory:', echo=True)
# session = scoped_session(sessionmaker(bind=engine, autoflush=True))
# Base = declarative_base()

# t_subscription = Table('subscription', Base.metadata,
#                        Column('userId', Integer, ForeignKey('user.id')),
#                        Column('channelId', Integer, ForeignKey('channel.id')),
#                        )


# class Channel(Base):
#     __tablename__ = 'channel'

#     id = Column(Integer, primary_key=True)
#     title = Column(String)
#     description = Column(String)
#     link = Column(String)
#     pubDate = Column(DateTime)


# class User(Base):
#     __tablename__ = 'user'

#     id = Column(Integer, primary_key=True)
#     username = Column(String)
#     password = Column(String)
#     sessionId = Column(String)

#     channels = relation("Channel", secondary=t_subscription)

# # NOTE: no need for this class
# # class Subscription(Base):
#     # ...


# Base.metadata.create_all(engine)


# # ######################
# # Add test data
# c1 = Channel()
# c1.title = 'channel-1'
# c2 = Channel()
# c2.title = 'channel-2'
# c3 = Channel()
# c3.title = 'channel-3'
# c4 = Channel()
# c4.title = 'channel-4'
# session.add(c1)
# session.add(c2)
# session.add(c3)
# session.add(c4)
# u1 = User()
# u1.username = 'user1'
# session.add(u1)
# u1.channels.append(c1)
# u1.channels.append(c3)
# u2 = User()
# u2.username = 'user2'
# session.add(u2)
# u2.channels.append(c2)
# session.commit()


# # ######################
# # clean the session and test the code
# session.expunge_all()

# # retrieve all (I assume those are not that many)
# channels = session.query(Channel).all()

# # get subscription info for the user
# #q = session.query(User)
# # use eagerload(...) so that all 'subscription' table data is loaded with the user itself, and not as a separate query
# q = session.query(User).options(eagerload(User.channels))
# for u in q.all():
#     for c in channels:
#         print (c.id, c.title, (c in u.channels))


# What a messy SQL query!
# stmt = query(Subscription).filter_by(userId=uid()).join(
#     (User, Subscription.userId == User.id)).filter_by(sessionId=id()).subquery()
# subs = aliased(Subscription, stmt)
# results = query(Channel.id, Channel.title, subs.userId).outerjoin(
#     (subs, subs.channelId == Channel.id))
