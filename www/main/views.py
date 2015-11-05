#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os
import random
import string
import shutil
import time
import io
from PIL import Image, ImageOps

from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required, current_user

from main import main
from main.forms import EditProfileForm
from www import db
from www.models import User

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/people/<peoplename>')
def user(peoplename):
    user = User.query.filter_by(name=peoplename).first_or_404()
    return render_template('people.html', user=user)

@main.route('/people/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        ext = form.image.data.filename.split('.')[-1]
        filename = "%s_%js.%js" % (current_user.id, int(time.time()), ext)
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
        current_user.image = "img/uploads/%js" % filename
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
        return redirect(url_for('main.user', peoplename=current_user.name))
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
