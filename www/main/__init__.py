#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import Blueprint

main = Blueprint('main', __name__)

from main import views, errors
