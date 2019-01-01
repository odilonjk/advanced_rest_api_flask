from flask_jwt_extended import jwt_required, get_jwt_claims, fresh_jwt_required
from flask_restful import Resource, reqparse
from models.store import StoreModel

BLANK_ERROR = '{} cannot be blank.'
DELETED = '{} deleted.'
ERROR_POST_STORE = 'An error occurred inserting the store.'
ONLY_ADMIN = 'Only admin users can execute this operation.'
STORE_ALREADY_EXISTS = 'An store called {} already exists.'
STORE_NOT_FOUND = 'There is no store called {}.'


class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('new_name',
                        type=str,
                        required=True,
                        help=BLANK_ERROR.format('new_name'))

    @jwt_required
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {'message': STORE_NOT_FOUND.format(name)}, 404

    @fresh_jwt_required
    def post(self, name: str):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ONLY_ADMIN}
        if StoreModel.find_by_name(name) is not None:
            return {'message': STORE_ALREADY_EXISTS.format(name)}, 400

        new_store = StoreModel(name=name)

        try:
            new_store.save_to_db()
        except:
            return {'message': ERROR_POST_STORE}, 500

        return new_store.json(), 201

    @fresh_jwt_required
    def delete(self, name: str):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ONLY_ADMIN}
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': DELETED.format(name)}
        return {'message': STORE_NOT_FOUND.format(name)}, 404


class StoreList(Resource):
    @jwt_required
    def get(self):
        stores = StoreModel.find_all()
        return [store.json() for store in stores]
