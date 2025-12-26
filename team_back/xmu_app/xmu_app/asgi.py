"""
ASGI config for xmu_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmu_app.settings')

# 确保首先加载Django应用
django_asgi_app = get_asgi_application()

# 延迟导入路由和中间件，避免循环导入
from user.routing import websocket_urlpatterns
from user.middleware import TokenAuthMiddlewareStack

# 创建ASGI应用
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket路由
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
