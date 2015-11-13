#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin

from www import db, login_manager


###################################  关联模型  ###################################

#########  关注关联表模型  #########
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
    user_questions = db.relationship('Question', primaryjoin='User.id==Question.author_id', backref='question_user', lazy='dynamic')
    user_answers = db.relationship('Answer', primaryjoin='User.id==Answer.author_id', backref='answer_user', lazy='dynamic')
    sender = db.relationship('Message', primaryjoin='User.id==Message.sender_id', backref='message_sender', lazy='dynamic')
    receiver = db.relationship('Message', primaryjoin='User.id==Message.receiver_id', backref='message_receiver', lazy='dynamic')

    def __init__(self, email, name, password,image):
        self.email = email
        self.name = name
        self.password = password
        self.image = image

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
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_comments = db.relationship('Comment', primaryjoin='Question.id==Comment.question_id', backref='comment_question', lazy='dynamic')
    question_answers = db.relationship('Answer', primaryjoin='Question.id==Answer.question_id', backref='answer_question', lazy='dynamic')
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

    def __repr__(self):
        return "<Question %r>" % self.title


###################################  回答模型  ###################################

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

    def __repr__(self):
        return "<Answer %r>" % self.content


####################################   话题模型  ###################################

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(50), nullable=False, default='img/default_topic.jpg')
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
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

    def tag_is_followed_by(self, user):
        return self.users.filter_by(users_id=user.id).first() is not None

    def __repr__(self):
        return "<Tag %r>" % self.title


###################################  收藏模型  ###################################

class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text)
    author = db.Column(db.String(50), nullable=False)
    author_desc = db.Column(db.String(50), nullable=False)
    author_image = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
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

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Collection %r>" % self.title


###################################  评论模型  ###################################

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


###################################  私信模型  ###################################

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
