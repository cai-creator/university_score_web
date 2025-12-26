from user import views
from django.urls import path, re_path

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('info/', views.UserInfoView.as_view(), name='user-info'),
    path('admin/statistics/', views.AdminStatisticsView.as_view(), name='admin-statistics'),
    
    # 学院管理
    path('admin/colleges/', views.CollegeManagementView.as_view(), name='college-management'),
    # 支持DELETE方法的学院管理路由（接受学院名称作为路径参数）
    re_path(r'admin/colleges/(?P<college_name>.*)/$', views.CollegeManagementView.as_view(), name='college-management-detail'),
    
    # 班级管理
    path('admin/classes/', views.ClassManagementView.as_view(), name='class-management'),
    # 班级详情路由（接受UUID格式的class_id）
    path('admin/classes/<uuid:class_id>/', views.ClassManagementView.as_view(), name='class-detail'),
    # 班级学生列表路由
    path('admin/classes/<uuid:class_id>/students/', views.ClassManagementView.as_view(), name='class-students'),
    # 班级删除路由（接受UUID格式的class_id）
    path('admin/classes/delete/<uuid:class_id>/', views.ClassManagementView.as_view(), name='class-delete'),
    
    # 账号管理
    path('admin/accounts/', views.AccountManagementView.as_view(), name='account-management'),
    
    # 学生管理
    path('admin/students/', views.StudentManagementView.as_view(), name='student-management'),
    
    # 教师管理
    path('admin/teachers/', views.TeacherManagementView.as_view(), name='teacher-management'),
    
    # 接受type参数的用户列表（兼容前端请求）
    path('admin/list/', views.AdminUserListView.as_view(), name='admin-user-list'),
    
    # 创建用户
    path('admin/create/', views.UserManagementView.as_view(), name='user-create'),
    
    # 删除用户
    path('admin/destroy/<uuid:user_id>/', views.UserManagementView.as_view(), name='user-destroy'),
    
    # 更新用户
    path('admin/update/', views.UserManagementView.as_view(), name='user-update'),
    # 重置密码
    path('admin/reset_password/<uuid:user_id>/', views.UserManagementView.as_view(), name='reset-password'),
    
    # 教师-班级绑定管理
    path('admin/class_bindings/', views.ClassBindingView.as_view(), name='class-binding-list'),
    # 支持DELETE方法的班级绑定管理路由（接受绑定ID作为路径参数）
    path('admin/class_bindings/<uuid:binding_id>/', views.ClassBindingView.as_view(), name='class-binding-detail'),
]