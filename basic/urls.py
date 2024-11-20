# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：urls.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/11/3 19:47 
@JianShu : 
'''

from django.urls import path
from .views import basic_list, BasicView, analyze_data, TradeCalView, StockListView

urlpatterns = [
    # 登录
    path('tushare/basic/', basic_list),
    path('basic/', BasicView.as_view({'get': 'list'})),
    path('date_is_open/', TradeCalView.as_view({'get': 'list'})),
    # 测试，从前端获取数据，进行分析后返回给前端
    path('analyze/', analyze_data),
    path('get_stock_list/', StockListView.as_view())

]
























