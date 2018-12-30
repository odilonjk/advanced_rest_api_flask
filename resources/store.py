from flask_jwt_extended import jwt_required, get_jwt_claims, fresh_jwt_required
from flask_restful import Resource, reqparse
from models.store import StoreModel


class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('new_name',
                        type=str,
                        required=True,
                        help='This field cannot be left blank.')

    @jwt_required
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {'message': 'Store not found.'}, 404

    @fresh_jwt_required
    def post(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Only admin users can create stores.'}
        if StoreModel.find_by_name(name) is not None:
            return {'message': 'An store called {} already exists.'.format(name)}, 400

        new_store = StoreModel(name=name)

        try:
            new_store.save_to_db()
        except:
            return {'message': 'An error occurred inserting the store.'}, 500

        return new_store.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Only admin users can delete stores.'}
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': '{} deleted.'.format(name)}
        return {'message': 'There is no store called {}.'.format(name)}, 404


class StoreList(Resource):
    @jwt_required
    def get(self):
        stores = StoreModel.find_all()
        return [store.json() for store in stores]
