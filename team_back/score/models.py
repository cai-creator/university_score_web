import uuid

from django.db import models

from user.models import User


class AcademicPerformance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_performance',
                                verbose_name='用户')

    # 基础学业信息
    gpa = models.DecimalField(max_digits=7, decimal_places=4, verbose_name='学分绩点')
    weighted_score = models.DecimalField(max_digits=7, decimal_places=4, verbose_name='加权分数')
    total_courses = models.IntegerField(verbose_name='总课程门数')
    total_credits = models.DecimalField(max_digits=7, decimal_places=4, verbose_name='总学分数')
    gpa_ranking = models.IntegerField(verbose_name='绩点排名')
    ranking_dimension = models.CharField(max_length=100, verbose_name='排名维度')  # 如：专业排名、年级排名等
    failed_courses = models.IntegerField(default=0, verbose_name='不及格门数')

    # 各项成绩
    academic_score = models.DecimalField(max_digits=7, decimal_places=4, verbose_name='学业成绩(满分80分)', default=0)
    academic_expertise_score = models.DecimalField(max_digits=7, decimal_places=4,
                                                   verbose_name='学术专长成绩(满分15分)', default=0)
    comprehensive_performance_score = models.DecimalField(max_digits=7, decimal_places=4,
                                                          verbose_name='综合表现成绩(满分5分)', default=0)
    total_comprehensive_score = models.DecimalField(max_digits=7, decimal_places=4, verbose_name='综合成绩(满分100分)',
                                                    default=0)

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_performance'
        verbose_name = '学业成绩'
        verbose_name_plural = '学业成绩'

    def __str__(self):
        return f"{self.user.name}的学业成绩"

