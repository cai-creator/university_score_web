from django.http import JsonResponse
from django.views.debug import technical_500_response
import sys
import traceback

class JSONErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # 处理所有错误状态码，转换为JSON格式
        if response.status_code >= 400:
            # 如果响应已经是JSON格式，直接返回
            if "application/json" in response.get("Content-Type", ""):
                return response
            
            # 获取错误信息
            if response.status_code == 404:
                error_msg = "请求的资源不存在"
            elif response.status_code == 403:
                error_msg = "没有权限访问该资源"
            elif response.status_code == 401:
                error_msg = "未授权的访问"
            elif response.status_code == 400:
                error_msg = "请求参数错误"
            elif response.status_code == 500:
                error_msg = "服务器内部错误"
            else:
                error_msg = f"请求失败，状态码: {response.status_code}"
            
            # 构建JSON响应
            response_data = {
                "errorcode": True,
                "error": error_msg,
                "status_code": response.status_code
            }
            
            # 返回JSON响应
            return JsonResponse(response_data, status=response.status_code)
        
        return response

    def process_exception(self, request, exception):
        # 在DEBUG模式下，为管理员提供详细的错误信息
        if request.user.is_superuser and hasattr(request, 'user'):
            return technical_500_response(request, *sys.exc_info())
        
        # 捕获所有异常，返回JSON格式的错误响应
        error_msg = str(exception)
        error_type = type(exception).__name__
        
        # 获取异常的堆栈信息
        traceback_info = traceback.format_exc()
        
        # 将详细错误信息记录到日志
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"API Error: {error_type}: {error_msg}\nURL: {request.get_full_path()}\nMethod: {request.method}\nUser: {request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'}\nTraceback: {traceback_info}")
        
        # 构建JSON响应
        response_data = {
            "errorcode": True,
            "error": error_msg,
            "error_type": error_type,
            "status_code": 500
        }
        
        # 返回JSON响应，状态码为500
        return JsonResponse(response_data, status=500)