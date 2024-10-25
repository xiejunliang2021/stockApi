from django.contrib import admin
from django.urls import path
from .views import LoginView, RegistrView, UserView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # 登录
    path('login/', LoginView.as_view()),
    # 注册
    path('register/', RegistrView.as_view()),
    # 刷新token
    path('token/refresh/', TokenRefreshView.as_view()),
    # 校验token
    path('token/verify/', TokenVerifyView.as_view()),
    # 获取单个用户信息的路由,as_view()中的参数是用来指定动作的
    path('users/<int:pk>/', UserView.as_view({'get': 'retrieve'}))
]
