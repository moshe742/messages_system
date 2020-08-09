#!/usr/bin/env python

import os
import logging

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

print('start of messaging_system')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app.config.update({
    'SQLALCHEMY_DATABASE_URI': f"sqlite:///{BASE_DIR}/db.sqlite",
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
})

app.secret_key = b'z\xe3\x8a\xe8\x1e\xdeR5\xaf\x1a1\xf6I\xd9\x02\x94'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from messaging.models.users import User
    return User.query.get(user_id)


@app.route('/', methods=['GET'])
def hello():
    return 'hello'


def main():
    from messaging.accounts import (
        LoginAPI,
        RegisterAPI
    )
    from messaging.messages import (
        MessageAPI,
        ListMessagesAPI,
    )

    app.add_url_rule('/messages/',
                     view_func=ListMessagesAPI.as_view('messages'))
    app.add_url_rule('/messages/<int:message_id>/',
                     view_func=MessageAPI.as_view('message'))

    app.add_url_rule('/login/',
                     view_func=LoginAPI.as_view('login'))
    app.add_url_rule('/register',
                     view_func=RegisterAPI.as_view('register'))

    login_manager.init_app(app)


if __name__ == 'messaging.messaging_system':
    main()
