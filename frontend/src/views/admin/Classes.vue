<template>
  <div class="admin-classes">
    <h2>班级管理</h2>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <a-button type="primary" @click="handleAddClass">添加班级</a-button>
      <a-upload
        name="file"
        :multiple="false"
        :before-upload="handleBeforeUpload"
        accept=".xlsx, .xls"
      >
        <a-button>
          <UploadOutlined /> 导入Excel
        </a-button>
      </a-upload>
      <a-button @click="handleExport">导出Excel</a-button>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-section">
      <a-row :gutter="[16, 16]">
        <a-col :span="12">
          <a-input
            v-model:value="searchKeyword"
            placeholder="搜索班级名称"
            prefix="🔍"
            @pressEnter="handleSearch"
          />
        </a-col>
      </a-row>
      <div class="search-actions">
        <a-button @click="handleSearch">搜索</a-button>
        <a-button @click="handleReset">重置</a-button>
      </div>
    </div>

    <!-- 班级列表 -->
    <a-card class="classes-list">
      <!-- 加载中状态 -->
      <div v-if="loading" class="table-loading">
        <a-spin size="large" tip="加载中..." />
      </div>
      
      <!-- 加载失败状态 -->
      <div v-else-if="error" class="table-error">
        <a-empty description="加载失败，请重新加载">
          <template #footer>
            <a-button type="primary" @click="fetchClasses">重新加载</a-button>
          </template>
        </a-empty>
      </div>
      
      <!-- 加载成功但无数据状态 -->
      <div v-else-if="filteredClasses.length === 0" class="table-empty">
        <a-empty description="暂无该数据" />
      </div>
      
      <!-- 正常数据展示 -->
      <a-table
        v-else
        :columns="columns"
        :data-source="filteredClasses"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
        :scroll="{ x: 1000 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button 
                type="primary" 
                size="small" 
                @click="handleViewClass(record)"
              >
                查看
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleEditClass(record)"
              >
                编辑
              </a-button>
              <a-button 
                danger 
                size="small" 
                @click="handleDeleteClass(record)"
              >
                删除
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleManageStudents(record)"
              >
                管理学生
              </a-button>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑班级模态框 -->
    <a-modal
      v-model:open="classModalVisible"
      :title="classModalTitle"
      @ok="handleConfirmClass"
      @cancel="handleCancelClass"
    >
      <a-form
        :model="classForm"
        :rules="classFormRules"
        ref="classFormRef"
        layout="vertical"
      >
        <a-form-item label="班级名称" name="name">
          <a-input v-model:value="classForm.name" placeholder="请输入班级名称" />
        </a-form-item>
        <a-form-item label="年级" name="grade">
          <a-select v-model:value="classForm.grade" placeholder="请选择年级">
            <a-select-option v-for="year in getGradeOptions" :key="year" :value="year">
              {{ year }}级
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="学院" name="college_id">
          <a-select 
            v-model:value="classForm.college_id" 
            placeholder="请选择学院" 
            :options="collegeOptions"
            show-search
            option-filter-prop="label"
          >
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 班级详情模态框 -->
    <a-modal
      v-model:open="viewClassModalVisible"
      title="班级详情"
      @ok="handleCloseViewModal"
      @cancel="handleCloseViewModal"
      width="800px"
    >
      <div v-if="selectedClass" class="class-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="班级名称">{{ selectedClass.name }}</a-descriptions-item>
          <a-descriptions-item label="年级">{{ selectedClass.grade }}级</a-descriptions-item>
          <a-descriptions-item label="学院">{{ selectedClass.college?.name || selectedClass.college || '未分配学院' }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ formatDate(selectedClass.created_at) }}</a-descriptions-item>
        </a-descriptions>
        
        <h3 style="margin-top: 20px;">班级学生</h3>
        <a-table
          :columns="studentColumns"
          :data-source="selectedClassStudents"
          :pagination="{ pageSize: 5 }"
          :row-key="record => record.id"
          style="margin-top: 10px;"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'student_id'">
              {{ record.student_id }}
            </template>
            <template v-else-if="column.key === 'name'">
              {{ record.name }}
            </template>
            <template v-else-if="column.key === 'gender'">
              {{ record.gender === 'male' ? '男' : '女' }}
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>

    <!-- 管理学生模态框 -->
    <a-modal
      v-model:open="manageStudentsModalVisible"
      title="管理班级学生"
      @cancel="handleCloseManageStudentsModal"
      width="800px"
    >
      <div v-if="selectedClass" class="manage-students">
        <h3>班级：{{ selectedClass.name }}</h3>
        
        <!-- 班级学生列表 -->
        <h4>班级学生列表</h4>
        <a-table
          :columns="classStudentColumns"
          :data-source="selectedClassStudents"
          :pagination="{ pageSize: 10 }"
          :row-key="record => record.id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'actions'">
              <a-button type="link" danger @click="handleRemoveStudentFromClass(record)">移除</a-button>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { message, Modal, notification } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import api from '@/utils/api'
import websocketClient from '@/utils/websocket'

// 数据
const classes = ref([])
const colleges = ref([]) // 学院列表
const searchKeyword = ref('')
const loading = ref(false)
const error = ref(false)

// 模态框状态
const classModalVisible = ref(false)
const viewClassModalVisible = ref(false)
const manageStudentsModalVisible = ref(false)
const classModalTitle = ref('添加班级')
const selectedClassId = ref(null)
const selectedClass = ref(null)

// 表单数据
const classForm = ref({
  name: '',
  grade: '',
  college_id: '' // 改为college_id存储学院ID
})

// 学生管理相关
const selectedClassStudents = ref([])

// 表单引用
const classFormRef = ref(null)

// 表单验证规则
const classFormRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  college_id: [{ required: true, message: '请选择学院', trigger: 'change' }] // 修改验证规则
}

// 表格列配置
const columns = [
  { title: '班级名称', dataIndex: 'name', key: 'name' },
  { title: '年级', dataIndex: 'grade', key: 'grade' },
  { 
    title: '学院', 
    dataIndex: 'college', 
    key: 'college',
    // 添加自定义渲染，确保只显示学院名称
    customRender: ({ text }) => {
      return text?.name || text || '未分配学院'
    }
  },
  { title: '操作', key: 'actions', fixed: 'right', width: 200 }
]

// 学生表格列配置
const studentColumns = [
  { title: '学号', dataIndex: 'student_id', key: 'student_id' },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '性别', dataIndex: 'gender', key: 'gender' }
]

// 班级学生表格列配置
const classStudentColumns = [
  { 
    title: '学号', 
    dataIndex: 'student_id', 
    key: 'student_id',
    // 添加自定义渲染，确保学号显示正确
    customRender: ({ text, record }) => {
      return text || record.school_id || ''
    }
  },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { 
    title: '性别', 
    dataIndex: 'gender', 
    key: 'gender',
    // 添加自定义渲染，将英文性别转换为中文
    customRender: ({ text }) => {
      return text === 'male' ? '男' : text === 'female' ? '女' : text || ''
    }
  },
  { 
    title: '综测成绩', 
    dataIndex: 'total_score', 
    key: 'total_score',
    // 添加自定义渲染，确保成绩显示正确
    customRender: ({ text }) => {
      return text || 0
    }
  },
  { 
    title: '上一次登录时间', 
    dataIndex: 'last_login', 
    key: 'last_login',
    // 添加自定义渲染，格式化日期
    customRender: ({ text }) => {
      if (!text) return '从未登录'
      return new Date(text).toLocaleString('zh-CN')
    }
  }
]

// 获取年级选项
const getGradeOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  // 生成近10年的年级选项
  for (let i = currentYear - 9; i <= currentYear; i++) {
    years.push(i)
  }
  return years
})

// 学院选择器选项
const collegeOptions = computed(() => {
  return colleges.value.map(college => ({
    label: college.name,
    value: college.id
  }))
})

// 筛选后的班级列表
const filteredClasses = computed(() => {
  if (!searchKeyword.value) {
    return classes.value || []
  }
  return (classes.value || []).filter(cls => 
    cls.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 获取班级列表
const fetchClasses = async () => {
  try {
    loading.value = true
    error.value = false
    const response = await api.admin.classes.getClasses()
    // 响应拦截器会直接返回class_list数组，所以直接使用response
    classes.value = response || []
  } catch (err) {
    message.error('获取班级列表失败: ' + (err.response?.data?.message || err.message))
    error.value = true
    classes.value = []
  } finally {
    loading.value = false
  }
}

// 获取学院列表
const fetchColleges = async () => {
  try {
    const response = await api.admin.getColleges()
    // 处理不同的响应格式
    if (Array.isArray(response)) {
      colleges.value = response
    } else if (response?.colleges) {
      colleges.value = response.colleges
    } else if (response?.data) {
      colleges.value = response.data
    } else {
      colleges.value = []
    }
  } catch (err) {
    message.error('获取学院列表失败: ' + (err.response?.data?.message || err.message))
    colleges.value = []
  }
}

// 搜索
const handleSearch = () => {
  fetchClasses()
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
  fetchClasses()
}

// 添加班级
const handleAddClass = () => {
  classModalTitle.value = '添加班级'
  selectedClassId.value = null
  resetClassForm()
  // 确保学院列表已加载
  if (colleges.value.length === 0) {
    fetchColleges()
  }
  classModalVisible.value = true
}

// 编辑班级
const handleEditClass = (record) => {
  classModalTitle.value = '编辑班级'
  selectedClassId.value = record.id
  classForm.value = {
    name: record.name,
    grade: record.grade,
    college_id: record.college_id || record.college // 处理可能的不同字段名
  }
  // 确保学院列表已加载
  if (colleges.value.length === 0) {
    fetchColleges()
  }
  classModalVisible.value = true
}

// 查看班级
const handleViewClass = async (record) => {
  try {
    selectedClass.value = record
    // 获取班级学生
    await fetchClassStudents(record.id)
    viewClassModalVisible.value = true
  } catch (err) {
    message.error('获取班级详情失败: ' + (err.response?.data?.message || err.message))
  }
}

// 管理班级学生
const handleManageStudents = async (record) => {
  try {
    selectedClass.value = record
    // 获取班级学生
    await fetchClassStudents(record.id)
    manageStudentsModalVisible.value = true
  } catch (err) {
    message.error('加载学生数据失败: ' + (err.response?.data?.message || err.message))
  }
}

// 删除班级
const handleDeleteClass = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除班级 "${record.name}" 吗？删除后该班级的所有绑定关系也将被删除。`,
    onOk: async () => {
      try {
        await api.admin.classes.deleteClass(record.id)
        message.success('班级删除成功')
        fetchClasses()
      } catch (err) {
        message.error('班级删除失败: ' + (err.response?.data?.message || err.message))
      }
    }
  })
}

// 确认添加/编辑班级
const handleConfirmClass = async () => {
      if (!classFormRef.value) return
      
      try {
        await classFormRef.value.validate()
        
        // 准备提交数据（使用college字段）
        const data = {
          name: classForm.value.name,
          grade: classForm.value.grade,
          college: classForm.value.college_id
        }
        
        if (selectedClassId.value) {
          // 更新班级
          await api.admin.classes.updateClass(selectedClassId.value, data)
          message.success('班级信息更新成功')
        } else {
          // 添加班级
          await api.admin.classes.createClass(data)
          message.success('班级添加成功')
        }
    
    // 关闭模态框并刷新列表
    classModalVisible.value = false
    fetchClasses()
  } catch (error) {
    if (error.errorFields) {
      // 表单验证错误，已由Ant Design处理
      return
    }
    message.error('操作失败: ' + (error.response?.data?.message || error.message))
  }
}

// 取消添加/编辑班级
const handleCancelClass = () => {
  classModalVisible.value = false
  resetClassForm()
}

// 关闭查看班级模态框
const handleCloseViewModal = () => {
  viewClassModalVisible.value = false
  selectedClass.value = null
  selectedClassStudents.value = []
}

// 关闭管理学生模态框
const handleCloseManageStudentsModal = () => {
  manageStudentsModalVisible.value = false
  selectedClass.value = null
  selectedClassStudents.value = []
}

// 重置添加/编辑班级表单
const resetClassForm = () => {
  classForm.value = {
    name: '',
    grade: '',
    college_id: '' // 更新为college_id
  }
  if (classFormRef.value) {
    classFormRef.value.resetFields()
  }
}

// 获取班级学生
const fetchClassStudents = async (classId) => {
  try {
    const data = await api.admin.classes.getClassStudents(classId)
    // 确保selectedClassStudents总是数组，处理不同的数据结构
    selectedClassStudents.value = Array.isArray(data) ? data : 
                               data?.students || 
                               data?.data || 
                               data?.results || []
  } catch (err) {
    message.error('获取班级学生失败: ' + (err.response?.data?.message || err.message))
    selectedClassStudents.value = []
  }
}

// 导出Excel
const handleExport = () => {
  message.info('导出功能开发中...')
}

// 上传Excel前的处理
const handleBeforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    message.error('请选择Excel文件!')
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    message.error('文件大小不能超过2MB!')
  }
  return isExcel && isLt2M
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 生命周期钩子
onMounted(() => {
  fetchClasses()
  fetchColleges()
  
  // 连接WebSocket
  connectWebSocket()
})

onUnmounted(() => {
  // 断开WebSocket连接
  disconnectWebSocket()
})

// 连接WebSocket
function connectWebSocket() {
  // 连接WebSocket服务器
  websocketClient.connect()
  
  // 注册事件监听器
  websocketClient.on('connected', handleWebSocketConnected)
  websocketClient.on('disconnected', handleWebSocketDisconnected)
  websocketClient.on('error', handleWebSocketError)
  websocketClient.on('class_binding_changed', handleClassBindingChanged)
  websocketClient.on('student_class_changed', handleStudentClassChanged)
}

// 断开WebSocket连接
function disconnectWebSocket() {
  // 移除事件监听器
  websocketClient.off('connected', handleWebSocketConnected)
  websocketClient.off('disconnected', handleWebSocketDisconnected)
  websocketClient.off('error', handleWebSocketError)
  websocketClient.off('class_binding_changed', handleClassBindingChanged)
  websocketClient.off('student_class_changed', handleStudentClassChanged)
  
  // 断开连接
  websocketClient.disconnect()
}

// WebSocket连接成功处理函数
function handleWebSocketConnected() {
  console.log('WebSocket连接成功')
  notification.success({
    message: 'WebSocket连接成功',
    description: '班级与辅导员分配关系将实时更新',
    placement: 'topRight'
  })
}

// WebSocket连接断开处理函数
function handleWebSocketDisconnected() {
  console.log('WebSocket连接断开')
  notification.warning({
    message: 'WebSocket连接断开',
    description: '实时更新功能已暂停',
    placement: 'topRight'
  })
}

// WebSocket错误处理函数
function handleWebSocketError(error) {
  console.error('WebSocket错误:', error)
  notification.error({
    message: 'WebSocket错误',
    description: '实时更新功能异常',
    placement: 'topRight'
  })
}

// 班级绑定关系变更处理函数
function handleClassBindingChanged(data) {
  console.log('班级绑定关系变更:', data)
  
  // 重新获取班级列表以更新分配关系
  fetchClasses()
  
  // 显示通知
  const actionText = data.action === 'created' ? '添加' : 
                     data.action === 'updated' ? '更新' : '删除'
  
  notification.info({
    message: '班级分配关系已更新',
    description: `班级ID: ${data.class_id} ${actionText}了辅导员分配`,
    placement: 'topRight'
  })
}

// 学生班级变更处理函数
function handleStudentClassChanged(data) {
  console.log('学生班级变更:', data)
  
  // 重新获取班级列表以更新学生分配情况
  fetchClasses()
  
  // 如果当前正在查看该班级的学生列表，也需要更新
  if (selectedClass.value && selectedClass.value.id === data.class_id) {
    fetchClassStudents(data.class_id)
  }
  
  // 显示通知
  notification.info({
    message: '学生分配情况已更新',
    description: `学生ID: ${data.student_id}的班级变更导致辅导员分配更新`,
    placement: 'topRight'
  })
}
</script>

<style scoped>
.admin-classes {
  padding: 20px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.search-section {
  margin-bottom: 20px;
}

.search-actions {
  margin-top: 10px;
}

.classes-list {
  margin-bottom: 20px;
  min-height: 300px;
  position: relative;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

/* 表格状态样式 */
.table-loading,
.table-error,
.table-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 0;
}

.class-detail {
  margin-top: 10px;
}

.manage-students {
  margin-top: 10px;
}
</style>