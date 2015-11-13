#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, RadioField, TextAreaField, SelectField, SubmitField, ValidationError
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

class EditProfileForm(Form):
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

class EditAvatarForm(Form):
    image = FileField('头像', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], '支持jpg、jpeg、png格式，不要超过2M。')
    ])
    submit = SubmitField('上传头像')

class AddTagForm(Form):
    title = StringField('话题名称', validators=[Required(), Length(0, 50)])
    desc = TextAreaField('话题描述', validators=[Required(), Length(0, 50)])
    submit = SubmitField('发布')

class AddQuestionForm(Form):
    title = StringField('写下你的问题', validators=[Required(), Length(0, 50)])
    content = TextAreaField('问题说明（可选）：')
    question_tag = StringField('选择话题', validators=[Required(), Length(0, 50)])
    submit = SubmitField('发布')