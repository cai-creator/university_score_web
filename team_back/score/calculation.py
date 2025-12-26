import uuid
from decimal import Decimal
from django.db import models
from django.db.models import Avg, Max, Min, Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from user.models import User
from material.models import (
    EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
    InnovationProject, CCFCSPCertification, InternationalInternship,
    MilitaryService, VolunteerService, HonoraryTitle, SocialWork, SportsCompetition
)
from .models import AcademicPerformance
from .serializers import AcademicPerformanceSerializer, AcademicPerformanceDetailSerializer, PerformanceStatsSerializer


def calculate_academic_score(gpa):
    """
    根据绩点计算学业成绩（满分80分）
    满绩点4.0对应80分，线性换算
    """
    if not gpa:
        return 0.0
    # 绩点4.0对应80分，线性换算
    academic_score = (float(gpa) / 4.0) * 80.0
    return min(80.0, max(0.0, academic_score))


def calculate_total_score(user_id):
    """
    计算学生总分
    总分 = 学业成绩（80分） + 加分成绩（20分）
    学业成绩：由绩点换算，满绩点4.0对应80分
    加分成绩：学术专长成绩（15分） + 综合表现成绩（5分）
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    
    # 获取学业成绩记录
    try:
        performance = AcademicPerformance.objects.get(user=user)
    except AcademicPerformance.DoesNotExist:
        # 如果没有学业成绩记录，创建一个
        performance = AcademicPerformance(
            user=user,
            gpa=user.gpa if hasattr(user, 'gpa') and user.gpa else 0.0,
            weighted_score=0.0,
            total_courses=0,
            total_credits=0.0,
            gpa_ranking=0,
            ranking_dimension='default'
        )
    
    # 计算学业成绩（80分）
    gpa = getattr(user, 'gpa', 0.0) or 0.0
    academic_score = calculate_academic_score(gpa)
    performance.academic_score = academic_score
    
    # 计算学术专长成绩（15分）
    academic_expertise_score = 0.0
    
    # 获取所有学术专长类申请
    expertise_applications = []
    
    # 学术专长类申请：英语成绩、学术论文、专利作品、学术竞赛、创新项目、CCF CSP认证
    expertise_models = [
        EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
        InnovationProject, CCFCSPCertification
    ]
    
    for model in expertise_models:
        expertise_applications.extend(
            model.objects.filter(user=user, review_status='approved')
        )
    
    # 计算学术专长总分
    for app in expertise_applications:
        # 尝试从不同字段获取分数
        score = getattr(app, 'score', 0.0) or 0.0
        if not score:
            score = getattr(app, 'estimated_score', 0.0) or 0.0
        if not score:
            score = getattr(app, 'actual_score', 0.0) or 0.0
        if not score:
            score = getattr(app, 'final_score', 0.0) or 0.0
        academic_expertise_score += float(score)
    
    # 学术专长成绩最高15分
    performance.academic_expertise_score = min(15.0, academic_expertise_score)
    
    # 计算综合表现成绩（5分）
    comprehensive_performance_score = 0.0
    
    # 获取所有综合表现类申请
    comprehensive_applications = []
    
    # 综合表现类申请：国际实习、兵役服务、志愿服务、荣誉称号、社会工作、体育竞赛
    comprehensive_models = [
        InternationalInternship, MilitaryService, VolunteerService,
        HonoraryTitle, SocialWork, SportsCompetition
    ]
    
    for model in comprehensive_models:
        comprehensive_applications.extend(
            model.objects.filter(user=user, review_status='approved')
        )
    
    # 计算综合表现总分
    for app in comprehensive_applications:
        # 尝试从不同字段获取分数
        score = getattr(app, 'score', 0.0) or 0.0
        if not score:
            score = getattr(app, 'estimated_score', 0.0) or 0.0
        if not score:
            score = getattr(app, 'actual_score', 0.0) or 0.0
        if not score:
            score = getattr(app, 'final_score', 0.0) or 0.0
        comprehensive_performance_score += float(score)
    
    # 综合表现成绩最高5分
    performance.comprehensive_performance_score = min(5.0, comprehensive_performance_score)
    
    # 计算总分（满分100分）
    total_score = academic_score + performance.academic_expertise_score + performance.comprehensive_performance_score
    performance.total_comprehensive_score = min(100.0, total_score)
    
    # 保存成绩记录
    performance.save()
    
    return performance


class ScoreCalculationViewSet(ViewSet):
    """成绩计算相关接口"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def recalculate_all(self, request):
        """重新计算所有学生的成绩"""
        # 权限检查
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'admin':
            return Response(
                {"error": "只有管理员可以重新计算所有学生成绩"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取所有学生
        students = User.objects.filter(user_type='student')
        
        # 重新计算每个学生的成绩
        success_count = 0
        total_count = students.count()
        
        for student in students:
            try:
                calculate_total_score(student.id)
                success_count += 1
            except Exception as e:
                print(f"计算学生{student.name}成绩失败: {str(e)}")
        
        return Response({
            "success": True,
            "message": f"成功计算{success_count}/{total_count}名学生的成绩"
        })
    
    @action(detail=False, methods=['post'])
    def recalculate_by_student(self, request):
        """重新计算指定学生的成绩"""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "请提供学生ID"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 权限检查
        current_user = request.user
        if not hasattr(current_user, 'user_type') or current_user.user_type not in ['teacher', 'admin']:
            return Response(
                {"error": "无权重新计算学生成绩"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 重新计算成绩
        try:
            performance = calculate_total_score(user_id)
            if performance:
                serializer = AcademicPerformanceDetailSerializer(performance)
                return Response({
                    "success": True,
                    "message": "成绩重新计算成功",
                    "data": serializer.data
                })
            else:
                return Response(
                    {"error": "学生不存在"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": f"成绩计算失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )