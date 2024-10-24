from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # 当路由匹配到'api/users/的时候，直接找users下面的urls
    path("api/users/", include('users.urls'))
]
