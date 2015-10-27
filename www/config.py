#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'set a secret key'
    SQLALCHEMY_COMMIT_ON_TEARDOWM = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 环境中定义：$ export MAIL_USERNAME=<完整用户名>
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 环境中定义：$ export MAIL_PASSWORD=<密码>
    FLASKY_MAIL_SUBJECT_PREFIX = '[Hipponensis]'
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')  # 环境中定义：$ export FLASKY_MAIL_SENDER=<邮箱>
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') # 环境中定义：$ export FLASKY_ADMIN=<邮箱>
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