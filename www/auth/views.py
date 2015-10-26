#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, login_required

from auth import auth
from www.models import User
from auth.forms import SigninForm

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    '''
    试图函数signin，实现登陆，重定向回到next参数储存的原地址，如果没有则回到首页。
    创建一个SigninForm对象，请求是GET时直接渲染，即显示表单；请求是POST时，validate_on_submit()验证表单数据。
    使用表单中填写的email从数据库中加载用户，邮箱对应的用户存在且密码verify_password验证无误，则调用login_user()在用户会话中把用户标记为已登陆。
    login_user()参数是要登陆的用户和可选的“记住我”布尔值。
    '''
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for(main.index))
        flash('邮箱或密码错误')
    return render_template('auth/signin.html', form=form)

@auth.route('/signout')
@login_required
def signout():
    '''
    视图函数signout，实现登出，重定向回到首页。
    login_required修饰器保护路由只让认证用户操作。
    '''
    logout_user()
    return redirect(url_for(main.index))

@auth.route('/secret')
@login_required
def secret():
    '''login_required修饰器保护路由只让认证用户访问。'''
    return '只有认证用户可以访问。'