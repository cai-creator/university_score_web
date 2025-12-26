from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # 调用默认的DRF异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF已经处理了异常，我们只需要重新格式化响应
        error_data = {
            "errorcode": True,
            "error": response.data,
            "status_code": response.status_code
        }
        return Response(error_data, status=response.status_code)
    
    # 如果DRF没有处理异常，记录日志并返回通用的服务器错误
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    # 构建自定义响应
    error_data = {
        "errorcode": True,
        "error": "服务器内部错误",
        "status_code": 500
    }
    
    return Response(error_data, status=500)