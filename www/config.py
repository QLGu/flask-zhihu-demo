#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'set a secret key'
    SQLALCHEMY_COMMIT_ON_TEARDOWM = True
    MAIL_SERVER = 'smtp.googleemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 环境中定义：$ export MAIL_USERNAME=<Gmail_username>
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 环境中定义：$ export MAIL_PASSWORD=<Gmail_password>
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASK_MAIL_SENDER = 'Flasky admin <flasky@example.com>'
    FLASK_ADMIN = os.environ.get('FLASKY_ADMIN')
    @staticmethod
    def inits_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:root@localhost/zhihu'

class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'mysql+pymysql://root:root@localhost/zhihu'

class ProductiontConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:root@localhost/zhihu'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductiontConfig,

    'default': DevelopmentConfig
}