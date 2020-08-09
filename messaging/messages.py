from datetime import date
import logging

from flask import jsonify
from flask import request
import simplejson
from flask.views import MethodView
from flask_login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from messaging.models.messages import Message
from messaging.models.users import User
from messaging.messaging_system import db


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MessageAPI(MethodView):
    @login_required
    def get(self, message_id):
        message = Message.query.get(message_id)
        users = User.query.all()
        users = {user.id: user.username for user in users}
        message.is_read = True
        db.session.add(message)
        db.session.commit()

        message = message.to_dict()
        message['sender'] = users[message['sender']]
        message['receiver'] = users[message['receiver']]

        return jsonify({
            'message': message
        }), 200

    @login_required
    def delete(self, message_id):
        try:
            message = Message.query.get(message_id)
            if not message:
                return jsonify({
                    'error': "this message doesn't exist"
                })
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
        except ValueError:
            return jsonify({
                'error': ''
            })
        except Exception as ex:
            print(ex)
            return jsonify({
                'error': str(ex)
            }), 500


class ListMessagesAPI(MethodView):
    @login_required
    def get(self):
        logger.info('logging in list of messages')
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
            message = message.to_dict()
            message['sender'] = users_id_to_username[message['sender']]
            message['receiver'] = users_id_to_username[message['receiver']]
            res.append(message)

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
            logger.error(ex)
            return jsonify({
                'error': str(ex)
            })

        users = User.query.all()
        users = {user.id: user.username for user in users}
        message = message.to_dict()
        message['sender'] = users[message['sender']]
        message['receiver'] = users[message['receiver']]

        return jsonify(message)
