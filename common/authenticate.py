# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：authenticate.py
@Author ：Anita_熙烨
@Date ：2024/10/24 11:18 
@JianShu : 自定义用户登录，实现多字段登录
'''
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class MyBackend(ModelBackend):
    """自定义登录认证"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        pass