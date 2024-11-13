from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    # 当路由匹配到'api/users/的时候，直接找users下面的urls
    path("api/users/", include('users.urls')),
    path("api/basics/", include('basic.urls')),
    # 添加接口文档的路由
    re_path(r'^docs/', include_docs_urls(title='接口文档')),

]
