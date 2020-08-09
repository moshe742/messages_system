from datetime import date

from flask import jsonify
from flask import request
import simplejson
from flask.views import MethodView
from flask_login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from models.messages import Message
from models.users import User
from messaging_system import db


class MessageAPI(MethodView):
    @login_required
    def get(self, message_id):
        message = Message.query.get(message_id)
        message.is_read = True
        db.session.add(message)
        db.session.commit()

        return jsonify({
            'message': message.to_dict()
        }), 200

    @login_required
    def delete(self, message_id):
        try:
            message = Message.query.get(message_id)
            if message.sender == current_user.id or message.receiver == current_user.id:
                db.session.delete(message)
                db.session.commit()
            else:
                return jsonify({
                    'error': 'only the sender or receiver can delete a message'
                }), 401
            return jsonify({
                'delete': 'ok'
            }), 200
        except Exception as ex:
            print(ex)
            return jsonify({
                'error': str(ex)
            }), 500


class ListMessagesAPI(MethodView):
    @login_required
    def get(self):
        message_types = {
            'unread': Message.query.filter_by(receiver=current_user.id).filter_by(is_read=False),
            'all': Message.query.filter_by(receiver=current_user.id),
        }
        message_type = request.args['type']
        messages = message_types[message_type].all()
        users = User.query.all()
        users_id_to_username = {user.id: user.username for user in users}
        res = []
        for message in messages:
            message.sender = users_id_to_username[message.sender]
            message.receiver = users_id_to_username[message.receiver]
            res.append(message.to_dict())

        return jsonify(res), 200

    @login_required
    def post(self):
        body = simplejson.loads(request.data)
        try:
            sender = User.query.filter_by(username=body['sender']).one()
        except NoResultFound:
            return jsonify({
                'error': "The sender doesn't exist!",
            })

        try:
            receiver = User.query.filter_by(username=body['receiver']).one()
        except NoResultFound:
            return jsonify({
                'error': "The receiver doesn't exist!",
            })

        try:
            message = Message(sender=sender.id, receiver=receiver.id,
                              subject=body['subject'], message=body['message'],
                              creation_date=date.fromisoformat(body['creation_date']))
            db.session.add(message)
        except ValueError:
            return jsonify({
                'error': 'The date is in the wrong format'
            }), 400

        try:
            db.session.commit()
        except Exception as ex:
            print(ex)
            return jsonify({
                'error': str(ex)
            })

        return jsonify({
            'message_id': message.id,
            'sender': message.sender,
            'receiver': message.receiver,
            'subject': message.subject,
            'message': message.message,
            'creation_date': message.creation_date,
        })
