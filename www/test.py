#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from datetime import datetime

from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'set a secret key'  # 不应该直接写入代码，正确的方式是保存在环境变量中，等后期该。
bootstrap = Bootstrap(app)
moment = Moment(app)

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
    anwser = None
    form = AnwserForm()
    if form.validate_on_submit():
        anwser = form.anwser.data
        form.anwser.data = ''
    return render_template('index.html', form=form, anwser=anwser, current_time=datetime.utcnow())

if __name__ == "__main__":
    app.run(debug=True)
