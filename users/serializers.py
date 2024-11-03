# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：serializers.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/10/25 17:35 
@JianShu : users表的序列化器
'''

from rest_framework import serializers
from .models import User, Addr


class UserSerializer(serializers.ModelSerializer):
    """ 用户模型的序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'avatar', 'last_name']
        # 下面的参数是只对数据进行序列化（只读），还有write_only，只对数据进行反序列化（只写）
        # extra_kwargs = {
        #     'id': {'read_only': True}
        # }


class AddrSerializer(serializers.ModelSerializer):
    """ 用户地址模型序列化器"""
    class Meta:
        model = Addr
        fields = '__all__'



















