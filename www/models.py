#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

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
    image = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.1')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

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

def create_user():
    u = User()
    u.email = 'test@example.com'
    u.password_hash = 'test1234'
    u.name = 'Test'
    db.session.add(u)
    db.session.flush()
    db.session.commit()

