from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限：仅允许申请的所有者（学生本人）提交和修改，其他人只读。
    """
    def has_object_permission(self, request, view, obj):
        # 读取操作（GET、HEAD、OPTIONS）允许所有请求
        if request.method in permissions.SAFE_METHODS:
            return True
        # 写入操作（POST、PUT、DELETE）仅允许所有者
        return obj.user == request.user