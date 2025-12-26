<template>
  <div class="admin-applications">
    <h2>学生材料申请管理</h2>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <a-button type="primary" @click="handleRefresh">刷新</a-button>
      <a-button @click="handleExport">导出Excel</a-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <a-row :gutter="[16, 16]">
        <a-col :span="6">
          <a-select v-model:value="filterForm.teacherId" placeholder="选择教师">
            <a-select-option value="">全部教师</a-select-option>
            <a-select-option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
              {{ teacher.name }} - {{ teacher.department }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="filterForm.classId" placeholder="选择班级">
            <a-select-option value="">全部班级</a-select-option>
            <a-select-option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.name }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="filterForm.status" placeholder="申请状态">
            <a-select-option value="">全部状态</a-select-option>
            <a-select-option value="pending">待审批</a-select-option>
            <a-select-option value="approved">已通过</a-select-option>
            <a-select-option value="rejected">已拒绝</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="filterForm.category" placeholder="项目分类">
            <a-select-option value="">全部分类</a-select-option>
            <a-select-option v-for="category in projectCategories" :key="category.value" :value="category.value">
              {{ category.label }}
            </a-select-option>
          </a-select>
        </a-col>
      </a-row>
    </div>

    <!-- 申请列表 -->
    <a-card class="applications-list">
      <!-- 加载中状态 -->
      <div v-if="loading" class="list-empty-state">
        <a-spin size="large" />
        <p>加载中...</p>
      </div>
      
      <!-- 加载失败状态 -->
      <div v-else-if="error" class="list-empty-state error-state">
        <a-alert
          message="获取数据失败"
          description="无法加载申请列表，请检查网络连接或稍后重试。"
          type="error"
          show-icon
          style="margin-bottom: 16px"
        />
        <a-button type="primary" @click="fetchApplications">重新加载</a-button>
      </div>
      
      <!-- 加载成功但数据为空的状态 -->
      <div v-else-if="filteredApplications.length === 0" class="list-empty-state">
        <a-empty description="暂无该数据" />
      </div>
      
      <!-- 正常显示表格 -->
      <a-table
        v-else
        :columns="columns"
        :data-source="filteredApplications"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
        :scroll="{ x: 1000 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'materials'">
            <div class="materials-list">
              <a-tag v-for="material in record.materials" :key="material.id" color="blue">
                {{ material.name }}
              </a-tag>
            </div>
          </template>
          <template v-else-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button 
                type="primary" 
                size="small" 
                @click="handleApprove(record)" 
                v-if="record.status === 'pending'"
              >
                通过
              </a-button>
              <a-button 
                danger 
                size="small" 
                @click="handleReject(record)" 
                v-if="record.status === 'pending'"
              >
                拒绝
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleEditApproved(record)" 
                v-if="record.status === 'approved'"
              >
                编辑
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleViewDetail(record)"
              >
                查看详情
              </a-button>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 审批模态框 -->
    <a-modal
      v-model:open="approveModalVisible"
      title="审批申请"
      @ok="handleConfirmApprove"
      @cancel="resetApproveForm"
    >
      <a-form :model="approveForm" layout="vertical" :rules="approveRules" ref="approveFormRef">
        <a-form-item label="申请信息">
          <div>
            <p><strong>学生:</strong> {{ selectedApplication?.studentName }}</p>
            <p><strong>班级:</strong> {{ selectedApplication?.className }}</p>
            <p><strong>项目:</strong> {{ selectedApplication?.projectName }}</p>
            <p><strong>申请时间:</strong> {{ selectedApplication?.appliedAt }}</p>
          </div>
        </a-form-item>
        <a-form-item label="审批分数" name="score">
          <a-input-number v-model:value="approveForm.score" :min="0" :max="100" style="width: 100%" />
        </a-form-item>
        <a-form-item label="审批备注" name="remark">
          <a-textarea v-model:value="approveForm.remark" placeholder="请输入审批备注" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 拒绝模态框 -->
    <a-modal
      v-model:open="rejectModalVisible"
      title="拒绝申请"
      @ok="handleConfirmReject"
      @cancel="resetRejectForm"
    >
      <a-form :model="rejectForm" layout="vertical" :rules="rejectRules" ref="rejectFormRef">
        <a-form-item label="申请信息">
          <div>
            <p><strong>学生:</strong> {{ selectedApplication?.studentName }}</p>
            <p><strong>班级:</strong> {{ selectedApplication?.className }}</p>
            <p><strong>项目:</strong> {{ selectedApplication?.projectName }}</p>
          </div>
        </a-form-item>
        <a-form-item label="拒绝理由" name="reason">
          <a-textarea v-model:value="rejectForm.reason" placeholder="请输入拒绝理由" :rows="4" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑已通过申请模态框 -->
    <a-modal
      v-model:open="editApprovedModalVisible"
      title="编辑已通过申请"
      @ok="handleConfirmEditApproved"
      @cancel="resetEditApprovedForm"
      width="600px"
    >
      <a-form :model="editApprovedForm" layout="vertical" :rules="editApprovedRules" ref="editApprovedFormRef">
        <a-form-item label="原始申请信息">
          <div>
            <p><strong>学生:</strong> {{ selectedApplication?.studentName }}</p>
            <p><strong>班级:</strong> {{ selectedApplication?.className }}</p>
            <p><strong>原项目:</strong> {{ selectedApplication?.projectName }}</p>
            <p><strong>原分数:</strong> {{ selectedApplication?.score }}</p>
          </div>
        </a-form-item>
        <a-form-item label="新项目名称" name="newProjectName">
          <a-input v-model:value="editApprovedForm.newProjectName" placeholder="请输入新项目名称" />
        </a-form-item>
        <a-form-item label="新分数" name="newScore">
          <a-input-number v-model:value="editApprovedForm.newScore" :min="0" :max="100" style="width: 100%" />
        </a-form-item>
        <a-form-item label="编辑原因" name="editReason">
          <a-textarea v-model:value="editApprovedForm.editReason" placeholder="请输入编辑原因" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { message, Modal } from 'ant-design-vue'
import api from '../../utils/api'

// 项目分类定义（用于筛选）
const projectCategories = [
  { value: 'english', label: '英语成绩', limit: null },
  { value: 'academic', label: '科研成果', limit: null },
  { value: 'comprehensive', label: '综合项目', limit: null }
]

// 项目类型映射
const projectTypeMap = {
  'english': '英语成绩',
  'academic': '科研成果',
  'comprehensive': '综合项目'
}

// 获取项目分类文本
const getProjectCategoryText = (category) => {
  return projectTypeMap[category] || category
}

// 状态管理
const applications = ref([])
const teachers = ref([])
const classes = ref([])
const loading = ref(false)
const error = ref(null)
const filterForm = ref({
  teacherId: '',
  classId: '',
  status: '',
  category: ''
})

// 监听筛选条件变化，自动刷新数据
watch(filterForm, () => {
  fetchApplications()
}, { deep: true })

// 模态框状态
const approveModalVisible = ref(false)
const rejectModalVisible = ref(false)
const editApprovedModalVisible = ref(false)
const selectedApplication = ref(null)

// 审批表单
const approveForm = ref({
  score: null,
  remark: ''
})

// 审批表单规则
const approveRules = {
  score: [{ required: true, message: '请输入审批分数', trigger: 'blur' }]
}

// 审批表单引用
const approveFormRef = ref(null)

// 拒绝表单
const rejectForm = ref({
  reason: ''
})

// 拒绝表单规则
const rejectRules = {
  reason: [{ required: true, message: '请输入拒绝理由', trigger: 'blur' }]
}

// 拒绝表单引用
const rejectFormRef = ref(null)

// 编辑已通过申请表单
const editApprovedForm = ref({
  newProjectName: '',
  newScore: null,
  editReason: ''
})

// 编辑已通过申请表单规则
const editApprovedRules = {
  newProjectName: [{ required: true, message: '请输入新项目名称', trigger: 'blur' }],
  newScore: [{ required: true, message: '请输入新分数', trigger: 'blur' }],
  editReason: [{ required: true, message: '请输入编辑原因', trigger: 'blur' }]
}

// 编辑已通过申请表单引用
const editApprovedFormRef = ref(null)

// 表格列配置
const columns = [
  { title: '申请ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '学生姓名', dataIndex: 'studentName', key: 'studentName', width: 120 },
  { title: '学号', dataIndex: 'studentId', key: 'studentId', width: 120 },
  { title: '班级', dataIndex: 'className', key: 'className', width: 150 },
  { 
    title: '项目分类', 
    dataIndex: 'category', 
    key: 'category', 
    width: 120,
    customRender: ({ text }) => getProjectCategoryText(text)
  },
  { title: '项目名称', dataIndex: 'projectName', key: 'projectName', width: 180 },
  { title: '申请分数', dataIndex: 'appliedScore', key: 'appliedScore', width: 100 },
  { title: '审批分数', dataIndex: 'score', key: 'score', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '申请时间', dataIndex: 'appliedAt', key: 'appliedAt', width: 180 },
  { title: '审批时间', dataIndex: 'reviewedAt', key: 'reviewedAt', width: 180 },
  { title: '拒绝理由', dataIndex: 'rejectionReason', key: 'rejectionReason', width: 150 },
  { title: '提交材料', dataIndex: 'materials', key: 'materials', width: 200 },
  { title: '操作', key: 'actions', fixed: 'right', width: 180 }
]

// 直接使用后端返回的筛选后的数据
const filteredApplications = computed(() => {
  return applications.value.data || []
})

// 获取状态颜色
const getStatusColor = (status) => {
  switch (status) {
    case 'pending':
    case 'first_reviewing':
    case 'first_approved':
    case 'second_reviewing':
    case 'second_approved':
    case 'third_reviewing':
      return 'blue'
    case 'approved':
      return 'green'
    case 'rejected':
    case 'first_rejected':
    case 'second_rejected':
    case 'third_rejected':
      return 'red'
    case 'withdrawn':
      return 'gray'
    default:
      return 'default'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'pending':
    case 'first_reviewing':
      return '一审中'
    case 'first_approved':
    case 'second_reviewing':
      return '二审中'
    case 'second_approved':
    case 'third_reviewing':
      return '三审中'
    case 'approved':
      return '审核通过'
    case 'rejected':
    case 'first_rejected':
    case 'second_rejected':
    case 'third_rejected':
      return '审核未通过'
    case 'withdrawn':
      return '已撤回'
    default:
      return status
  }
}

// 刷新申请列表
const handleRefresh = () => {
  fetchApplications()
  message.success('申请列表已刷新')
}

// 导出Excel
const handleExport = () => {
  // 这里应该调用API导出Excel
  message.info('导出功能开发中...')
}

// 审批申请
const handleApprove = (record) => {
  selectedApplication.value = record
  approveForm.value = {
    score: null,
    remark: ''
  }
  approveModalVisible.value = true
}

// 拒绝申请
const handleReject = (record) => {
  selectedApplication.value = record
  rejectForm.value = {
    reason: ''
  }
  rejectModalVisible.value = true
}

// 编辑已通过申请
const handleEditApproved = (record) => {
  selectedApplication.value = record
  editApprovedForm.value = {
    newProjectName: '',
    newScore: null,
    editReason: ''
  }
  editApprovedModalVisible.value = true
}

// 查看详情
const handleViewDetail = (record) => {
  // 这里可以实现查看详情的功能
  message.info('查看详情功能开发中...')
}

// 确认审批
const handleConfirmApprove = async () => {
  if (!approveFormRef.value) return
  
  try {
    await approveFormRef.value.validate()
    
    // 调用API审批申请
    await api.admin.approveApplication(selectedApplication.value.id, {
      score: approveForm.value.score,
      remark: approveForm.value.remark
    })
    
    // 更新本地数据
    const index = applications.value.findIndex(app => app.id === selectedApplication.value.id)
    if (index !== -1) {
      applications.value[index] = {
        ...applications.value[index],
        status: 'approved',
        score: approveForm.value.score,
        reviewedAt: new Date().toISOString().slice(0, 19).replace('T', ' ')
      }
    }
    
    approveModalVisible.value = false
    resetApproveForm()
    message.success('申请已通过')
  } catch (error) {
    message.error('审批失败: ' + (error.response?.data?.message || error.message))
  }
}

// 确认拒绝
const handleConfirmReject = async () => {
  if (!rejectFormRef.value) return
  
  try {
    await rejectFormRef.value.validate()
    
    // 调用API拒绝申请
    await api.admin.rejectApplication(selectedApplication.value.id, {
      reason: rejectForm.value.reason
    })
    
    // 更新本地数据
    const index = applications.value.findIndex(app => app.id === selectedApplication.value.id)
    if (index !== -1) {
      applications.value[index] = {
        ...applications.value[index],
        status: 'rejected',
        score: 0,
        rejectionReason: rejectForm.value.reason,
        reviewedAt: new Date().toISOString().slice(0, 19).replace('T', ' ')
      }
    }
    
    rejectModalVisible.value = false
    resetRejectForm()
    message.success('申请已拒绝')
  } catch (error) {
    message.error('拒绝失败: ' + (error.response?.data?.message || error.message))
  }
}

// 确认编辑已通过申请
const handleConfirmEditApproved = async () => {
  if (!editApprovedFormRef.value) return
  
  try {
    await editApprovedFormRef.value.validate()
    
    // 调用API编辑已通过的申请
    await api.admin.editApprovedApplication(selectedApplication.value.id, {
      newProjectName: editApprovedForm.value.newProjectName,
      newScore: editApprovedForm.value.newScore,
      editReason: editApprovedForm.value.editReason
    })
    
    // 更新本地数据 - 实际应该删除原项目并添加新项目
    // 这里简化处理，直接更新当前项目
    const index = applications.value.findIndex(app => app.id === selectedApplication.value.id)
    if (index !== -1) {
      applications.value[index] = {
        ...applications.value[index],
        projectName: editApprovedForm.value.newProjectName,
        score: editApprovedForm.value.newScore,
        reviewedAt: new Date().toISOString().slice(0, 19).replace('T', ' ')
      }
    }
    
    editApprovedModalVisible.value = false
    resetEditApprovedForm()
    message.success('申请已编辑')
  } catch (error) {
    message.error('编辑失败: ' + (error.response?.data?.message || error.message))
  }
}

// 重置审批表单
const resetApproveForm = () => {
  approveForm.value = {
    score: null,
    remark: ''
  }
  if (approveFormRef.value) {
    approveFormRef.value.resetFields()
  }
}

// 重置拒绝表单
const resetRejectForm = () => {
  rejectForm.value = {
    reason: ''
  }
  if (rejectFormRef.value) {
    rejectFormRef.value.resetFields()
  }
}

// 重置编辑已通过申请表单
const resetEditApprovedForm = () => {
  editApprovedForm.value = {
    newProjectName: '',
    newScore: null,
    editReason: ''
  }
  if (editApprovedFormRef.value) {
    editApprovedFormRef.value.resetFields()
  }
}

// 获取申请列表
const fetchApplications = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await api.admin.getApplications(filterForm.value)
    applications.value = data
  } catch (err) {
    error.value = err
    applications.value = [] // 发生错误时清空列表
    message.error('获取申请列表失败: ' + (err.response?.data?.message || err.message))
  } finally {
    loading.value = false
  }
}

// 获取教师列表
const fetchTeachers = async () => {
  try {
    const response = await api.admin.getTeachers()
    teachers.value = response?.users || []
  } catch (error) {
    message.error('获取教师列表失败: ' + (error.response?.data?.message || error.message))
    teachers.value = []
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await api.admin.classes.getClasses()
    classes.value = response?.classes || []
  } catch (error) {
    message.error('获取班级列表失败: ' + (error.response?.data?.message || error.message))
    classes.value = []
  }
}

onMounted(() => {
  fetchApplications()
  fetchTeachers()
  fetchClasses()
})
</script>

<style scoped>
.admin-applications {
  padding: 0;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.applications-list {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  min-height: 300px;
}

.list-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  text-align: center;
}

.error-state {
  max-width: 500px;
  margin: 0 auto;
}

.materials-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}
</style>