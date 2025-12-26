from rest_framework import serializers
from .models import AcademicPerformance
from user.models import User

class StudentBasicInfoSerializer(serializers.ModelSerializer):
    """学生基本信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'school_id', 'name', 'college', 'major', 'grade']

class AcademicPerformanceDetailSerializer(serializers.ModelSerializer):
    """学业成绩详情序列化器"""
    student = StudentBasicInfoSerializer(source='user', read_only=True)

    class Meta:
        model = AcademicPerformance
        fields = [
            'id', 'student', 'gpa', 'weighted_score', 'total_courses',
            'total_credits', 'gpa_ranking', 'ranking_dimension', 'failed_courses',
            'academic_score', 'academic_expertise_score',
            'comprehensive_performance_score', 'total_comprehensive_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class AcademicPerformanceListSerializer(serializers.ModelSerializer):
    """学业成绩列表序列化器"""
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    college = serializers.CharField(source='user.college', read_only=True)
    major = serializers.CharField(source='user.major', read_only=True)
    grade = serializers.CharField(source='user.grade', read_only=True)

    class Meta:
        model = AcademicPerformance
        fields = [
            'id', 'student_name', 'student_id', 'college', 'major', 'grade',
            'gpa', 'weighted_score', 'gpa_ranking', 'ranking_dimension',
            'total_comprehensive_score', 'updated_at'
        ]
        read_only_fields = fields

class PerformanceStatsSerializer(serializers.Serializer):
    """成绩统计序列化器"""
    avg_gpa = serializers.FloatField()
    max_gpa = serializers.FloatField()
    min_gpa = serializers.FloatField()
    avg_total_score = serializers.FloatField()
    total_students = serializers.IntegerField()
    ranking_distribution = serializers.DictField()