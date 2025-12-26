import uuid
from django.db import models
from django.utils import timezone

from user.models import User


class ReviewMixin(models.Model):
    """审核混入类"""
    REVIEW_STATUS = [
        ('pending', '待一审'),
        ('first_reviewing', '一审中'),
        ('first_approved', '一审通过'),
        ('first_rejected', '一审不通过'),
        ('second_reviewing', '二审中'),
        ('second_approved', '二审通过'),
        ('second_rejected', '二审不通过'),
        ('third_reviewing', '三审中'),
        ('approved', '审核通过'),
        ('rejected', '审核不通过'),
        ('withdrawn', '已撤回'),
    ]

    # 一审相关字段
    first_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='first_reviewed_%(class)s',
        verbose_name='一审老师'
    )
    first_review_comment = models.TextField(blank=True, null=True, verbose_name='一审意见')
    first_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='一审时间')

    # 二审相关字段
    second_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='second_reviewed_%(class)s',
        verbose_name='二审老师'
    )
    second_review_comment = models.TextField(blank=True, null=True, verbose_name='二审意见')
    second_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='二审时间')

    # 三审相关字段
    third_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='third_reviewed_%(class)s',
        verbose_name='三审老师'
    )
    third_review_comment = models.TextField(blank=True, null=True, verbose_name='三审意见')
    third_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='三审时间')

    # 审核状态
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS,
        default='pending',
        verbose_name='审核状态'
    )

    # 审核结果和加分（所有申请类型共用）
    result = models.CharField(
        max_length=10,
        choices=[('passed', '通过'), ('failed', '不通过')],
        blank=True,
        null=True,
        verbose_name='结果'
    )
    # 预估分数，由学生提交申请时计算
    estimated_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        verbose_name='预估分数'
    )
    # 最终加分，由审核后确定
    bonus_points = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        verbose_name='加分'
    )
    college_opinion = models.TextField(blank=True, null=True, verbose_name='学院意见')

    class Meta:
        abstract = True

    def get_current_review_stage(self):
        """获取当前审核阶段"""
        if self.review_status in ['pending', 'first_reviewing']:
            return 'first_review'
        elif self.review_status in ['first_approved', 'second_reviewing']:
            return 'second_review'
        elif self.review_status in ['second_approved', 'third_reviewing']:
            return 'third_review'
        else:
            return 'completed'

    def can_first_review(self, reviewer):
        """检查是否可以一审"""
        if (reviewer.user_type in ['teacher', 'admin'] and
                self.review_status in ['pending', 'first_reviewing']):
            # 管理员可以审核所有申请
            if reviewer.user_type == 'admin':
                return True
            # 教师只能审核自己学院的学生申请
            return reviewer.college == self.user.college
        return False

    def can_second_review(self, reviewer):
        """检查是否可以二审"""
        if (reviewer.user_type in ['teacher', 'admin'] and
                self.review_status in ['first_approved', 'second_reviewing']):
            # 管理员可以审核所有申请
            if reviewer.user_type == 'admin':
                return True
            # 教师只能审核自己学院的学生申请
            return reviewer.college == self.user.college
        return False

    def can_third_review(self, reviewer):
        """检查是否可以三审"""
        if (reviewer.user_type in ['teacher', 'admin'] and
                self.review_status in ['second_approved', 'third_reviewing']):
            # 管理员可以审核所有申请
            if reviewer.user_type == 'admin':
                return True
            # 教师只能审核自己学院的学生申请
            return reviewer.college == self.user.college
        return False

    def perform_first_review(self, reviewer, result, review_comment=""):
        """执行一审"""
        if not self.can_first_review(reviewer):
            return False, "当前状态无法进行一审"

        self.first_reviewer = reviewer
        self.first_review_comment = review_comment
        self.first_reviewed_at = timezone.now()

        if result == 'passed':
            self.review_status = 'first_approved'
            # 一审通过时，默认使用预估分数作为加分
            # 如果后续有更低的分数，会在二审或三审时被覆盖
            if hasattr(self, 'estimated_score') and self.estimated_score > 0:
                if not hasattr(self, 'bonus_points') or self.bonus_points <= 0:
                    self.bonus_points = self.estimated_score
            message = "一审通过，等待二审"
        else:
            self.review_status = 'first_rejected'
            self.result = 'failed'
            message = "一审不通过"

        self.save()
        return True, message

    def perform_second_review(self, reviewer, result, review_comment="", bonus_points=None):
        """执行二审"""
        if not self.can_second_review(reviewer):
            return False, "当前状态无法进行二审"

        self.second_reviewer = reviewer
        self.second_review_comment = review_comment
        self.second_reviewed_at = timezone.now()

        if result == 'passed':
            self.review_status = 'second_approved'
            if bonus_points is not None:
                # 取最低分：如果已有分数，取两者中的最小值；否则使用当前分数
                if self.bonus_points > 0:
                    self.bonus_points = min(self.bonus_points, bonus_points)
                else:
                    self.bonus_points = bonus_points
            message = "二审通过，等待三审"
        else:
            self.review_status = 'second_rejected'
            self.result = 'failed'
            message = "二审不通过"

        self.save()
        return True, message

    def perform_third_review(self, reviewer, result, review_comment="", bonus_points=None):
        """执行三审"""
        if not self.can_third_review(reviewer):
            return False, "当前状态无法进行三审"

        self.third_reviewer = reviewer
        self.third_review_comment = review_comment
        self.third_reviewed_at = timezone.now()

        if result == 'passed':
            self.review_status = 'approved'
            self.result = 'passed'
            if bonus_points is not None:
                # 取最低分：如果已有分数，取两者中的最小值；否则使用当前分数
                if self.bonus_points > 0:
                    self.bonus_points = min(self.bonus_points, bonus_points)
                else:
                    self.bonus_points = bonus_points
            message = "三审通过"
        else:
            self.review_status = 'rejected'
            self.result = 'failed'
            message = "三审不通过"

        self.save()
        return True, message


# 英语四六级成绩审核
class EnglishScore(ReviewMixin):
    EXAM_TYPES = [
        ('cet4', '大学英语四级'),
        ('cet6', '大学英语六级'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='english_scores', verbose_name='用户')

    # 考试信息
    exam_type = models.CharField(
        max_length=10,
        choices=EXAM_TYPES,
        verbose_name='考试类型',
        default='cet4'
    )
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='考试成绩',
        help_text='请输入具体的分数'
    )
    exam_date = models.DateField(verbose_name='考试日期', null=True, blank=True)

    # 成绩证明
    score_report = models.FileField(
        upload_to='english_scores/%Y/%m/%d/',
        verbose_name='成绩报告单'
    )

    # 英语成绩特有字段
    meets_standard = models.BooleanField(null=True, blank=True, verbose_name='是否达到标准')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'english_score'
        verbose_name = '英语成绩'
        verbose_name_plural = '英语成绩'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'exam_type'],
                name='unique_user_exam_type',
                condition=models.Q(review_status__in=['pending', 'first_approved', 'approved'])
            )
        ]
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['exam_date']),
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        return f"{self.user.name}的英语成绩"

    def save(self, *args, **kwargs):
        # 自动计算是否达到标准（可根据学校要求调整）
        if self.exam_type == 'cet4' and self.exam_score >= 425:
            self.meets_standard = True
        elif self.exam_type == 'cet6' and self.exam_score >= 425:
            self.meets_standard = True
        else:
            self.meets_standard = False

        super().save(*args, **kwargs)

    @property
    def is_passed(self):
        """是否通过考试"""
        return self.meets_standard

    @classmethod
    def get_passing_score(cls, exam_type):
        """获取及格分数线"""
        passing_scores = {
            'cet4': 425,
            'cet6': 425
        }
        return passing_scores.get(exam_type, 425)

    def get_application_type_display(self):
        return "英语成绩"

    def perform_first_review(self, reviewer, result, review_comment=""):
        """英语成绩一审"""
        if not self.can_first_review(reviewer):
            return False, "当前状态无法进行一审"

        self.first_reviewer = reviewer
        self.first_review_comment = review_comment
        self.first_reviewed_at = timezone.now()

        if result == 'passed':
            self.review_status = 'first_approved'
            # 一审通过时设置是否达标
            passing_score = 425
            self.meets_standard = self.exam_score >= passing_score
            # 英语成绩不加分，设置为0
            self.bonus_points = 0
            message = "一审通过，等待二审"
        else:
            self.review_status = 'first_rejected'
            self.meets_standard = False
            self.result = 'failed'
            message = "一审不通过"

        self.save()
        return True, message

    def perform_second_review(self, reviewer, result, review_comment="", bonus_points=None):
        """英语成绩二审"""
        if not self.can_second_review(reviewer):
            return False, "当前状态无法进行二审"

        self.second_reviewer = reviewer
        self.second_review_comment = review_comment
        self.second_reviewed_at = timezone.now()

        if result == 'passed':
            self.review_status = 'approved'
            self.result = 'passed'
            if bonus_points is not None:
                # 取最低分：如果已有分数，取两者中的最小值；否则使用当前分数
                if self.bonus_points > 0:
                    self.bonus_points = min(self.bonus_points, bonus_points)
                else:
                    self.bonus_points = bonus_points
            message = "二审通过"
        else:
            self.review_status = 'rejected'
            self.result = 'failed'
            message = "二审不通过"

        self.save()
        return True, message


# 学术专长基本（移除重复的审核字段和方法）
class AcademicExpertiseBase(ReviewMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    # 通用字段
    screenshot = models.FileField(upload_to='academic_expertise/%Y/%m/%d/', blank=True, null=True, verbose_name='截图')
    user_explanation = models.TextField(blank=True, null=True, verbose_name='用户说明')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_application_type_display(self):
        """获取申请类型显示名称"""
        return self._meta.verbose_name

    class Meta:
        abstract = True


# 学术论文
class AcademicPaper(AcademicExpertiseBase):
    paper_title = models.CharField(max_length=200, verbose_name='论文标题', blank=True, null=True)
    journal_category = models.CharField(max_length=50, verbose_name='期刊/会议分类', blank=True, null=True)
    is_independent_author = models.BooleanField(default=False, verbose_name='是否为独立作者')
    is_co_first_author = models.BooleanField(default=False, verbose_name='是否为共同一作')
    author_rank = models.CharField(max_length=10, verbose_name='作者排序', blank=True, null=True)
    is_xmu_first_unit = models.BooleanField(default=True, verbose_name='厦门大学是否为第一单位')

    class Meta:
        db_table = 'academic_paper'
        verbose_name = '学术论文'
        verbose_name_plural = '学术论文'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['paper_title']),
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        return f"{self.user.name}的论文: {self.paper_title}"
    
    def calculate_bonus_points(self):
        """根据学术专长成绩加分细则计算学术论文的加分"""
        bonus_points = 0
        
        # 1. 科研成果加分
        # 期刊/会议分类加分基数
        category_scores = {
            'A': 10,
            'B': 6,
            'C': 1,
            'Nature': 20,
            'Science': 20,
            'Cell': 20,
            'Nature *': 20,
            'Science *': 20,
            'CELL *': 20
        }
        
        # 获取期刊/会议分类
        journal_category = self.journal_category or ''
        
        # 检查是否是Nature/Science/Cell主刊或子刊
        is_high_impact = False
        for high_impact_type in ['Nature', 'Science', 'Cell', 'Nature *', 'Science *', 'CELL *']:
            if high_impact_type in journal_category:
                is_high_impact = True
                break
        
        # 根据分类获取加分基数
        base_score = 0
        if is_high_impact:
            base_score = category_scores['Nature']  # 使用Nature的分数作为所有高影响因子期刊的分数
        elif journal_category in category_scores:
            base_score = category_scores[journal_category]
        elif journal_category in ['A+', 'A++']:
            base_score = category_scores['A']  # A+和A++也按照A类加分
        
        # 2. 作者排序加分比例
        author_ratio = 0
        if self.is_independent_author:
            # 独立作者，加100%
            author_ratio = 1.0
        elif self.is_co_first_author:
            # 共同第一作者，加50%
            author_ratio = 0.5
        else:
            # 普通作者，根据排序加分
            try:
                rank = int(self.author_rank) if self.author_rank else 0
                if rank == 1:
                    # 排序第一的加80%
                    author_ratio = 0.8
                elif rank == 2:
                    # 排序第二的加20%
                    author_ratio = 0.2
            except ValueError:
                # 作者排序不是数字，默认加50%
                author_ratio = 0.5
        
        # 3. 计算最终加分
        bonus_points = base_score * author_ratio
        
        # 4. 确保厦门大学是第一单位
        if not self.is_xmu_first_unit:
            bonus_points *= 0  # 不是第一单位，不加分数
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存学术论文时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 专利著作
class PatentWork(AcademicExpertiseBase):
    # 作者类型选项
    AUTHOR_TYPE_CHOICES = [
        ('first_author_except_teacher', '除老师外第一作者'),
        ('independent_author', '独立作者'),
    ]
    
    # 添加专利名称字段，与学术论文保持一致
    paper_title = models.CharField(max_length=200, verbose_name='专利名称', blank=True, null=True)
    
    # 移除不需要的字段：patent_number、patent_type
    # 添加新字段，设置默认值
    author_type = models.CharField(max_length=50, choices=AUTHOR_TYPE_CHOICES, default='first_author_except_teacher', verbose_name='作者类型')
    is_xmu_first_unit = models.BooleanField(default=True, verbose_name='厦门大学是否为第一单位')

    class Meta:
        db_table = 'patent_work'
        verbose_name = '专利著作'
        verbose_name_plural = '专利著作'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的发明专利: {self.paper_title if hasattr(self, 'paper_title') else '未知'}"
    
    def calculate_bonus_points(self):
        """根据学术专长成绩加分细则计算专利著作的加分"""
        bonus_points = 0
        
        # 1. 专利基础加分
        base_score = 2.0  # 每项国家发明专利授权加2分
        
        # 2. 作者类型加分比例
        author_ratio = 0
        if self.author_type == 'independent_author':
            # 独立作者，加100%
            author_ratio = 1.0
        elif self.author_type == 'first_author_except_teacher':
            # 除老师外第一作者，加80%
            author_ratio = 0.8
        else:
            # 其他作者类型，默认加50%
            author_ratio = 0.5
        
        # 3. 计算最终加分
        bonus_points = base_score * author_ratio
        
        # 4. 确保厦门大学是第一单位
        if not self.is_xmu_first_unit:
            bonus_points *= 0  # 不是第一单位，不加分数
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存专利著作时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 学业竞赛
class AcademicCompetition(AcademicExpertiseBase):
    COMPETITION_LEVELS = [
        ('A+', 'A+级'),
        ('A', 'A级'),
        ('A-', 'A-级'),
        ('B+', 'B+级'),
        ('B', 'B级'),
    ]

    COMPETITION_NAMES = [
        ('math_modeling', '数学建模竞赛'),
        ('programming', '程序设计竞赛'),
        ('electronic_design', '电子设计竞赛'),
        ('robotics', '机器人竞赛'),
        ('business_plan', '创业计划大赛'),
        ('other', '其他竞赛'),
    ]

    competition_level = models.CharField(max_length=5, choices=COMPETITION_LEVELS, verbose_name='竞赛级别')
    competition_name = models.CharField(max_length=50, choices=COMPETITION_NAMES, verbose_name='竞赛名称')
    competition_specific_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='具体竞赛名称')
    award_level = models.CharField(max_length=20, blank=True, null=True, verbose_name='获奖等级')

    class Meta:
        db_table = 'academic_competition'
        verbose_name = '学业竞赛'
        verbose_name_plural = '学业竞赛'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['competition_level']),
            models.Index(fields=['competition_name']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的学业竞赛: {self.competition_specific_name or self.competition_name}"
    
    def calculate_bonus_points(self):
        """根据学术专长成绩加分细则计算学业竞赛的加分"""
        bonus_points = 0
        
        # 1. 竞赛级别和获奖等级对应加分表
        competition_scores = {
            'A+': {
                'national': {
                    'first_plus': 30,  # 一等奖及以上
                    'first': 30,
                    'second': 15,
                    'third': 10
                },
                'provincial': {
                    'first_plus': 5,
                    'first': 5,
                    'second': 2,
                    'third': 1
                }
            },
            'A': {
                'national': {
                    'first_plus': 15,  # 一等奖及以上
                    'first': 15,
                    'second': 10,
                    'third': 5
                },
                'provincial': {
                    'first_plus': 2,
                    'first': 2,
                    'second': 1,
                    'third': 0.5
                }
            },
            'A-': {
                'national': {
                    'first_plus': 10,  # 一等奖及以上
                    'first': 10,
                    'second': 5,
                    'third': 2
                },
                'provincial': {
                    'first_plus': 1,
                    'first': 1,
                    'second': 0.5,
                    'third': 0
                }
            }
        }
        
        # 2. 获取竞赛级别和获奖等级
        competition_level = self.competition_level or 'A'
        award_level = self.award_level or 'third'
        
        # 3. 默认国家级
        competition_scale = 'national'  # 默认国家级
        
        # 4. 根据竞赛级别和获奖等级计算加分
        if competition_level in competition_scores:
            scale_scores = competition_scores[competition_level].get(competition_scale, {})
            bonus_points = scale_scores.get(award_level, 0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存学业竞赛时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 大创项目
class InnovationProject(AcademicExpertiseBase):
    PROJECT_LEVELS = [
        ('national', '国家级'),
        ('provincial', '省级'),
        ('university', '校级'),
    ]

    project_name = models.CharField(max_length=200, verbose_name='项目名称')
    project_level = models.CharField(max_length=20, choices=PROJECT_LEVELS, verbose_name='项目级别')
    project_duration = models.CharField(max_length=100, blank=True, null=True, verbose_name='项目周期')
    is_team_leader = models.BooleanField(default=False, verbose_name='是否为项目组长')

    class Meta:
        db_table = 'innovation_project'
        verbose_name = '大创项目'
        verbose_name_plural = '大创项目'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['project_level']),
            models.Index(fields=['project_name']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的大创项目: {self.project_name}"
    
    def calculate_bonus_points(self):
        """根据学术专长成绩加分细则计算大创项目的加分"""
        bonus_points = 0
        
        # 1. 项目级别加分表
        project_scores = {
            'national': {
                'leader': 1.0,
                'member': 0.3
            },
            'provincial': {
                'leader': 0.5,
                'member': 0.2
            },
            'university': {
                'leader': 0.1,
                'member': 0.05
            }
        }
        
        # 2. 获取项目级别
        project_level = self.project_level or 'university'
        
        # 3. 判断是否为组长
        role = 'leader' if self.is_team_leader else 'member'
        
        # 4. 计算加分
        if project_level in project_scores:
            bonus_points = project_scores[project_level].get(role, 0)
        
        # 5. 限制最大加分2分
        bonus_points = min(bonus_points, 2.0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存大创项目时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# CCF CSP认证
class CCFCSPCertification(AcademicExpertiseBase):
    score = models.IntegerField(verbose_name='CCF CSP分数')
    certification_date = models.DateField(verbose_name='认证日期')
    csp_rank_percentage = models.CharField(max_length=10, blank=True, null=True, verbose_name='排名百分比')

    class Meta:
        db_table = 'ccf_csp_certification'
        verbose_name = 'CCF CSP认证'
        verbose_name_plural = 'CCF CSP认证'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['certification_date']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的CCF CSP认证: {self.score}分"
    
    def calculate_bonus_points(self):
        """根据学术专长成绩加分细则计算CCF CSP认证的加分"""
        bonus_points = 0
        
        # 1. CSP排名加分表（A-类竞赛标准）
        csp_scores = {
            '0.2': 10,  # 排名前0.2%，等同全国一等奖
            '1.5': 5,   # 排名前1.5%，等同全国二等奖
            '3': 2      # 排名前3%，等同全国三等奖
        }
        
        # 2. 获取排名百分比
        rank_percentage = self.csp_rank_percentage or '3'
        
        # 3. 计算加分
        bonus_points = csp_scores.get(rank_percentage, 0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存CCF CSP认证时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 综合表现加分基本（移除重复的审核字段和方法）
class ComprehensivePerformanceBase(ReviewMixin):
    LEVELS = [
        ('national', '国家级'),
        ('provincial', '省级'),
        ('university', '校级'),
        ('college', '院级'),
        ('school', '校级'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    # 通用字段
    level = models.CharField(max_length=20, choices=LEVELS, blank=True, null=True, verbose_name='级别')
    working_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='工时数')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='工作职位')
    screenshot = models.FileField(upload_to='comprehensive_performance/%Y/%m/%d/', blank=True, null=True, verbose_name='截图')
    user_explanation = models.TextField(blank=True, null=True, verbose_name='用户说明')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_application_type_display(self):
        """获取申请类型显示名称"""
        return self._meta.verbose_name

    class Meta:
        abstract = True


# 国际组织实习
class InternationalInternship(ComprehensivePerformanceBase):
    organization_name = models.CharField(max_length=200, verbose_name='组织名称')
    internship_duration = models.CharField(max_length=100, verbose_name='实习时长')
    country = models.CharField(max_length=100, verbose_name='国家', blank=True, null=True)

    class Meta:
        db_table = 'international_internship'
        verbose_name = '国际组织实习'
        verbose_name_plural = '国际组织实习'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['organization_name']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的国际组织实习: {self.organization_name}"
    
    def calculate_bonus_points(self):
        """根据综合表现加分细则计算国际组织实习的加分"""
        bonus_points = 0
        
        # 1. 实习时长加分规则
        # 假设实习时长以月为单位，或者我们尝试从字符串中提取时长
        duration_str = self.internship_duration or ''
        
        # 简化处理：如果包含"一年"或"12个月"等关键词，加1分
        if '一年' in duration_str or '12个月' in duration_str:
            bonus_points = 1.0
        # 如果包含"半年"或"6个月"等关键词，加0.5分
        elif '半年' in duration_str or '6个月' in duration_str:
            bonus_points = 0.5
        # 其他情况，检查是否包含"月"关键字并尝试提取数字
        else:
            import re
            match = re.search(r'(\d+)个月?', duration_str)
            if match:
                months = int(match.group(1))
                if months >= 12:
                    bonus_points = 1.0
                elif months >= 6:
                    bonus_points = 0.5
        
        # 2. 限制最大加分1分
        bonus_points = min(bonus_points, 1.0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存国际组织实习时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 参军入伍
class MilitaryService(ComprehensivePerformanceBase):
    service_start_date = models.DateField(verbose_name='入伍时间')
    service_end_date = models.DateField(verbose_name='退伍时间')
    military_unit = models.CharField(max_length=200, verbose_name='服役部队')

    class Meta:
        db_table = 'military_service'
        verbose_name = '参军入伍'
        verbose_name_plural = '参军入伍'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['service_start_date']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的参军入伍: {self.military_unit}"
    
    def calculate_bonus_points(self):
        """根据综合表现加分细则计算参军入伍的加分"""
        bonus_points = 0
        
        try:
            # 1. 计算服役时长（天）
            service_duration = self.service_end_date - self.service_start_date
            days_served = service_duration.days
            
            # 2. 根据服役时长计算加分
            if days_served >= 730:  # 2年以上（含2年）
                bonus_points = 2.0
            elif days_served >= 365:  # 1年以上（含1年），2年以内
                bonus_points = 1.0
        except Exception as e:
            print(f"计算服役时长出错: {e}")
        
        # 3. 限制最大加分2分
        bonus_points = min(bonus_points, 2.0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存参军入伍时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 志愿服务
class VolunteerService(ComprehensivePerformanceBase):
    SERVICE_TYPES = [
        ('hours', '志愿工时'),
        ('recognition', '志愿表彰'),
    ]
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name='服务类型')
    activity_name = models.CharField(max_length=200, verbose_name='活动名称')
    activity_date = models.DateField(verbose_name='活动日期')
    award_level = models.CharField(max_length=20, blank=True, null=True, verbose_name='表彰级别')
    is_team = models.BooleanField(default=False, verbose_name='是否为团队')
    team_role = models.CharField(max_length=20, blank=True, null=True, verbose_name='团队角色')

    class Meta:
        db_table = 'volunteer_service'
        verbose_name = '志愿服务'
        verbose_name_plural = '志愿服务'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['service_type']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的志愿服务: {self.service_type}"
    
    def calculate_bonus_points(self):
        """根据综合表现加分细则计算志愿服务的加分"""
        bonus_points = 0
        
        if self.service_type == 'hours':
            # 1. 志愿工时加分
            working_hours = self.working_hours or 0.0
            
            # 工时阈值：200小时
            threshold_hours = 200.0
            
            if working_hours >= threshold_hours:
                # 超过阈值的工时
                extra_hours = working_hours - threshold_hours
                # 每2小时加0.05分，大型赛会和支教工时减半
                bonus_points = (extra_hours / 2.0) * 0.05
        elif self.service_type == 'recognition':
            # 2. 志愿表彰加分
            award_scores = {
                'national': {
                    'team': {
                        'leader': 1.0,
                        'member': 0.5
                    },
                    'individual': 1.0
                },
                'provincial': {
                    'team': {
                        'leader': 0.5,
                        'member': 0.25
                    },
                    'individual': 0.5
                },
                'university': {
                    'team': {
                        'leader': 0.25,
                        'member': 0.1
                    },
                    'individual': 0.25
                }
            }
            
            # 获取表彰级别
            award_level = self.level or 'university'
            
            # 判断是团队还是个人
            entity_type = 'team' if self.is_team else 'individual'
            
            # 团队角色
            team_role = self.team_role or 'member'
            
            # 计算加分
            if award_level in award_scores:
                if entity_type == 'team':
                    bonus_points = award_scores[award_level][entity_type].get(team_role, 0)
                else:
                    bonus_points = award_scores[award_level][entity_type]
        
        # 3. 限制最大加分1分
        bonus_points = min(bonus_points, 1.0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存志愿服务时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 荣誉称号
class HonoraryTitle(ComprehensivePerformanceBase):
    title_name = models.CharField(max_length=200, verbose_name='荣誉称号名称', blank=True, null=True)
    awarding_organization = models.CharField(max_length=200, verbose_name='授予单位', blank=True, null=True)
    awarding_date = models.DateField(verbose_name='授予日期', blank=True, null=True)
    is_collective = models.BooleanField(default=False, verbose_name='是否为集体荣誉')

    class Meta:
        db_table = 'honorary_title'
        verbose_name = '荣誉称号'
        verbose_name_plural = '荣誉称号'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['title_name']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的荣誉称号: {self.title_name}"
    
    def calculate_bonus_points(self):
        """根据综合表现加分细则计算荣誉称号的加分"""
        bonus_points = 0
        
        # 1. 荣誉级别加分表
        honor_scores = {
            'national': 2.0,
            'provincial': 1.0,
            'university': 0.2,
            'college': 0.1
        }
        
        # 2. 获取荣誉级别
        level = self.level or 'university'
        
        # 3. 计算基础加分
        bonus_points = honor_scores.get(level, 0)
        
        # 4. 集体荣誉加分减半
        if self.is_collective:
            bonus_points *= 0.5
        
        # 5. 限制最大加分2分
        bonus_points = min(bonus_points, 2.0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存荣誉称号时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 社会工作
class SocialWork(ComprehensivePerformanceBase):
    position = models.CharField(max_length=100, default='', verbose_name='工作职位')
    work_duration = models.CharField(max_length=100, default='', verbose_name='任职时长')
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name='工作表现评分')
    position_coefficient = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, verbose_name='职位系数')
    organization = models.CharField(max_length=200, default='', verbose_name='工作组织')
    work_period = models.CharField(max_length=100, default='', verbose_name='工作时间')
    work_description = models.TextField(blank=True, null=True, verbose_name='工作描述')

    class Meta:
        db_table = 'social_work'
        verbose_name = '社会工作'
        verbose_name_plural = '社会工作'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['organization']),
            models.Index(fields=['work_period']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.user.name}的社会工作: {self.position}"
    
    def calculate_bonus_points(self):
        """根据综合表现加分细则计算社会工作的加分"""
        bonus_points = 0
        
        # 1. 职位系数映射
        position_coefficients = {
            '院学生会执行主席': 2.0,
            '团总支书记': 2.0,
            '院学生会主席团成员': 1.5,
            '团总支副书记': 1.5,
            '院学生会、团总支各部部长': 1.0,
            '党支部书记': 1.0,
            '班长': 1.0,
            '团支部书记': 1.0,
            '系团总支书记': 0.75,
            '院学生会、团总支各部门副部长': 0.75,
            '社团社长': 0.75,
            '党支部委员': 0.5,
            '系团总支各部部长': 0.5,
            '各班班委': 0.5,
            '团支部委员': 0.5,
            '院学生会、团总支长期志愿者': 0.5,
            '社团副社长': 0.5,
            '社团主要干部': 0.5,
            '辩论队队长': 0.5,
            '球队队长': 0.5
        }
        
        # 2. 获取职位系数
        coefficient = self.position_coefficient
        if not coefficient or coefficient == 1.0:
            # 从职位名称获取系数
            for pos, coeff in position_coefficients.items():
                if pos in self.position:
                    coefficient = coeff
                    break
        
        # 3. 获取工作表现评分
        performance_score = self.performance_score or 0.0
        
        # 4. 计算加分：最终得分 = 系数 * 任职学年辅导员或指导老师打分 / 100
        bonus_points = coefficient * (performance_score / 100.0)
        
        # 5. 检查任职时长
        duration_str = self.work_duration or ''
        if '半年' in duration_str or '6个月' in duration_str:
            # 超过一学期但不满一年，按一学年标准减半
            bonus_points *= 0.5
        elif '一学期' in duration_str or '3个月' in duration_str:
            # 不满一个学期，不加分
            bonus_points = 0
        
        # 6. 限制最大加分2分
        bonus_points = min(bonus_points, 2.0)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存社会工作时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)


# 体育比赛
class SportsCompetition(ComprehensivePerformanceBase):
    # 竞赛级别选项
    COMPETITION_LEVELS = [
        ('international', '国际级'),
        ('national', '国家级'),
        ('provincial', '省级'),
        ('school', '校级'),
    ]
    
    # 获奖等级选项
    ACHIEVEMENT_LEVELS = [
        ('champion', '冠军'),
        ('runner_up', '亚军'),
        ('third_place', '季军'),
        ('fourth_to_eighth', '第四至八名'),
    ]
    
    # 项目类型选项
    PROJECT_TYPES = [
        ('individual', '单人项目'),
        ('two_person', '二人项目'),
    ]
    
    competition_name = models.CharField(max_length=200, verbose_name='比赛名称')
    competition_level = models.CharField(max_length=20, choices=COMPETITION_LEVELS, null=True, blank=True, verbose_name='竞赛级别')
    achievement = models.CharField(max_length=100, choices=ACHIEVEMENT_LEVELS, null=True, blank=True, verbose_name='获奖等级')
    is_team_project = models.BooleanField(default=False, verbose_name='是否是团队项目')
    team_size = models.IntegerField(default=1, verbose_name='队伍人数')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, null=True, blank=True, verbose_name='项目类型')
    competition_date = models.DateField(null=True, blank=True, verbose_name='比赛日期')
    
    def __str__(self):
        return f"{self.user.name}的体育竞赛: {self.competition_name}"
    
    def calculate_bonus_points(self):
        """根据综合表现加分细则计算体育竞赛的加分"""
        bonus_points = 0
        
        # 1. 体育竞赛加分表
        sports_scores = {
            'international': {
                'champion': 8.0,
                'runner_up': 6.5,
                'third_place': 5.0,
                'fourth_to_eighth': 3.5
            },
            'national': {
                'champion': 5.0,
                'runner_up': 3.5,
                'third_place': 2.0,
                'fourth_to_eighth': 1.0
            }
        }
        
        # 2. 获取竞赛级别和获奖等级
        competition_level = self.competition_level or 'national'
        achievement = self.achievement or 'fourth_to_eighth'
        
        # 3. 计算基础加分
        if competition_level in sports_scores:
            bonus_points = sports_scores[competition_level].get(achievement, 0)
        
        # 4. 团队项目加分调整
        if self.is_team_project:
            team_size = self.team_size or 1
            if team_size == 1:
                # 单人项目按团队项目加分值的1/3计算
                bonus_points *= (1/3)
            elif team_size > 1:
                # 多人团队按参赛人数平均计算
                bonus_points /= team_size
        else:
            # 个人项目按团队项目加分值的1/3计算
            bonus_points *= (1/3)
        
        return round(bonus_points, 4)
    
    def save(self, *args, **kwargs):
        """保存体育竞赛时，自动计算加分"""
        # 如果还没有设置bonus_points，使用calculate_bonus_points计算
        if not self.bonus_points:
            self.bonus_points = self.calculate_bonus_points()
        
        # 调用父类save方法
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'sports_competition'
        verbose_name = '体育比赛'
        verbose_name_plural = '体育比赛'
        indexes = [
            models.Index(fields=['user', 'review_status']),
            models.Index(fields=['review_status']),
            models.Index(fields=['competition_name']),
            models.Index(fields=['competition_level']),
            models.Index(fields=['achievement']),
            models.Index(fields=['is_team_project']),
            models.Index(fields=['competition_date']),
            models.Index(fields=['created_at'])
        ]