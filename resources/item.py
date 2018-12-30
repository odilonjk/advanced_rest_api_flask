from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional, fresh_jwt_required
from flask_restful import Resource, reqparse
from models.item import ItemModel
from models.user import UserModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank.')

    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='Every item needs a store id.')

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {'message': 'Item not found.'}, 404

    @fresh_jwt_required
    def post(self, name):
        user = UserModel.find_by_id(get_jwt_identity())
        print('{} is trying to create a new item called {}.'.format(user.username, name))
        if ItemModel.find_by_name(name) is not None:
            return {'message': 'An item called {} already exists.'.format(name)}, 400
        data = Item.parser.parse_args()
        new_item = ItemModel(name=name, **data)

        try:
            new_item.save_to_db()
        except:
            return {'message': 'An error occurred inserting the item.'}, 500

        return new_item.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': '{} deleted.'.format(name)}
        return {'message': 'There is no item called {}.'.format(name)}, 404

    @fresh_jwt_required
    def put(self, name):
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
        return {'items': [item['name'] for item in items],
                'message': 'More data available if you log in.'}, 200
