import os
from typing import List
from requests import Response, post
from flask import request, url_for


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    FROM_TITLE = 'Stores REST API'
    FROM_EMAIL = 'postmaster@sandbox7774f5aea48d4e29a723063289131582.mailgun.org'

    @classmethod
    def send_confirmation_email(cls, emails: List[str], subject: str, text: str) -> Response:
            return post(
                f'http://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages',
                auth=('api', cls.MAILGUN_API_KEY),
                data={
                    'from': f'{cls.FROM_TITLE} <{cls.FROM_EMAIL}>',
                    'to': emails,
                    'subject': subject,
                    'text': text
                }
            )
