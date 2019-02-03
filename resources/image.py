import os
import traceback

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs import image_helper
from libs.strings import gettext
from schemas.image import ImageSchema

image_schema = ImageSchema()
AVATAR_FOLDER = "avatars"


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        """
        Used to upload an image file.
        It uses JWT to retrieve user info and then saves the image to the user's folder.
        Whether there is a filename conflict, it appends a number at the end of the filename.
        """
        data = image_schema.load(request.files)  # {"image": FileStorage}
        image = data["image"]
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            image_path = image_helper.save_image(image, folder)
            basename = image_helper.get_basename(image_path)
            return {"message": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(image)
            return {"message": gettext("image_extension_not_allowed").format(extension)}, 400


class Image(Resource):
    @jwt_required
    def get(self, filename: str):
        """Returns the requested image if it exists."""
        folder = f"user_{get_jwt_identity()}"
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400

        try:
            return send_file(image_helper.get_path(filename, folder))
        except FileNotFoundError:
            return {"message": gettext("image_not_found")}, 404

    @jwt_required
    def delete(self, filename: str):
        """Delete the image based on the file name."""
        folder = f"user_{get_jwt_identity()}"
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder))
            return {"message": gettext("generic_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("image_not_found")}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("image_delete_failed")}, 500


class AvatarUpload(Resource):
    @jwt_required
    def put(self):
        """
        This endpoint is used to upload user avatars.
        Uploading a new avatar overwrites the existing one.
        """
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = AVATAR_FOLDER
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": gettext("avatar_delete_failed")}, 500

        try:
            image = data["image"]
            ext = image_helper.get_extension(image.filename)
            avatar_name = filename + ext
            avatar_path = image_helper.save_image(image, folder, avatar_name)
            basename = image_helper.get_basename(avatar_path)
            return {"message": gettext("avatar_uploaded")}, 200
        except UploadNotAllowed:
            extension = image_helper.get_extension(image)
            return {"message": gettext("image_extension_not_allowed").format(extension)}, 400
