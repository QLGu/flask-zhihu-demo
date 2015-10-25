#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from www import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.1')

    @password.setter
    def password(self, passwd):
        self.password = generate_password_hash(passwd)

    def verify_password(self, passwd):
        return check_password_hash(self.password, passwd)

    def __repr__(self):
        return '<User %r>' % self.email
