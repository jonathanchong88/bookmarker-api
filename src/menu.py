from src.constant.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database2 import Menu, db, menu_schema, menus_schema, Person, Churchgroup, group_schema, groups_schema, Group_menu, group_menu_schema, groups_menu_schema
from flasgger import swag_from

menus = Blueprint("menus", __name__, url_prefix="/api/v1/menus")

# @app.route('/friendList<int:page>', methods=['GET', 'POST'])
# http: // 10.1.1.1: 5000/login?username = alex & password = pw1
@menus.get("/group")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_group_menu():
    person_id = get_jwt_identity()
    group_id = request.args.get('id')

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        # .add_columns(Group_menu.menu_id, Menu.type)
        groupMenus = Group_menu.query.join(
            Menu).filter(Group_menu.menu_id == Menu.menu_id)\
            .filter(Group_menu.group_id==group_id)\
            .all()
       
        # userList = users.query.join(friendships).add_columns(users.id, users.userName, users.userEmail, friendships.user_id, friendships.friend_id).filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)
        # groupMenus = Group_menu.query.all()
        # userList = users.query\
        #     .join(friendships, users.id == friendships.user_id)\
        #     .add_columns(users.userId, users.name, users.email, friends.userId, friendId)\
        #     .filter(users.id == friendships.friend_id)\
        #     .filter(friendships.user_id == userID)\
        #     .paginate(page, 1, False)
        # groupMenus = db.session.query(Group_menu, Menu).filter(
        #     Group_menu.menu_id == Menu.menu_id).all()
        # db.session.query(Post, db.func.count(Like.id)
        #                  ).outerjoin(Like).group_by(Post.id)
        # for row in q:
        #         print (row.Group_menu.menu_id, row.Menu.type)
        print(groupMenus)

        if groupMenus:
            data = []

            for groupMenu in groupMenus:
                data.append({
                    'group_id': groupMenu.group_id,
                    'menu_id': groupMenu.menu_id,
                    'type': groupMenu.menu.type,
                })
            return jsonify({'data': data}), HTTP_200_OK
        else:
            return jsonify({'error': 'group not found'}), HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@menus.get("/")
@jwt_required()
# @swag_from("./docs/bookmarks/stats.yaml")
def get_group():
    person_id = get_jwt_identity()

    person = Person.query.filter_by(person_id=person_id).first()

    if person:
        groupMenus = Churchgroup.query.all()
        return jsonify({'data': groups_schema.dump(groupMenus)}), HTTP_200_OK
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
