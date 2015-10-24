#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os

from www import create_app, db

from www.models import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run(debug=True)

