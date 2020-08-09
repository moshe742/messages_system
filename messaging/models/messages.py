from datetime import date
from messaging_system import db
from models import DatabaseModel
from models.users import User


class Message(DatabaseModel):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.ForeignKey(User.id), nullable=False)
    receiver = db.Column(db.ForeignKey(User.id), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    creation_date = db.Column(db.Date, nullable=False, default=date.today)
