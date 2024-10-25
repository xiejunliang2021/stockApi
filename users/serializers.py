# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：serializers.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/10/25 17:35 
@JianShu : users表的序列化器
'''

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ 用户模型的序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'avatar', 'last_name']



















