# users/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(serializers.Serializer):
    """创建用户序列化器"""
    school_id = serializers.CharField(required=True, label='学号/工号')
    name = serializers.CharField(required=True, label='姓名')
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, label='密码')
    user_type = serializers.ChoiceField(required=True, choices=User.USER_TYPES, label='用户类型')
    gender = serializers.CharField(required=False, label='性别')
    gpa = serializers.FloatField(required=False, label='平均绩点')
    college = serializers.UUIDField(required=False, label='学院ID')
    class_id = serializers.UUIDField(required=False, label='班级ID')
    grade = serializers.CharField(required=False, label='年级')
    major = serializers.CharField(required=False, label='专业')
    title = serializers.CharField(required=False, label='职称')
    contact = serializers.CharField(required=False, label='联系方式')
    is_active = serializers.BooleanField(required=False, default=True, label='是否活跃')
    is_superuser = serializers.BooleanField(required=False, default=False, label='是否超级管理员')
    is_staff = serializers.BooleanField(required=False, default=False, label='是否管理员')
    
    def validate_college(self, value):
        """验证学院ID是否有效"""
        if value:
            from .models import College
            try:
                College.objects.get(id=value)
            except (College.DoesNotExist, TypeError, ValueError):
                raise serializers.ValidationError("学院ID无效")
        return value
    
    def validate_class_id(self, value):
        """验证班级ID是否有效"""
        if value:
            from .models import Class
            try:
                Class.objects.get(id=value)
            except (Class.DoesNotExist, TypeError, ValueError):
                raise serializers.ValidationError("班级ID无效")
        return value

    def validate_school_id(self, value):
        """验证学号/工号是否已存在"""
        if User.objects.filter(school_id=value).exists():
            raise serializers.ValidationError("学号/工号已存在")
        return value


class LoginSerializer(serializers.Serializer):
    school_id = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        school_id = data.get('school_id')
        password = data.get('password')

        if school_id and password:
            # 使用 authenticate 验证用户
            user = authenticate(username=school_id, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("账号已被禁用")
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("学号/工号或密码错误")
        else:
            raise serializers.ValidationError("请提供学号/工号和密码")


class ClassBindingSerializer(serializers.ModelSerializer):
    """教师-班级绑定序列化器"""
    teacher = serializers.UUIDField(source='teacher.id', required=True, label='教师ID')
    class_obj = serializers.UUIDField(source='class_obj.id', required=True, label='班级ID')
    created_at = serializers.DateTimeField(read_only=True, label='创建时间')
    updated_at = serializers.DateTimeField(read_only=True, label='更新时间')
    
    class Meta:
        model = None  # 暂时设置为None，稍后在Meta类中动态导入
        fields = ['id', 'teacher', 'class_obj', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        # 动态导入模型以避免循环导入
        from .models import ClassBinding, User, Class
        self.Meta.model = ClassBinding
        super().__init__(*args, **kwargs)
    
    def validate_teacher(self, value):
        """验证教师ID是否有效且为教师类型"""
        try:
            from .models import User
            teacher = User.objects.get(id=value)
            if teacher.user_type != 'teacher':
                raise serializers.ValidationError("只能绑定教师类型的用户")
        except (User.DoesNotExist, TypeError, ValueError):
            raise serializers.ValidationError("教师ID无效")
        return value
    
    def validate_class_obj(self, value):
        """验证班级ID是否有效"""
        try:
            from .models import Class
            Class.objects.get(id=value)
        except (Class.DoesNotExist, TypeError, ValueError):
            raise serializers.ValidationError("班级ID无效")
        return value
    
    def create(self, validated_data):
        """创建教师-班级绑定"""
        from .models import ClassBinding, User, Class
        
        # 获取教师和班级对象
        teacher = User.objects.get(id=validated_data['teacher']['id'])
        class_obj = Class.objects.get(id=validated_data['class_obj']['id'])
        
        # 创建绑定
        binding, created = ClassBinding.objects.get_or_create(
            teacher=teacher,
            class_obj=class_obj
        )
        
        return binding

class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    is_student = serializers.BooleanField(read_only=True)
    is_teacher = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    class_name = serializers.CharField(source='clazz.name', read_only=True, allow_null=True)
    class_id = serializers.UUIDField(source='clazz.id', read_only=True, allow_null=True)
    college_name = serializers.CharField(source='college.name', read_only=True, allow_null=True)
    total_score = serializers.SerializerMethodField(read_only=True)
    bonus_score = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'school_id', 'name', 'user_type', 'gender', 'phone', 'email', 'birth_date', 'gpa',
                  'college', 'college_name', 'class_id', 'class_name', 'grade', 'major', 'title', 'contact',
                  'is_active', 'is_superuser', 'is_staff', 'is_student',
                  'is_teacher', 'is_admin', 'date_joined', 'last_login', 'total_score', 'bonus_score']
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_student',
                           'is_teacher', 'is_admin', 'college_name', 'class_name', 'class_id', 'total_score', 'bonus_score']
    
    def get_bonus_score(self, obj):
        """计算学生加分成绩：学术专长成绩（15分）+综合表现成绩（5分）"""
        if obj.user_type != 'student':
            return 0.0
        
        # 计算加分成绩（20分）：学术专长成绩（15分）+综合表现成绩（5分）
        bonus_score = 0.0
        
        try:
            # 学术专长类申请：英语成绩、学术论文、专利作品、学术竞赛、创新项目、CCF CSP认证
            from material.models import (
                EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
                InnovationProject, CCFCSPCertification, InternationalInternship,
                MilitaryService, VolunteerService, HonoraryTitle, SocialWork, SportsCompetition
            )
            
            # 计算学术专长成绩（15分）
            academic_expertise_score = 0.0
            expertise_models = [
                EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
                InnovationProject, CCFCSPCertification
            ]
            
            for model in expertise_models:
                # 获取已批准的申请
                applications = model.objects.filter(user=obj, review_status='approved')
                for app in applications:
                    # 直接使用bonus_points字段，而不是重新计算
                    try:
                        score = float(app.bonus_points)
                        academic_expertise_score += score
                    except Exception as e:
                        print(f"计算学术专长加分失败 for {app}: {e}")
            
            # 学术专长成绩最高15分
            academic_expertise_score = min(15.0, academic_expertise_score)
            
            # 计算综合表现成绩（5分）
            comprehensive_performance_score = 0.0
            comprehensive_models = [
                InternationalInternship, MilitaryService, VolunteerService,
                HonoraryTitle, SocialWork, SportsCompetition
            ]
            
            for model in comprehensive_models:
                # 获取已批准的申请
                applications = model.objects.filter(user=obj, review_status='approved')
                for app in applications:
                    # 直接使用bonus_points字段，而不是重新计算
                    try:
                        score = float(app.bonus_points)
                        comprehensive_performance_score += score
                    except Exception as e:
                        print(f"计算综合表现加分失败 for {app}: {e}")
            
            # 综合表现成绩最高5分
            comprehensive_performance_score = min(5.0, comprehensive_performance_score)
            
            # 计算总分加分
            bonus_score = academic_expertise_score + comprehensive_performance_score
        except Exception as e:
            print(f"计算加分失败 for user {obj}: {e}")
            # 如果所有方法都失败，使用默认值0
            bonus_score = 0.0
        
        return round(bonus_score, 2)
    
    def get_total_score(self, obj):
        """计算学生总分：学业成绩（80分）+加分成绩（20分）"""
        if obj.user_type != 'student':
            return 0
        
        # 计算学业成绩（80分）：由绩点转化，满绩点4.0对应80分
        gpa = getattr(obj, 'gpa', 0.0) or 0.0
        academic_score = (float(gpa) / 4.0) * 80.0
        academic_score = min(80.0, max(0.0, academic_score))
        
        # 使用get_bonus_score方法获取加分成绩
        bonus_score = self.get_bonus_score(obj)
        
        # 总分 = 学业成绩 + 加分成绩
        total_score = academic_score + bonus_score
        # 总分最高100分
        return round(total_score, 2)


