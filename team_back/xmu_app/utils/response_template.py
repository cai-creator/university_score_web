from rest_framework.response import Response


class ResponseTemplate:
    """统一响应格式模板"""
    
    @staticmethod
    def success(data=None, message="success"):
        """返回成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            Response: 符合{code, message, data}格式的成功响应
        """
        response_data = {
            "code": 200,
            "message": message,
            "data": data if data is not None else {}
        }
        return Response(response_data)
    
    @staticmethod
    def error(code=400, message="请求失败", data=None):
        """返回错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            data: 错误数据（可选）
            
        Returns:
            Response: 符合{code, message, data}格式的错误响应
        """
        response_data = {
            "code": code,
            "message": message,
            "data": data if data is not None else {}
        }
        return Response(response_data, status=code)
    
    @staticmethod
    def pagination(results, total, message="success"):
        """返回分页响应
        
        Args:
            results: 分页数据列表
            total: 总记录数
            message: 响应消息
            
        Returns:
            Response: 符合前端期望的分页响应格式
        """
        # 为了兼容前端，同时支持两种格式
        # 1. 标准格式 {code, message, data}
        # 2. 前端期望的分页格式 {results, total}
        response_data = {
            "code": 200,
            "message": message,
            "data": {
                "results": results if results else [],
                "total": total
            }
        }
        return Response(response_data)