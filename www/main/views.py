#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import render_template

from main import main

@main.route('/')
def index():
    return render_template('index.html')

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
