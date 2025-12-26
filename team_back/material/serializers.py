# application/serializers.py
from rest_framework import serializers
from .models import (
    EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
    InnovationProject, CCFCSPCertification, InternationalInternship,
    MilitaryService, VolunteerService, HonoraryTitle, SocialWork, SportsCompetition
)
from django.contrib.auth import get_user_model

User = get_user_model()


# 英语成绩序列化器
class EnglishScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)

    class Meta:
        model = EnglishScore
        fields = [
            'id', 'student_name', 'student_id', 'exam_type', 'exam_type_display',
            'exam_score', 'exam_date', 'score_report', 'meets_standard',
            'estimated_score', 'bonus_points',
            'review_status', 'review_status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'student_id', 'exam_type_display',
                            'review_status_display', 'meets_standard', 'review_status',
                            'bonus_points', 'created_at', 'updated_at']


class EnglishScoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishScore
        fields = ['exam_type', 'exam_score', 'exam_date', 'score_report', 'estimated_score']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        exam_type = data.get('exam_type')

        # 检查是否已存在同类型的待审核或已通过的申请
        existing = EnglishScore.objects.filter(
            user=user,
            exam_type=exam_type,
            review_status__in=['first_reviewing', 'second_reviewing', 'third_reviewing', 'approved']
        )

        if self.instance:
            existing = existing.exclude(id=self.instance.id)

        if existing.exists():
            raise serializers.ValidationError(f"您已经提交过{exam_type}的申请")

        return data


# 学术论文序列化器
class AcademicPaperSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)

    class Meta:
        model = AcademicPaper
        fields = '__all__'
        read_only_fields = ['id', 'user', 'review_status', 'result', 'college_opinion',
                            'bonus_points', 'review_status_display', 'created_at', 'updated_at']


class AcademicPaperCreateSerializer(serializers.ModelSerializer):
    # 添加title字段来接受前端提交的数据，将其映射到paper_title
    title = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = AcademicPaper
        fields = ['title', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']
    
    def validate(self, data):
        # 确保title不为空
        if not data.get('title') or not data.get('title').strip():
            raise serializers.ValidationError({
                'title': '论文标题不能为空'
            })
        return data
    
    def create(self, validated_data):
        # 将title字段的值赋值给paper_title
        validated_data['paper_title'] = validated_data.pop('title')
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # 如果提交了title字段，将其赋值给paper_title
        if 'title' in validated_data:
            validated_data['paper_title'] = validated_data.pop('title')
        return super().update(instance, validated_data)


# 专利著作序列化器
class PatentWorkSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)
    author_type_display = serializers.CharField(source='get_author_type_display', read_only=True)

    class Meta:
        model = PatentWork
        fields = ['id', 'student_name', 'student_id', 'paper_title', 'author_type', 'author_type_display', 'is_xmu_first_unit',
                  'estimated_score', 'bonus_points',
                  'review_status', 'review_status_display', 'result', 'college_opinion',
                  'screenshot', 'user_explanation', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'review_status', 'result', 'college_opinion',
                            'bonus_points', 'review_status_display', 'author_type_display', 'created_at', 'updated_at']


class PatentWorkCreateSerializer(serializers.ModelSerializer):
    # 添加title字段来接受前端提交的数据，将其映射到paper_title
    title = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = PatentWork
        fields = ['title', 'author_type', 'is_xmu_first_unit', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']
        extra_kwargs = {
            'author_type': {'required': True},
            'is_xmu_first_unit': {'required': True}
        }
    
    def validate(self, data):
        # 确保title不为空
        if not data.get('title') or not data.get('title').strip():
            raise serializers.ValidationError({
                'title': '专利名称不能为空'
            })
        
        # 确保厦门大学是第一单位
        if not data.get('is_xmu_first_unit'):
            raise serializers.ValidationError({
                'is_xmu_first_unit': '厦门大学必须为第一单位才能提交申请'
            })
        
        return data
    
    def create(self, validated_data):
        # 将title字段的值赋值给paper_title
        validated_data['paper_title'] = validated_data.pop('title')
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # 如果提交了title字段，将其赋值给paper_title
        if 'title' in validated_data:
            validated_data['paper_title'] = validated_data.pop('title')
        return super().update(instance, validated_data)


# 学业竞赛序列化器
class AcademicCompetitionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)
    competition_level_display = serializers.CharField(source='get_competition_level_display', read_only=True)
    competition_name_display = serializers.CharField(source='get_competition_name_display', read_only=True)

    class Meta:
        model = AcademicCompetition
        fields = '__all__'
        read_only_fields = ['id', 'user', 'review_status', 'result', 'college_opinion',
                            'bonus_points', 'review_status_display', 'competition_level_display',
                            'competition_name_display', 'created_at', 'updated_at']


class AcademicCompetitionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCompetition
        fields = ['competition_level', 'competition_name', 'competition_specific_name',
                  'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']


# 为其他模型创建类似的序列化器...
class BaseApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)

    class Meta:
        abstract = True
        fields = ['id', 'student_name', 'student_id', 'estimated_score', 'bonus_points',
                  'review_status', 'review_status_display', 'result', 'college_opinion',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'review_status', 'result', 'college_opinion',
                            'bonus_points', 'review_status_display', 'created_at', 'updated_at']


class InnovationProjectSerializer(BaseApplicationSerializer):
    project_level_display = serializers.CharField(source='get_project_level_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = InnovationProject
        fields = BaseApplicationSerializer.Meta.fields + ['project_name', 'project_level', 'project_level_display', 'screenshot', 'user_explanation']


class InnovationProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InnovationProject
        fields = ['project_name', 'project_level', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']


# CCF CSP认证序列化器
class CCFCSPCertificationSerializer(BaseApplicationSerializer):
    class Meta(BaseApplicationSerializer.Meta):
        model = CCFCSPCertification
        fields = BaseApplicationSerializer.Meta.fields + ['score', 'certification_date', 'screenshot', 'user_explanation']


class CCFCSPCertificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCFCSPCertification
        fields = ['score', 'certification_date', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']


# 国际组织实习序列化器
class InternationalInternshipSerializer(BaseApplicationSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = InternationalInternship
        fields = BaseApplicationSerializer.Meta.fields + ['organization_name', 'internship_duration', 'country', 'level', 'level_display',
                  'working_hours', 'position', 'screenshot', 'user_explanation']


class InternationalInternshipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalInternship
        fields = ['organization_name', 'internship_duration', 'country', 'level',
                  'working_hours', 'position', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']
        extra_kwargs = {
            'country': {'required': False, 'allow_blank': True, 'allow_null': True},
            'level': {'required': False, 'allow_blank': True, 'allow_null': True},
            'working_hours': {'required': False, 'allow_null': True},
            'position': {'required': False, 'allow_blank': True, 'allow_null': True}
        }


# 参军入伍序列化器
class MilitaryServiceSerializer(BaseApplicationSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = MilitaryService
        fields = BaseApplicationSerializer.Meta.fields + ['service_start_date', 'service_end_date', 'military_unit', 'level', 'level_display',
                  'working_hours', 'position', 'screenshot', 'user_explanation']


class MilitaryServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilitaryService
        fields = ['service_start_date', 'service_end_date', 'military_unit', 'level',
                  'working_hours', 'position', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']
        extra_kwargs = {
            'military_unit': {'required': False, 'allow_blank': True},
            'level': {'required': False, 'allow_blank': True, 'allow_null': True},
            'working_hours': {'required': False, 'allow_null': True},
            'position': {'required': False, 'allow_blank': True, 'allow_null': True}
        }


# 志愿服务序列化器
class VolunteerServiceSerializer(BaseApplicationSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = VolunteerService
        fields = BaseApplicationSerializer.Meta.fields + ['service_type', 'service_type_display', 'activity_name', 'activity_date', 'level', 'level_display',
                  'working_hours', 'position', 'screenshot', 'user_explanation']


class VolunteerServiceCreateSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(required=True, allow_blank=False)
    
    class Meta:
        model = VolunteerService
        fields = ['service_type', 'activity_name', 'activity_date', 'level',
                  'working_hours', 'position', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']
    
    def to_internal_value(self, data):
        # 处理前端可能发送的camelCase字段名，转换为snake_case
        if isinstance(data, dict):
            # 检查是否有activityName字段，如果有则映射到activity_name
            if 'activityName' in data and 'activity_name' not in data:
                data['activity_name'] = data.pop('activityName')
            # 检查是否有serviceType字段，如果有则映射到service_type
            if 'serviceType' in data and 'service_type' not in data:
                data['service_type'] = data.pop('serviceType')
            # 检查是否有activityDate字段，如果有则映射到activity_date
            if 'activityDate' in data and 'activity_date' not in data:
                data['activity_date'] = data.pop('activityDate')
        return super().to_internal_value(data)


# 荣誉称号序列化器
class HonoraryTitleSerializer(BaseApplicationSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = HonoraryTitle
        fields = BaseApplicationSerializer.Meta.fields + ['title_name', 'awarding_organization', 'awarding_date', 'level', 'level_display',
                  'screenshot', 'user_explanation']


class HonoraryTitleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HonoraryTitle
        fields = ['title_name', 'awarding_organization', 'awarding_date', 'level',
                  'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']


# 社会工作序列化器
class SocialWorkSerializer(BaseApplicationSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = SocialWork
        fields = BaseApplicationSerializer.Meta.fields + ['organization', 'work_period', 'work_description', 'level', 'level_display',
                  'working_hours', 'position', 'screenshot', 'user_explanation']


class SocialWorkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialWork
        fields = ['organization', 'work_period', 'work_description', 'level',
                  'working_hours', 'position', 'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']


# 体育比赛序列化器
class SportsCompetitionSerializer(BaseApplicationSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = SportsCompetition
        fields = BaseApplicationSerializer.Meta.fields + ['competition_name', 'competition_level', 'achievement', 'is_team_project',
                  'team_size', 'project_type', 'competition_date', 'level', 'level_display',
                  'screenshot', 'user_explanation']


class SportsCompetitionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsCompetition
        fields = ['competition_name', 'competition_level', 'achievement', 'is_team_project',
                  'team_size', 'project_type', 'competition_date', 'level',
                  'screenshot', 'user_explanation', 'estimated_score']
        read_only_fields = ['user']


# 申请汇总序列化器
class ApplicationSummarySerializer(serializers.Serializer):
    english_scores = EnglishScoreSerializer(many=True, read_only=True)
    academic_papers = AcademicPaperSerializer(many=True, read_only=True)
    patent_works = PatentWorkSerializer(many=True, read_only=True)
    academic_competitions = AcademicCompetitionSerializer(many=True, read_only=True)
    innovation_projects = InnovationProjectSerializer(many=True, read_only=True)
    ccf_csp_certifications = serializers.SerializerMethodField()
    international_internships = serializers.SerializerMethodField()
    military_services = serializers.SerializerMethodField()
    volunteer_services = serializers.SerializerMethodField()
    honorary_titles = serializers.SerializerMethodField()
    social_works = serializers.SerializerMethodField()
    sports_competitions = serializers.SerializerMethodField()

    # def get_ccf_csp_certifications(self, obj):
    #     from .models import CCFCSPCertification
    #     return CCFCSPCertificationSerializer(obj['ccf_csp_certifications'], many=True).data

    # def get_international_internships(self, obj):
    #     from .models import InternationalInternship
    #     return InternationalInternshipSerializer(obj['international_internships'], many=True).data

    # 为其他模型添加类似的方法...


# 申请统计序列化器
class ApplicationStatsSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    approved_applications = serializers.IntegerField()
    rejected_applications = serializers.IntegerField()
    by_category = serializers.DictField()



# application/serializers.py (在原有基础上添加)

class FirstReviewActionSerializer(serializers.Serializer):
    result = serializers.ChoiceField(choices=[('passed', '通过'), ('failed', '不通过')], required=True)
    review_comment = serializers.CharField(required=False, allow_blank=True, max_length=500)

# 二审操作序列化器
class SecondReviewActionSerializer(serializers.Serializer):
    result = serializers.ChoiceField(choices=[('passed', '通过'), ('failed', '不通过')], required=True)
    review_comment = serializers.CharField(required=False, allow_blank=True, max_length=500)
    bonus_points = serializers.DecimalField(
        max_digits=7,
        decimal_places=4,
        required=False,
        min_value=0,
        help_text="加分分数（仅二审通过时有效）"
    )

    def validate_bonus_points(self, value):
        if value and value < 0:
            raise serializers.ValidationError("加分分数不能为负数")
        return value

# 批量一审序列化器
class BatchFirstReviewSerializer(serializers.Serializer):
    application_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="申请ID列表"
    )
    result = serializers.ChoiceField(choices=[('passed', '通过'), ('failed', '不通过')], required=True)
    review_comment = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_application_ids(self, value):
        if not value:
            raise serializers.ValidationError("申请ID列表不能为空")
        if len(value) > 100:
            raise serializers.ValidationError("一次最多审核100个申请")
        return value

# 三审操作序列化器
class ThirdReviewActionSerializer(serializers.Serializer):
    result = serializers.ChoiceField(choices=[('passed', '通过'), ('failed', '不通过')], required=True)
    review_comment = serializers.CharField(required=False, allow_blank=True, max_length=500)
    bonus_points = serializers.DecimalField(
        max_digits=7,
        decimal_places=4,
        required=False,
        min_value=0,
        help_text="加分分数（仅三审通过时有效）"
    )

    def validate_bonus_points(self, value):
        if value and value < 0:
            raise serializers.ValidationError("加分分数不能为负数")
        return value

# 审核记录序列化器
class ReviewRecordSerializer(serializers.ModelSerializer):
    first_reviewer_name = serializers.CharField(source='first_reviewer.name', read_only=True)
    second_reviewer_name = serializers.CharField(source='second_reviewer.name', read_only=True)
    third_reviewer_name = serializers.CharField(source='third_reviewer.name', read_only=True)
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    college = serializers.CharField(source='user.college', read_only=True)
    current_stage = serializers.SerializerMethodField()

    class Meta:
        model = None  # 将在具体视图中设置
        fields = [
            'id', 'student_name', 'student_id', 'college',
            'first_reviewer_name', 'first_review_comment', 'first_reviewed_at',
            'second_reviewer_name', 'second_review_comment', 'second_reviewed_at',
            'third_reviewer_name', 'third_review_comment', 'third_reviewed_at',
            'review_status', 'result', 'bonus_points', 'current_stage', 'created_at'
        ]
        read_only_fields = fields

    def get_current_stage(self, obj):
        return obj.get_current_review_stage()

# 待审核申请列表序列化器
class PendingReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.name', read_only=True)
    student_id = serializers.CharField(source='user.school_id', read_only=True)
    college = serializers.CharField(source='user.college', read_only=True)
    major = serializers.CharField(source='user.major', read_only=True)
    current_stage = serializers.SerializerMethodField()
    days_pending = serializers.SerializerMethodField()

    class Meta:
        model = None  # 将在具体视图中设置
        fields = [
            'id', 'student_name', 'student_id', 'college', 'major',
            'review_status', 'current_stage', 'days_pending', 'created_at'
        ]

    def get_current_stage(self, obj):
        return obj.get_current_review_stage()

    def get_days_pending(self, obj):
        from django.utils import timezone
        if obj.review_status in ['first_reviewing', 'second_reviewing', 'third_reviewing']:
            delta = timezone.now() - obj.created_at
            return delta.days
        return 0