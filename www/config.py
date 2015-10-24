#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'set a secret key'
    SQLALCHEMY_COMMIT_ON_TEARDOWM = True

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