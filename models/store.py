from typing import List
from database import db


class StoreModel(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    items = db.relationship('ItemModel', lazy='dynamic')

    @classmethod
    def find_by_name(cls, name: str) -> 'StoreModel':
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls) -> List['StoreModel']:
        return cls.query.all()
