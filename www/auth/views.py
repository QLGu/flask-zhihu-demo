#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from auth import auth
from www import db
from www.models import User
from www.emailbinding import send_email
from auth.forms import SigninForm, RegistrationForm

'''
@auth.before_app_request
def before_request():
    ''''''
    钩子，在处理请求之前执行代码。
    auth.before_app_request修饰器保证在蓝本中使用针对程序全局请求的钩子。
    当用户已登陆、注册邮箱还未认证或请求的端点（使用request.endpoint获取）不在认证蓝本中时，拦截请求，重定向到auth/unconfirmed。
    ''''''
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    ''''''为未认证用户提供信息的页面，未登陆和已认证用户进入时自动回到首页''''''
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
'''

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
            return redirect(request.args.get('next') or url_for('main.index'))
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
    return redirect(url_for('main.index'))

@auth.route('/secret')
@login_required
def secret():
    '''login_required修饰器保护路由只让认证用户访问。'''
    return '只有认证用户可以访问。'

@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''
    注册，并发送认证邮件。
    即使通过配置程序已经可以在末尾自动提交数据库变化，这里也要添加db.session.commit()，因为后续确定令牌要用到id。
    '''
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, name=form.name.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # token = user.generate_confirmation_token()
        # send_email(user.email, '认证邮箱', 'auth/email/confirm', user=user, token=token)
        # flash('一封认证邮件已发往您的注册邮箱，请尽快前往确认。')
        return redirect(url_for('auth.signin'))
    return render_template('auth/register.html', form=form)

'''
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    ''''''
    认证邮箱模板文件中的{{ url_for('auth.confirm', token=token, _external=True) }}生成绝对URL。
    此视图函数中login_required修饰器会保护这个路由，用户点击确认邮件的链接后，要先登陆，然后才能执行做个试图函数。
    若用户已经认证，则回到首页。
    ''''''
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您的邮箱已通过认证！')
    else:
        flash('认证链接已过期！')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    ''''''为已登陆用户重新发送确认邮件。''''''
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '激活邮箱', 'auth/email/confirm', user=current_user, token=token)
    flash('激活邮件已重送发送。')
    return redirect(url_for('main.index'))
'''