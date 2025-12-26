from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.isauthenticated and request.user.is_student

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.isauthenticated and request.user.is_teacher

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.isauthenticated and request.user.is_admin