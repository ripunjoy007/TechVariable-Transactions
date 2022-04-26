from app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from uuid import uuid4


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    _password = db.Column(db.String)
    created_at = db.Column(db.Date)

    def __init__(self, username_, password_):
        self.username = username_
        self.password = password_
        self.created_at = datetime.now()

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self._password, value)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': '*********'
        }

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', created at={self.created_at}"


class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.String, primary_key=True)
    transaction_name = db.Column(db.String)
    product_name = db.Column(db.String)
    transaction_time = db.Column(db.String)
    timestamp = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    delivered_to_city = db.Column(db.String)

    def __init__(self, name_, product_name_, quantity_, unit_price_, delivered_city_):

        transaction_time = datetime.now()
        self.transaction_id = str(uuid4().hex)
        self.transaction_name = name_
        self.product_name = product_name_
        self.transaction_time = transaction_time.strftime('%Y%m%d %H%M%S')
        self.timestamp = int(transaction_time.timestamp())
        self.quantity = quantity_
        self.unit_price = unit_price_
        self.total_price = quantity_ * unit_price_
        self.delivered_to_city = delivered_city_

    def serialize(self):
        return {
            'transaction_id': self.transaction_id,
            'transaction_name': self.transaction_name,
            'transaction_time': self.transaction_time,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'delivered_to_city': self.delivered_to_city
        }

    def __repr__(self):
        return f"<Transaction(id='{self.transaction_id}', " \
               f"name='{self.transaction_name}', " \
               f"product_name={self.product_name}, " \
               f"time={self.transaction_time}," \
               f"quantity={self.quantity}"
