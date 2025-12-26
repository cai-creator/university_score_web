<template>
  <div class="local-estimation">
    <div class="page-header">
      <h2>本地分数估算</h2>
      <div>
        <a-button type="primary" @click="showAddManualModal = true" style="margin-right: 8px;">
          <PlusOutlined /> 手动添加
        </a-button>
        <a-button type="primary" @click="showAddFromApplicationModal = true">
          <PlusOutlined /> 从我的申请中选择
        </a-button>
      </div>
    </div>
    
    <div class="score-summary">
      <a-card title="当前估算总分">
        <div class="total-score">{{ totalScore.toFixed(2) }}</div>
        <div class="score-explanation">
          注：此分数仅为本地估算，不代表最终审核结果。
          部分项目有数量或分数上限限制。
        </div>
      </a-card>
    </div>
    
    <div class="project-list">
      <a-card title="本地项目列表">
        <a-table 
          :columns="columns" 
          :data-source="localProjects" 
          row-key="id"
          :pagination="false"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'actions'">
              <a-button type="text" @click="editProject(record)">
                <EditOutlined /> 编辑
              </a-button>
              <a-button type="text" danger @click="deleteProject(record.id)">
                <DeleteOutlined /> 删除
              </a-button>
            </template>
            <template v-if="column.key === 'score'">
              {{ record.score?.toFixed(2) || '0.00' }}
            </template>
          </template>
        </a-table>
        
        <div v-if="localProjects.length === 0" class="empty-state">
          <Empty description="暂无本地项目" />
        </div>
      </a-card>
    </div>
    
    <!-- 手动添加项目弹窗 -->
    <a-modal
      v-model:open="showAddManualModal"
      title="手动添加项目"
      @ok="handleManualModalOk"
      @cancel="handleManualModalCancel"
      width="600px"
    >
      <a-form :model="currentProject" :rules="formRules" ref="formRef" layout="vertical">
        <a-form-item label="项目类型" name="type">
          <a-select 
            v-model:value="currentProject.type" 
            placeholder="请选择项目类型"
          >
            <a-select-option value="research">科研成果</a-select-option>
            <a-select-option value="competition">学业竞赛</a-select-option>
            <a-select-option value="innovation">创新创业训练</a-select-option>
            <a-select-option value="internship">国际组织实习</a-select-option>
            <a-select-option value="military">参军入伍服兵役</a-select-option>
            <a-select-option value="volunteer">志愿服务</a-select-option>
            <a-select-option value="honor">荣誉称号</a-select-option>
            <a-select-option value="social">社会工作</a-select-option>
            <a-select-option value="sports">体育比赛</a-select-option>
            <a-select-option value="ccf">CCF CSP认证</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="项目名称" name="name">
          <a-input v-model:value="currentProject.name" placeholder="请输入项目名称" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 从申请中选择项目弹窗 -->
    <a-modal
      v-model:open="showAddFromApplicationModal"
      title="从我的申请中选择项目"
      @ok="handleApplicationModalOk"
      @cancel="handleApplicationModalCancel"
      @open="fetchApplications"
      width="800px"
    >
      <a-spin v-if="applicationLoading" tip="加载中...">
        <a-table 
          :columns="applicationColumns" 
          :data-source="applications" 
          row-key="id"
          :pagination="false"
          :scroll="{ y: 400 }"
          :row-selection="rowSelection"
          :locale="{ emptyText: '暂无申请项目' }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'review_status'">
              <a-tag :color="getStatusColor(record.review_status)">{{ record.review_status || '未知状态' }}</a-tag>
            </template>
            <template v-if="column.key === 'score'">
              <span>{{ record.bonus_points || record.estimated_score || 0 }}分</span>
            </template>
          </template>
        </a-table>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { Empty } from 'ant-design-vue'
import {
  calculateTotalScore,
  calculateProjectScore
} from '@/utils/scoreCalculator'
import api from '@/utils/api.js'

// 本地项目数据
const localProjects = ref([])

// 用户信息，用于获取绩点计算基础分数
const userInfo = ref(JSON.parse(localStorage.getItem('user')))

// 手动添加弹窗状态
const showAddManualModal = ref(false)
const formRef = ref(null)
const currentProject = ref({
  id: '',
  name: '',
  type: '',
  score: 0
})

// 从申请中选择弹窗状态
const showAddFromApplicationModal = ref(false)
const applications = ref([])
const selectedApplications = ref([])
const applicationLoading = ref(false)

// 表单验证规则
const formRules = {
  type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ]
}

// 申请表格列配置
const applicationColumns = [
  {
    title: '项目名称',
    dataIndex: 'title',
    key: 'title'
  },
  {
    title: '项目类型',
    dataIndex: 'displayCategory',
    key: 'displayCategory'
  },
  {
    title: '状态',
    dataIndex: 'review_status',
    key: 'review_status'
  },
  {
    title: '审核分数',
    dataIndex: 'bonus_points',
    key: 'score'
  }
]

// 申请项目选择配置
const rowSelection = {
  type: 'checkbox',
  onChange: (selectedRowKeys, selectedRows) => {
    selectedApplications.value = selectedRows
  }
}

// 申请类型映射
const applicationTypeMap = {
  'academic_paper': 'research',
  'patent_work': 'research',
  'academic_competition': 'competition',
  'innovation': 'innovation',
  'ccf_csp': 'ccf',
  'internship': 'internship',
  'military': 'military',
  'volunteer': 'volunteer',
  'honor': 'honor',
  'social': 'social',
  'sports_competition': 'sports'
}

// 获取申请状态颜色
const getStatusColor = (status) => {
  const colorMap = {
    'pending': 'orange',
    'first_reviewing': 'blue',
    'first_approved': 'blue',
    'second_reviewing': 'blue',
    'second_approved': 'blue',
    'third_reviewing': 'blue',
    'third_approved': 'blue',
    'approved': 'green',
    'rejected': 'red',
    'first_rejected': 'red',
    'second_rejected': 'red',
    'third_rejected': 'red',
    'withdrawn': 'gray',
    '待审核': 'orange',
    '一审中': 'blue',
    '一审通过': 'blue',
    '二审中': 'blue',
    '二审通过': 'blue',
    '三审中': 'blue',
    '三审通过': 'blue',
    '审核通过': 'green',
    '审核未通过': 'red',
    '已撤回': 'gray'
  }
  return colorMap[status] || 'default'
}

// 表格列配置
const columns = [
  {
    title: '项目名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '项目类型',
    dataIndex: 'type',
    key: 'type',
    customRender: (text) => {
      const typeMap = {
        research: '科研成果',
        competition: '学业竞赛',
        innovation: '创新创业训练',
        internship: '国际组织实习',
        military: '参军入伍服兵役',
        volunteer: '志愿服务',
        honor: '荣誉称号',
        social: '社会工作',
        sports: '体育比赛',
        ccf: 'CCF CSP认证'
      }
      return typeMap[text] || text
    }
  },
  {
    title: '估算分数',
    dataIndex: 'score',
    key: 'score',
    sorter: (a, b) => a.score - b.score
  },
  {
    title: '操作',
    key: 'actions'
  }
]

// 将绩点换算为基础分数（80分）
const calculateBaseScore = (gpa) => {
  if (!gpa) return 0
  const baseScore = (parseFloat(gpa) / 4.0) * 80.0
  return Math.min(80.0, Math.max(0.0, baseScore))
}

// 计算总分数，包含基础分数和加分项目分数
const totalScore = computed(() => {
  const baseScore = calculateBaseScore(userInfo.value?.gpa || 0)
  const bonusScore = calculateTotalScore(localProjects.value)
  return baseScore + bonusScore
})

// 从本地存储加载项目
const loadProjects = () => {
  const savedProjects = localStorage.getItem('localEstimationProjects')
  if (savedProjects) {
    localProjects.value = JSON.parse(savedProjects)
  }
}

// 保存项目到本地存储
const saveProjects = () => {
  localStorage.setItem('localEstimationProjects', JSON.stringify(localProjects.value))
}

// 获取用户信息，用于获取最新的绩点
const fetchUserInfo = async () => {
  try {
    const data = await api.student.getCurrentUser()
    userInfo.value = data
    localStorage.setItem('user', JSON.stringify(data))
  } catch (error) {
    message.error('获取用户信息失败')
  }
}

// 获取申请列表
const fetchApplications = async () => {
  applicationLoading.value = true
  try {
    const data = await api.student.getApplications()
    let rawApplications = []
    if (data.results) {
      rawApplications = data.results
    } else if (data.data && Array.isArray(data.data)) {
      rawApplications = data.data
    } else if (Array.isArray(data)) {
      rawApplications = data
    }
    
    // 处理申请列表数据，保留原始category用于映射，添加displayCategory用于显示
    const typeMap = {
      'english': '英语成绩',
      'academic_paper': '学术论文',
      'patent_work': '发明专利',
      'academic_competition': '学业竞赛',
      'innovation': '创新创业训练',
      'ccf_csp': 'CCF CSP认证',
      'internship': '国际组织实习',
      'military': '参军入伍服兵役',
      'volunteer': '志愿服务',
      'honor': '荣誉称号',
      'social': '社会工作',
      'sports_competition': '体育比赛'
    }
    
    const statusMap = {
      'pending': '待审核',
      'first_reviewing': '一审中',
      'first_approved': '一审通过',
      'second_reviewing': '二审中',
      'second_approved': '二审通过',
      'third_reviewing': '三审中',
      'third_approved': '三审通过',
      'approved': '审核通过',
      'rejected': '审核未通过',
      'first_rejected': '一审未通过',
      'second_rejected': '二审未通过',
      'third_rejected': '三审未通过',
      'withdrawn': '已撤回'
    }
    
    const processedApplications = (rawApplications || []).map(application => ({
      ...application,
      displayCategory: typeMap[application.category] || application.category,
      review_status: statusMap[application.review_status] || application.review_status
    }))
    
    applications.value = processedApplications
  } catch (error) {
    console.error('获取申请列表失败:', error)
    message.error('获取申请列表失败')
    applications.value = []
  } finally {
    applicationLoading.value = false
  }
}

// 处理手动添加弹窗确认
const handleManualModalOk = async () => {
  try {
    if (!formRef.value) return
    await formRef.value.validate()
    
    const projectScore = calculateProjectScore(currentProject.value)
    currentProject.value.score = projectScore
    
    localProjects.value.push({
      ...JSON.parse(JSON.stringify(currentProject.value)),
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9)
    })
    
    message.success('项目已添加')
    saveProjects()
    showAddManualModal.value = false
    
    // 重置表单
    currentProject.value = {
      name: '',
      type: '',
      score: 0
    }
    if (formRef.value) {
      formRef.value.resetFields()
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 处理手动添加弹窗取消
const handleManualModalCancel = () => {
  showAddManualModal.value = false
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 处理从申请中选择弹窗确认
const handleApplicationModalOk = async () => {
  try {
    if (selectedApplications.value.length === 0) {
      message.error('请至少选择一个项目')
      return
    }
    
    selectedApplications.value.forEach(application => {
      const localType = applicationTypeMap[application.category] || 'research'
      const localProject = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        name: application.title || '未命名项目',
        type: localType,
        score: parseFloat(application.bonus_points || application.estimated_score || 0)
      }
      localProjects.value.push(localProject)
    })
    
    message.success(`成功添加${selectedApplications.value.length}个项目`)
    saveProjects()
    showAddFromApplicationModal.value = false
    selectedApplications.value = []
  } catch (error) {
    console.error('添加项目失败:', error)
    message.error('添加项目失败')
  }
}

// 处理从申请中选择弹窗取消
const handleApplicationModalCancel = () => {
  showAddFromApplicationModal.value = false
  selectedApplications.value = []
}

// 编辑项目
const editProject = (record) => {
  message.info('编辑功能暂未实现')
}

// 删除项目
const deleteProject = (id) => {
  localProjects.value = localProjects.value.filter(project => project.id !== id)
  saveProjects()
  message.success('项目已删除')
}

// 加载数据
onMounted(() => {
  loadProjects()
  fetchUserInfo()
})
</script>

<style scoped>
.local-estimation {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.score-summary {
  margin-bottom: 20px;
}

.total-score {
  font-size: 48px;
  font-weight: bold;
  color: #1890ff;
  text-align: center;
}

.score-explanation {
  text-align: center;
  color: #666;
  margin-top: 10px;
}

.project-list {
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}
</style>