from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required,
)
from flask_restful import Resource, reqparse
from models.item import ItemModel
from models.user import UserModel

BLANK_ERROR = '{} cannot be blank.'
ERROR_POST_ITEM = 'An error occurred inserting the item.'
ITEM_ALREADY_EXISTS = 'An item called {} already exists.'
DELETED = '{} deleted.'
ITEM_NOT_FOUND = 'There is no item called {}.'
MORE_DATA_AVAILABLE = 'More data available if you log in.'
USER_INFO = '{} is trying to create a new item called {}.'


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help=BLANK_ERROR.format('price'))

    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help=BLANK_ERROR.format('store_id'))

    @jwt_required
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {'message': ITEM_NOT_FOUND.format(name)}, 404

    @fresh_jwt_required
    def post(self, name: str):
        user = UserModel.find_by_id(get_jwt_identity())
        print(USER_INFO.format(user.username, name))
        if ItemModel.find_by_name(name) is not None:
            return {'message': ITEM_ALREADY_EXISTS.format(name)}, 400
        data = Item.parser.parse_args()
        new_item = ItemModel(name=name, **data)

        try:
            new_item.save_to_db()
        except:
            return {'message': ERROR_POST_ITEM}, 500

        return new_item.json(), 201

    @fresh_jwt_required
    def delete(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': DELETED.format(name)}
        return {'message': ITEM_NOT_FOUND.format(name)}, 404

    @fresh_jwt_required
    def put(self, name: str):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(None, name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        item.save_to_db()
        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        items = [item.json() for item in ItemModel.find_all()]
        if get_jwt_identity():
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': MORE_DATA_AVAILABLE
        }, 200
