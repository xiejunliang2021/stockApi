# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：filters.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/11/3 20:32 
@JianShu : 
'''
# filters.py
import django_filters
from .models import StockBasic


class StockBasicFilter(django_filters.FilterSet):
    class Meta:
        model = StockBasic
        fields = {
            'name': ['exact', 'icontains'],  # 精确匹配和不区分大小写的包含
            'area': ['exact'],
            'industry': ['exact'],
            'list_date': ['gte', 'lte'],  # 大于等于和小于等于
            'ts_code': ['exact', 'icontains'],
            'symbol': ['exact', 'icontains']
        }
