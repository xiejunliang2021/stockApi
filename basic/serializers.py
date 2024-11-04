# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：serializers.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/11/3 19:19 
@JianShu : 
'''

from rest_framework import serializers
from .models import StockBasic


class BasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockBasic
        fields = '__all__'



































