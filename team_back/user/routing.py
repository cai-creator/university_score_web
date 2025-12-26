"""WebSocket路由配置"""
from django.urls import re_path

# 导入WebSocket consumers（如果有）
# from .consumers import AdvisorAllocationConsumer

# WebSocket路由配置
websocket_urlpatterns = [
    # 导师分配WebSocket路由
    # re_path(r'ws/advisor-allocation/$', AdvisorAllocationConsumer.as_asgi()),
    # 目前没有实际的WebSocket consumers，所以路由列表为空
]
