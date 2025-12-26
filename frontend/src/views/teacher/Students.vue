<template>
  <div class="teacher-students">
    <h2>学生信息管理</h2>
    
    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <a-row :gutter="[16, 16]">
        <a-col :span="12">
          <a-input v-model:value="searchText" placeholder="搜索学生姓名、学号或班级" @pressEnter="handleSearch" />
        </a-col>
        <a-col :span="12" style="text-align: right;">
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-col>
      </a-row>
    </div>

    <!-- 学生列表 -->
    <a-card class="students-list" style="margin-top: 20px;">
      <a-table
        :loading="loading"
        :columns="columns"
        :data-source="filteredStudents"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
        :locale="{ emptyText: loading ? '加载中...' : '暂无数据' }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'totalScore'">
            {{ record.totalScore }}分
          </template>
          <template v-else-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button type="link" @click="handleView(record)">查看</a-button>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 学生详情模态框 -->
    <a-modal
      v-model:open="viewModalVisible"
      title="学生详情"
      :footer="null"
      width="800px"
    >
      <div v-if="selectedStudent" class="student-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="学号">{{ selectedStudent.studentId }}</a-descriptions-item>
          <a-descriptions-item label="姓名">{{ selectedStudent.name }}</a-descriptions-item>
          <a-descriptions-item label="班级">{{ selectedStudent.class }}</a-descriptions-item>
          <a-descriptions-item label="院系">{{ selectedStudent.department }}</a-descriptions-item>
          <a-descriptions-item label="联系方式">{{ selectedStudent.phone }}</a-descriptions-item>
          <a-descriptions-item label="邮箱">{{ selectedStudent.email }}</a-descriptions-item>
          <a-descriptions-item label="绩点">{{ selectedStudent.gpa || 0 }}</a-descriptions-item>
          <a-descriptions-item label="加分成绩">{{ selectedStudent.bonusScore }}分</a-descriptions-item>
          <a-descriptions-item label="综合总分（综测成绩）" :span="2">{{ selectedStudent.comprehensiveScore }}分</a-descriptions-item>
        </a-descriptions>

        <!-- 成绩构成 -->
        <a-card title="综测成绩构成" style="margin-top: 20px;">
          <div v-if="selectedStudent.scoreBreakdown && Object.keys(selectedStudent.scoreBreakdown).length > 0" class="score-breakdown">
            <a-table
              :columns="scoreBreakdownColumns"
              :data-source="scoreBreakdownData"
              :pagination="false"
              bordered
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'score'">
                  {{ record.score }}分
                </template>
              </template>
            </a-table>
          </div>
          <div v-else class="no-score-breakdown">
            <a-empty description="暂无成绩构成数据" />
          </div>
        </a-card>
      </div>
    </a-modal>


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api.js'

// 状态管理
const students = ref([])
const searchText = ref('')
const loading = ref(false) // 确保加载状态变量已定义

// 模态框状态
const viewModalVisible = ref(false)
const selectedStudent = ref(null)

// 路由
const router = useRouter()

// 表格列配置
const columns = [
  { title: '学号', dataIndex: 'studentId', key: 'studentId', width: 120, ellipsis: true },
  { title: '姓名', dataIndex: 'name', key: 'name', width: 100, ellipsis: true },
  { title: '班级', dataIndex: 'class', key: 'class', width: 120, ellipsis: true },
  { title: '院系', dataIndex: 'department', key: 'department', width: 150, ellipsis: true },
  { 
    title: '综测成绩', 
    dataIndex: 'totalScore', 
    key: 'totalScore', 
    width: 100, 
    align: 'right',
    customCell: (_, { text }) => ({
      children: text || 0
    })
  },
  { title: '操作', key: 'actions', fixed: 'right', width: 100 }
]

// 成绩构成表格列配置
const scoreBreakdownColumns = [
  { title: '加分类型', dataIndex: 'type', key: 'type', width: 150 },
  { title: '分数', dataIndex: 'score', key: 'score', width: 100, align: 'right' },
  { title: '备注', dataIndex: 'remark', key: 'remark' }
]

// 综测分数计算函数 - 由80分的学业成绩（绩点4分转化为80分）和20分的加分构成
const calculateTotalScore = (gpa, bonusScore) => {
  // 绩点4.0对应80分，线性换算
  const academicScore = (parseFloat(gpa) / 4.0) * 80.0;
  const finalAcademicScore = Math.min(80.0, Math.max(0.0, academicScore));
  // 加分最高20分
  const finalBonus = Math.min(20.0, Math.max(0.0, bonusScore));
  // 总分 = 学业成绩 + 加分
  return Math.round((finalAcademicScore + finalBonus) * 100) / 100;
}

// 成绩构成数据转换为表格格式
const scoreBreakdownData = computed(() => {
  if (!selectedStudent.value || !selectedStudent.value.scoreBreakdown) {
    return []
  }
  
  const breakdown = selectedStudent.value.scoreBreakdown
  return Object.entries(breakdown).map(([type, score]) => {
    // 类型名称映射
    const typeMap = {
      'academic_papers': '学术论文',
      'patent_works': '专利著作',
      'academic_competitions': '学业竞赛',
      'innovation_projects': '大创项目',
      'ccf_csp_certifications': 'CCF CSP认证',
      'international_internships': '国际组织实习',
      'military_services': '参军入伍',
      'volunteer_services': '志愿服务',
      'honorary_titles': '荣誉称号',
      'social_works': '社会工作',
      'sports_competitions': '体育比赛',
      'english_scores': '英语成绩'
    }
    return {
      key: type,
      type: typeMap[type] || type,
      score: score,
      remark: ''
    }
  })
})

// 筛选后的学生列表
const filteredStudents = computed(() => {
  if (!searchText.value.trim()) {
    return students.value
  }
  
  const search = searchText.value.toLowerCase()
  return students.value.filter(student => 
    (student.name && student.name.toLowerCase().includes(search)) ||
    (student.studentId && student.studentId.toLowerCase().includes(search)) ||
    (student.class && student.class.toLowerCase().includes(search)) ||
    (student.department && student.department.toLowerCase().includes(search))
  )
})

// 搜索
const handleSearch = async () => {
  try {
    const response = await api.teacher.getStudents({
      search: searchText.value // 后端使用search参数而非keyword
    })
    // 确保获取到正确的数组数据并进行字段映射
    const rawStudents = response.students || (Array.isArray(response) ? response : [])
    students.value = rawStudents.map(mapStudentFields)
  } catch (error) {
    message.error('搜索学生失败: ' + (error.response?.data?.message || error.message))
  }
}

// 重置搜索
const handleReset = () => {
  searchText.value = ''
}

// 查看学生详情
const handleView = (record) => {
  selectedStudent.value = record
  viewModalVisible.value = true
}





// 字段映射函数 - 处理后端返回的学生数据，支持对象格式的班级和院系信息
const mapStudentFields = (student) => {
  // 确保student是对象
  if (!student || typeof student !== 'object') {
    console.warn('无效的学生数据:', student)
    return null
  }
  
  // 处理班级信息 - 支持对象格式和直接名称格式
  let className = '未分配'
  if (student.class && typeof student.class === 'object') {
    // 后端返回的是对象格式 {id: '', name: ''}
    className = student.class.name || '未分配'
  } else if (student.class_name) {
    // 旧数据格式，直接返回名称
    className = student.class_name
  } else if (student.class) {
    // 可能直接是字符串
    className = student.class
  }
  
  // 处理院系信息 - 支持对象格式和直接名称格式
  let collegeName = '未分配'
  if (student.college && typeof student.college === 'object') {
    // 后端返回的是对象格式 {id: '', name: ''}
    collegeName = student.college.name || '未分配'
  } else if (student.college_name) {
    // 旧数据格式，直接返回名称
    collegeName = student.college_name
  } else if (student.college) {
    // 可能直接是字符串
    collegeName = student.college
  }
  
  // 获取绩点
  const gpa = student.gpa || 0
  
  // 获取加分成绩（确保使用正确的加分数据：bonus_score字段是审核通过的申请分数）
  const bonusScore = student.bonus_score || student.total_bonus || 0
  
  // 计算综测成绩（作为后备）
  const calculatedScore = calculateTotalScore(gpa, bonusScore)
  
  // 优先使用后端返回的total_score，如果后端没有返回则使用前端计算的分数
  // 确保使用正确的字段名：后端可能返回total_score或totalScore
  const totalScoreFromBackend = student.total_score || student.totalScore
  const comprehensiveScore = totalScoreFromBackend !== undefined ? totalScoreFromBackend : calculatedScore
  
  // 直接构建需要的字段，避免使用...student覆盖处理后的字段
  return {
    id: student.id || '',
    studentId: student.school_id || '', // 后端使用school_id字段
    name: student.name || '未知',
    class: className,
    department: collegeName,
    bonusScore: bonusScore, // 加分成绩
    comprehensiveScore: comprehensiveScore, // 综合总分（综测成绩）
    phone: student.contact || '', // 后端使用contact表示联系方式
    email: student.email || '',
    // 补充完整字段
    grade: student.grade || '',
    major: student.major || '',
    gender: student.gender || '',
    gpa: gpa, // 保留绩点信息
    user_type: student.user_type || '',
    user_type_display: student.user_type_display || '',
    // 成绩构成 - 支持对象格式
    scoreBreakdown: student.score_breakdown || student.scoreBreakdown || {},
    // 兼容旧代码，保留totalScore字段，优先使用后端返回的分数
    totalScore: comprehensiveScore,
    // 避免原始对象覆盖处理后的字段，不使用...student
  }
}

// 获取学生列表
const fetchStudents = async () => {
  try {
    loading.value = true // 显示加载状态
    const response = await api.teacher.getStudents()
    
    // 详细解析响应数据结构
    console.log('原始响应数据:', response)
    
    // 适配后端可能的不同返回格式
    let rawStudents = []
    if (response && Array.isArray(response)) {
      // 如果直接返回数组
      rawStudents = response
    } else if (response && response.results) {
      // 如果是分页格式
      rawStudents = response.results
    } else if (response && response.students) {
      // 如果包含students字段
      rawStudents = response.students
    }
    
    console.log('提取的学生原始数据:', rawStudents)
    
    // 过滤无效数据并进行字段映射
    const validStudents = rawStudents
      .map(student => mapStudentFields(student))
      .filter(student => student !== null)
    
    students.value = validStudents
    // 移除对未定义变量total的赋值
    
    console.log('处理后的学生数据:', students.value)
    
    // 如果没有数据，显示提示信息
    if (validStudents.length === 0) {
      message.info('暂无学生数据')
    }
  } catch (error) {
    console.error('获取学生列表错误详情:', error)
    console.error('错误响应:', error.response)
    message.error('获取学生列表失败: ' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    loading.value = false // 隐藏加载状态
  }
}

onMounted(() => {
  fetchStudents()
})
</script>

<style scoped>
.teacher-students {
  padding: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  align-items: center;
}

.student-detail {
  max-height: 600px;
  overflow-y: auto;
}
</style>