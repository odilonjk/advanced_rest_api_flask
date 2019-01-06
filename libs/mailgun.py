import os
from typing import List
from requests import Response, post
from flask import request, url_for

ERROR_SENDING_EMAIL = 'Error sending confirmation email.'
FAILED_TO_LOAD_API_KEY = 'Failed to load MailGun API Key.'
FAILED_TO_LOAD_DOMAIN = 'Failed to load MailGun Domain.'


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    FROM_TITLE = 'Stores REST API'
    FROM_EMAIL = 'postmaster@sandbox7774f5aea48d4e29a723063289131582.mailgun.org'

    @classmethod
    def send_confirmation_email(cls, emails: List[str], subject: str, text: str) -> Response:
            if cls.MAILGUN_API_KEY is None:
                raise MailGunException(FAILED_TO_LOAD_API_KEY)
            if cls.MAILGUN_DOMAIN is None:
                raise MailGunException(FAILED_TO_LOAD_DOMAIN)
            response = post(
                f'http://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages',
                auth=('api', cls.MAILGUN_API_KEY),
                data={
                    'from': f'{cls.FROM_TITLE} <{cls.FROM_EMAIL}>',
                    'to': emails,
                    'subject': subject,
                    'text': text
                }
            )
            if response.status_code != 200:
                raise MailGunException(ERROR_SENDING_EMAIL)
