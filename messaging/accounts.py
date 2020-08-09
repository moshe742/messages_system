from flask import jsonify
from flask.views import MethodView
from flask import request

from flask_login import login_user
from passlib.handlers.bcrypt import bcrypt
import simplejson
from sqlalchemy.exc import IntegrityError

from messaging_system import db
from models.users import User


class LoginAPI(MethodView):
    def post(self):
        body = simplejson.loads(request.data)
        user = User.query.filter_by(username=body['username']).first()

        if user:
            if bcrypt.verify(body['password'], user.password):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return jsonify({
                    'login': True,
                    'user': {
                        'id': user.id,
                        'username': user.username
                    }
                }), 200

        return jsonify({
            'error': 'username or password are wrong'
        }), 400


class RegisterAPI(MethodView):
    def post(self):
        body = simplejson.loads(request.data)
        user = User(username=body['username'],
                    password=bcrypt.hash(body['password']))
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as ex:
            print(ex)
            return jsonify({
                'error': 'This username already exists!'
            }), 409
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
            }
        }), 201
