<template>
  <div class="application-category">
    <div class="page-header">
      <a-row :gutter="[16, 16]">
        <a-col :span="20">
          <h2>{{ currentCategory.label }} 申请管理</h2>
          <p>管理该分类下的所有学生申请</p>
        </a-col>
        <a-col :span="4" style="text-align: right;">
          <a-button type="primary" @click="backToMain">
            <a-icon type="arrow-left" /> 返回分类列表
          </a-button>
        </a-col>
      </a-row>
    </div>
    
    <!-- 筛选条件 -->
    <div class="filter-section">
      <a-card>
        <a-row :gutter="[16, 16]">
          <a-col :span="8">
            <a-select v-model:value="filterForm.teacherId" placeholder="选择教师">
              <a-select-option value="">全部教师</a-select-option>
              <a-select-option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                {{ teacher.name }} - {{ teacher.department }}
              </a-select-option>
            </a-select>
          </a-col>
          <a-col :span="8">
            <a-select v-model:value="filterForm.classId" placeholder="选择班级">
              <a-select-option value="">全部班级</a-select-option>
              <a-select-option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                {{ classItem.name }}
              </a-select-option>
            </a-select>
          </a-col>
          <a-col :span="8">
            <a-select v-model:value="filterForm.status" placeholder="申请状态">
              <a-select-option value="">全部状态</a-select-option>
              <a-select-option value="pending">待审批</a-select-option>
              <a-select-option value="approved">已通过</a-select-option>
              <a-select-option value="rejected">已拒绝</a-select-option>
            </a-select>
          </a-col>
        </a-row>
      </a-card>
    </div>
    
    <!-- 申请列表 -->
    <div class="table-section">
      <a-card title="申请列表">
        <a-table
          :columns="columns"
          :data-source="filteredApplications"
          :pagination="{ pageSize: 10, showSizeChanger: true }"
          row-key="id"
          :scroll="{ x: 1200 }"
          :loading="loading"
        >
          <!-- 状态列渲染 -->
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <a-tag
                :color="record.status === 'pending' ? 'orange' : record.status === 'approved' ? 'green' : 'red'"
              >
                {{ record.status === 'pending' ? '待审批' : record.status === 'approved' ? '已通过' : '已拒绝' }}
              </a-tag>
            </template>
            <!-- 材料列渲染 -->
            <template v-else-if="column.key === 'materials'">
              <a-space>
                <a-button
                  v-for="material in record.materials"
                  :key="material.id"
                  type="link"
                  @click="previewMaterial(material)"
                  size="small"
                >
                  {{ material.name }}
                </a-button>
              </a-space>
            </template>
            <!-- 操作列渲染 -->
            <template v-else-if="column.key === 'actions'">
              <a-space>
                <!-- 待审批状态的操作 -->
                <a-button
                  v-if="record.status === 'pending'"
                  type="primary"
                  size="small"
                  @click="handleApprove(record)"
                >
                  审批通过
                </a-button>
                <a-button
                  v-if="record.status === 'pending'"
                  danger
                  size="small"
                  @click="handleReject(record)"
                >
                  拒绝
                </a-button>
                <!-- 已通过状态的操作 -->
                <a-button
                  v-if="record.status === 'approved'"
                  type="default"
                  size="small"
                  @click="handleEditApproved(record)"
                >
                  编辑
                </a-button>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>
    
    <!-- 审批通过模态框 -->
    <a-modal
      v-model:open="approveModalVisible"
      title="审批通过申请"
      @ok="handleConfirmApprove"
      @cancel="handleCancelApprove"
      ok-text="确认"
      cancel-text="取消"
    >
      <a-form :model="approveForm" layout="vertical">
        <a-form-item label="学生姓名">
          <a-input disabled :value="selectedApplication?.studentName" />
        </a-form-item>
        <a-form-item label="项目名称">
          <a-input disabled :value="selectedApplication?.projectName" />
        </a-form-item>
        <a-form-item label="申请分数">
          <a-input-number disabled :value="selectedApplication?.appliedScore" />
        </a-form-item>
        <a-form-item label="审批分数" required>
          <a-input-number
            v-model:value="approveForm.score"
            :min="0"
            :step="0.5"
            placeholder="输入审批分数"
          />
        </a-form-item>
        <a-form-item label="审批意见">
          <a-textarea
            v-model:value="approveForm.comment"
            placeholder="输入审批意见（可选）"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 拒绝申请模态框 -->
    <a-modal
      v-model:open="rejectModalVisible"
      title="拒绝申请"
      @ok="handleConfirmReject"
      @cancel="handleCancelReject"
      ok-text="确认"
      cancel-text="取消"
    >
      <a-form :model="rejectForm" layout="vertical">
        <a-form-item label="学生姓名">
          <a-input disabled :value="selectedApplication?.studentName" />
        </a-form-item>
        <a-form-item label="项目名称">
          <a-input disabled :value="selectedApplication?.projectName" />
        </a-form-item>
        <a-form-item label="拒绝理由" required>
          <a-textarea
            v-model:value="rejectForm.reason"
            placeholder="请输入拒绝理由"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 编辑已通过申请模态框 -->
    <a-modal
      v-model:open="editApprovedModalVisible"
      title="编辑已通过申请"
      @ok="handleConfirmEditApproved"
      @cancel="handleCancelEditApproved"
      ok-text="确认"
      cancel-text="取消"
    >
      <a-form :model="editApprovedForm" :rules="editApprovedFormRules" ref="editApprovedFormRef" layout="vertical">
        <a-form-item label="学生姓名">
          <a-input disabled :value="selectedApplication?.studentName" />
        </a-form-item>
        <a-form-item label="原项目名称">
          <a-input disabled :value="selectedApplication?.projectName" />
        </a-form-item>
        <a-form-item label="原审批分数">
          <a-input-number disabled :value="selectedApplication?.score" />
        </a-form-item>
        <a-form-item name="newProjectName" label="新项目名称" required>
          <a-input
            v-model:value="editApprovedForm.newProjectName"
            placeholder="输入新项目名称"
          />
        </a-form-item>
        <a-form-item name="newScore" label="新审批分数" required>
          <a-input-number
            v-model:value="editApprovedForm.newScore"
            :min="0"
            :step="0.5"
            placeholder="输入新审批分数"
          />
        </a-form-item>
        <a-form-item name="editReason" label="编辑理由" required>
          <a-textarea
            v-model:value="editApprovedForm.editReason"
            placeholder="请输入编辑理由"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { Modal, Form, Input, InputNumber, Textarea, Button, Select, Table, Tag, Space, Card, Row, Col } from 'ant-design-vue'
import { ArrowLeftOutlined } from '@ant-design/icons-vue'
import api from '../../utils/api'

const router = useRouter()
const route = useRoute()

// 项目分类定义
const projectCategories = [
  { value: 'english', label: '英语成绩', limit: null },
  { value: 'academic', label: '科研成果', limit: null },
  { value: 'comprehensive', label: '综合项目', limit: null }
]

// 获取当前分类
const currentCategory = computed(() => {
  const categoryValue = route.params.category
  return projectCategories.find(cat => cat.value === categoryValue) || { value: categoryValue, label: categoryValue, limit: null }
})

// 状态管理
const applications = ref([])
const teachers = ref([])
const classes = ref([])
const loading = ref(false)

// 筛选表单
const filterForm = ref({
  teacherId: '',
  classId: '',
  status: ''
})

// 模态框状态
const approveModalVisible = ref(false)
const rejectModalVisible = ref(false)
const editApprovedModalVisible = ref(false)

// 表单数据
const selectedApplication = ref(null)
const approveForm = ref({
  score: null,
  comment: ''
})
const rejectForm = ref({
  reason: ''
})
const editApprovedForm = ref({
  newProjectName: '',
  newScore: null,
  editReason: ''
})

// 表单验证规则
const editApprovedFormRules = {
  newProjectName: [
    { required: true, message: '请输入新项目名称', trigger: 'blur' }
  ],
  newScore: [
    { required: true, message: '请输入新审批分数', trigger: 'blur' },
    { type: 'number', min: 0, message: '分数不能为负数', trigger: 'blur' }
  ],
  editReason: [
    { required: true, message: '请输入编辑理由', trigger: 'blur' }
  ]
}

// 表单引用
const editApprovedFormRef = ref(null)

// 表格列配置
const columns = [
  { title: '申请ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '学生姓名', dataIndex: 'studentName', key: 'studentName', width: 120 },
  { title: '学号', dataIndex: 'studentId', key: 'studentId', width: 120 },
  { title: '班级', dataIndex: 'className', key: 'className', width: 150 },
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

// 筛选后的申请列表
const filteredApplications = computed(() => {
  return (applications.value.data || []).filter(app => {
    let match = true
    
    if (filterForm.value.teacherId) {
      match = match && app.teacherId === filterForm.value.teacherId
    }
    
    if (filterForm.value.classId) {
      match = match && app.classId === filterForm.value.classId
    }
    
    if (filterForm.value.status) {
      match = match && app.status === filterForm.value.status
    }
    
    // 只显示当前分类的申请
    match = match && app.category === currentCategory.value.value
    
    return match
  })
})

// 获取申请列表
const fetchApplications = async () => {
  try {
    loading.value = true
    const params = {
      ...filterForm.value,
      category: currentCategory.value.value
    }
    const data = await api.admin.getApplications(params)
    applications.value = data
  } catch (error) {
    message.error('获取申请列表失败: ' + (error.response?.data?.message || error.message))
    applications.value = { data: [] }
  } finally {
    loading.value = false
  }
}

// 获取教师列表
const fetchTeachers = async () => {
  try {
    const data = await api.admin.getTeachers()
    teachers.value = data
  } catch (error) {
    message.error('获取教师列表失败: ' + (error.response?.data?.message || error.message))
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

// 返回分类列表页面
const backToMain = () => {
  const query = route.query.status ? { status: route.query.status } : {}
  router.push({
    path: '/admin/applications',
    query
  })
}

// 预览材料
const previewMaterial = (material) => {
  message.info(`预览材料: ${material.name}`)
}

// 审批通过
const handleApprove = (record) => {
  selectedApplication.value = record
  approveForm.value = {
    score: record.appliedScore, // 默认使用申请分数
    comment: ''
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
    newProjectName: record.projectName,
    newScore: record.score,
    editReason: ''
  }
  editApprovedModalVisible.value = true
}

// 确认审批通过
const handleConfirmApprove = async () => {
  if (!selectedApplication.value) return
  
  try {
    await api.admin.approveApplication(selectedApplication.value.id, {
      score: approveForm.value.score,
      comment: approveForm.value.comment
    })
    
    // 更新本地数据
    const index = applications.value.findIndex(app => app.id === selectedApplication.value.id)
    if (index !== -1) {
      applications.value[index] = {
        ...applications.value[index],
        score: approveForm.value.score,
        status: 'approved',
        reviewedAt: new Date().toISOString().slice(0, 19).replace('T', ' ')
      }
    }
    
    approveModalVisible.value = false
    resetApproveForm()
    message.success('申请已批准')
  } catch (error) {
    message.error('审批失败: ' + (error.response?.data?.message || error.message))
  }
}

// 取消审批通过
const handleCancelApprove = () => {
  approveModalVisible.value = false
  resetApproveForm()
}

// 重置审批表单
const resetApproveForm = () => {
  selectedApplication.value = null
  approveForm.value = {
    score: null,
    comment: ''
  }
}

// 确认拒绝申请
const handleConfirmReject = async () => {
  if (!selectedApplication.value) return
  if (!rejectForm.value.reason) {
    message.error('请输入拒绝理由')
    return
  }
  
  try {
    await api.admin.rejectApplication(selectedApplication.value.id, {
      reason: rejectForm.value.reason
    })
    
    // 更新本地数据
    const index = applications.value.findIndex(app => app.id === selectedApplication.value.id)
    if (index !== -1) {
      applications.value[index] = {
        ...applications.value[index],
        status: 'rejected',
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

// 取消拒绝申请
const handleCancelReject = () => {
  rejectModalVisible.value = false
  resetRejectForm()
}

// 重置拒绝表单
const resetRejectForm = () => {
  selectedApplication.value = null
  rejectForm.value = {
    reason: ''
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
    
    // 更新本地数据
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

// 取消编辑已通过申请
const handleCancelEditApproved = () => {
  editApprovedModalVisible.value = false
  resetEditApprovedForm()
}

// 重置编辑已通过表单
const resetEditApprovedForm = () => {
  selectedApplication.value = null
  editApprovedForm.value = {
    newProjectName: '',
    newScore: null,
    editReason: ''
  }
  if (editApprovedFormRef.value) {
    editApprovedFormRef.value.resetFields()
  }
}

// 监听分类变化
watch(() => route.params.category, () => {
  fetchApplications()
})

// 监听路由参数变化
watch(() => route.query.status, (newStatus) => {
  if (newStatus) {
    filterForm.value.status = newStatus
  }
})

onMounted(() => {
  fetchApplications()
  fetchTeachers()
  fetchClasses()
  // 初始化状态筛选
  if (route.query.status) {
    filterForm.value.status = route.query.status
  }
})
</script>

<style scoped>
.application-category {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #262626;
}

.page-header p {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

.filter-section {
  margin-bottom: 24px;
}

.table-section {
  margin-bottom: 24px;
}
</style>