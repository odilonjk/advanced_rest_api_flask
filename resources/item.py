from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required,
)
from flask import request
from flask_restful import Resource, reqparse
from marshmallow import ValidationError

from libs.strings import gettext
from models.item import ItemModel
from models.user import UserModel
from schemas.item import ItemSchema


item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {'message': gettext("item_not_found").format(item.name)}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        user = UserModel.find_by_id(get_jwt_identity())
        print(gettext("security_user_post_log").format(user.username, name))
        if ItemModel.find_by_name(name) is not None:
            return {'message': gettext("item_already_exists").format(name)}, 400

        item_json = request.get_json()
        item_json['name'] = name

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {'message': gettext("item_error_creating")}, 500

        return item_schema.dump(item), 201

    @classmethod
    @fresh_jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': gettext("generic_deleted").format(name)}
        return {'message': gettext("item_not_found").format(name)}, 404

    @classmethod
    @fresh_jwt_required
    def put(self, name: str):
        item_json = request.get_json()
        item_json['name'] = name

        update_item = item_schema.load(item_json)

        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(None, name, **update_item)
        else:
            item.price = update_item.price
            item.store_id = update_item.store_id
        item.save_to_db()
        return item_schema.dump(item)


class ItemList(Resource):
    @classmethod
    @jwt_optional
    def get(self):
        items = ItemModel.find_all()
        if get_jwt_identity():
            return {'items': item_list_schema.dump(items)}, 200
        return {
            'items': [item.name for item in items],
            'message': gettext("security_more_data_available")
        }, 200
