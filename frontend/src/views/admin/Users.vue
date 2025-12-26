<template>
  <div class="admin-users">
    <h2>用户管理</h2>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <a-button type="primary" @click="showAddModal">添加用户</a-button>
      <a-button type="primary" :loading="importLoading">
        <template #icon>
          <UploadOutlined />
        </template>
        导入Excel
        <a-upload
          v-model:fileList="fileList"
          :before-upload="beforeUpload"
          :show-upload-list="false"
          accept=".xlsx,.xls"
        >
        </a-upload>
      </a-button>
      <a-button @click="handleRefresh">刷新</a-button>
    </div>

    <!-- 导入模板下载 -->
    <div class="import-template">
      <a-button type="link" @click="downloadTemplate">下载导入模板</a-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <a-row :gutter="[16, 16]">
        <a-col :span="6">
          <a-select v-model:value="filterForm.userType" placeholder="用户类型">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="student">学生</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="12">
          <a-input v-model:value="filterForm.searchText" placeholder="搜索用户名、姓名或学号/工号" @pressEnter="handleSearch" />
        </a-col>
        <a-col :span="6" style="text-align: right;">
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-col>
      </a-row>
    </div>

    <!-- 用户列表 -->
    <a-card class="users-list" style="margin-top: 20px;">
      <!-- 加载中状态 -->
      <div v-if="loading" class="list-empty-state">
        <a-spin size="large" />
        <p>加载中...</p>
      </div>
      
      <!-- 加载失败状态 -->
      <div v-else-if="error" class="list-empty-state error-state">
        <a-alert
          message="获取数据失败"
          description="无法加载用户列表，请检查网络连接或稍后重试。"
          type="error"
          show-icon
          style="margin-bottom: 16px"
        />
        <a-button type="primary" @click="fetchUsers">重新加载</a-button>
      </div>
      
      <!-- 加载成功但数据为空的状态 -->
      <div v-else-if="filteredUsers.length === 0" class="list-empty-state">
        <a-empty description="暂无该数据" />
      </div>
      
      <!-- 正常显示表格 -->
      <a-table
        v-else
        :columns="columns"
        :data-source="filteredUsers"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'user_type_display'">
    <a-tag :color="record.user_type === 'student' ? 'blue' : record.user_type === 'teacher' ? 'green' : 'red'">
      {{ record.user_type_display }}
    </a-tag>
  </template>
          <template v-else-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button type="link" @click="handleEdit(record)">编辑</a-button>
              <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
              <a-button type="link" @click="handleResetPassword(record)">重置密码</a-button>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加用户模态框 -->
    <a-modal
      v-model:open="addModalVisible"
      title="添加用户"
      @ok="handleConfirmAdd"
      @cancel="resetAddForm"
      width="600px"
    >
      <a-form :model="addForm" layout="vertical" :rules="addRules" ref="addFormRef">
        <a-form-item label="用户类型" name="userType">
          <a-select v-model:value="addForm.userType" placeholder="请选择用户类型">
            <a-select-option value="student">学生</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学生专属字段 -->
        <a-form-item v-if="addForm.userType === 'student'" label="学号（账号）" name="studentId">
          <a-input v-model:value="addForm.studentId" placeholder="请输入学号" />
        </a-form-item>
        
        <!-- 教师专属字段 -->
        <a-form-item v-if="addForm.userType === 'teacher'" label="工号" name="studentId">
          <a-input v-model:value="addForm.studentId" placeholder="请输入工号" />
        </a-form-item>
        
        <!-- 管理员专属字段 -->
        <a-form-item v-if="addForm.userType === 'admin'" label="用户名" name="studentId">
          <a-input v-model:value="addForm.studentId" placeholder="请输入用户名" />
        </a-form-item>
        
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="addForm.name" placeholder="请输入姓名" />
        </a-form-item>
        
        <a-form-item label="性别" name="gender">
          <a-select v-model:value="addForm.gender" placeholder="请选择性别">
            <a-select-option value="male">男</a-select-option>
            <a-select-option value="female">女</a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学院选择 -->
        <a-form-item label="学院" name="department">
          <a-select v-model:value="addForm.department" placeholder="请选择学院">
            <a-select-option v-for="item in colleges" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学生专属字段 -->
        <a-form-item v-if="addForm.userType === 'student'" label="班级" name="class_name">
          <a-select v-model:value="addForm.class_name" placeholder="请选择班级">
            <a-select-option v-for="cls in filteredClasses" :key="cls.id" :value="cls.id">
              {{ cls.name }} ({{ cls.grade }})
            </a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学生专属字段 -->
        <a-form-item v-if="addForm.userType === 'student'" label="平均绩点" name="gpa">
          <a-input-number v-model:value="addForm.gpa" :min="0" :max="5" :step="0.1" placeholder="请输入平均绩点" />
        </a-form-item>
        
        <!-- 教师专属字段 -->
        <a-form-item v-if="addForm.userType === 'teacher'" label="管辖班级（选填）" name="class_ids">
          <a-select
            v-model:value="addForm.class_ids"
            mode="multiple"
            placeholder="请选择班级"
            :options="classes.map(cls => ({ value: cls.id, label: cls.name }))"
          />
        </a-form-item>
        
        <!-- 密码提示 -->
        <a-form-item class="password-tip">
          <p style="color: #999;">密码将自动设置为学号/工号/用户名后六位</p>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑用户模态框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑用户"
      @ok="handleConfirmEdit"
      @cancel="resetEditForm"
      width="600px"
    >
      <a-form :model="editForm" layout="vertical" :rules="editRules" ref="editFormRef">
        <a-form-item label="用户类型" name="userType">
          <a-select v-model:value="editForm.userType" placeholder="请选择用户类型" disabled>
            <a-select-option value="student">学生</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学生专属字段 -->
        <a-form-item v-if="editForm.userType === 'student'" label="学号（账号）" name="studentId">
          <a-input v-model:value="editForm.studentId" placeholder="请输入学号" />
        </a-form-item>
        
        <!-- 教师专属字段 -->
        <a-form-item v-if="editForm.userType === 'teacher'" label="工号" name="studentId">
          <a-input v-model:value="editForm.studentId" placeholder="请输入工号" />
        </a-form-item>
        
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="editForm.name" placeholder="请输入姓名" />
        </a-form-item>
        <a-form-item label="性别" name="gender">
          <a-select v-model:value="editForm.gender" placeholder="请选择性别">
            <a-select-option value="male">男</a-select-option>
            <a-select-option value="female">女</a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学院选择 -->
        <a-form-item label="学院" name="department">
          <a-select v-model:value="editForm.department" placeholder="请选择学院">
            <a-select-option v-for="item in colleges" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 学生专属字段 -->
        <a-form-item v-if="editForm.userType === 'student'" label="班级" name="class_name">
          <a-select v-model:value="editForm.class_name" placeholder="请选择班级">
            <a-select-option v-for="cls in filteredClasses" :key="cls.id" :value="cls.id">
              {{ cls.name }} ({{ cls.grade }})
            </a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 移除年级字段 - 根据新需求，禁止修改学生年级 -->
        
        <!-- 移除专业字段 - 根据需求1 -->
        
        <a-form-item v-if="editForm.userType === 'student'" label="平均绩点" name="gpa">
          <a-input-number v-model:value="editForm.gpa" :min="0" :max="5" :step="0.1" placeholder="请输入平均绩点" />
        </a-form-item>
        
        <!-- 移除职称字段 - 根据需求2 -->
        
        <!-- 教师专属字段 -->
        <a-form-item v-if="editForm.userType === 'teacher'" label="管辖班级（选填）" name="class_ids">
          <a-select
            v-model:value="editForm.class_ids"
            mode="multiple"
            placeholder="请选择班级"
            :options="classes.map(cls => ({ value: cls.id, label: cls.name }))"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 重置密码模态框 -->
    <a-modal
      v-model:open="resetPasswordModalVisible"
      title="重置密码"
      @ok="handleConfirmResetPassword"
      @cancel="resetResetPasswordForm"
    >
      <a-form :model="resetPasswordForm" layout="vertical" :rules="resetPasswordRules" ref="resetPasswordFormRef">
        <a-form-item label="新密码" name="newPassword">
          <a-input-password v-model:value="resetPasswordForm.newPassword" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item label="确认密码" name="confirmPassword">
          <a-input-password v-model:value="resetPasswordForm.confirmPassword" placeholder="请确认新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import * as XLSX from 'xlsx'
import api from '@/utils/api'

// 状态管理
const users = ref([])
const loading = ref(false)
const error = ref(null)
const filterForm = ref({
  userType: '',
  searchText: ''
})

// 获取当前登录用户信息
const currentUser = ref(JSON.parse(localStorage.getItem('user')))

// 模态框状态
const addModalVisible = ref(false)
const editModalVisible = ref(false)
const resetPasswordModalVisible = ref(false)
const selectedUser = ref(null)

// 学院和班级数据
const colleges = ref([])
const classes = ref([])

// 根据选择的学院过滤班级
const filteredClasses = computed(() => {
  if (!editForm.value.department) {
    return classes.value
  }
  return classes.value.filter(cls => cls.college_id === editForm.value.department || cls.college === editForm.value.department)
})

// 获取学院和班级列表
const fetchCollegesAndClasses = async () => {
  try {
    // 获取学院列表
    const collegesResponse = await api.admin.getColleges()
    colleges.value = Array.isArray(collegesResponse) ? collegesResponse : 
                    collegesResponse?.colleges || 
                    collegesResponse?.data || 
                    collegesResponse?.results || []
    
    // 获取班级列表 - 修复调用路径，getClasses方法在admin.classes子对象上
    const classesResponse = await api.admin.classes.getClasses()
    classes.value = Array.isArray(classesResponse) ? classesResponse : 
                   classesResponse?.classes || 
                   classesResponse?.data || 
                   classesResponse?.results || []
  } catch (error) {
    console.error('获取学院和班级列表失败:', error)
  }
}

// 添加表单
const addForm = ref({
  userType: 'student',
  studentId: '', // 学号/工号/管理员用户名
  name: '',
  gender: 'male',
  department: '',
  class_name: '',
  class_ids: [], // 教师管辖班级
  gpa: 0, // 学生平均绩点
  password: '',
  password_confirm: ''
})

// 添加表单验证规则
const addRules = {
  userType: [{ required: true, message: '请选择用户类型', trigger: 'change' }],
  studentId: [{ required: true, message: '请输入学号/工号/用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  department: [{ required: true, message: '请选择学院', trigger: 'change' }],
  // 学生专属规则
  class_name: [
    { 
      required: ({ model }) => model.userType === 'student', 
      message: '请选择班级', 
      trigger: 'change' 
    }
  ],
  gpa: [
    { 
      required: ({ model }) => model.userType === 'student', 
      message: '请输入平均绩点', 
      trigger: 'blur' 
    },
    { 
      type: 'number', 
      min: 0, 
      max: 5, 
      message: '平均绩点应在0-5之间', 
      trigger: 'blur' 
    }
  ]
}

// 添加表单引用
const addFormRef = ref(null)

// 编辑表单
const editForm = ref({
  userType: 'student',
  username: '',
  name: '',
  studentId: '', // 学号或工号
  title: '', // 教师职称 - 保留用于数据处理，不再显示
  class_name: '',
  class_ids: [], // 教师管辖班级
  department: '',
  gender: 'male',
  grade: '',
  gpa: 0 // 学生平均绩点
})

// 编辑表单验证规则
const editRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  studentId: [{ required: true, message: '请输入学号/工号', trigger: 'blur' }],
  department: [{ required: true, message: '请输入院系', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  // 学生专属规则
  grade: [
    { 
      required: ({ model }) => model.userType === 'student', 
      message: '请输入年级', 
      trigger: 'blur' 
    }
  ],
  class_name: [
    { 
      required: ({ model }) => model.userType === 'student', 
      message: '请输入班级', 
      trigger: 'blur' 
    }
  ]
}

// 编辑表单引用
const editFormRef = ref(null)

// 重置密码表单
const resetPasswordForm = ref({
  newPassword: '',
  confirmPassword: ''
})

// 重置密码表单验证规则
const resetPasswordRules = {
  newPassword: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    ({ getFieldValue }) => ({
      validator(_, value) {
        if (!value || getFieldValue('newPassword') === value) {
          return Promise.resolve()
        }
        return Promise.reject(new Error('两次输入的密码不一致'))
      },
      trigger: 'blur'
    })
  ]
}

// 重置密码表单引用
const resetPasswordFormRef = ref(null)

// 导入相关状态
const fileList = ref([])
const importLoading = ref(false)

// 表格列配置
const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '用户类型', dataIndex: 'user_type_display', key: 'user_type_display' },
  { title: '学号/工号', dataIndex: 'school_id', key: 'school_id' },
  { title: '班级', dataIndex: 'class_name', key: 'class_name' },
  { title: '院系', dataIndex: 'college', key: 'college' },
  { title: '操作', key: 'actions', fixed: 'right', width: 200 }
]

// 筛选后的用户列表
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    let match = true
    
    if (filterForm.value.userType) {
      match = match && user.user_type === filterForm.value.userType
    }
    
    if (filterForm.value.searchText) {
      const searchText = filterForm.value.searchText.toLowerCase()
      match = match && (
        (user.username && user.username.toLowerCase().includes(searchText)) ||
        user.name.toLowerCase().includes(searchText) ||
        (user.school_id && user.school_id.toLowerCase().includes(searchText))
      )
    }
    
    return match
  })
})

// 显示添加用户模态框
const showAddModal = () => {
  addModalVisible.value = true
}

// 搜索
const handleSearch = () => {
  fetchUsers()
}

// 重置筛选条件
const handleReset = () => {
  filterForm.value = {
    userType: '',
    searchText: ''
  }
}

// 刷新用户列表
const handleRefresh = () => {
  fetchUsers()
  message.success('用户列表已刷新')
}

// 编辑用户
const handleEdit = async (record) => {
  selectedUser.value = record
  
  // 确保学院和班级数据已加载
  if (colleges.value.length === 0 || classes.value.length === 0) {
    await fetchCollegesAndClasses()
  }
  
  // 获取教师管辖的班级ID列表
  let class_ids = []
  if (record.user_type === 'teacher') {
    try {
      const response = await api.admin.classBindings.getClassBindings({ teacher_id: record.id })
      class_ids = response.bindings?.map(binding => binding.class_obj) || []
    } catch (error) {
      console.error('获取教师班级绑定失败:', error)
    }
  }
  
  editForm.value = {
    userType: record.user_type,
    username: record.username,
    name: record.name,
    studentId: record.school_id || '',
    class_name: record.class_name || '',
    department: record.college,
    gender: record.gender || 'male',
    grade: record.grade || '',
    major: record.major || '',
    // 教师专属字段
    title: record.title || '',
    class_ids: class_ids,
    // 学生专属字段
    gpa: record.gpa || 0
  }
  editModalVisible.value = true
}

// 删除用户
const handleDelete = (record) => {
  // 检查是否是当前登录用户
  if (currentUser.value && currentUser.value.id === record.id) {
    message.warning('不能删除当前登录的用户账号')
    return
  }
  
  // 检查是否是教师账号
  let confirmContent = `确定要删除用户 ${record.name} 吗？`
  if (record.user_type === 'teacher') {
    // 查找该教师指导的学生数量
    const adviseesCount = users.value.filter(u => u.user_type === 'student' && u.advisor?.id === record.id).length
    if (adviseesCount > 0) {
      confirmContent += `\n\n注意：该教师目前指导了 ${adviseesCount} 名学生，删除后这些学生的指导教师将被清空。`
    }
  }
  
  Modal.confirm({
    title: '确认删除',
    content: confirmContent,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await api.admin.deleteUser(record.id)
        // 更新本地数据
        const index = users.value.findIndex(u => u.id === record.id)
        if (index !== -1) {
          users.value.splice(index, 1)
        }
        message.success('用户已删除')
      } catch (error) {
        console.error('删除用户错误:', error)
        // 详细错误信息处理
        const errorMsg = error.response?.data?.error || error.response?.data || error.message
        let errorDetails = ''
        if (typeof errorMsg === 'object') {
          errorDetails = Object.entries(errorMsg).map(([field, msg]) => {
            return `${field}: ${Array.isArray(msg) ? msg[0] : msg}`
          }).join('，')
        } else {
          errorDetails = errorMsg
        }
        message.error('删除用户失败: ' + errorDetails)
      }
    }
  })
}

// 重置密码
const handleResetPassword = (record) => {
  selectedUser.value = record
  resetPasswordModalVisible.value = true
}

// 确认添加用户
const handleConfirmAdd = async () => {
  if (!addFormRef.value) return
  
  try {
    await addFormRef.value.validate()
    
    // 转换表单数据以匹配后端API要求
    const userData = {
      name: addForm.value.name,
      gender: addForm.value.gender,
      college: addForm.value.department,
      user_type: addForm.value.userType
    }
    
    // 根据用户类型添加不同的字段
    if (addForm.value.userType === 'student') {
      // 学生专属字段
      userData.school_id = addForm.value.studentId
      userData.class_name = addForm.value.class_name
      userData.gpa = addForm.value.gpa
    } else if (addForm.value.userType === 'teacher') {
      // 教师专属字段
      userData.school_id = addForm.value.studentId
    } else if (addForm.value.userType === 'admin') {
      // 管理员专属字段 - 密码自动生成为用户名后六位
      userData.school_id = addForm.value.studentId
      // 为管理员生成密码：用户名后六位
      const password = addForm.value.studentId.slice(-6).padStart(6, '0')
      userData.password = password
      userData.password_confirm = password
    }
    
    // 调用API添加用户
    let teacherId = null
    if (addForm.value.userType === 'student') {
      // 学生类型用户添加，与学生信息管理页面保持一致
      const response = await api.admin.addUser(userData)
      message.success('学生添加成功')
    } else if (addForm.value.userType === 'teacher') {
      // 教师类型用户添加，与教师信息管理页面保持一致
      const response = await api.admin.addUser(userData)
      teacherId = response.user?.id || response.id
      message.success('教师添加成功')
    } else if (addForm.value.userType === 'admin') {
      // 管理员类型用户添加
      await api.admin.addUser(userData)
      message.success('管理员添加成功')
    }
    
    // 处理教师班级绑定
    if (addForm.value.userType === 'teacher' && teacherId) {
      try {
        // 要绑定的班级ID数组
        const newClassIds = addForm.value.class_ids || []
        
        // 添加新的绑定
        for (const classId of newClassIds) {
          await api.admin.classBindings.createClassBinding({
            teacher: teacherId,
            class_obj: classId
          })
        }
        message.success('教师班级绑定成功')
      } catch (error) {
        console.error('处理教师班级绑定失败:', error)
        message.error('教师班级绑定失败: ' + (error.response?.data?.message || error.message))
      }
    }
    
    addModalVisible.value = false
    resetAddForm()
    fetchUsers()
  } catch (error) {
    console.error('添加用户错误:', error)
    // 详细错误信息处理
    const errorMsg = error.response?.data?.error || {};
    let errorDetails = '';
    if (typeof errorMsg === 'object') {
      // 提取字段验证错误
      errorDetails = Object.entries(errorMsg).map(([field, msg]) => {
        // 字段名映射为中文显示
        const fieldMap = {
          school_id: '学号/工号',
          password: '密码',
          password_confirm: '确认密码',
          grade: '年级',
          major: '专业'
        };
        return `${fieldMap[field] || field}: ${Array.isArray(msg) ? msg[0] : msg}`;
      }).join('，');
    } else {
      errorDetails = errorMsg || error.message || '未知错误';
    }
    message.error(`添加用户失败: ${errorDetails}`);
    console.error('添加用户错误详情:', error.response?.data);
  }
}

// 重置添加表单
const resetAddForm = () => {
  addForm.value = {
    userType: 'student',
    studentId: '', // 学号/工号/管理员用户名
    name: '',
    gender: 'male',
    department: '',
    class_name: '',
    class_ids: [], // 教师管辖班级
    gpa: 0, // 学生平均绩点
    password: '',
    password_confirm: ''
  }
  if (addFormRef.value) {
    addFormRef.value.resetFields()
  }
}

// 确认编辑用户
const handleConfirmEdit = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    // 转换表单数据以匹配后端API要求
    const userData = {
      name: editForm.value.name,
      gender: editForm.value.gender,
      college: editForm.value.department
    }
    
    // 根据用户类型添加不同的字段
    if (editForm.value.userType === 'student') {
      // 学生专属字段 - 移除major字段
      userData.grade = editForm.value.grade
      userData.class_name = editForm.value.class_name
      userData.gpa = editForm.value.gpa
    } else if (editForm.value.userType === 'teacher') {
      // 教师专属字段 - 移除title字段
      // userData.title = editForm.value.title
    }
    
    // 调用API更新用户信息
    await api.admin.editUser(selectedUser.value.id, userData)
    
    // 处理教师班级绑定
    if (editForm.value.userType === 'teacher' && selectedUser.value.id) {
      try {
        // 获取当前绑定
        const currentBindingsResponse = await api.admin.classBindings.getClassBindings({ teacher_id: selectedUser.value.id })
        const currentBindings = currentBindingsResponse.bindings || []
        
        // 提取当前绑定的班级ID数组
        const currentClassIds = currentBindings.map(binding => binding.class_obj)
        
        // 要绑定的班级ID数组
        const newClassIds = editForm.value.class_ids || []
        
        // 找出需要删除的绑定
        const bindingsToDelete = currentBindings.filter(binding => !newClassIds.includes(binding.class_obj))
        
        // 找出需要新增的绑定
        const classIdsToAdd = newClassIds.filter(id => !currentClassIds.includes(id))
        
        // 先删除不需要的绑定
        for (const binding of bindingsToDelete) {
          await api.admin.classBindings.deleteClassBinding(binding.id)
        }
        
        // 再添加新的绑定
        for (const classId of classIdsToAdd) {
          await api.admin.classBindings.createClassBinding({
            teacher: selectedUser.value.id,
            class_obj: classId
          })
        }
      } catch (error) {
        console.error('处理教师班级绑定失败:', error)
        message.error('教师班级绑定更新失败: ' + (error.response?.data?.message || error.message))
      }
    }
    
    editModalVisible.value = false
    fetchUsers()
    message.success('用户信息更新成功')
  } catch (error) {
    console.error('编辑用户错误:', error)
    message.error('用户信息更新失败: ' + (error.response?.data?.error || error.message || '未知错误'))
  }
}

// 重置编辑表单
const resetEditForm = () => {
  editForm.value = {
    userType: 'student',
    username: '',
    name: '',
    studentId: '',
    title: '',
    class_name: '',
    class_ids: [],
    department: '',
    gender: 'male',
    grade: '',
    gpa: 0
  }
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
}

// 确认重置密码
const handleConfirmResetPassword = async () => {
  if (!resetPasswordFormRef.value) return
  
  try {
    await resetPasswordFormRef.value.validate()
    
    // 调用API重置密码
    await api.admin.resetPassword(selectedUser.value.id, {
      password: resetPasswordForm.value.newPassword
    })
    
    resetPasswordModalVisible.value = false
    resetResetPasswordForm()
    message.success('密码重置成功')
  } catch (error) {
    message.error('密码重置失败: ' + (error.response?.data?.message || error.message))
  }
}

// 重置重置密码表单
const resetResetPasswordForm = () => {
  resetPasswordForm.value = {
    newPassword: '',
    confirmPassword: ''
  }
  if (resetPasswordFormRef.value) {
    resetPasswordFormRef.value.resetFields()
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    loading.value = true
    error.value = null
    // 转换参数格式以匹配后端API期望
    const apiParams = {
      type: filterForm.value.userType,
      search: filterForm.value.searchText
    }
    const response = await api.admin.getUsers(apiParams)
    // 适配不同的数据结构，先检查响应中的results字段
    const rawUsers = response?.results || response?.users || response?.data || []
    
    // 添加user_type_display字段，将user_type转换为中文显示名称
    users.value = rawUsers.map(user => {
      // 用户类型映射关系
      const userTypeMap = {
        'student': '学生',
        'teacher': '老师',
        'admin': '超级管理员'
      }
      
      return {
        ...user,
        // 添加用户类型显示字段
        user_type_display: userTypeMap[user.user_type] || user.user_type
      }
    })
  } catch (err) {
    error.value = err
    users.value = [] // 发生错误时清空列表
    message.error('获取用户列表失败: ' + (err.response?.data?.message || err.message))
  } finally {
    loading.value = false
  }
}

// 组件销毁时的清理逻辑
onUnmounted(() => {
  // 清理API请求（如果有需要）
  // 清空引用以避免内存泄漏
  addFormRef.value = null
  editFormRef.value = null
  resetPasswordFormRef.value = null
  selectedUser.value = null
})

// 导入Excel文件
const beforeUpload = async (file) => {
  importLoading.value = true
  try {
    // 解析Excel文件
    const data = await parseExcel(file)
    // 处理导入数据
    await handleImportData(data)
    message.success('导入成功')
    fetchUsers()
  } catch (error) {
    message.error('导入失败：' + error.message)
  } finally {
    importLoading.value = false
    fileList.value = []
  }
  return false // 阻止自动上传
}

// 解析Excel文件
const parseExcel = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        resolve(jsonData)
      } catch (error) {
        reject(new Error('Excel解析失败'))
      }
    }
    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }
    reader.readAsArrayBuffer(file)
  })
}

// 处理导入数据
const handleImportData = async (data) => {
  // 数据格式验证
  if (!data || data.length === 0) {
    throw new Error('Excel文件中没有数据')
  }
  
  // 创建临时文件并调用API
  const jsonString = JSON.stringify(data)
  const blob = new Blob([jsonString], { type: 'application/json' })
  const file = new File([blob], 'import-data.json')
  
  // 调用导入API
  const result = await api.admin.importUsers(file)
  return result
}

// 下载导入模板
const downloadTemplate = () => {
  // 创建模板数据
  const templateData = [
    {
      '用户类型': 'teacher', // teacher或student
      '用户名': 'teacher001',
      '密码': '123456',
      '姓名': '张老师',
      '院系': '计算机科学与技术学院',
      '负责班级': '计算机科学与技术1班,软件工程2班', // 教师负责的班级，多个班级用逗号分隔
      '学号': '' // 教师不需要填写学号
    },
    {
      '用户类型': 'student',
      '用户名': 'student001',
      '密码': '123456',
      '姓名': '李同学',
      '院系': '计算机科学与技术学院',
      '班级': '计算机科学与技术1班',
      '学号': '202001001',
      '班主任': '张老师', // 学生的班主任
      '审核教师': '张老师,王老师' // 学生的审核教师，多个教师用逗号分隔
    }
  ]
  
  // 创建工作簿和工作表
  const workbook = XLSX.utils.book_new()
  const worksheet = XLSX.utils.json_to_sheet(templateData)
  XLSX.utils.book_append_sheet(workbook, worksheet, '用户数据')
  
  // 下载文件
  XLSX.writeFile(workbook, '用户导入模板.xlsx')
}

onMounted(async () => {
  await fetchUsers()
  await fetchCollegesAndClasses()
})
</script>

<style scoped>
.admin-users {
  padding: 20px;
}

.action-bar {
  margin-bottom: 10px;
}

.import-template {
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.users-list {
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

.action-buttons {
  display: flex;
  align-items: center;
}
</style>