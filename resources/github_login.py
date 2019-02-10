from flask import g, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from oa import github

from models.user import UserModel
from models.confirmation import ConfirmationModel
from resources.user import UserLogin


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        return github.authorize(callback="http://localhost:5000/login/github/authorized")


class GithubAuthorized(Resource):
    @classmethod
    def get(cls):
        resp = github.authorized_response()

        if resp is None or resp.get("access_token") is None:
            return {
                "error": request.args["error"],
                "error_description": request.args["error_description"]
            }, 500

        g.access_token = resp["access_token"]
        github_user = github.get("user")
        github_username = github_user.data["login"]

        user = UserModel.find_by_username(github_username)
        if not user:
            user = UserModel(username=github_username, password=None)
            user.save_to_db()
            confirmation = ConfirmationModel(user_id=user.id)
            confirmation.confirmed = True
            confirmation.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200
