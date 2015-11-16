#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import Flask

from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown

from www.config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # session_protection属性可设置为None，'Basic'或'Strong'，提供不同的安全等级防止用户会话被篡改。
login_manager.login_view = 'main.signin'  # login_view属性设置登陆页面的端点，路由在蓝本中定义，要加上蓝本名。
pagedown = PageDown()

def create_app(config_name):
    '''初始化。'''
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].inits_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    db.init_app(app)
    db.create_all(app=app)

    '''附加蓝本main'''
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
