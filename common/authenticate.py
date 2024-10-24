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
from rest_framework import serializers

from users.models import User


class MyBackend(ModelBackend):
    """自定义登录认证"""
    # 如果用户认证通过直接返回用户，否则返回未找到用户
    def authenticate(self, request, username=None, password=None, **kwargs):
        """ 支持使用手机号，邮箱，用户名登录"""
        try:
            # 利用Q对象多条件查找
            user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
        except:
            # 返回异常用raise
            raise serializers.ValidationError({'error': '未找到该用户！'})

        # 判断密码
        if user.check_password(password):
            return user
        else:
            raise serializers.ValidationError({'error': '密码错误！请重试！'})
