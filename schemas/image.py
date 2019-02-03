from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage

from libs.strings import gettext


class FileStorageField(fields.Field):
    default_error_messages = {
        "invalid": gettext("image_not_valid")
    }

    def _deserialize(self, value, attr, data) -> FileStorage:
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            self.fail("invalid")  # Raises ValidationError

        return value


class ImageSchema(Schema):
    image = FileStorageField(required=True)
