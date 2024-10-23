# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：db.py
@Author ：Anita_熙烨
@Date ：2024/10/23 10:15 
@JianShu : 人生在世不容易，求佛祖保佑我们全家苦难不近身，平安健康永相随，
            远离小人讹诈，万事如意，心想事成！！！
'''

from django.db import models


class BaseModel(models.Model):
    """ 公共字段模型 """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        # 声明这是一个抽象的模型，在执行迁移文件时，不会在数据库中生成表
        abstract = True
        verbose_name_plural = "公共字段表"
        db_table = 'BaseTable'
