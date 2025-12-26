"""
URL configuration for xmu_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from typing import List, Union
from django.conf import settings
from django.conf.urls.static import static

class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema

# Schema view 配置 - 修复类型注解问题
schema_view = get_schema_view(
    openapi.Info(
        title="学生申请管理系统 API",
        default_version='v1.0',
        description="""
        学生申请管理系统 API 文档

        ## 功能概述

        - **学生功能**: 提交各类申请、查看申请状态、管理个人申请
        - **教师功能**: 审核学生申请、查看审核记录、统计信息
        - **管理员功能**: 用户管理、系统监控、数据统计

        ## 认证方式

        使用 Token 认证，在登录后获取 token，在请求头中添加：
        `Authorization: Token {your_token}`

        ## 权限说明

        - **学生**: 只能操作自己的申请数据
        - **教师**: 可以审核所有申请
        - **管理员**: 拥有所有权限
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@xmu.edu.cn"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    # 修复权限类类型问题
    permission_classes=(permissions.AllowAny,),  # type: ignore
    generator_class=BothHttpAndHttpsSchemaGenerator,
)

urlpatterns: List[Union[path, re_path]] = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('user.api_urls')),
    # 移除重复的'/api/auth/'路径，避免路由冲突
    path('api/score/', include('score.api_urls')),
    path('api/student/material/', include('material.api_urls')),
    # 添加直接的api路径，匹配前端调用
    path('api/applications/', include('material.api_urls')),
    path('api/files/', include('material.api_urls')),
    # 添加material应用的根路径，匹配前端的/api/material/请求
    path('api/material/', include('material.api_urls')),

    # Swagger 文档路由 - 添加类型忽略注释
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),  # type: ignore
            name='schema-json'),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),  # type: ignore
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),  # type: ignore
         name='schema-redoc'),

    # 根路径重定向到文档
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)