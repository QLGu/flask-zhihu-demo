#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin

from www import db, login_manager


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)


questions_users = db.Table(
    'questions_users',
    db.Column('questions_id', db.Integer, db.ForeignKey('questions.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
)

questions_tags = db.Table(
    'questions_tags',
    db.Column('questions_id', db.Integer, db.ForeignKey('questions.id')),
    db.Column('tags_id', db.Integer, db.ForeignKey('tags.id'))
)

answers_users = db.Table(
    'answers_users',
    db.Column('answers_id', db.Integer, db.ForeignKey('answers.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
)

answers_collections = db.Table(
    'answers_collections',
    db.Column('answers_id', db.Integer, db.ForeignKey('answers.id')),
    db.Column('collections_id', db.Integer, db.ForeignKey('collections.id'))
)

tags_users = db.Table(
    'tags_users',
    db.Column('tags_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
)

collections_users = db.Table(
    'collections_users',
    db.Column('collections_id', db.Integer, db.ForeignKey('collections.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
)


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
    user_followed = db.relationship('Follow',
                                    foreign_keys=[Follow.follower_id],
                                    backref=db.backref('user_follower', lazy='joined'),
                                    lazy='dynamic',
                                    cascade='all, delete-orphan')
    user_followers = db.relationship('Follow',
                                     foreign_keys=[Follow.followed_id],
                                     backref=db.backref('user_followed', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')
    user_questions = db.relationship('Question', primaryjoin='User.id==Question.author_id', backref='question_user', lazy='dynamic')
    user_answers = db.relationship('Answer', primaryjoin='User.id==Answer.author_id', backref='answer_user', lazy='dynamic')
    sender = db.relationship('Message', primaryjoin='User.id==Message.sender_id', backref='message_sender', lazy='dynamic')
    receiver = db.relationship('Message', primaryjoin='User.id==Message.receiver_id', backref='message_receiver', lazy='dynamic')

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

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def __init__(self, email, name, password,image):
        self.email = email
        self.name = name
        self.password = password
        self.image = image

    def __repr__(self):
        return '<User %r>' % self.email


@login_manager.user_loader
def load_user(user_id):
    # 加载用户的回调函数。
    # 接受以UNICODE字符串形式的用户标识符。
    # 若找到用户，返回用户对象；否则，返回None。
    return User.query.get(int(user_id))


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.String(50), nullable=False)
    question_comments = db.relationship('Comment', primaryjoin='Question.id==Comment.question_id', backref='comment_question', lazy='dynamic')
    question_answers = db.relationship('Answer', primaryjoin='Question.id==Answer.question_id', backref='answer_question', lazy='dynamic')
    question_follower = db.relationship('User',
                                        secondary=questions_users,
                                        primaryjoin=(questions_users.c.questions_id==id),
                                        secondaryjoin=(questions_users.c.users_id==id),
                                        backref=db.backref('following_question', lazy='dynamic'),
                                        lazy='dynamic')
    question_tag = db.relationship('Tag',
                                   secondary=questions_tags,
                                   primaryjoin=(questions_tags.c.questions_id==id),
                                   secondaryjoin=(questions_tags.c.tags_id==id),
                                   backref=db.backref('tag_question', lazy='dynamic'),
                                   lazy='dynamic')

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Question %r>" % self.title


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    thanks = db.Column(db.Integer, default=0)
    no_help = db.Column(db.Integer, default=0)
    vote_up = db.Column(db.Integer, default=0)
    vote_down = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_comments = db.relationship('Comment', primaryjoin='Answer.id==Comment.answer_id', backref='comment_answer', lazy='dynamic')
    vote_user = db.relationship('User',
                                secondary=answers_users,
                                primaryjoin=(answers_users.c.answers_id==id),
                                secondaryjoin=(answers_users.c.users_id==id),
                                backref=db.backref('user_vote', lazy='dynamic'),
                                lazy='dynamic')
    answer_collection = db.relationship('Collection',
                                        secondary=answers_collections,
                                        primaryjoin=(answers_collections.c.answers_id==id),
                                        secondaryjoin=(answers_collections.c.collections_id==id),
                                        backref=db.backref('collection_answer', lazy='dynamic'),
                                        lazy='dynamic')

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<Answer %r>" % self.content


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)  # 话题结构多对多？节点的父级和父级的父级不能作为自己或自己子级的子级? redis实现？
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    tag_follower = db.relationship('User',
                                   secondary=tags_users,
                                   primaryjoin=(tags_users.c.tags_id==id),
                                   secondaryjoin=(tags_users.c.users_id==id),
                                   backref=db.backref('following_tag', lazy='dynamic'),
                                   lazy='dynamic')

    def __init__(self, title, desc):
        self.title = title
        self.desc = desc

    def __repr__(self):
        return "<Tag %r>" % self.title


class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text)
    author = db.Column(db.String(50), nullable=False)
    author_desc = db.Column(db.String(50), nullable=False)
    author_image = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    collection_follower = db.relationship('User',
                                          secondary=collections_users,
                                          primaryjoin=(collections_users.c.collections_id==id),
                                          secondaryjoin=(collections_users.c.users_id==id),
                                          backref=db.backref('following_collection', lazy='dynamic'),
                                          lazy='dynamic')

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Collection %r>" % self.title


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    author_image = db.Column(db.String(50), nullable=False)
    vote_up = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<Comment %r>" % self.content


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    message_status = db.Column(db.Enum('unread', 'read', 'delete'), default='unread', nullable=False)
    posted_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<Message %r>" % self.content
