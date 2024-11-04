# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：urls.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/11/3 19:47 
@JianShu : 
'''
from django.urls import path
from .views import basic_list, BasicView

from .views import basic_list

urlpatterns = [
    # 登录
    path('tushare/basic/', basic_list),
    path('basic/', BasicView.as_view({'get': 'list'}))

]























