#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask.ext.wtf import Form

from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Required

class UserForm(Form):
    email = StringField('输入邮箱', validators=[Required()])
    password = StringField('输入密码', validators=[Required()])
    name = StringField('输入用户名', validators=[Required()])
    submit = SubmitField('提交')
