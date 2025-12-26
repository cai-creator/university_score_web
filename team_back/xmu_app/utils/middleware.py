from django.http import JsonResponse
from rest_framework.response import Response
import json


class ResponseFormatMiddleware:
    """统一API响应格式中间件
    
    确保所有API响应都返回统一的{code, message, data}格式
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 只处理API路径的响应，避免影响静态文件等
        if request.path.startswith('/api/') or request.path.startswith('/teacher/'):
            # 如果是DRF的Response对象
            if isinstance(response, Response):
                # 检查是否已经是标准格式 {code, message, data}
                if isinstance(response.data, dict) and 'code' in response.data and 'message' in response.data:
                    return response
                
                # 检查是否是分页格式 {results, total}
                if isinstance(response.data, dict) and 'results' in response.data and 'total' in response.data:
                    # 转换为标准格式，但保留原有数据结构
                    response.data = {
                        'code': 200,
                        'message': 'success',
                        'data': response.data
                    }
                    return response
                
                # 对于其他DRF响应，转换为标准格式
                response.data = {
                    'code': response.status_code if 200 <= response.status_code < 300 else 400,
                    'message': 'success' if 200 <= response.status_code < 300 else '请求失败',
                    'data': response.data
                }
                return response
            
            # 如果是Django的JsonResponse对象
            elif isinstance(response, JsonResponse):
                try:
                    # 获取响应数据
                    response_data = json.loads(response.content.decode('utf-8'))
                    
                    # 检查是否已经是标准格式
                    if isinstance(response_data, dict) and 'code' in response_data and 'message' in response_data:
                        return response
                    
                    # 转换为标准格式
                    response_data = {
                        'code': response.status_code if 200 <= response.status_code < 300 else 400,
                        'message': 'success' if 200 <= response.status_code < 300 else '请求失败',
                        'data': response_data
                    }
                    
                    # 创建新的JsonResponse
                    return JsonResponse(response_data, status=response.status_code)
                except:
                    # 如果解析失败，保持原响应
                    pass
        
        return response