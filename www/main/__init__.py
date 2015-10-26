#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'hipponensis'

from flask import Blueprint

main = Blueprint('main', __name__)  # 创建main蓝本，参数有2个，分别为蓝本名和蓝本所在的包/模块。

from main import views, errors  # 放在末尾导入，避免循环导入依赖，因为在viwes.py和errors.py中还要导入蓝本main。
