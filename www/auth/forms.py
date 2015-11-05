#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask.ext.wtf import Form

from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, EqualTo

from www.models import User

class SigninForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 50), Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')

class RegistrationForm(Form):
    email = StringField('输入邮箱', validators=[Required(), Length(0, 50), Email()])
    name = StringField('输入昵称', validators=[Required(), Length(0, 50)])
    password = PasswordField('输入密码', validators=[Required(), EqualTo('password2', message='密码输入不一致')])
    password2 = PasswordField('再次输入密码', validators=[Required()])
    submit = SubmitField('注册')

def validate_email(self, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('此邮箱已注册')
