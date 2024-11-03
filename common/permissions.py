# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：permissions.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/10/26 16:55 
@JianShu : 权限校验
'''

from rest_framework import permissions


class UserPermissions(permissions.BasePermission):
    """ 控制用户对象级别的高级权限"""
    def has_object_permission(self, request, view, obj):
        # 如果是管理员用户，则可以进行所有操作，否则只能读取用户的数据
        if request.user.is_superuser:
            return True

        # 校验用户,如果不是管理员，则判断操作用户对象和登录的用户对象是否为同一个
        return obj == request.user


class AddrPermissions(permissions.BasePermission):
    """ 控制用户对象级别的高级权限"""
    def has_object_permission(self, request, view, obj):
        # 如果是管理员用户，则可以进行所有操作，否则只能读取用户的数据
        if request.user.is_superuser:
            return True

        # 校验用户,如果不是管理员，则判断操作用户对象和登录的用户对象是否为同一个
        '''
        为什么这里用obj.user而上面却用obj呢，据我估计，这里表中有user字段，而且这个字段是关联其它表的字段
        并且也是过滤的字段，根据这个字段来判断是否为当前用户，不知是否正确，以后有时间来确认
        '''
        return obj.user == request.user







