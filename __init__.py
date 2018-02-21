#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/2/14 12:56
# @Author  : Xu
# @Site    : https://xuccc.github.io/
# @Version : $

import arrow

from flask import render_template, Blueprint
from flask import request, jsonify

from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, CTFdStandardChallenge
from CTFd.models import Challenges, db, Keys
from CTFd.plugins.keys import BaseKey, KEY_CLASSES
from CTFd.utils import admins_only, is_admin

dynamic = Blueprint('dynamic', __name__)


class OnlineKey(BaseKey):
    id = 2
    name = "online"
    templates = {
        'create': '/plugins/OnlineChallenge/assets/create-dynamic-modal.njk',
        'update': '/plugins/OnlineChallenge/assets/edit-dynamic-modal.njk',
    }

    @staticmethod
    def compare(saved, provided):
        if len(saved) != len(provided):
            return False
        result = 0
        for x, y in zip(saved, provided):
            result |= ord(x) ^ ord(y)
        return result == 0


class OnlineChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'online'}
    id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
    token = db.Column(db.String(80))

    def __init__(self, name, description, value, category, token, type='online'):
        self.name = name
        self.description = description
        self.value = value
        self.category = category
        self.type = type
        self.token = token


class OnlineTypeChallenge(CTFdStandardChallenge):
    id = 'online'
    name = 'online'
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        'create': '/plugins/OnlineChallenge/assets/online-challenge-create.njk',
        'update': '/plugins/OnlineChallenge/assets/online-challenge-update.njk',
        'modal' : '/plugins/OnlineChallenge/assets/online-challenge-modal.njk',
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/OnlineChallenge/assets/online-challenge-create.js',
        'update': '/plugins/OnlineChallenge/assets/online-challenge-update.js',
        'modal' : '/plugins/OnlineChallenge/assets/online-challenge-modal.js',
    }

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        # Create challenge
        chal = OnlineChallenge(
                name=request.form['name'],
                description=request.form['description'],
                token=request.form.get('keydata'),
                value=request.form['value'],
                category=request.form['category'],
                type=request.form['chaltype']
        )

        if 'hidden' in request.form:
            chal.hidden = True
        else:
            chal.hidden = False

        max_attempts = request.form.get('max_attempts')
        if max_attempts and max_attempts.isdigit():
            chal.max_attempts = int(max_attempts)

        db.session.add(chal)
        db.session.commit()

        flag = Keys(chal.id, request.form['key'], request.form['key_type[0]'])
        if request.form.get('keydata'):
            flag.data = request.form.get('keydata')
        db.session.add(flag)

        db.session.commit()

        files = request.files.getlist('files[]')
        for f in files:
            utils.upload_file(file=f, chalid=chal.id)

        db.session.commit()


def filter(request):
    """

    :param request:
    :return:
    """
    flag = request.args.get('flag')
    token = request.args.get('token')
    time = request.args.get('time',arrow.now().timestamp)
    k = Keys.query.filter_by(data=token).first() if token else None
    return flag, token, time, k


def save(k, flag):
    """

    :param k: class 'CTFd.models.Keys'
    :param flag: string
    :return:
    """
    k.flag = flag
    db.session.commit()
    db.session.close()
    return '1'

def client(**kwargs):
    """
    Return data to client
    :param kwargs:
    :return: dict
    """
    return {
        'check': kwargs.get('check',False),
        'reason': kwargs.get('reason'),
        'flag_old': kwargs.get('flag_old'),
        'flag_new': kwargs.get('flag_new'),
        'timestamp': kwargs.get('time')
    }


def load(app):
    @dynamic.route('/dynamic/keys', methods=['POST', 'GET'])
    def show():
        if request.method == 'GET':
            flag, token, time, k = filter(request)
            if k is not None:
                data = client(check=True,flag_old=k.flag,flag_new=flag,time=time)
                save(k, flag)
            else:
                data = client(reason='token wrong',time=time)
            return jsonify(data)
        elif request.method == 'POST':
            # TODO
            data = {}
            return jsonify(data)

    app.db.create_all()
    KEY_CLASSES['online'] = OnlineKey
    CHALLENGE_CLASSES['online'] = OnlineTypeChallenge
    app.register_blueprint(dynamic)
    register_plugin_assets_directory(app, base_path='/plugins/OnlineChallenge/assets')
