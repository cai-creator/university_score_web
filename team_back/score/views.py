from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min, Count, Q
from django.shortcuts import get_object_or_404
from .models import AcademicPerformance
from .serializers import (
    AcademicPerformanceDetailSerializer,
    AcademicPerformanceListSerializer,
    PerformanceStatsSerializer
)
from user.models import User


class StudentPerformanceViewSet(viewsets.ViewSet):
    """学生成绩查询接口"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_performance(self, request):
        """获取当前学生的个人成绩"""
        user = request.user

        # 检查用户类型
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response(
                {"error": "只有学生可以查看个人成绩"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            performance = AcademicPerformance.objects.get(user=user)
            serializer = AcademicPerformanceDetailSerializer(performance)
            return Response(serializer.data)
        except AcademicPerformance.DoesNotExist:
            return Response(
                {"error": "未找到学业成绩记录"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def by_student_id(self, request):
        """根据学号查询学生成绩（教师/管理员）"""
        student_id = request.query_params.get('student_id')

        if not student_id:
            return Response(
                {"error": "请提供学号"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 权限检查
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response(
                {"error": "无权访问其他学生成绩"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student = User.objects.get(school_id=student_id, user_type='student')
            performance = AcademicPerformance.objects.get(user=student)
            serializer = AcademicPerformanceDetailSerializer(performance)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "学生不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except AcademicPerformance.DoesNotExist:
            return Response(
                {"error": "该学生暂无学业成绩记录"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def list_all(self, request):
        """获取所有学生成绩列表（教师/管理员）"""
        user = request.user

        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response(
                {"error": "无权访问学生成绩列表"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 获取查询参数
        college = request.query_params.get('college')
        major = request.query_params.get('major')
        grade = request.query_params.get('grade')
        ranking_dimension = request.query_params.get('ranking_dimension')

        # 构建查询条件
        queryset = AcademicPerformance.objects.filter(user__user_type='student')

        # 权限控制：
        # 管理员可以看到所有学生成绩
        # 教师只能看到自己管辖班级的学生成绩
        if user.user_type == 'teacher':
            # 获取教师管辖的所有班级
            teacher_classes = user.class_bindings.values_list('class_obj_id', flat=True)
            # 过滤出学生所在班级在教师管辖班级列表中的成绩
            queryset = queryset.filter(user__clazz_id__in=teacher_classes)

        if college:
            queryset = queryset.filter(user__college=college)
        if major:
            queryset = queryset.filter(user__major=major)
        if grade:
            queryset = queryset.filter(user__grade=grade)
        if ranking_dimension:
            queryset = queryset.filter(ranking_dimension=ranking_dimension)

        # 排序
        sort_by = request.query_params.get('sort_by', 'gpa_ranking')
        sort_order = request.query_params.get('sort_order', 'asc')

        # 可排序的字段白名单（防止SQL注入）
        allowed_sort_fields = {
            'gpa', 'weighted_score', 'gpa_ranking',
            'total_comprehensive_score', 'academic_score',
            'user__school_id', 'user__name'
        }

        if sort_by not in allowed_sort_fields:
            sort_by = 'gpa_ranking'  # 如果字段不在白名单，使用默认

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = queryset.order_by(sort_by)

        # 分页 - 使用 DRF 的分页器
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 20)  # 默认20条

        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AcademicPerformanceListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # 如果没有分页，返回所有数据
        serializer = AcademicPerformanceListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取成绩统计信息（教师/管理员）"""
        user = request.user

        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response(
                {"error": "无权查看统计信息"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 获取查询参数
        college = request.query_params.get('college')
        major = request.query_params.get('major')
        grade = request.query_params.get('grade')

        # 构建查询条件
        queryset = AcademicPerformance.objects.filter(user__user_type='student')

        # 权限控制：
        # 管理员可以看到所有学生成绩统计
        # 教师只能看到自己管辖班级的学生成绩统计
        if user.user_type == 'teacher':
            # 获取教师管辖的所有班级
            teacher_classes = user.class_bindings.values_list('class_obj_id', flat=True)
            # 过滤出学生所在班级在教师管辖班级列表中的成绩统计
            queryset = queryset.filter(user__clazz_id__in=teacher_classes)

        if college:
            queryset = queryset.filter(user__college=college)
        if major:
            queryset = queryset.filter(user__major=major)
        if grade:
            queryset = queryset.filter(user__grade=grade)

        # 计算统计信息
        stats = queryset.aggregate(
            avg_gpa=Avg('gpa'),
            max_gpa=Max('gpa'),
            min_gpa=Min('gpa'),
            avg_total_score=Avg('total_comprehensive_score'),
            total_students=Count('id')
        )

        # 排名分布
        ranking_distribution = {}
        for performance in queryset:
            rank_range = f"{(performance.gpa_ranking - 1) // 10 * 10 + 1}-{(performance.gpa_ranking - 1) // 10 * 10 + 10}"
            ranking_distribution[rank_range] = ranking_distribution.get(rank_range, 0) + 1

        stats['ranking_distribution'] = ranking_distribution

        serializer = PerformanceStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ranking(self, request):
        """获取排名信息"""
        user = request.user

        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response(
                {"error": "只有学生可以查看排名"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            my_performance = AcademicPerformance.objects.get(user=user)

            # 获取同维度下的所有排名
            same_dimension_performances = AcademicPerformance.objects.filter(
                ranking_dimension=my_performance.ranking_dimension
            ).order_by('gpa_ranking')

            # 构建排名列表
            ranking_list = []
            for idx, performance in enumerate(same_dimension_performances, 1):
                ranking_list.append({
                    'rank': idx,
                    'student_name': performance.user.name,
                    'student_id': performance.user.school_id,
                    'gpa': float(performance.gpa),
                    'total_score': float(performance.total_comprehensive_score),
                    'is_me': performance.user == user
                })

            return Response({
                'my_ranking': my_performance.gpa_ranking,
                'ranking_dimension': my_performance.ranking_dimension,
                'total_students': len(ranking_list),
                'ranking_list': ranking_list
            })

        except AcademicPerformance.DoesNotExist:
            return Response(
                {"error": "未找到学业成绩记录"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='student/score-items')
    def score_items(self, request):
        """获取学生加分项目列表，整合material应用中的所有加分项目"""
        user = request.user
        
        # 权限检查：只有学生可以查看自己的加分项目
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response(
                {"error": "只有学生可以查看加分项目"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # 动态导入material应用的所有模型
            from material.models import (
                EnglishScore,
                AcademicPaper,
                PatentWork,
                AcademicCompetition,
                InnovationProject,
                CCFCSPCertification,
                InternationalInternship,
                MilitaryService,
                VolunteerService,
                HonoraryTitle,
                SocialWork,
                SportsCompetition
            )
            
            # 定义模型与类型映射
            model_type_mapping = {
                EnglishScore: 'english_score',
                AcademicPaper: 'scientific_research',
                PatentWork: 'scientific_research',
                AcademicCompetition: 'academic_competition',
                InnovationProject: 'innovation',
                CCFCSPCertification: 'academic_competition',
                InternationalInternship: 'internship',
                MilitaryService: 'military',
                VolunteerService: 'volunteer',
                HonoraryTitle: 'honor',
                SocialWork: 'social_work',
                SportsCompetition: 'sports'
            }
            
            # 获取所有加分项目
            all_score_items = []
            
            for model, item_type in model_type_mapping.items():
                # 获取当前学生的所有该类型项目
                items = model.objects.filter(user=user)
                
                # 转换为统一格式
                for item in items:
                    # 确保项目状态为已通过审核（包括一审通过、二审通过和最终审核通过）
                    if hasattr(item, 'review_status'):
                        # 允许的审核通过状态
                        approved_statuses = ['first_approved', 'second_approved', 'approved']
                        if item.review_status not in approved_statuses:
                            continue
                    
                    # 直接使用bonus_points字段，而不是重新计算
                    score = float(item.bonus_points) if hasattr(item, 'bonus_points') else 0
                    
                    # 获取项目名称，兼容不同模型的字段名
                    project_name = getattr(item, 'name', '')
                    if not project_name:
                        # 根据不同模型获取合适的名称字段
                        if hasattr(item, 'paper_title'):
                            project_name = item.paper_title
                        elif hasattr(item, 'competition_specific_name'):
                            project_name = item.competition_specific_name
                        elif hasattr(item, 'project_name'):
                            project_name = item.project_name
                        elif hasattr(item, 'organization_name'):
                            project_name = item.organization_name
                        elif hasattr(item, 'title_name'):
                            project_name = item.title_name
                        elif hasattr(item, 'competition_name'):
                            project_name = item.competition_name
                        else:
                            project_name = f'{item_type.replace("_", " ").title()}'
                    
                    # 根据不同模型构建统一格式的项目
                    score_item = {
                        'id': str(item.id),
                        'name': project_name,
                        'type': item_type,
                        'score': score,
                        'description': getattr(item, 'description', '') or getattr(item, 'user_explanation', ''),
                        'created_at': item.created_at.isoformat() if hasattr(item, 'created_at') else '',
                        'updated_at': item.updated_at.isoformat() if hasattr(item, 'updated_at') else ''
                    }
                    
                    # 添加模型特定字段
                    if isinstance(item, EnglishScore):
                        score_item['level'] = item.level
                    elif isinstance(item, AcademicCompetition):
                        score_item['level'] = getattr(item, 'competition_level', '')
                    
                    all_score_items.append(score_item)
            
            # 返回统一格式的加分项目列表
            return Response({
                'score_items': all_score_items
            })
            
        except Exception as e:
            import traceback
            print(f"获取加分项目失败的完整错误信息: {traceback.format_exc()}")
            return Response(
                {"error": f"获取加分项目失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


