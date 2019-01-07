from typing import Dict, Union
from database import db
from flask import request
from requests import Response
from flask import request, url_for
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90), nullable=False, unique=True)
    password = db.Column(db.String(90), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(90), nullable=False, unique=True)

    confirmation = db.relationship(
        'ConfirmationModel', laze='dynamic', cascade='all, delete-orphan'
    )

    @property
    def most_recent_confirmation(self) -> 'ConfirmationModel':
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        link = request.url_root[0:-1] + url_for(
            'confirmation', confirmation_id=self.most_recent_confirmation.id
        )
        subject = 'Registration confirmation'
        text = f'Please click the link to confirm your registration: {link}'
        return Mailgun.send_confirmation_email(emails=[self.email], subject=subject, text=text)

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email: str) -> 'UserModel':
        return cls.query.filter_by(email=email).first()
