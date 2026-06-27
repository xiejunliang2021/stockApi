import re
from django.shortcuts import render
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.views import APIView
from .models import User, Addr, TestStatic
from .serializers import UserSerializer, AddrSerializer
from rest_framework.permissions import IsAuthenticated
from common.permissions import UserPermissions, AddrPermissions
from django.views.decorators.csrf import csrf_exempt


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data)
        if not serializer.is_valid():
            # print(serializer.errors)  # 打印错误信息
            # 返回标准的错误信息
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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

    def upload_avatar(self, request, *args, **kwargs):
        """ 用户上传头像"""

        return Response({'url': '头像上传成功'})


class AddrView(GenericViewSet,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.ListModelMixin,
               mixins.DestroyModelMixin):
    queryset = Addr.objects.all()
    serializer_class = AddrSerializer
    # 设置认证用户才能登录
    permission_classes = [IsAuthenticated, AddrPermissions]
    # 指定过滤器字段
    filterset_fields = ('user',)


class StaticView(APIView):
    """ 策略视图 """

    def post(self, request):
        """注册接口"""
        # 接收用户参数
        stop_profit = request.data.get('stop_profit')
        date = request.data.get('date')

        # 校验参数是否为空
        if not stop_profit:
            return Response({'status_code': 422, 'errors': '止盈涨幅不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if not date:
            return Response({'status_code': 422, 'errors': '日期不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        buy_01 = 888.88
        buy_02 = 999.99
        code = 'sh601618'
        name = '中国中冶'
        loss = 666

        # 创建用户
        obj = TestStatic.objects.create(stop_profit=stop_profit, date=date, buy_01=buy_01, buy_02=buy_02,
                                        code=code,
                                        name=name, loss=loss)
        res = {
            'id': obj.id,
            'stop_profit': obj.stop_profit,
            'date': obj.date,
            'buy_01': obj.buy_01,
            'buy_02': obj.buy_02,
            'loss': obj.loss,
            'code': obj.code,
            'name': obj.name,

        }

        return Response(res, status=status.HTTP_201_CREATED)


import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserKey, BrowseRecord

class LoginByKeyView(APIView):
    def post(self, request):
        key_str = request.data.get('key')
        if not key_str:
            return Response({'errors': 'Key不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            user_key = UserKey.objects.select_related('user').get(key=key_str)
            user = user_key.user
            if not user.is_active:
                return Response({'errors': '该Key关联的用户已被禁用'}, status=status.HTTP_400_BAD_REQUEST)
        except UserKey.DoesNotExist:
            return Response({'errors': '无效的Key'}, status=status.HTTP_400_BAD_REQUEST)

        # 手动生成 SimpleJWT token
        refresh = RefreshToken.for_user(user)
        res = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'mobile': user.mobile,
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'is_superuser': user.is_superuser
        }
        return Response(res, status=status.HTTP_200_OK)


class GenerateKeyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_superuser and not request.user.is_staff:
            return Response({'errors': '权限不足，只有管理员可以生成Key'}, status=status.HTTP_403_FORBIDDEN)
            
        target_username = request.data.get('username')
        if not target_username:
            return Response({'errors': '目标用户名不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
        try:
            target_user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            return Response({'errors': '目标用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
            
        new_key_str = str(uuid.uuid4()).replace('-', '')
        
        user_key, created = UserKey.objects.update_or_create(
            user=target_user,
            defaults={'key': new_key_str}
        )
        
        return Response({
            'username': target_user.username,
            'key': new_key_str,
            'created': not created
        }, status=status.HTTP_200_OK)


class BrowseRecordListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser and not request.user.is_staff:
            return Response({'errors': '权限不足，只有管理员可以查看浏览记录'}, status=status.HTTP_403_FORBIDDEN)
            
        records = BrowseRecord.objects.select_related('user').all()[:500]
        res_list = []
        for r in records:
            res_list.append({
                'id': r.id,
                'username': r.user.username if r.user else 'Anonymous',
                'path': r.path,
                'method': r.method,
                'ip': r.ip,
                'user_agent': r.user_agent,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return Response(res_list, status=status.HTTP_200_OK)
