#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, RadioField, TextAreaField, SelectField, SubmitField
from wtforms.validators import Required, Length

class EditProfileForm(Form):
    image = FileField('头像', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], '支持jpg、jpeg、png格式，不要超过2M。')
    ])
    sex = RadioField('性别', choices=[('1', '男'), ('0', '女')], default='1')
    one_desc = StringField('一句话介绍自己', validators=[Length(0, 50)])
    about_me = TextAreaField('个人简介')
    location = StringField('居住地', validators=[Length(0, 50)])
    industry = StringField('所在行业', validators=[Length(0, 50)])
    company = StringField('公司或组织名称', validators=[Length(0, 50)])
    job = StringField('你的职位', validators=[Length(0, 50)])
    school = StringField('学校或教育机构名', validators=[Length(0, 50)])
    majar = StringField('专业方向', validators=[Length(0, 50)])
    submit = SubmitField('保存设置')
