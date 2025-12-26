"""
URL configuration for xmuhelper project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('user.api_urls')),
    path('api/score/', include('score.api_urls')),
    path('api/student/material/', include('material.api_urls')),
    # 添加新的路径配置，让material应用也能处理/api/material/开头的请求
    path('api/material/', include('material.api_urls')),
]

# 添加媒体文件和静态文件的路由
if settings.DEBUG:
    # 处理所有媒体文件
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 处理静态文件
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
