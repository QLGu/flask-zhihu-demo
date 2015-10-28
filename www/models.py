#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin

from www import db
from www import login_manager

class User(UserMixin, db.Model):
    '''
    定义User模型。
    继承的UserMixin类包含了Flask-login要求实现的用户方法。
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500))
    one_desc = db.Column(db.String(50))
    location = db.Column(db.String(50))
    industry = db.Column(db.String(50))
    company = db.Column(db.String(50))
    job = db.Column(db.String(50))
    school = db.Column(db.String(50))
    majar = db.Column(db.String(50))
    about_me = db.Column(db.Text())
    is_admin = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.1')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        '''
        cookie——使用itsdangerous包的方法生成令牌。
        TimedJSONWebSignatureSerializer类接受一个密钥，以及过期时间，这里默认3600秒。
        dumps()方法为指定的数据生成加密签名。
        '''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        '''解码令牌，序列化对象提供了loads()方法，唯一参数是令牌字符串。'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<User %r>' % self.email


@login_manager.user_loader
def load_user(user_id):
    '''
    加载用户的回调函数。
    接受以UNICODE字符串形式的用户标识符。
    若找到用户，返回用户对象；否则，返回None。
    '''
    return User.query.get(int(user_id))

