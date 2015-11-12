#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

import os

from www import create_app, db

from www.models import User, Question, Answer, Tag, Collection, Comment, Message

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def test():
    '''
    单元测试
    '''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    app.run(debug=True)

