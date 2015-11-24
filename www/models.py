#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin

from markdown import markdown
import bleach

from www import db, login_manager


###################################  关联模型  ###################################

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Questionsusers(db.Model):
    __tablename__ = 'questions_users'
    questions_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Questionstags(db.Model):
    __tablename__ = 'questions_tags'
    questions_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    tags_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class Answersusers(db.Model):
    __tablename__ = 'answers_users'
    answers_id = db.Column(db.Integer, db.ForeignKey('answers.id'), primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class Answerscollections(db.Model):
    __tablename__ = 'answers_collections'
    answers_id = db.Column(db.Integer, db.ForeignKey('answers.id'), primary_key=True)
    collections_id = db.Column(db.Integer, db.ForeignKey('collections.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class Tagsusers(db.Model):
    __tablename__ = 'tags_users'
    tags_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class Collectionsusers(db.Model):
    __tablename__ = 'collections_users'
    collections_id = db.Column(db.Integer, db.ForeignKey('collections.id'), primary_key=True)
    users_id = db.Column( db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)


###################################  用户模型  ###################################

############  用户模型  ############
class User(UserMixin, db.Model):
    '''
    定义User模型。
    继承的UserMixin类包含了Flask-login要求实现的用户方法。
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500))
    one_desc = db.Column(db.String(50))
    location = db.Column(db.String(50))
    industry = db.Column(db.String(50))
    sex = db.Column(db.Integer, default=1)
    company = db.Column(db.String(50))
    job = db.Column(db.String(50))
    school = db.Column(db.String(50))
    majar = db.Column(db.String(50))
    about_me = db.Column(db.Text())
    is_admin = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    user_questions = db.relationship('Question', backref='question_author', lazy='dynamic')
    user_answers = db.relationship('Answer', backref='answer_author', lazy='dynamic')
    user_collections = db.relationship('Collection', backref='collection_author', lazy='dynamic')
    user_comments = db.relationship('Comment', backref='comment_author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    questions = db.relationship('Questionsusers',
                                foreign_keys=[Questionsusers.users_id],
                                backref=db.backref('q_user', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    answers = db.relationship('Answersusers',
                              foreign_keys=[Answersusers.users_id],
                              backref=db.backref('a_user', lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')
    tags = db.relationship('Tagsusers',
                           foreign_keys=[Tagsusers.users_id],
                           backref=db.backref('user_set', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')
    collections = db.relationship('Collectionsusers',
                                  foreign_keys=[Collectionsusers.users_id],
                                  backref=db.backref('set_user', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __init__(self, email, name, password, image , confirmed):
        self.email = email
        self.name = name
        self.password = password
        self.image = image
        self.confirmed = confirmed

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.1')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        '''
        cookie——使用itsdangerous包的方法生成令牌。
        TimedJSONWebSignatureSerializer类接受一个密钥，以及过期时间，这里默认3600秒。
        dumps()方法为指定的数据生成加密签名。
        '''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        '''解码令牌，序列化对象提供了loads()方法，唯一参数是令牌字符串。'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    ############  用户关注与被关注  ############
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    ############  用户关注话题  ############
    def follow_tag(self, tag):
        if not self.is_following_tag(tag):
            f = Tagsusers(user_set=self, tag_set=tag)
            db.session.add(f)
            db.session.commit()

    def unfollow_tag(self, tag):
        f = self.tags.filter_by(tags_id=tag.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following_tag(self, tag):
        return self.tags.filter_by(tags_id=tag.id).first() is not None

    ############  用户关注问题  ############
    def follow_question(self, question):
        if not self.is_following_question(question):
            f = Questionsusers(q_user=self, u_question=question)
            db.session.add(f)
            db.session.commit()

    def unfollow_question(self, question):
        f = self.questions.filter_by(questions_id=question.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following_question(self, question):
        return self.questions.filter_by(questions_id=question.id).first() is not None

    ############  用户赞同回答  ############
    def follow_answer(self, answer):
        if not self.is_following_answer(answer):
            f = Answersusers(a_user=self, u_answer=answer)
            db.session.add(f)
            db.session.commit()

    def unfollow_answer(self, answer):
        f = self.answers.filter_by(answers_id=answer.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following_answer(self, answer):
        return self.answers.filter_by(answers_id=answer.id).first() is not None

    def __repr__(self):
        return '<User %r>' % self.email


@login_manager.user_loader
def load_user(user_id):
    # 加载用户的回调函数。
    # 接受以UNICODE字符串形式的用户标识符。
    # 若找到用户，返回用户对象；否则，返回None。
    return User.query.get(int(user_id))


###################################  问题模型  ###################################

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    modified_at = db.Column(db.DateTime)
    followed_at = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_answers = db.relationship('Answer', backref='answer_question', lazy='dynamic')
    question_comments = db.relationship('Comment', backref='comment_question', lazy='dynamic')
    users = db.relationship('Questionsusers',
                            foreign_keys=[Questionsusers.questions_id],
                            backref=db.backref('u_question', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    tags = db.relationship('Questionstags',
                           foreign_keys=[Questionstags.questions_id],
                           backref=db.backref('t_question', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def __init__(self, title, content):
        self.title = title
        self.content = content


    ############  关注问题的用户  ############
    def question_is_followed_by(self, user):
        return self.users.filter_by(users_id=user.id).first() is not None

    ############  问题加上话题标签  ############
    def question_follow_tag(self, tag):
        if not self.question_is_following_tag(tag):
            f = Questionstags(t_question=self, q_tag=tag)
            db.session.add(f)
            db.session.commit()

    def question_unfollow_tag(self, tag):
        f = self.tags.filter_by(tags_id=tag.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def question_is_following_tag(self, tag):
        return self.tags.filter_by(tags_id=tag.id).first() is not None

    ############  markdown  ############
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def __repr__(self):
        return "<Question %r>" % self.title

db.event.listen(Question.content, 'set', Question.on_changed_body)


###################################  回答模型  ###################################

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)
    thanks = db.Column(db.Integer, default=0)
    no_help = db.Column(db.Integer, default=0)
    vote_up = db.Column(db.Integer, default=0)
    vote_down = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    modified_at = db.Column(db.DateTime)
    followed_at = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_comments = db.relationship('Comment', backref='comment_answer', lazy='dynamic')
    users = db.relationship('Answersusers',
                            foreign_keys=[Answersusers.answers_id],
                            backref=db.backref('u_answer', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    collections = db.relationship('Answerscollections',
                                  foreign_keys=[Answerscollections.answers_id],
                                  backref=db.backref('c_answer', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __init__(self, content):
        self.content = content

    ############  赞同问题的用户  ############
    def answer_is_followed_by(self, user):
        return self.users.filter_by(users_id=user.id).first() is not None

    ############  收藏答案  ############
    def answer_follow_collection(self, collection):
        if not self.answer_is_following_collection(collection):
            f = Answerscollections(c_answer=self, a_collection=collection)
            db.session.add(f)
            db.session.commit()

    def answer_unfollow_collection(self, collection):
        f = self.collections.filter_by(collections_id=collection.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def answer_is_following_collection(self, collection):
        return self.collections.filter_by(collections_id=collection.id).first() is not None

    ############  markdown  ############
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def __repr__(self):
        return "<Answer %r>" % self.content

db.event.listen(Answer.content, 'set', Answer.on_changed_body)


####################################   话题模型  ###################################

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(50), nullable=False, default='img/default_topic.jpg')
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    followed_at = db.Column(db.DateTime)
    users = db.relationship('Tagsusers',
                            foreign_keys=[Tagsusers.tags_id],
                            backref=db.backref('tag_set', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    questions = db.relationship('Questionstags',
                                foreign_keys=[Questionstags.tags_id],
                                backref=db.backref('q_tag', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, title, desc):
        self.title = title
        self.desc = desc

    ############  关注话题的用户  ############
    def tag_is_followed_by(self, user):
        return self.users.filter_by(users_id=user.id).first() is not None

    ############  话题下的问题  ############
    def tag_is_followed_by_question(self, question):
        return self.questionrs.filter_by(questions_id=question.id).first() is not None

    def __repr__(self):
        return "<Tag %r>" % self.title


###################################  收藏模型  ###################################

class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    users = db.relationship('Collectionsusers',
                            foreign_keys=[Collectionsusers.collections_id],
                            backref=db.backref('set_collection', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    answers = db.relationship('Answerscollections',
                              foreign_keys=[Answerscollections.collections_id],
                              backref=db.backref('a_collection', lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')

    def __init__(self, title, desc):
        self.title = title
        self.desc = desc

    def __repr__(self):
        return "<Collection %r>" % self.title


###################################  评论模型  ###################################

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    vote_up = db.Column(db.Integer, default=0)
    disabled = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<Collection %r>" % self.content


###################################  私信模型  ###################################

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    message_status = db.Column(db.Enum('unread', 'read', 'delete'), default='unread', nullable=False)
    posted_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User', backref='send_messages', lazy='joined', foreign_keys=[sender_id])
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver = db.relationship('User', backref='receive_messages', lazy='joined', foreign_keys=[receiver_id])

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<Message %r>" % self.content
