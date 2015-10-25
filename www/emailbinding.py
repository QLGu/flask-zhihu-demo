#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from threading import Thread

from flask import current_app, render_template

from flask.ext.mail import Message

from www import mail

def send_ansyc_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    '''
    简单的新建一个线程实现异步发送邮件。
    可改进为使用Celery任务列队执行send_ansyc_email()函数。
    '''
    app = current_app.get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + '.' + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_ansyc_email, args=[app, msg])
    thr.start()
    return thr
