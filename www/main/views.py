#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os
import random
import string
import shutil
import time
import datetime
import io
from PIL import Image, ImageOps

from flask import render_template, request, redirect, url_for, abort, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from main import main
from main.forms import SigninForm, RegistrationForm, EditProfileForm, EditAvatarForm, AddQuestionForm
from www import db
from www.models import User, Question, Answer, Tag, Collection, Comment, Message
from www.emailbinding import send_email


@main.route('/')
def index():
    return render_template('index.html')


@main.before_app_request
def before_request():
    '''
    钩子，在处理请求之前执行代码。
    main.before_app_request修饰器保证在蓝本中使用针对程序全局请求的钩子。
    当用户已登陆、注册邮箱还未认证或请求的端点（使用request.endpoint获取）不在认证蓝本中时，拦截请求，重定向到unconfirmed。
    '''
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'main.'\
            and request.endpoint != 'static':
        return redirect(url_for('main.unconfirmed'))


@main.route('/unconfirmed')
def unconfirmed():
    '''为未认证用户提供信息的页面，未登陆和已认证用户进入时自动回到首页'''
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')


@main.route('/signin', methods=['GET', 'POST'])
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
    return render_template('signin.html', form=form)


@main.route('/signout')
@login_required
def signout():
    '''
    视图函数signout，实现登出，重定向回到首页。
    login_required修饰器保护路由只让认证用户操作。
    '''
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/secret')
@login_required
def secret():
    '''login_required修饰器保护路由只让认证用户访问。'''
    return '只有认证用户可以访问。'


@main.route('/register', methods=['GET', 'POST'])
def register():
    '''
    注册，并发送认证邮件。
    即使通过配置程序已经可以在末尾自动提交数据库变化，这里也要添加db.session.commit()，因为后续确定令牌要用到id。
    '''
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, name=form.name.data, password=form.password.data, image='img/default_avatar.jpg')
        if User.query.filter_by(email=form.email.data).first():
            flash('该邮箱已注册')
        else:
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(user.email, '认证邮箱', 'email/confirm', user=user, token=token)
            flash('一封认证邮件已发往您的注册邮箱，请尽快前往确认。')
            return redirect(url_for('main.signin'))
    return render_template('register.html', form=form)


@main.route('/confirm/<token>')
@login_required
def confirm(token):
    '''
    认证邮箱模板文件中的{{ url_for('main.confirm', token=token, _external=True) }}生成绝对URL。
    此视图函数中login_required修饰器会保护这个路由，用户点击确认邮件的链接后，要先登陆，然后才能执行做个试图函数。
    若用户已经认证，则回到首页。
    '''
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您的邮箱已通过认证！')
    else:
        flash('认证链接已过期！')
    return redirect(url_for('main.index'))


@main.route('/confirm')
@login_required
def resend_confirmation():
    '''为已登陆用户重新发送确认邮件。'''
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '激活邮箱', 'email/confirm', user=current_user, token=token)
    flash('激活邮件已重送发送。')
    return redirect(url_for('main.index'))


@main.route('/people/<id>')
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('people.html', user=user)


@main.route('/people/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.sex = form.sex.data
        current_user.one_desc = form.one_desc.data
        current_user.about_me = form.about_me.data
        current_user.location = form.location.data
        current_user.industry = form.industry.data
        current_user.company = form.company.data
        current_user.job = form.job.data
        current_user.school = form.school.data
        current_user.majar = form.majar.data
        db.session.add(current_user)
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('main.user', id=current_user.id))
    form.sex.data = str(current_user.sex)
    form.one_desc.data = current_user.one_desc
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    form.industry.data = current_user.industry
    form.company.data = current_user.company
    form.job.data = current_user.job
    form.school.data = current_user.school
    form.majar.data = current_user.majar
    return render_template('edit_profile.html', form=form)


@main.route('/people/avatar', methods=['GET', 'POST'])
@login_required
def edit_avatar():
    form = EditAvatarForm()
    if form.validate_on_submit():
        ext = form.image.data.filename.split('.')[-1]
        filename = "%s_%s.%s" % (current_user.id, int(time.time()), ext)
        base = os.path.join('www/static/img/', 'uploads')

        stream = form.image.data.stream
        img = io.BytesIO()
        shutil.copyfileobj(stream, img)
        img.seek(0)

        with open(os.path.join(base, filename), "wb") as f:
            f.write(img.read())
        img.seek(0)

        im = Image.open(img)
        size = 100,100
        image = ImageOps.fit(im, size, Image.ANTIALIAS)
        filename = str(int(time.time())) + str(current_user.id) + '.jpg'

        image.save(os.path.join(base, filename))
        current_user.image = "img/uploads/%s" % filename
        db.session.add(current_user)
        db.session.commit()
        flash('头像上传成功')
        return redirect(url_for('main.user', id=current_user.id))
    return render_template('edit_avatar.html', form=form)


@main.route('/people/<id>/follow')
@login_required
def follow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已经关注了该用户。')
        return redirect(url_for('main.user', id=id))
    current_user.follow(user)
    flash('你关注了 %s。' % user.name)
    return redirect(url_for('main.user', id=id))


@main.route('/people/<id>/unfollow')
@login_required
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('你还没有关注该用户。')
        return redirect(url_for('main.user', id=id))
    current_user.unfollow(user)
    flash('你取消了对 %s 的关注。' % user.name)
    return redirect(url_for('main.user', id=id))


@main.route('/people/<id>/following')
def followers(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=100, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="的关注者",
                           endpoint='main.followers', pagination=pagination,
                           follows=follows)


@main.route('/people/<id>/followed')
def followed_by(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=100, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="关注的人",
                           endpoint='main.followed_by', pagination=pagination,
                           follows=follows)



'''
@main.route('/question/<id>')
def question(id):
    question = Question.query.filter_by(id=id).first_or_404()
    if (datetime.datetime.now()-question.created_at).days == 0:
        created_time = datetime.datetime.strftime(question.created_at, '%H:%M')
    else:
        created_time = datetime.datetime.strftime(question.created_at, '%Y-%m-%d')
    return render_template('question.html', question=question, created_time=created_time)


@main.route('/question/add', methods=['GET', 'POST'])
@login_required
def add_question():
    form = AddQuestionForm()
    if form.validate_on_submit():
        question = Question(title=form.title.data,
                            content=form.content.data,

                            question_user=current_user._get_current_object())
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.question', id=question.id))
    return render_template('add_question.html', form=form)

'''

'''
from datetime import datetime

from flask import render_template, session, redirect, url_for, current_app

from www import db
from www.models import User
from www.emailbinding import send_email
from main import main
from main.forms import UserForm

@main.route('/', methods=['GET', 'POST'])
def index():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(email=form.email.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['email'] = form.email.data
        form.email.data = ''
        return redirect(url_for('main.index'))
    return render_template('index.html', form=form, email=session.get('email'), known=session.get('known', False), current_time=datetime.utcnow())
'''
