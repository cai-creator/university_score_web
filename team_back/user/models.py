import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class College(models.Model):
    """学院模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='学院名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'college'
        verbose_name = '学院'
        verbose_name_plural = '学院'

    def __str__(self):
        return self.name


class Class(models.Model):
    """班级模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='班级名称')
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name='年级')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='classes', verbose_name='所属学院')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'class'
        verbose_name = '班级'
        verbose_name_plural = '班级'

    def __str__(self):
        return f"{self.name} ({self.grade})"


class CustomUserManager(BaseUserManager):
    def create_user(self, school_id=None, name=None, college=None, user_type='student', password=None, **extra_fields):
        if user_type=='student':
            if not school_id:
                raise ValueError('请提供学号')
            identifier = school_id
        elif user_type in ['teacher', 'admin']:
            if not school_id:
                raise ValueError('请提供工号')
            identifier = school_id
        else:
            raise ValueError('无效的用户类型')

        if not name:
            raise ValueError('请提供姓名')
        
        # 普通管理员必须有学院，超级管理员可以没有学院
        if not college and not extra_fields.get('is_superuser', False):
            raise ValueError('请提供学院名称')

        user = self.model(
            school_id=identifier,
            name=name,
            user_type=user_type,
            **extra_fields
        )
        
        # 设置学院和班级
        if college:
            user.college = college
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, school_id, name, college=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(school_id=school_id, name=name, college=college, user_type='admin', password=password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = [
        ('student', '学生'),
        ('teacher', '老师'),
        ('admin', '超级管理员'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_id = models.CharField(max_length=20, unique=True, verbose_name='学号或工号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name='性别')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name='所属学院')

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES,
        default='student',
        verbose_name='用户类型'
    )

    # 学生字段
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name='年级')
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='专业')
    gpa = models.FloatField(blank=True, null=True, verbose_name='平均绩点')
    clazz = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='所属班级', db_column='class_id')
    # 保研相关字段
    has_postgraduate_qualification = models.BooleanField(default=False, verbose_name='是否有保研资格')
    is_applying_postgraduate = models.BooleanField(default=False, verbose_name='是否申请保研')

    # 老师字段
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='职称')

    # 通用字段
    contact = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系方式')

    # 系统字段
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    failed_login_attempts = models.IntegerField(default=0, verbose_name='登录失败次数')
    totp_enabled = models.BooleanField(default=False, verbose_name='是否启用TOTP')

    objects = CustomUserManager()

    USERNAME_FIELD = 'school_id'
    REQUIRED_FIELDS = ['name', 'user_type']

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.name} ({self.school_id})"

    @property
    def is_student(self):
        return self.user_type == 'student'

    @property
    def is_teacher(self):
        return self.user_type == 'teacher'

    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def class_name(self):
        """返回班级名称"""
        return self.clazz.name if self.clazz else None
    
    @property
    def counselors(self):
        """返回学生的辅导员老师列表，根据所在班级自动绑定"""
        if self.is_student and self.clazz:
            # 获取与学生所在班级绑定的所有教师
            from django.db import models
            try:
                # 通过反向关系获取班级绑定的所有教师
                teacher_bindings = self.clazz.teacher_bindings.all()
                # 提取教师对象
                teachers = [binding.teacher for binding in teacher_bindings]
                # 返回教师信息列表
                return [{
                    'id': str(teacher.id),
                    'school_id': teacher.school_id,
                    'name': teacher.name,
                    'title': teacher.title,
                    'college': teacher.college.name if teacher.college else None
                } for teacher in teachers]
            except Exception:
                return []
        return []
    
    @property
    def counselor_names(self):
        """返回学生辅导员老师的姓名列表，用于显示"""
        return [counselor['name'] for counselor in self.counselors] if self.counselors else []


class ClassBinding(models.Model):
    """教师-班级绑定模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_bindings', verbose_name='教师', limit_choices_to={'user_type': 'teacher'})
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='teacher_bindings', verbose_name='班级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'class_binding'
        verbose_name = '教师-班级绑定'
        verbose_name_plural = '教师-班级绑定'
        unique_together = ('teacher', 'class_obj')  # 确保每个教师和班级只能绑定一次
    
    def __str__(self):
        return f"{self.teacher.name} - {self.class_obj.name}"

