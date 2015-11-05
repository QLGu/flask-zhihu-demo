#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import Blueprint

auth = Blueprint('auth', __name__)  # 创建auth蓝本，参数有2个，分别为蓝本名和蓝本所在的包/模块。

from auth import views  # 放在末尾导入，避免循环导入依赖，因为在viwes.py中还要导入蓝本auth。
