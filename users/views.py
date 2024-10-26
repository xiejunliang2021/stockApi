import re
from django.shortcuts import render
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from common.permissions import UserPermissions


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # 自定义登陆成功后返回的数据信息
        result = serializer.validated_data
        result['id'] = serializer.user.id
        result['username'] = serializer.user.username
        result['email'] = serializer.user.email
        result['mobile'] = serializer.user.mobile
        # 将access名称改为token
        result['token'] = result.pop('access')

        return Response(result, status=status.HTTP_200_OK)


class RegistrationView(ViewSet):
    """ 注册视图 如果使用ViewSet的话直接写create方法"""

    def create(self, request):
        pass


class RegistrView(APIView):
    """ 注册视图 """

    def post(self, request):
        """注册接口"""
        # 接收用户参数
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password_confirmation = request.data.get('password_confirmation')
        mobile = request.data.get('mobile')
        # 校验参数是否为空
        if not username:
            return Response({'status_code': 422, 'errors': '用户名不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if not email:
            return Response({'status_code': 422, 'errors': '邮箱不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if not password:
            return Response({'status_code': 422, 'errors': '密码不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if not password_confirmation:
            return Response({'status_code': 422, 'errors': '确认密码不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 校验用户名是否存在
        if User.objects.filter(username=username).exists():
            return Response({'status_code': 422, 'message': '注册失败', 'errors': '用户已存在'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 校验两次密码是否一致
        if password != password_confirmation:
            return Response({'status_code': 422, 'message': '注册失败', 'errors': '两次输入的密码不一致'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 校验密码长度
        if not (6 <= len(password) <= 18):
            return Response({'status_code': 422, 'message': '注册失败', 'errors': '密码的长度需要在6到18位之间'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 校验邮箱是否存在
        if User.objects.filter(email=email).exists():
            return Response({'status_code': 422, 'message': '注册失败', 'errors': '邮箱已使用'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 校验手机号码是否存在
        if not mobile or len(mobile) != 11:
            return Response({'status_code': 422, 'message': '注册失败', 'errors': '手机号码未填写或者手机号码位数不对'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 校验邮箱是否符合邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$', email):
            return Response({'status_code': 422, 'message': '注册失败', 'errors': '邮箱的格式不正确，请检查后重新输入'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 创建用户
        obj = User.objects.create_user(username=username, password=password, email=email, mobile=mobile)
        res = {
            'id': obj.id,
            'username': username,
            'email': obj.email,
            'mobile': mobile
        }

        return Response(res, status=status.HTTP_201_CREATED)


class UserView(GenericViewSet, mixins.RetrieveModelMixin):
    """
        用户相关操作的视图 ，
        由于我们不需要增删改查太多的功能，所以我们值继承了mixins中的获取单个用户信息的功能
    """
    # 获取用户的信息
    queryset = User.objects.all()
    # 指定序列化器
    serializer_class = UserSerializer
    # 权限认证(设置认证用户才能查看当前信息）
    permission_classes = [IsAuthenticated, UserPermissions]













