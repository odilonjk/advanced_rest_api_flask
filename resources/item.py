from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required,
)
from flask import request
from flask_restful import Resource, reqparse
from models.item import ItemModel
from models.user import UserModel
from schemas.item import ItemSchema
from marshmallow import ValidationError

ERROR_POST_ITEM = 'An error occurred inserting the item.'
ITEM_ALREADY_EXISTS = 'An item called {} already exists.'
DELETED = '{} deleted.'
ITEM_NOT_FOUND = 'There is no item called {}.'
MORE_DATA_AVAILABLE = 'More data available if you log in.'
USER_INFO = '{} is trying to create a new item called {}.'

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {'message': ITEM_NOT_FOUND.format(item.name)}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        user = UserModel.find_by_id(get_jwt_identity())
        print(USER_INFO.format(user.username, name))
        if ItemModel.find_by_name(name) is not None:
            return {'message': ITEM_ALREADY_EXISTS.format(name)}, 400

        item_json = request.get_json()
        item_json['name'] = name

        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.message, 400

        try:
            item.save_to_db()
        except:
            return {'message': ERROR_POST_ITEM}, 500

        return item_schema.dump(item), 201

    @classmethod
    @fresh_jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': DELETED.format(name)}
        return {'message': ITEM_NOT_FOUND.format(name)}, 404

    @classmethod
    @fresh_jwt_required
    def put(self, name: str):
        item_json = request.get_json()
        item_json['name'] = name

        try:
            update_item = item_schema.load(item_json)
        except ValidationError as err:
            return err.message, 400

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
            'message': MORE_DATA_AVAILABLE
        }, 200
