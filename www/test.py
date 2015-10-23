#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from flask import Flask, request, render_template, session, redirect, url_for, flash

from flask.ext.bootstrap import Bootstrap

from flask.ext.moment import Moment

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Required

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'set a secret key'  # 不应该直接写入代码，正确的方式是保存在环境变量中，等后期该。
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/zhihu'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWM'] = True
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<User %r>' % self.email

class AnwserForm(Form):
    anwser = TextAreaField('输入答案', validators=[Required()])
    submit = SubmitField('发布')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = AnwserForm()
    if form.validate_on_submit():
        old_anwser = session.get('anwser')
        if old_anwser is not None and old_anwser != form.anwser.data:
            flash('答案已重新编辑')
        session['anwser'] = form.anwser.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, anwser=session.get('anwser'), current_time=datetime.utcnow())

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
