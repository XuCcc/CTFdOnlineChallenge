#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/2/15 13:39
# @Author  : Xu
# @Site    : https://xuccc.github.io/
# @Version : $

import arrow
import requests
from random import choice
from string import ascii_letters, digits
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import pyinotify
from time import sleep

class State(object):
    info = "Info"
    error = "ERROR"
    success = "Success"

def random_string(size=8):
    return ''.join(choice(ascii_letters + digits) for _ in range(size))


def log(path,state,content):
    with open(path,'a') as f:
        line = "[{}]  <{}>  {}\n".format(arrow.now().format(),state,content)
        f.write(line)

class FlagMonitor(object):
    mask = pyinotify.IN_ACCESS  # flag has been read
    wm = pyinotify.WatchManager()
    def __init__(self,path='flag'):
        self.path = path

    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_OPEN(self,event):
            with open(event.pathname) as f:
                print f.read()


    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)

    def add(self):
        wdd = self.wm.add_watch(self.path,pyinotify.ALL_EVENTS)

    def run(self):
        self.notifier.loop()


class FlagFactory(object):
    def __init__(self, url, token, flag_path='flag',log_path='log'):
        self.path = flag_path
        self.url = url
        self.token = token
        self.logger = log_path

    @staticmethod
    def generate(prefix, size=32):
        return "{0}{{{1}}}".format(prefix, random_string(size))

    def write(self, flag):
        with open(self.path, 'wb') as f:
            f.write(flag)

    def read(self):
        with open(self.path, 'r') as f:
            return f.read().strip('\n').strip()

    def send(self, flag):
        data = {
            'token': self.token,
            'flag' : flag,
            'time': arrow.now().timestamp
        }
        log(self.logger,State.info,str(data))
        try:
            response = requests.get(self.url,params=data)
        except Exception as e:
            log(self.logger,State.error,str(e.message))
        else:
            if response.status_code == requests.codes.ok:
                log(self.logger,State.success,'Send {};Recv {}'.format(flag,response.content.replace('\n','')))
            else:
                log(self.logger,State.error,'GET {} {}'.format(response.status_code,self.url))

class Scheduler(object):
    mission = BlockingScheduler()

    #TODO Change here to modify interval
    def add(self, job, seconds=5):
        self.mission.add_job(job, 'interval', seconds=seconds)

    def run(self):
        self.mission.start()



def main(url,token,flagfile='flag',logfile='log',flag_prefix='flag',flag_length=32,round_time=5):
    """

    :param url: CTFd platform
    :param token: Challenge token
    :param flagfile:
    :param logfile:
    :param flag_prefix: flag template prefix
    :param flag_length:
    :param round_time: interval
    :return:

    Usage::
        >>> main('http://192.168.23.158:8000/dynamic/keys','c3ac27054735388abcb5c89e21cd1f23',flag_prefix='XuCTF')
    """
    log(logfile,State.info,"Load Platform: {} Challenge token: {}".format(url,token))
    flag = FlagFactory(url,token,flag_path=flagfile,log_path=logfile)
    scheduler = Scheduler()
    def job():
        new = flag.generate(flag_prefix,flag_length)
        flag.write(new)
        flag.send(new)
    scheduler.add(job,round_time)
    scheduler.run()

if __name__ == '__main__':
    #TODO insert your detail information here
    main('example url','examplt token',flagfile='/home/ctf/flag',logfile='/root/log')
