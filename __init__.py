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
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.models import db, Solves, WrongKeys, Keys, Challenges, Files, Tags, Teams
from CTFd.plugins.keys import BaseKey,KEY_CLASSES
from CTFd.models import db, Keys
from CTFd.utils import admins_only, is_admin

dynamic = Blueprint('dynamic', __name__)

class Online(object):
    def __init__(self, ):
        """Constructor for Online"""
        super(Online, self).__init__()
        
    


class OnlineTypeChallenge(BaseChallenge):
    id = 'online'
    name = 'online'
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        'create': '/plugins/DynamicFlag/assets/online-challenge-create.njk',
        'update': '/plugins/DynamicFlag/assets/online-challenge-update.njk',
        'modal': '/plugins/DynamicFlag/assets/online-challenge-modal.njk',
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/DynamicFlag/assets/online-challenge-create.js',
        'update': '/plugins/DynamicFlag/assets/online-challenge-update.js',
        'modal': '/plugins/DynamicFlag/assets/online-challenge-modal.js',
    }

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        # Create challenge
        chal = Challenges(
            name=request.form['name'],
            description=request.form['description'],
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

class DynamicKey(BaseKey):
    id = 2
    name = "dynamic"
    templates = {
        'create': '/plugins/DynamicFlag/assets/create-dynamic-modal.njk',
        'update': '/plugins/DynamicFlag/assets/edit-dynamic-modal.njk',
    }

    @staticmethod
    def compare(saved, provided):
        if len(saved) != len(provided):
            return False
        result = 0
        for x, y in zip(saved, provided):
            result |= ord(x) ^ ord(y)
        return result == 0


def filter(token=None):
    k = Keys.query.filter_by(data=token).first()
    return k

def save(k, flag):
    """

    :param k: class 'CTFd.models.Keys'
    :param token:
    :param flag:
    :return:
    """
    k.flag = flag
    db.session.commit()
    db.session.close()
    return '1'


def load(app):
    @dynamic.route('/dynamic/keys', methods=['POST', 'GET'])
    def show():
        if request.method == 'GET':
            flag = request.args.get('flag')
            token = request.args.get('token')
            time = request.args.get('time')
            if flag and token and time:
                k = filter(token)
                if k is not None:
                    data = {
                        'check': True,
                        'old'  : k.flag,
                        'new'  : flag,
                        'time' : time or arrow.now().timestamp
                    }
                    save(k,flag)
                else:
                    data = {
                        'check' : False,
                        'reason': 'token wrong',
                        'time'  : time or arrow.now().timestamp
                    }
                return jsonify(data)
            else:
                return jsonify({'check': 'wrong'})
        elif request.method == 'POST':
            # TODO
            data = {}
            return jsonify(data)


    KEY_CLASSES['dynamic'] = DynamicKey
    app.register_blueprint(dynamic)
    register_plugin_assets_directory(app,base_path='/plugins/DynamicFlag/assets')

