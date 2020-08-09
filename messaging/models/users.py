from flask_login import UserMixin

from messaging_system import db
from models import DatabaseModel


class User(DatabaseModel, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)
