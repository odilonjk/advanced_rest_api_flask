from typing import Dict, Union
from database import db

UserJSON = Dict[str, Union[int, str, bool]]


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90), nullable=False, unique=True)
    password = db.Column(db.String(90), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()
