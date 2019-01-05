from typing import Dict, Union
from database import db
from flask import request
from requests import Response, post
from flask import request, url_for

MAILGUN_DOMAIN = 'sandbox7774f5aea48d4e29a723063289131582.mailgun.org'
MAILGUN_API_KEY = 'ae032876014905a8828b2267fa5e52c6-49a2671e-8f171534'
FROM_TITLE = 'Stores REST API'
FROM_EMAIL = 'postmaster@sandbox7774f5aea48d4e29a723063289131582.mailgun.org'


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90), nullable=False, unique=True)
    password = db.Column(db.String(90), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    activated = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(90), nullable=False, unique=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        print('Sending confirmation email to {}'.format(self.username))
        link = request.url_root[0:-1] + url_for('useractivation', user_id=self.id)
        return post(
            f'http://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages',
            auth=('api', MAILGUN_API_KEY),
            data={
                'from': f'{FROM_TITLE} <{FROM_EMAIL}>',
                'to': self.email,
                'subject': 'Registration confirmation.',
                'text': f'Please click the link to confirm your registration: {link}',
            }
        )

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email: str) -> 'UserModel':
        return cls.query.filter_by(email=email).first()
