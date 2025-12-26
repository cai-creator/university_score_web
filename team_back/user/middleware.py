"""WebSocket认证中间件"""
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

class TokenAuthMiddleware(BaseMiddleware):
    """基于Token的WebSocket认证中间件"""
    
    async def __call__(self, scope, receive, send):
        # 从查询字符串中获取token
        query_string = scope.get('query_string', b'').decode()
        token_key = None
        
        # 解析查询字符串获取token
        for param in query_string.split('&'):
            if param.startswith('token='):
                token_key = param.split('=')[1]
                break
        
        # 如果没有token，直接继续处理（允许匿名连接）
        if not token_key:
            scope['user'] = None
            return await super().__call__(scope, receive, send)
        
        # 异步获取用户
        scope['user'] = await self.get_user(token_key)
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, token_key):
        """通过token获取用户"""
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None

def TokenAuthMiddlewareStack(inner):
    """WebSocket认证中间件堆栈"""
    return TokenAuthMiddleware(inner)
