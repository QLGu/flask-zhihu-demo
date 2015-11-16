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
from main.forms import SigninForm, RegistrationForm, EditProfileForm, EditAvatarForm, AddTagForm, AddQuestionForm, CommentForm
from www import db
from www.models import User, Question, Answer, Tag, Collection, Comment, Message
from www.emailbinding import send_email



###################################  主页视图  ###################################

@main.route('/')
def index():
    return render_template('index.html')


###################################  注册登陆视图  ###################################

############  钩子函数  ############
@main.before_app_request
def before_request():
    '''
    钩子，在处理请求之前执行代码。
    main.before_app_request修饰器保证在蓝本中使用针对程序全局请求的钩子。
    当用户已登陆、注册邮箱还未激活或请求的端点（使用request.endpoint获取）不在激活蓝本中时，拦截请求，重定向到unconfirmed。
    '''
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'main.'\
            and request.endpoint != 'static':
        return redirect(url_for('main.unconfirmed'))

###########  未激活页面  ###########
@main.route('/unconfirmed')
def unconfirmed():
    '''为未激活用户提供信息的页面，未登陆和已激活用户进入时自动回到首页'''
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')

############  用户登陆  ############
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

############  用户登出  ############
@main.route('/signout')
@login_required
def signout():
    '''
    视图函数signout，实现登出，重定向回到首页。
    login_required修饰器保护路由只让激活用户操作。
    '''
    logout_user()
    return redirect(url_for('main.index'))

############  未激活限制  ############
@main.route('/secret')
@login_required
def secret():
    '''login_required修饰器保护路由只让激活用户访问。'''
    return '只有激活用户可以访问。'

############  注册账户  ############
@main.route('/register', methods=['GET', 'POST'])
def register():
    '''
    注册，并发送激活邮件。
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
            send_email(user.email, '激活邮箱', 'email/confirm', user=user, token=token)
            flash('一封激活邮件已发往您的注册邮箱，请尽快前往确认。')
            return redirect(url_for('main.signin'))
    return render_template('register.html', form=form)

############  激活账户  ############
@main.route('/confirm/<token>')
@login_required
def confirm(token):
    '''
    激活邮箱模板文件中的{{ url_for('main.confirm', token=token, _external=True) }}生成绝对URL。
    此视图函数中login_required修饰器会保护这个路由，用户点击确认邮件的链接后，要先登陆，然后才能执行做个试图函数。
    若用户已经激活，则回到首页。
    '''
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您的邮箱已通过激活！')
    else:
        flash('激活链接已过期！')
    return redirect(url_for('main.index'))

##########  重发激活邮件  ##########
@main.route('/confirm')
@login_required
def resend_confirmation():
    '''为已登陆用户重新发送确认邮件。'''
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '激活邮箱', 'email/confirm', user=current_user, token=token)
    flash('激活邮件已重送发送。')
    return redirect(url_for('main.index'))


###################################  个人主页视图  ###################################

############  个人主页  ############
@main.route('/people/<id>')
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    following_questions = user.questions.all()
    return render_template('people.html', user=user, following_questions=following_questions)

############  编辑资料  ############
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

############  上传头像  ############
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

############  关注他人  ############
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

############  取消关注  ############
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

###########  我关注的人  ###########
@main.route('/people/<id>/following')
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

###########  关注我的人  ###########
@main.route('/people/<id>/followers')
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


###################################  话题视图  ###################################

############  话题动态  ############
@main.route('/topic')
@login_required
def topic_index():
    topics = Tag.query.all()
    tags = []
    for topic in topics:
        if current_user.is_following_tag(topic):
            tags.append(topic)
    return render_template('topic_index.html', tags=tags)

############  话题广场  ############
@main.route('/topics')
@login_required
def topics():
    topics = Tag.query.order_by(Tag.created_at.asc()).all()
    return render_template('topics.html', topics=topics)

############  添加话题  ############
@main.route('/topics/add', methods=['GET', 'POST'])
@login_required
def topics_add():
    form = AddTagForm()
    if form.validate_on_submit():
        tag = Tag(title=form.title.data, desc=form.desc.data)
        if Tag.query.filter_by(title=form.title.data).first():
            flash('该话题已创建。')
        else:
            db.session.add(tag)
            db.session.commit()
            flash('成功添加话题。')
            return redirect(url_for('main.topics'))
    return render_template('topics_add.html', form=form)

############  话题页面  ############
@main.route('/topic/<id>')
@login_required
def topic(id):
    topic = Tag.query.filter_by(id=id).first_or_404()
    if topic is None:
        flash('Invalid topic.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = topic.questions.paginate(page, per_page=100, error_out=False)
    questions = [{'question': item.t_question} for item in pagination.items]
    return render_template('topic.html', topic=topic,
                           endpoint='main.topic', pagination=pagination,
                           questions=questions)

############  关注话题  ############
@main.route('/topic/<id>/follow')
@login_required
def follow_tag(id):
    topic = Tag.query.filter_by(id=id).first()
    if topic is None:
        flash('Invalid topic.')
        return redirect(url_for('main.index'))
    if current_user.is_following_tag(topic):
        flash('你已经关注了该话题。')
        return redirect(url_for('main.topic', id=id))
    current_user.follow_tag(topic)
    flash('你关注了话题： %s。' % topic.title)
    return redirect(url_for('main.topic', id=id))

############  取消关注  ############
@main.route('/topic/<id>/unfollow')
@login_required
def unfollow_tag(id):
    topic = Tag.query.filter_by(id=id).first()
    if topic is None:
        flash('Invalid topic.')
        return redirect(url_for('main.index'))
    if not current_user.is_following_tag(topic):
        flash('你还没有关注该话题。')
        return redirect(url_for('main.topic', id=id))
    current_user.unfollow_tag(topic)
    flash('你取消了对话题： %s 的关注。' % topic.title)
    return redirect(url_for('main.topic', id=id))

###########  关注的话题  ###########
@main.route('/people/<id>/topics')
def following_tag(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.tags.paginate(page, per_page=100, error_out=False)
    following_tags = [{'tag': item.tag_set} for item in pagination.items]
    return render_template('following_topics.html', user=user, title="关注的话题",
                           endpoint='main.following_tag', pagination=pagination,
                           following_tags=following_tags)

###########  话题关注者  ###########
@main.route('/topic/<id>/followers')
def tag_followers(id):
    topic = Tag.query.filter_by(id=id).first()
    if topic is None:
        flash('Invalid topic.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = topic.users.paginate(page, per_page=100, error_out=False)
    tag_followers = [{'user': item.user_set} for item in pagination.items]
    return render_template('topic_followers.html', topic=topic, title="人关注了该话题",
                           endpoint='main.tag_followers', pagination=pagination,
                           tag_followers=tag_followers)


###################################  问题视图  ###################################

############  问题页面  ############
@main.route('/question/<id>', methods=['GET', 'POST'])
@login_required
def question(id):
    question = Question.query.filter_by(id=id).first_or_404()
    tags = question.tags.all()
    if (datetime.datetime.now()-question.created_at).days == 0:
        created_time = datetime.datetime.strftime(question.created_at, '%H:%M')
    else:
        created_time = datetime.datetime.strftime(question.created_at, '%Y-%m-%d')
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data)
        comment.comment_question = question
        author = User.query.filter_by(id=current_user.id).first()
        comment.comment_author = author
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
        return redirect(url_for('main.question', id=question.id))
    comments = question.question_comments
    return render_template('question.html', form=form, question=question, tags=tags, created_time=created_time, comments=comments)

############  添加问题  ############
@main.route('/question/add', methods=['GET', 'POST'])
@login_required
def question_add():
    form = AddQuestionForm()
    if form.validate_on_submit():
        question = Question(title=form.title.data, content=form.content.data)
        if Question.query.filter_by(title=form.title.data).first():
            flash('该问题已创建。')
        else:
            tags = form.tags.data
            topics = tags.split(',')
            if len(topics) > 4:
                flash('最多只能关注5个话题。')
                topics = topics[:5]
            author = User.query.filter_by(id=current_user.id).first()
            question.question_author = author
            db.session.commit()
            for topic in topics:
                tag = Tag.query.filter_by(title=topic).first()
                question.question_follow_tag(tag)
            flash('成功添加问题。')
            return redirect(url_for('main.question', id=question.id))
    return render_template('question_add.html', form=form)

###########  用户的提问  ###########
@main.route('/people/<id>/questions')
def people_questions(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.user_questions.paginate(page, per_page=100, error_out=False)
    questions = pagination.items
    return render_template('people_questions.html', user=user,
                           endpoint='main.people_questions', pagination=pagination,
                           questions=questions)

############  用户关注问题  ############
@main.route('/question/<id>/follow')
@login_required
def follow_question(id):
    question = Question.query.filter_by(id=id).first()
    if question is None:
        flash('Invalid question.')
        return redirect(url_for('main.index'))
    if current_user.is_following_question(question):
        flash('你已经关注了该问题。')
        return redirect(url_for('main.question', id=id))
    current_user.follow_question(question)
    flash('你关注了问题： %s。' % question.title)
    return redirect(url_for('main.question', id=id))

############  用户取关问题  ############
@main.route('/question/<id>/unfollow')
@login_required
def unfollow_question(id):
    question = Question.query.filter_by(id=id).first()
    if question is None:
        flash('Invalid question.')
        return redirect(url_for('main.index'))
    if not current_user.is_following_question(question):
        flash('你还没有关注该问题。')
        return redirect(url_for('main.question', id=id))
    current_user.unfollow_question(question)
    flash('你取消了对问题： %s 的关注。' % question.title)
    return redirect(url_for('main.question', id=id))

###########  问题下的关注者  ###########
@main.route('/question/<id>/followers')
def question_followers(id):
    question = Question.query.filter_by(id=id).first()
    if question is None:
        flash('Invalid question.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = question.users.paginate(page, per_page=100, error_out=False)
    question_followers = [{'user': item.q_user} for item in pagination.items]
    return render_template('question_followers.html', question=question,
                           endpoint='main.question_followers', pagination=pagination,
                           question_followers=question_followers)

###################################   答案视图  ###################################

############  答案页面  ############

############  用户的回答  ############

############  用户关注答案  ############

############  用户取关答案  ############


'''
@main.route('/comment/<id>/vote_up')
@login_required
def vote_up_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment is None:
        flash('Invalid comment.')
        return redirect(url_for('main.index'))
    vote = comment.vote_up
    vote = vote + 1
    comment.vote_up = vote
    return redirect(url_for('main.question', id=comment.comment_question.id))

@main.route('/comment/<id>/vote_down')
@login_required
def vote_down_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment is None:
        flash('Invalid comment.')
        return redirect(url_for('main.index'))
    vote = comment.vote_up
    vote = vote - 1
    comment.vote_up = vote
    return redirect(url_for('main.question', id=comment.comment_question.id))
'''
