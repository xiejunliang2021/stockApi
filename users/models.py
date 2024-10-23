from django.db import models
# 导入公共模型类
from common.db import BaseModel
# django中自带的用户认证模型
from django.contrib.auth.models import AbstractUser


# 创建用户类，继承AbstractUser django用户自带的模型类 和 BaseModel 自己编写的公共类
class User(AbstractUser, BaseModel):
    """用户模型类"""
    mobile = models.CharField(verbose_name='手机号', default='', max_length=11)
    avatar = models.ImageField(verbose_name='用户头像', blank=True, null=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户表'


class Addr(models.Model):
    """收获地址模型"""
    user = models.ForeignKey('User', verbose_name='所属用户', on_delete=models.CASCADE)
    phone = models.CharField(verbose_name='手机号码', max_length=11)
    province = models.CharField(verbose_name='省份', max_length=20)
    name = models.CharField(verbose_name='联系人', max_length=20)
    city = models.CharField(verbose_name='城市', max_length=20)
    county = models.CharField(verbose_name='区县', max_length=20)
    address = models.CharField(verbose_name='详细地址', max_length=100)
    is_default = models.BooleanField(verbose_name='是否为默认收获地址', default=False)

    class Meta:
        db_table = 'addr'
        verbose_name = '收获地址表'


class Area(models.Model):
    """ 省市区县模型 """
    pid = models.IntegerField(verbose_name='上级id')
    name = models.CharField(verbose_name='地区名称', max_length=22)
    level = models.CharField(verbose_name='区域等级', max_length=3)

    class Meta:
        db_table = 'area'
        verbose_name = '地区表'


class AuthCode(models.Model):
    """验证码模型"""
    mobile = models.CharField(verbose_name='手机号码', max_length=11)
    code = models.CharField(max_length=6, verbose_name='验证码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')

    class Meta:
        db_table = 'authcode'
        verbose_name = '手机验证码表'
