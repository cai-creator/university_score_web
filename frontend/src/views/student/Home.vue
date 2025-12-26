<template>
  <div class="student-home">
    <a-card title="学生综合素质加分系统" class="welcome-card">
      <div class="welcome-info">
        <h3>欢迎，{{ userInfo?.name }}同学</h3>
        <p>班级：{{ userInfo?.class_name }}</p>
      </div>
    </a-card>

    <a-card title="当前加分情况" class="score-card">
      <div class="score-content">
        <div class="score-item">
          <div class="score-label">当前总分数</div>
          <div class="score-value">{{ currentScore }}</div>
        </div>
        <div class="score-breakdown">
          <a-row :gutter="[16, 16]">
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">科研成果</div>
                <div class="category-score">{{ scoreBreakdown.research }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">学业竞赛</div>
                <div class="category-score">{{ scoreBreakdown.competition }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">创新创业</div>
                <div class="category-score">{{ scoreBreakdown.innovation }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">国际组织实习</div>
                <div class="category-score">{{ scoreBreakdown.internship }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">参军入伍</div>
                <div class="category-score">{{ scoreBreakdown.military }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">志愿服务</div>
                <div class="category-score">{{ scoreBreakdown.volunteer }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">荣誉称号</div>
                <div class="category-score">{{ scoreBreakdown.honor }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">社会工作</div>
                <div class="category-score">{{ scoreBreakdown.socialWork }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="score-category">
                <div class="category-name">体育比赛</div>
                <div class="category-score">{{ scoreBreakdown.sports }}</div>
              </div>
            </a-col>
          </a-row>
        </div>
      </div>
    </a-card>

    <a-card title="加分项目展示" class="projects-card">
      <a-table
        :columns="projectColumns"
        :data-source="allProjects"
        :pagination="{ pageSize: 10 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            {{ getProjectTypeText(record.type) }}
          </template>
          <template v-if="column.key === 'score'">
            <span class="score-text">{{ record.score !== undefined ? record.score : 0 }}分</span>
          </template>
          <template v-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import api from '../../utils/api'

const router = useRouter()
// 用户信息
const userInfo = ref(JSON.parse(localStorage.getItem('user')))

// 当前总分数
const currentScore = ref(0)

// 分数明细
const scoreBreakdown = ref({
  research: 0,
  competition: 0,
  innovation: 0,
  internship: 0,
  military: 0,
  volunteer: 0,
  honor: 0,
  socialWork: 0,
  sports: 0
})

// 科研成果项目
const researchProjects = ref([])

// 学业竞赛项目
const competitionProjects = ref([])

// 其他项目
const otherProjects = ref([])

// 所有项目
const allProjects = computed(() => {
  return [...researchProjects.value, ...competitionProjects.value, ...otherProjects.value]
})

// 表格列配置
const projectColumns = [
  { title: '项目名称', dataIndex: 'name', key: 'name', ellipsis: true },
  { title: '项目类型', dataIndex: 'type', key: 'type' },
  { title: '申请分数', dataIndex: 'score', key: 'score', sorter: (a, b) => (a.score || 0) - (b.score || 0) },
  { title: '申请时间', dataIndex: 'created_at', key: 'created_at', sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at) },
  { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true }
]

// 日期格式化函数
const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return ''
  }
}

// 将绩点换算为基础分数（80分）
const calculateBaseScore = (gpa) => {
  if (!gpa) return 0
  // 绩点4.0对应80分，线性换算
  const baseScore = (parseFloat(gpa) / 4.0) * 80.0
  return Math.min(80.0, Math.max(0.0, baseScore))
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const data = await api.student.getCurrentUser()
    userInfo.value = data
    
    // 如果后端返回了total_score，直接使用，无论值是多少
    if (data.total_score !== undefined) {
      currentScore.value = data.total_score
    } else {
      // 否则，根据绩点和加分计算总分
      const baseScore = calculateBaseScore(data.gpa)
      const bonusScore = data.currentScore || 0
      currentScore.value = baseScore + bonusScore
    }
    console.log('当前总分数:', currentScore.value)
  } catch (error) {
    message.error('获取用户信息失败')
  }
}

// 获取加分项目列表
const fetchScoreItems = async () => {
  try {
    // 由于API拦截器的处理，getScoreItems直接返回score_items数组
    const response = await api.student.getScoreItems()
    
    // 确保items是数组，防止filter方法调用失败
    const validItems = Array.isArray(response) ? response : []
    
    // 过滤掉英语成绩相关项目，其他项目全部保留
    const filteredItems = validItems.filter(item => {
      // 过滤掉英语成绩项目
      const isNotEnglish = item.type !== 'english' && 
                           item.type !== 'english_score' &&
                           !item.type?.includes('english');
      return isNotEnglish;
    })
    
    // 为每个项目添加默认分数，确保score字段有值
    const itemsWithDefaultScore = filteredItems.map(item => ({
      ...item,
      score: typeof item.score === 'number' ? item.score : parseFloat(item.bonus_points || 0) || 0
    }))
    
    // 分类项目 - 使用与后端匹配的下划线命名法，同时支持多种类型映射
    researchProjects.value = itemsWithDefaultScore.filter(item => 
      ['scientific_research', 'academic_paper', 'patent_work', 'paper', 'patent', 'research'].includes(item.type)
    )
    
    competitionProjects.value = itemsWithDefaultScore.filter(item => 
      ['academic_competition', 'competition', 'sports_competition', 'sports'].includes(item.type)
    )
    
    // 其他项目：除了科研和竞赛之外的所有项目
    otherProjects.value = itemsWithDefaultScore.filter(item => {
      const isResearch = researchProjects.value.includes(item);
      const isCompetition = competitionProjects.value.includes(item);
      return !isResearch && !isCompetition;
    })
    
    // 计算各分类分数
    const calculateCategoryScore = (items) => {
      return items.reduce((sum, item) => sum + (item.score || 0), 0);
    }
    
    // 分类计算分数
    const researchScore = calculateCategoryScore(researchProjects.value)
    const competitionScore = calculateCategoryScore(competitionProjects.value)
    const otherScore = calculateCategoryScore(otherProjects.value)
    
    // 调试：打印获取到的加分项目和分数明细
    console.log('获取到的所有项目:', validItems)
    console.log('过滤后的项目:', itemsWithDefaultScore)
    console.log('科研成果项目:', researchProjects.value)
    console.log('学业竞赛项目:', competitionProjects.value)
    console.log('其他项目:', otherProjects.value)
    
  } catch (error) {
    console.error('获取加分项目失败:', error)
    message.error('获取加分项目失败')
    // 发生错误时确保项目列表为空数组
    researchProjects.value = []
    competitionProjects.value = []
    otherProjects.value = []
  }
}

// 获取项目类型中文文本
const getProjectTypeText = (type) => {
  // 健壮性处理：确保输入是字符串类型
  const typeStr = String(type || '')
  if (!typeStr.trim()) return ''
  
  // 检查是否已经是中文（包含中文字符）
  if (/[\u4e00-\u9fa5]/.test(typeStr)) {
    return typeStr
  }
  
  // 项目类型中英文映射
  const typeMap = {
    // 基础核心类型
    'scientific_research': '科研成果',
    'academic_competition': '学业竞赛',
    'academic': '科研成果',
    'innovation': '创新创业训练',
    'internship': '国际组织实习',
    'military': '参军入伍服兵役',
    'volunteer': '志愿服务',
    'honor': '荣誉称号',
    'social_work': '社会工作',
    'social': '社会工作',
    'sports': '体育比赛',
    'english': '英语成绩',
    'ccf': 'CCF CSP认证',
    
    // 扩展类型
    'research': '科研成果',
    'competition': '学业竞赛',
    'project_innovation': '创新创业训练',
    'international_intern': '国际组织实习',
    'military_service_experience': '参军入伍服兵役',
    'volunteer_activity': '志愿服务',
    'honor_award': '荣誉称号',
    'social_practice': '社会实践',
    'sports_game': '体育比赛',
    'english_proficiency': '英语成绩',
    
    // 英语成绩类
    'english_cet4': '全国大学英语四级考试',
    'english_cet6': '全国大学英语六级考试',
    'english_other': '其他英语成绩',
    'cet4': '全国大学英语四级考试',
    'cet6': '全国大学英语六级考试',
    'toefl': '托福考试',
    'ielts': '雅思考试',
    'gre': 'GRE考试',
    'gmat': 'GMAT考试',
    
    // 学术专长类
    'academic_paper': '学术论文',
    'paper': '学术论文',
    'patent_work': '发明专利',
    'patent': '发明专利',
    'academic_competition': '学业竞赛',
    
    // 综合表现类
    'international_internship': '国际组织实习',
    'military_service': '参军入伍服兵役',
    'volunteer_service': '志愿服务',
    'honorary_title': '荣誉称号',
    'social_activity': '社会工作',
    'sports_competition': '体育比赛',
    
    // 详细子类映射
    'A': 'A类期刊论文',
    'B': 'B类期刊论文',
    'C': 'C类期刊论文',
    'invention': '发明专利',
    'utility': '实用新型专利',
    'independent': '独立作者',
    'first': '第一作者',
    'other': '其他作者',
    'national': '国家级竞赛',
    'provincial': '省级竞赛',
    'A+': 'A+类学科竞赛',
    'A-': 'A-类学科竞赛',
    'individual': '个人参赛',
    'team2': '2人团队',
    'team3': '2-3人团队',
    'team4': '4-5人团队',
    
    // 其他常见类型
    'scholarship': '奖学金',
    'national_scholarship': '国家奖学金',
    'provincial_scholarship': '省级奖学金',
    'school_scholarship': '校级奖学金',
    'excellent_student': '优秀学生',
    'excellent_student_leader': '优秀学生干部',
    'merit_student': '三好学生',
    'sports_meeting': '运动会',
    'basketball': '篮球比赛',
    'football': '足球比赛',
    'volleyball': '排球比赛',
    'cultural_activity': '文化活动',
    'art_performance': '文艺表演',
    'social_service': '社会服务',
    'field_work': '实地调研',
    'course_project': '课程项目',
    'team_project': '团队项目',
    'individual_project': '个人项目',
    'certificate': '证书',
    'skill_certificate': '技能证书',
    'professional_certificate': '职业证书'
  }
  
  // 大小写不敏感的匹配
  const normalizedType = typeStr.trim().toLowerCase()
  
  // 尝试直接精确匹配
  if (typeMap[normalizedType]) {
    return typeMap[normalizedType]
  }
  
  // 尝试前缀匹配
  const prefixMatch = Object.keys(typeMap).find(key => normalizedType.startsWith(key.toLowerCase()))
  if (prefixMatch) {
    return typeMap[prefixMatch]
  }
  
  // 尝试关键词映射
  const keywordMap = {
    'paper': '学术论文',
    'patent': '发明专利',
    'competition': '竞赛',
    'innovation': '创新创业',
    'intern': '实习',
    'military': '参军入伍',
    'volunteer': '志愿服务',
    'honor': '荣誉',
    'social': '社会',
    'sports': '体育',
    'english': '英语成绩',
    'cet4': '英语四级',
    'cet6': '英语六级',
    'toefl': '托福',
    'ielts': '雅思',
    'ccf': 'CCF CSP认证'
  }
  
  // 检查是否包含关键词
  for (const [keyword, chinese] of Object.entries(keywordMap)) {
    if (normalizedType.includes(keyword.toLowerCase())) {
      return chinese
    }
  }
  
  // 默认返回原始中文值（去掉英文前缀）
  return normalizedType
}

onMounted(() => {
  fetchUserInfo()
  fetchScoreItems()
  
  // 如果没有登录信息，跳转到登录页面
  if (!userInfo.value) {
    router.push('/login')
  }
})
</script>

<style scoped>
.student-home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.welcome-card {
  margin-bottom: 24px;
}

.welcome-info h3 {
  margin-bottom: 8px;
  color: #1890ff;
}

.score-card {
  margin-bottom: 24px;
}

.score-content {
  padding: 16px 0;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.score-label {
  font-size: 18px;
  color: #666;
  margin-bottom: 8px;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .score-value {
    font-size: 36px;
  }
  
  .category-score {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .score-value {
    font-size: 28px;
  }
  
  .category-score {
    font-size: 18px;
  }
  
  .student-home {
    gap: 16px;
  }
}

.score-breakdown {
  margin-top: 32px;
}

.score-category {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.category-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.category-score {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.projects-card {
    margin-bottom: 24px;
  }
  
  /* 表格样式，参照教师端设计 */
  :deep(.ant-table-thead > tr > th) {
    font-weight: bold;
    background-color: #f0f2f5;
  }
  
  :deep(.ant-table-tbody > tr:hover) {
    background-color: #fafafa;
  }
  
  .score-text {
    color: #52c41a;
    font-weight: bold;
  }
</style>