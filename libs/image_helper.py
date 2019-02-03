"""
libs.image_helper

Encapsulate methods to work with image files.
"""
import os
import re

from typing import Union
from werkzeug.datastructures import FileStorage
from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)  # Set name and allowed extension


def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    """Takes FileStorage and saves it to a folder."""
    return IMAGE_SET.save(image, folder, name)


def get_path(filename: str, folder: str) -> str:
    """Return the full path to an image."""
    return IMAGE_SET.path(filename, folder)


def find_image_any_format(filename: str, folder: str) -> Union[str, None]:
    """Takes a filename and returns an image of any of the supported formats."""
    for _format in IMAGES:
        image = f"{filename}.{format}"
        image_path = IMAGE_SET.path(filename=image, folder=folder)
        if os.path.isfile(image_path):
            return image_path
    return None


def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    """Take a FileStore or file file name and return the file name."""
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    """Check our regex and return whether the string matches."""
    filename = _retrieve_filename(file)
    allowed_format = "|".join(IMAGES)  # png|svg|jpeg|jpg|...
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"  # Check filename and extension
    return re.match(regex, filename) is not None


def get_basename(file: Union[str, FileStorage]) -> str:
    """
    Receives the full path and return the file name with extension.
    Example: get_basename('folder/subfolder/image_101.png') will return 'image_101.png'
    """
    filename = _retrieve_filename(file)
    return os.path.split(filename)[1]


def get_extension(file: Union[str, FileStorage]) -> str:
    """
    Return the file extension, based on the file full name.
    Example: get_extension('image_101.png') will return '.png'
    """
    filename = _retrieve_filename(file)
    return os.path.splitext(filename)[1]
