from django.contrib import admin
from django.urls import path
from .views import LoginView, RegistrView, UserView, AddrView, StaticView
# from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # 登录
    path('login/', LoginView.as_view()),
    # 注册
    path('register/', RegistrView.as_view()),
    # # 刷新token
    # path('token/refresh/', TokenRefreshView.as_view()),
    # # 校验token
    # path('token/verify/', TokenVerifyView.as_view()),
    # 获取单个用户信息的路由,as_view()中的参数是用来指定动作的
    path('users/<int:pk>/', UserView.as_view({'get': 'retrieve'})),
    # 头像上传路由
    path('<int:pk>/avatar/upload/', UserView.as_view({'post': 'upload_avatar'})),
    # 获取收货地址的路由
    path('address/', AddrView.as_view({'post': 'create', 'get': 'list'})),
    # 修改和删除收货地址的路由
    path('address/<int:pk>/', AddrView.as_view({
        'put': 'update',
        'delete': 'destroy'
    })),
    path('static/', StaticView.as_view()),
]
