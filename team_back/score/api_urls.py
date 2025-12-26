from score import views
from django.urls import path

urlpatterns = [
    path('student-performance/my_performance/',views.StudentPerformanceViewSet.as_view({'get':'my_performance'}),name='student-performance'),
    path('student-performance/by_student_id/',views.StudentPerformanceViewSet.as_view({'get':'by_student_id'}),name='student-performance'),
    path('student-performance/list_all/',views.StudentPerformanceViewSet.as_view({'get':'list_all'}),name='student-performance'),
    path('student-performance/statistics/',views.StudentPerformanceViewSet.as_view({'get':'statistics'}),name='student-performance'),
    path('student-performance/ranking/',views.StudentPerformanceViewSet.as_view({'get':'ranking'}),name='student-performance'),
    path('student/score-items/',views.StudentPerformanceViewSet.as_view({'get':'score_items'}),name='score-items'),
]