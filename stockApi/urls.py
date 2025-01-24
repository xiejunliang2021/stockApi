from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # 当路由匹配到'api/users/的时候，直接找users下面的urls
    path("api/users/", include('users.urls')),
    path("api/basics/", include('basic.urls')),
    # 添加接口文档的路由
    re_path(r'^docs/', include_docs_urls(title='接口文档')),

]
