from django.urls import path
from material import views

urlpatterns = [
    # 学生端我的申请路由
    path('student/applications/', views.StudentApplicationViewSet.as_view({'get': 'list'})),
    path('student/applications/<uuid:pk>/', views.StudentApplicationViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'})),
    path('student/application-summary/', views.StudentApplicationViewSet.as_view({'get': 'application_summary'})),
    path('student/application-stats/', views.StudentApplicationViewSet.as_view({'get': 'application_stats'})),

    # 英语成绩相关路由
    path('english_scores/', views.EnglishScoreViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('english_scores/<uuid:pk>/', views.EnglishScoreViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 学术论文相关路由
    path('academic_papers/', views.AcademicPaperViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('academic_papers/<uuid:pk>/', views.AcademicPaperViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 专利作品相关路由
    path('patent_works/', views.PatentWorkViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('patent_works/<uuid:pk>/', views.PatentWorkViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 学术竞赛相关路由
    path('academic_competitions/', views.AcademicCompetitionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('academic_competitions/<uuid:pk>/', views.AcademicCompetitionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 创新项目相关路由
    path('innovation_projects/', views.InnovationProjectViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('innovation_projects/<uuid:pk>/', views.InnovationProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # CCF-CSP认证相关路由
    path('ccf_csp_certifications/', views.CCFCSPCertificationViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('ccf_csp_certifications/<uuid:pk>/', views.CCFCSPCertificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 国际组织实习相关路由
    path('international_internships/', views.InternationalInternshipViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('international_internships/<uuid:pk>/', views.InternationalInternshipViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 兵役服务相关路由
    path('military_services/', views.MilitaryServiceViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('military_services/<uuid:pk>/', views.MilitaryServiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 志愿服务相关路由
    path('volunteer_services/', views.VolunteerServiceViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('volunteer_services/<uuid:pk>/', views.VolunteerServiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 荣誉称号相关路由
    path('honorary_titles/', views.HonoraryTitleViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('honorary_titles/<uuid:pk>/', views.HonoraryTitleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 社会工作相关路由
    path('social_works/', views.SocialWorkViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('social_works/<uuid:pk>/', views.SocialWorkViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 体育竞赛相关路由
    path('sports_competitions/', views.SportsCompetitionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('sports_competitions/<uuid:pk>/', views.SportsCompetitionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # 通用申请相关路由
    path('applications/', views.ApplicationViewSet.as_view({'post': 'create'})),
    path('applications/<uuid:pk>/', views.ApplicationViewSet.as_view({'put': 'update'})),
    path('applications/<uuid:pk>/withdraw/', views.ApplicationViewSet.as_view({'post': 'withdraw'})),
    path('applications/withdraw/<uuid:pk>/', views.ApplicationViewSet.as_view({'post': 'withdraw'})),
    path('applications/types/', views.ApplicationViewSet.as_view({'get': 'types'})),
    path('applications/application-stats/', views.ApplicationViewSet.as_view({'get': 'application_stats'})),
    
    # 管理员/教师相关路由
    path('admin/applications/', views.AdminMaterialApplicationViewSet.as_view({'get': 'list'})),
    path('admin/applications/<uuid:pk>/', views.AdminMaterialApplicationViewSet.as_view({'get': 'retrieve'})),
    path('admin/applications/<uuid:pk>/approve/', views.AdminMaterialApplicationViewSet.as_view({'post': 'approve'})),
    path('admin/applications/<uuid:pk>/reject/', views.AdminMaterialApplicationViewSet.as_view({'post': 'reject'})),
    path('reviews/recent-applications/', views.AdminMaterialApplicationViewSet.as_view({'get': 'recent_applications'})),
    path('reviews/recent-applications/<uuid:pk>/', views.AdminMaterialApplicationViewSet.as_view({'get': 'retrieve'})),
]