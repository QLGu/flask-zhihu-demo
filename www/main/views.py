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

from flask import render_template, request, redirect, url_for, abort, flash, make_response
from flask.ext.login import login_user, logout_user, login_required, current_user

from main import main
from main.forms import SigninForm, RegistrationForm, EditProfileForm, EditAvatarForm,\
    AddTagForm, AddQuestionForm, AddAnswerForm, CommentForm, AddCollectionForm, CollectForm
from www import db
from www.models import User, Question, Answer, Tag, Collection, Comment, Message
from www.emailbinding import send_email



###################################  主页视图  ###################################

############  首页动态  ############
@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.signin'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    users = current_user.followed.all()
    questions_all = Question.query.all()
    answers_all = Answer.query.all()
    tags_all = Tag.query.all()
    quoras = questions_all + answers_all + tags_all
    for i in range(1,len(quoras)):
        for j in range(0,len(quoras)-i):
            if quoras[j].followed_at and quoras[j+1].followed_at:
                if quoras[j].followed_at < quoras[j+1].followed_at:
                    quoras[j],quoras[j+1] = quoras[j+1],quoras[j]
            if quoras[j].followed_at and not quoras[j+1].followed_at:
                if quoras[j].followed_at < quoras[j+1].created_at:
                    quoras[j],quoras[j+1] = quoras[j+1],quoras[j]
            if quoras[j+1].followed_at and not quoras[j].followed_at:
                if quoras[j].created_at < quoras[j+1].followed_at:
                    quoras[j],quoras[j+1] = quoras[j+1],quoras[j]
            if not quoras[j].followed_at and not quoras[j+1].followed_at:
                if quoras[j].created_at < quoras[j+1].created_at:
                    quoras[j],quoras[j+1] = quoras[j+1],quoras[j]
    return render_template('index.html', show_followed=show_followed, quoras=quoras, users=users)

############  所有动态  ############
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

############  关注动态  ############
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

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
    return redirect(url_for('main.signin'))

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
        user = User(email=form.email.data, name=form.name.data, password=form.password.data, confirmed=1, image='img/default_avatar.jpg')
        if User.query.filter_by(email=form.email.data).first():
            flash('该邮箱已注册')
        else:
            db.session.add(user)
            db.session.commit()
            # token = user.generate_confirmation_token()
            # send_email(user.email, '激活邮箱', 'email/confirm', user=user, token=token)
            # flash('一封激活邮件已发往您的注册邮箱，请尽快前往确认。')
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
    user_questions = user.user_questions.all()
    for i in range(1,len(user_questions)):
        for j in range(0,len(user_questions)-i):
            if user_questions[j].created_at < user_questions[j+1].created_at:
                user_questions[j],user_questions[j+1] = user_questions[j+1],user_questions[j]
    user_answers = user.user_answers.all()
    for i in range(1,len(user_answers)):
        for j in range(0,len(user_answers)-i):
            if user_answers[j].created_at < user_answers[j+1].created_at:
                user_answers[j],user_answers[j+1] = user_answers[j+1],user_answers[j]
    questions_all = Question.query.all()
    answers_all = Answer.query.all()
    tags_all = Tag.query.all()
    quoras = questions_all + answers_all + tags_all
    for i in range(1,len(quoras)):
        for j in range(0,len(quoras)-i):
            if quoras[j].followed_at and quoras[j+1].followed_at:
                if quoras[j].followed_at < quoras[j+1].followed_at:
                    quoras[j],quoras[j+1] = quoras[j+1],quoras[j]
    return render_template('people.html', user=user, user_questions=user_questions, user_answers=user_answers,
                           quoras=quoras)

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
    questions = topic.questions.all()
    for i in range(1,len(questions)):
        for j in range(0,len(questions)-i):
            if questions[j].t_question.created_at < questions[j+1].t_question.created_at:
                questions[j],questions[j+1] = questions[j+1],questions[j]
    return render_template('topic.html', topic=topic, questions=questions)

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
    topic.followed_at = datetime.datetime.now()
    db.session.add(topic)
    db.session.commit()
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
    topic.followed_at = ''
    db.session.add(topic)
    db.session.commit()
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
    form_question_comment = CommentForm(prefix="form_question_comment")
    if form_question_comment.validate_on_submit() and form_question_comment.submit.data:
        comment = Comment(content=form_question_comment.content.data)
        comment.comment_question = question
        author = User.query.filter_by(id=current_user.id).first()
        comment.comment_author = author
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
        return redirect(url_for('main.question', id=question.id))
    question_comments = question.question_comments
    form_add_answer = AddAnswerForm(prefix="form_add_answer")
    if form_add_answer.validate_on_submit() and form_add_answer.submit.data:
        ans = Answer(content=form_add_answer.content.data)
        ans.answer_question = question
        author = User.query.filter_by(id=current_user.id).first()
        ans.answer_author = author
        db.session.add(ans)
        db.session.commit()
        flash('回答成功')
        return redirect(url_for('main.question', id=question.id))
    answers = question.question_answers.all()
    for i in range(1,len(answers)):
        for j in range(0,len(answers)-i):
            if answers[j].users.count() < answers[j+1].users.count():
                answers[j],answers[j+1] = answers[j+1],answers[j]
    return render_template('question.html', question=question, tags=tags, created_time=created_time,
                               form_question_comment=form_question_comment, question_comments=question_comments,
                               form_add_answer=form_add_answer, answers=answers)

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
                if not Tag.query.filter_by(title=topic).first():
                    topic = Tag(title=topic, desc='话题描述')
                    db.session.add(topic)
                    db.session.commit()
                    question.question_follow_tag(topic)
                else:
                    tag = Tag.query.filter_by(title=topic).first()
                    question.question_follow_tag(tag)
            flash('成功添加问题。')
            return redirect(url_for('main.question', id=question.id))
    return render_template('question_add.html', form=form)

############  修改问题  ############
@main.route('/question/<id>/edit', methods=['GET', 'POST'])
@login_required
def question_edit(id):
    question = Question.query.filter_by(id=id).first()
    form = AddQuestionForm()
    if form.validate_on_submit():
        question.title = form.title.data
        question.content = form.content.data
        tags = form.tags.data
        topics = tags.split(',')
        if len(topics) > 4:
            flash('最多只能关注5个话题。')
            topics = topics[:5]
        db.session.commit()
        for topic in topics:
            tag = Tag.query.filter_by(title=topic).first()
            question.question_follow_tag(tag)
        flash('成功添加问题。')
        return redirect(url_for('main.question', id=question.id))
    form.title.data = question.title
    form.content.data = question.content
    topics = ''
    for question in question.tags.all():
        if not topics:
            topics= topics +question.q_tag.title
        else:
            topics= topics + ',' +question.q_tag.title
    form.tags.data = topics
    return render_template('question_edit.html', form=form)

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
    for i in range(1,len(questions)):
        for j in range(0,len(questions)-i):
            if questions[j].created_at < questions[j+1].created_at:
                questions[j],questions[j+1] = questions[j+1],questions[j]
    return render_template('following_questions.html', user=user,
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
    question.followed_at = datetime.datetime.now()
    db.session.add(question)
    db.session.commit()
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
    question.followed_at = ''
    db.session.add(question)
    db.session.commit()
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
@main.route('/question/<qid>/answer/<aid>', methods=['GET', 'POST'])
@login_required
def answer(qid, aid):
    answer = Answer.query.filter_by(id=aid).first_or_404()
    question = Question.query.filter_by(id=answer.answer_question.id).first_or_404()
    tags = question.tags.all()
    if (datetime.datetime.now()-question.created_at).days == 0:
        created_time = datetime.datetime.strftime(question.created_at, '%H:%M')
    else:
        created_time = datetime.datetime.strftime(question.created_at, '%Y-%m-%d')
    if (datetime.datetime.now()-answer.created_at).days == 0:
        answer_created_time = datetime.datetime.strftime(answer.created_at, '%H:%M')
    else:
        answer_created_time = datetime.datetime.strftime(answer.created_at, '%Y-%m-%d')
    form_question_comment = CommentForm(prefix="form_question_comment")
    if form_question_comment.validate_on_submit() and form_question_comment.submit.data:
        comment = Comment(content=form_question_comment.content.data)
        comment.comment_question = question
        author = User.query.filter_by(id=current_user.id).first()
        comment.comment_author = author
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
        return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))
    question_comments = question.question_comments
    form_answer_comment = CommentForm(prefix="form_answer_comment")
    if form_answer_comment.validate_on_submit() and form_answer_comment.submit.data:
        comment = Comment(content=form_answer_comment.content.data)
        comment.comment_answer = answer
        author = User.query.filter_by(id=current_user.id).first()
        comment.comment_author = author
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
        return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))
    answer_comments = answer.answer_comments
    return render_template('answer.html', question=question, answer=answer, tags=tags,
                           created_time=created_time, answer_created_time=answer_created_time,
                           form_question_comment=form_question_comment, question_comments=question_comments,
                           form_answer_comment=form_answer_comment, answer_comments=answer_comments)

############  编辑答案  ############
@main.route('/answer/<id>/edit', methods=['GET', 'POST'])
@login_required
def answer_edit(id):
    answer = Answer.query.filter_by(id=id).first()
    form_answer_edit = AddAnswerForm(prefix="form_answer_edit")
    if form_answer_edit.validate_on_submit() and form_answer_edit.submit.data:
        answer.content = form_answer_edit.content.data
        answer.modified_at = datetime.datetime.now()
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))
    form_answer_edit.content.data = answer.content
    return render_template('answer_edit.html', form_answer_edit=form_answer_edit, answer=answer)

############  编辑答案2  ############
@main.route('/answer/<id>/edit2', methods=['GET', 'POST'])
@login_required
def answer_edit2(id):
    answer = Answer.query.filter_by(id=id).first()
    form_answer_edit = AddAnswerForm(prefix="form_answer_edit")
    if form_answer_edit.validate_on_submit() and form_answer_edit.submit.data:
        answer.content = form_answer_edit.content.data
        answer.modified_at = datetime.datetime.now()
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('main.question', id=answer.answer_question.id))
    form_answer_edit.content.data = answer.content
    return render_template('answer_edit.html', form_answer_edit=form_answer_edit, answer=answer)

############  用户的回答  ############
@main.route('/people/<id>/answers')
def people_answers(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.user_answers.paginate(page, per_page=100, error_out=False)
    answers = pagination.items
    for i in range(1,len(answers)):
        for j in range(0,len(answers)-i):
            if answers[j].created_at < answers[j+1].created_at:
                answers[j],answers[j+1] = answers[j+1],answers[j]
    return render_template('following_answers.html', user=user,
                           endpoint='main.people_answers', pagination=pagination,
                           answers=answers)

############  用户点赞答案  ############
@main.route('/answer/<id>/follow')
@login_required
def follow_answer(id):
    answer = Answer.query.filter_by(id=id).first()
    if answer is None:
        flash('Invalid answer.')
        return redirect(url_for('main.index'))
    if current_user.is_following_answer(answer):
        flash('你已经赞同了该答案。')
        return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))
    answer.followed_at = datetime.datetime.now()
    db.session.add(answer)
    db.session.commit()
    current_user.follow_answer(answer)
    return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))

############  用户取赞答案  ############
@main.route('/answer/<id>/unfollow')
@login_required
def unfollow_answer(id):
    answer = Answer.query.filter_by(id=id).first()
    if answer is None:
        flash('Invalid answer.')
        return redirect(url_for('main.index'))
    if not current_user.is_following_answer(answer):
        flash('你还没有赞同该答案。')
        return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))
    answer.followed_at = ''
    db.session.add(answer)
    db.session.commit()
    current_user.unfollow_answer(answer)
    return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))

############  用户点赞答案2  ############
@main.route('/answer/<id>/follow2')
@login_required
def follow_answer2(id):
    answer = Answer.query.filter_by(id=id).first()
    if answer is None:
        flash('Invalid answer.')
        return redirect(url_for('main.index'))
    if current_user.is_following_answer(answer):
        flash('你已经赞同了该答案。')
        return redirect(url_for('main.question', id=answer.answer_question.id))
    answer.followed_at = datetime.datetime.now()
    db.session.add(answer)
    db.session.commit()
    current_user.follow_answer(answer)
    return redirect(url_for('main.question', id=answer.answer_question.id))

############  用户取赞答案2  ############
@main.route('/answer/<id>/unfollow2')
@login_required
def unfollow_answer2(id):
    answer = Answer.query.filter_by(id=id).first()
    if answer is None:
        flash('Invalid answer.')
        return redirect(url_for('main.index'))
    if not current_user.is_following_answer(answer):
        flash('你还没有赞同该答案。')
        return redirect(url_for('main.question', id=answer.answer_question.id))
    answer.followed_at = ''
    db.session.add(answer)
    db.session.commit()
    current_user.unfollow_answer(answer)
    return redirect(url_for('main.question', id=answer.answer_question.id))

############  答案点赞的用户  ############
@main.route('/answer/<id>/followers')
def answer_followers(id):
    answer = Answer.query.filter_by(id=id).first()
    if answer is None:
        flash('Invalid answer.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = answer.users.paginate(page, per_page=100, error_out=False)
    answer_followers = [{'user': item.a_user} for item in pagination.items]
    return render_template('answer_followers.html', answer=answer,
                           endpoint='main.answer_followers', pagination=pagination,
                           answer_followers=answer_followers)

############  收藏答案  ############
@main.route('/answer/<id>/collect', methods=['GET', 'POST'])
@login_required
def answer_collect(id):
    answer = Answer.query.filter_by(id=id).first()
    if not current_user.user_collections:
        flash('你还没有创建收藏夹，请先创建。')
        return redirect(url_for('main.collection_add'))
    form = CollectForm()
    form.collection.choices = [(collection.title, collection.title) for collection in Collection.query.filter_by(author_id=current_user.id).all()]
    if form.validate_on_submit():
        collection = Collection.query.filter_by(title=form.collection.data).first()
        if answer.answer_is_following_collection(collection):
            flash('该收藏夹已经收藏了此答案')
        answer.answer_follow_collection(collection)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('main.answer', qid=answer.answer_question.id, aid=answer.id))
    return render_template('answer_collect.html', form=form, answer=answer)

############  收藏答案2  ############
@main.route('/answer/<id>/collect2', methods=['GET', 'POST'])
@login_required
def answer_collect2(id):
    answer = Answer.query.filter_by(id=id).first()
    if not current_user.user_collections:
        flash('你还没有创建收藏夹，请先创建。')
        return redirect(url_for('main.collection_add'))
    form = CollectForm()
    form.collection.choices = [(collection.title, collection.title) for collection in Collection.query.filter_by(author_id=current_user.id).all()]
    if form.validate_on_submit():
        collection = Collection.query.filter_by(title=form.collection.data).first()
        if answer.answer_is_following_collection(collection):
            flash('该收藏夹已经收藏了此答案')
        answer.answer_follow_collection(collection)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('main.question', id=answer.answer_question.id))
    return render_template('answer_collect.html', form=form, answer=asnwer)


###################################   收藏视图  ###################################

############  收藏夹页面  ############
@main.route('/collection/<id>', methods=['GET', 'POST'])
@login_required
def collection(id):
    collection = Collection.query.filter_by(id=id).first()
    answers = collection.answers.all()
    return render_template('collection.html', collection=collection, answers=answers)

############  创建收藏夹  ############
@main.route('/collection/add', methods=['GET', 'POST'])
@login_required
def collection_add():
    form = AddCollectionForm()
    if form.validate_on_submit():
        collection = Collection(title=form.title.data, desc=form.desc.data)
        if Collection.query.filter_by(title=form.title.data).first():
            flash('该收藏已创建。')
        else:
            author = User.query.filter_by(id=current_user.id).first()
            collection.collection_author = author
            db.session.add(collection)
            db.session.commit()
            flash('成功添加收藏。')
            return redirect(url_for('main.collection', id=collection.id))
    return render_template('collection_add.html', form=form)

############  取消收藏  ############
@main.route('/collection/<cid>/uncollect-answer/<aid>')
@login_required
def uncollect_answer(cid, aid):
    collection = Collection.query.filter_by(id=cid).first()
    answer = Answer.query.filter_by(id=aid).first()
    answer.answer_unfollow_collection(collection)
    return redirect(url_for('main.collection', id=collection.id))

############  用户的所有收藏夹  ############
@main.route('/people/<id>/collections')
@login_required
def collections(id):
    user = User.query.filter_by(id=id).first()
    collections = Collection.query.order_by(Collection.created_at.asc()).all()
    return render_template('collections.html', collections=collections, user=user)


