#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'set a secret key'
    SQLALCHEMY_COMMIT_ON_TEARDOWM = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'hipponensis@foxmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 环境中定义 $ export MAIL_PASSWORD="password" 环境变量设置有问题直接改为'password'。
    FLASKY_MAIL_SUBJECT_PREFIX = '[Hipponensis]'
    FLASKY_MAIL_SENDER = 'hipponensis@foxmail.com'
    FLASKY_ADMIN = 'hipponensis@foxmail.com'

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