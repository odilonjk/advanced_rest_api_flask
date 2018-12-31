from typing import Dict
from database import db


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90))
    password = db.Column(db.String(90))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username: str, password: str, is_admin: bool):
        self.username = username
        self.password = password
        self.is_admin = is_admin

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    def json(self) -> Dict:
        return {
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin
        }
