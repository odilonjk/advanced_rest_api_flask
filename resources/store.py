from flask import request
from flask_jwt_extended import jwt_required, get_jwt_claims, fresh_jwt_required
from flask_restful import Resource, reqparse

from models.store import StoreModel
from schemas.store import StoreSchema

DELETED = '{} deleted.'
ERROR_POST_STORE = 'An error occurred inserting the store.'
ONLY_ADMIN = 'Only admin users can execute this operation.'
STORE_ALREADY_EXISTS = 'An store called {} already exists.'
STORE_NOT_FOUND = 'There is no store called {}.'

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200
        return {'message': STORE_NOT_FOUND.format(name)}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
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

        return store_schema.dump(new_store), 201

    @classmethod
    @fresh_jwt_required
    def delete(cls, name: str):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ONLY_ADMIN}
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': DELETED.format(name)}
        return {'message': STORE_NOT_FOUND.format(name)}, 404


class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {'stores': store_list_schema.dump(StoreModel.find_all())}
