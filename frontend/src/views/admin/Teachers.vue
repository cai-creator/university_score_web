<template>
  <div class="admin-teachers">
    <h2>教师信息管理</h2>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <a-button type="primary" @click="handleAddTeacher">添加教师</a-button>
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
        <a-col :span="8">
          <a-input
            v-model:value="searchKeyword"
            placeholder="搜索工号/姓名/学院"
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

    <!-- 教师列表 -->
    <a-card class="teachers-list">
      <!-- 加载中状态 -->
      <div v-if="loading" class="table-loading">
        <a-spin size="large" tip="加载中..." />
      </div>
      
      <!-- 加载失败状态 -->
      <div v-else-if="error" class="table-error">
        <a-empty description="加载失败，请重新加载">
          <template #footer>
            <a-button type="primary" @click="fetchTeachers">重新加载</a-button>
          </template>
        </a-empty>
      </div>
      
      <!-- 加载成功但无数据状态 -->
      <div v-else-if="filteredTeachers.length === 0" class="table-empty">
        <a-empty description="暂无该数据" />
      </div>
      
      <!-- 正常数据展示 -->
      <a-table
        v-else
        :columns="columns"
        :data-source="filteredTeachers"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
        :scroll="{ x: 1000 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'last_login'">
            {{ record.last_login ? new Date(record.last_login).toLocaleString() : '暂无' }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button 
                type="primary" 
                size="small" 
                @click="handleViewTeacher(record)"
              >
                查看
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleEditTeacher(record)"
              >
                编辑
              </a-button>
              <a-button 
                danger 
                size="small" 
                @click="handleDeleteTeacher(record)"
              >
                删除
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleResetPassword(record)"
              >
                重置密码
              </a-button>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑教师模态框 -->
    <a-modal
      v-model:open="teacherModalVisible"
      :title="teacherModalTitle"
      @ok="handleConfirmTeacher"
      @cancel="handleCancelTeacher"
    >
      <a-form
        :model="teacherForm"
        :rules="teacherFormRules"
        ref="teacherFormRef"
        layout="vertical"
      >
        <a-form-item label="工号" name="school_id">
          <a-input v-model:value="teacherForm.school_id" placeholder="请输入工号" :disabled="selectedTeacherId" />
        </a-form-item>
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="teacherForm.name" placeholder="请输入姓名" />
        </a-form-item>
        <a-form-item label="学院" name="college">
          <a-select v-model:value="teacherForm.college" placeholder="请选择学院">
            <a-select-option v-for="item in colleges" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="默认密码" name="password" v-if="!selectedTeacherId">
          <a-input-password
            v-model:value="teacherForm.password"
            placeholder="密码将自动生成"
            disabled
          />
          <template #extra>密码为工号后六位</template>
        </a-form-item>
        <a-form-item label="管辖班级（选填）" name="class_ids">
          <div style="display: flex; gap: 8px; align-items: center;">
            <a-select
              v-model:value="teacherForm.class_ids"
              mode="multiple"
              placeholder="请选择班级"
              :options="classes.map(cls => ({ value: cls.id, label: cls.name }))"
              style="flex: 1;"
            />
            <a-button 
              type="primary" 
              size="small" 
              @click="handleOpenClassManagement"
            >
              班级管理
            </a-button>
          </div>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 教师详情模态框 -->
    <a-modal
      v-model:open="viewTeacherModalVisible"
      title="教师详情"
      @cancel="handleCloseViewModal"
      width="600px"
    >
      <div v-if="selectedTeacher" class="teacher-detail">
        <div class="detail-row">
          <span class="detail-label">工号：</span>
          <span class="detail-value">{{ selectedTeacher.school_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">姓名：</span>
          <span class="detail-value">{{ selectedTeacher.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">学院：</span>
          <span class="detail-value">{{ selectedTeacher.college }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">角色：</span>
          <span class="detail-value">{{ selectedTeacher.user_type === 'teacher' ? '教师' : '管理员' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">最后登录：</span>
          <span class="detail-value">{{ selectedTeacher.last_login ? new Date(selectedTeacher.last_login).toLocaleString() : '暂无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间：</span>
          <span class="detail-value">{{ selectedTeacher.created_at ? new Date(selectedTeacher.created_at).toLocaleString() : '暂无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">管辖班级：</span>
          <div class="detail-value">
            <a-tag 
              v-for="cls in selectedTeacherClasses" 
              :key="cls.id" 
              color="blue" 
              style="margin: 2px;"
            >
              {{ cls.name }}
            </a-tag>
            <span v-if="selectedTeacherClasses.length === 0">暂无管辖班级</span>
          </div>
        </div>
        <div class="detail-row">
          <span class="detail-label">指导学生：</span>
          <div class="detail-value">
            <span v-if="selectedTeacher.advisees && selectedTeacher.advisees.length > 0">
              {{ selectedTeacher.advisees.length }} 名
            </span>
            <span v-else>暂无指导学生</span>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 班级管理模态框 -->
    <a-modal
      v-model:open="classManagementModalVisible"
      title="班级管理"
      @cancel="handleCloseClassManagement"
      width="800px"
    >
      <a-table
        :columns="classColumns"
        :data-source="classes"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button type="link" size="small" @click="handleOpenClassModal(record)">编辑</a-button>
              <a-button type="link" size="small" danger @click="editingClass.value = record; handleDeleteClass()">删除</a-button>
            </div>
          </template>
        </template>
      </a-table>
      <template #footer>
        <div style="display: flex; justify-content: space-between;">
          <a-button type="primary" @click="handleOpenClassModal()">添加班级</a-button>
          <a-button @click="classManagementModalVisible = false">关闭</a-button>
        </div>
      </template>
    </a-modal>

    <!-- 编辑/添加班级模态框 -->
    <a-modal
      v-model:open="isEditingClassVisible"
      :title="editingClass ? '编辑班级' : '添加班级'"
      @ok="handleSaveClass"
      @cancel="handleCloseClassEditModal"
      width="500px"
    >
      <a-form :model="classForm.value" layout="vertical" ref="classFormRef" :rules="classFormRules">
        <a-form-item label="班级名称" name="name">
          <a-input v-model:value="classForm.value.name" placeholder="请输入班级名称" />
        </a-form-item>
        <a-form-item label="年级" name="grade">
          <a-select v-model:value="classForm.value.grade" placeholder="请选择年级">
            <a-select-option v-for="year in getGradeOptions" :key="year" :value="year">{{ year }}级</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="学院" name="college">
          <a-select v-model:value="classForm.value.college" placeholder="请选择学院">
            <a-select-option v-for="item in colleges" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 重置密码模态框 -->
    <a-modal
      v-model:open="resetPasswordModalVisible"
      title="重置密码"
      @ok="handleConfirmResetPassword"
      @cancel="handleCancelResetPassword"
    >
      <a-form
        :model="resetPasswordForm"
        :rules="resetPasswordFormRules"
        ref="resetPasswordFormRef"
        layout="vertical"
      >
        <a-form-item label="新密码" name="password">
          <a-input-password v-model:value="resetPasswordForm.password" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item label="确认密码" name="confirmPassword">
          <a-input-password v-model:value="resetPasswordForm.confirmPassword" placeholder="请确认新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { message, Modal, notification } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import api from '@/utils/api'

// 数据
const teachers = ref([])

// 获取当前登录用户信息
const currentUser = ref(JSON.parse(localStorage.getItem('user')))

// 班级列表数据
const classes = ref([])

// 学院列表数据
const colleges = ref([])
const searchKeyword = ref('')
const loading = ref(false)
const error = ref(false)

// 模态框状态
const teacherModalVisible = ref(false)
const viewTeacherModalVisible = ref(false)
const resetPasswordModalVisible = ref(false)
const teacherModalTitle = ref('添加教师')
const selectedTeacherId = ref(null)
const selectedTeacher = ref(null)
const selectedTeacherClasses = ref([])

// 表单数据
const teacherForm = ref({
  school_id: '',
  name: '',
  college: '', // 学院ID
  collegeName: '', // 学院名称，用于显示
  password: '', // 默认密码，自动生成
  class_ids: [] // 教师管辖的班级ID列表
})

const resetPasswordForm = ref({
  password: '',
  confirmPassword: ''
})

// 表单引用
const teacherFormRef = ref(null)
const resetPasswordFormRef = ref(null)
const classFormRef = ref(null)

// 表单验证规则
const teacherFormRules = {
  school_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  college: [{ required: true, message: '请输入学院', trigger: 'blur' }]
}

const resetPasswordFormRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    ({ getFieldValue }) => ({
      validator(_, value) {
        if (!value || getFieldValue('password') === value) {
          return Promise.resolve()
        }
        return Promise.reject(new Error('两次输入的密码不一致'))
      },
      trigger: 'blur'
    })
  ]
}

// 班级表单验证规则（简单验证）
const classFormRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: ['blur', 'change'] }],
  college: [{ required: true, message: '请选择学院', trigger: ['blur', 'change'] }]
}

// 表格列配置
const columns = [
  { title: '工号', dataIndex: 'school_id', key: 'school_id' },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '学院', dataIndex: 'college', key: 'college' },
  { title: '最后登录时间', dataIndex: 'last_login', key: 'last_login' },
  { title: '操作', key: 'actions', fixed: 'right', width: 200 }
]

// 班级管理表格列配置
const classColumns = [
  { title: '班级名称', dataIndex: 'name', key: 'name', width: '40%' },
  { title: '年级', dataIndex: 'grade', key: 'grade', width: '30%' },
  { 
    title: '学院', 
    dataIndex: 'college', 
    key: 'college', 
    width: '30%',
    // 修复：自定义渲染，确保显示学院名称
    customRender: ({ text }) => {
      return text ? text.name : '未分配学院';
    }
  },
  { title: '操作', key: 'actions', width: '30%', fixed: 'right' }
]

// 筛选后的教师列表
const filteredTeachers = computed(() => {
  return teachers.value || []
})

// 获取教师列表
const fetchTeachers = async () => {
  try {
    loading.value = true
    error.value = false
    const response = await api.admin.getTeachers({
      search: searchKeyword.value
    })
    
    // 适配不同的数据结构，先检查响应中的results字段
    let teacherData = response?.results || response?.users || response?.data || []
    
    // 字段映射，确保数据结构一致
    teachers.value = teacherData.map(teacher => {
      // 先保存原始数据的引用
      const college_obj = teacher.college;
      
      // 先展开原始数据，再处理需要转换的字段，这样转换后的字段会覆盖原始字段
      const mappedTeacher = {
        ...teacher,
        id: teacher.id || '',
        school_id: teacher.school_id || '',
        name: teacher.name || '',
        // 处理college对象，只显示学院名称
        college: teacher.college?.name || teacher.college || '',
        last_login: teacher.last_login || '',
        // 保存原始的college对象，用于详情展示
        college_obj
      };
      
      return mappedTeacher;
    })
    
    // 加载学院列表，用于显示
    await fetchColleges()
  } catch (err) {
    message.error('获取教师列表失败: ' + (err.response?.data?.message || err.message))
    error.value = true
    teachers.value = []
  } finally {
    loading.value = false
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await api.admin.classes.getClasses()
    // 调试：打印班级数据
    console.log('班级数据:', response)
    // 适配不同的数据结构，确保获取到正确的班级列表
    const classData = Array.isArray(response) ? response : 
                    response?.data || 
                    response?.classes || 
                    response?.results || []
    // 调试：打印处理后的班级数据
    console.log('处理后的班级数据:', classData)
    classes.value = classData
  } catch (error) {
    message.error('获取班级列表失败: ' + (error.response?.data?.message || error.message))
    console.error('获取班级列表失败:', error)
    classes.value = []
  }
}

// 获取学院列表
const fetchColleges = async () => {
  try {
    const response = await api.admin.getColleges()
    // 适配不同的数据结构，先检查响应是否为数组
    colleges.value = Array.isArray(response) ? response : 
                    response?.colleges || 
                    response?.data || 
                    response?.results || []
  } catch (error) {
    message.error('获取学院列表失败: ' + (error.response?.data?.message || error.message))
    colleges.value = []
  }
}

// 获取教师已绑定的班级
const fetchTeacherClassBindings = async (teacherId) => {
  try {
    const response = await api.admin.classBindings.getClassBindings({ teacher_id: teacherId })
    // 适配不同的响应数据结构
    // 注意：后端返回的是 {code, message, data} 格式
    const bindingsData = response.data || response.bindings || response.results || response || []
    // 提取班级ID数组，后端返回的班级ID在 class.id 字段中
    teacherForm.value.class_ids = bindingsData.map(binding => 
      binding.class?.id || binding.class_id || binding.class_obj
    )
  } catch (error) {
    message.error('获取教师绑定班级失败: ' + (error.response?.data?.message || error.message))
    teacherForm.value.class_ids = []
  }
}

// 搜索
const handleSearch = () => {
  fetchTeachers()
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
  fetchTeachers()
}

// 添加教师
const handleAddTeacher = async () => {
  teacherModalTitle.value = '添加教师'
  selectedTeacherId.value = null
  resetTeacherForm()
  // 打开模态框前获取学院列表和班级列表
  await fetchColleges()
  await fetchClasses()
  teacherModalVisible.value = true
}

// 监听工号变化，自动生成密码
watch(() => teacherForm.value.school_id, (newSchoolId) => {
  if (newSchoolId && !selectedTeacherId.value) {
    // 仅在添加教师且工号变化时生成密码
    teacherForm.value.password = newSchoolId.slice(-6) // 取工号后六位作为密码
  }
})

// 编辑教师
const handleEditTeacher = async (record) => {
  teacherModalTitle.value = '编辑教师'
  selectedTeacherId.value = record.id
  
  // 查找对应的学院ID
  const college = colleges.value.find(c => c.name === record.college || c.id === record.college)
  
  teacherForm.value = {
    school_id: record.school_id,
    name: record.name,
    college: college?.id || record.college, // 使用学院ID
    collegeName: record.college, // 保存原始学院名称用于显示
    class_ids: []
  }
  
  // 打开模态框前获取班级列表和教师已绑定的班级
  await fetchClasses()
  await fetchTeacherClassBindings(record.id)
  await fetchColleges() // 确保有最新的学院列表
  
  teacherModalVisible.value = true
}

// 查看教师详情
const handleViewTeacher = async (record) => {
  // 确保college字段只包含学院名称，避免显示完整JSON对象
  const processedRecord = {
    ...record,
    college: record.college?.name || record.college || ''
  };
  
  selectedTeacher.value = processedRecord
  selectedTeacherClasses.value = []
  
  try {
    // 获取教师绑定的班级信息
    const response = await api.admin.classBindings.getClassBindings({ teacher_id: record.id })
    // 适配不同的响应数据结构
    // 注意：后端返回的是 {code, message, data} 格式
    const bindingsData = response.data || response.bindings || response.results || response || []
    
    // 如果有绑定信息，获取班级详情
    if (bindingsData.length > 0) {
      // 从班级列表中找出对应的班级
      // 注意：后端返回的班级ID在 binding.class.id 字段中
      selectedTeacherClasses.value = classes.value.filter(cls => 
        bindingsData.some(binding => binding.class?.id === cls.id || binding.class_id === cls.id || binding.class_obj === cls.id)
      )
      
      // 如果班级列表中没有，尝试获取完整的班级信息
      if (selectedTeacherClasses.value.length === 0) {
        const response = await api.admin.classes.getClasses()
        const allClasses = response?.classes || response.results || response.data || response || []
        selectedTeacherClasses.value = allClasses.filter(cls => 
          bindingsData.some(binding => binding.class?.id === cls.id || binding.class_id === cls.id || binding.class_obj === cls.id)
        )
      }
    }
  } catch (error) {
    message.error('获取教师班级信息失败: ' + (error.response?.data?.message || error.message))
  }
  
  // 打开详情模态框
  viewTeacherModalVisible.value = true
}

// 关闭教师详情模态框
const handleCloseViewModal = () => {
  viewTeacherModalVisible.value = false
  selectedTeacher.value = null
  selectedTeacherClasses.value = []
}

// 班级管理相关功能
// 获取年级选项（当前年份及前后5年）
const getGradeOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 5; i <= currentYear + 5; i++) {
    years.push(i)
  }
  return years
})

// 班级管理状态
const classManagementModalVisible = ref(false)
const isEditingClassVisible = ref(false)
const editingClass = ref(null)
const classForm = ref({
  name: '',
  grade: new Date().getFullYear(),
  college: ''
})

// 打开班级管理界面
const handleOpenClassManagement = async () => {
  // 确保有最新的学院列表
  await fetchColleges()
  classManagementModalVisible.value = true
}

// 关闭班级管理界面
const handleCloseClassManagement = () => {
  classManagementModalVisible.value = false
}

// 打开编辑/添加班级模态框
const handleOpenClassModal = async (classItem = null) => {
  // 确保有最新的学院列表
  await fetchColleges()
  editingClass.value = classItem
  if (classItem) {
    classForm.value.name = classItem.name
    classForm.value.grade = classItem.grade || new Date().getFullYear()
    // 修复：如果classItem.college是对象，使用id字段；否则直接使用（兼容字符串ID）
    classForm.value.college = classItem.college?.id || classItem.college || ''
  } else {
    classForm.value.name = ''
    classForm.value.grade = new Date().getFullYear()
    classForm.value.college = '' // 修复：添加新班级时，学院字段默认为空
  }
  isEditingClassVisible.value = true
}

// 关闭编辑/添加班级模态框
const handleCloseClassEditModal = () => {
  isEditingClassVisible.value = false
  editingClass.value = null
  resetClassForm()
}

// 重置班级表单
const resetClassForm = () => {
  classForm.value = {
    name: '',
    grade: new Date().getFullYear(),
    college: ''
  }
  if (classFormRef.value) {
    classFormRef.value.resetFields()
  }
}

// 保存班级修改
const handleSaveClass = async () => {
  if (!classFormRef.value) return
  
  try {
    await classFormRef.value.validate()
    
    // 调试：打印表单数据
    console.log('班级表单数据:', classForm.value)
    // 调试：打印学院字段的类型和值
    console.log('学院字段类型:', typeof classForm.value.college)
    console.log('学院字段值:', classForm.value.college)
    
    const data = {
      name: classForm.value.name.trim(),
      grade: classForm.value.grade,
      college_id: classForm.value.college // 修复：使用 college_id 参数传递学院ID
    }
    // 调试：打印API调用参数
    console.log('API调用参数:', data)
    // 调试：打印API调用参数中的college_id类型和值
    console.log('API调用参数中的college_id类型:', typeof data.college_id)
    console.log('API调用参数中的college_id值:', data.college_id)
    
    let classId
    if (editingClass.value && editingClass.value.id) {
        // 更新班级
        console.log('更新班级，调用API:', data)
        const updatedClass = await api.admin.classes.updateClass(editingClass.value.id, data)
        console.log('更新班级成功，返回结果:', updatedClass)
        // 更新班级列表
        const index = classes.value.findIndex(c => c.id === updatedClass.id)
        if (index !== -1) {
          classes.value[index] = updatedClass
        }
        message.success('班级已更新')
      } else {
        // 创建班级
        console.log('创建班级，调用API:', data)
        const newClass = await api.admin.classes.createClass(data)
        console.log('创建班级成功，返回结果:', newClass)
        // 添加到班级列表
        classes.value.push(newClass)
        message.success('班级已创建')
      }
    
    // 关闭模态框
    isEditingClassVisible.value = false
    editingClass.value = null
    resetClassForm()
    
    // 如果班级管理模态框是打开的，不需要重新获取教师列表
    if (!classManagementModalVisible.value) {
      // 刷新教师列表
      fetchTeachers()
    }
  } catch (error) {
    if (error.errorFields) {
      // 表单验证错误，已由Ant Design处理
      console.error('表单验证错误:', error.errorFields)
      return
    }
    console.error('保存班级失败:', error)
    console.error('保存班级失败的错误详情:', error.response?.data)
    console.error('保存班级失败的状态:', error.response?.status)
    message.error('操作失败: ' + (error.response?.data?.message || error.message))
  }
}

// 删除班级
const handleDeleteClass = async () => {
  if (!editingClass.value || !editingClass.value.id) return
  
  try {
    await api.admin.classes.deleteClass(editingClass.value.id)
    // 从班级列表中移除
    const index = classes.value.findIndex(c => c.id === editingClass.value.id)
    if (index !== -1) {
      classes.value.splice(index, 1)
    }
    message.success('班级已删除')
    
    // 关闭编辑模态框
    isEditingClassVisible.value = false
    editingClass.value = null
    
    // 刷新教师列表
    fetchTeachers()
  } catch (error) {
    message.error('删除班级失败: ' + (error.response?.data?.message || error.message))
  }
}

// 删除教师
const handleDeleteTeacher = (record) => {
  // 检查是否是当前登录用户
  if (currentUser.value && currentUser.value.id === record.id) {
    message.warning('不能删除当前登录的用户账号')
    return
  }
  
  // 查找该教师指导的学生数量
  const adviseesCount = teachers.value.filter(t => t.id === record.id)[0]?.advisees?.length || 0
  let confirmContent = `确定要删除教师 ${record.name} 吗？`
  
  if (adviseesCount > 0) {
    confirmContent += `\n\n注意：该教师目前指导了 ${adviseesCount} 名学生，删除后这些学生的指导教师将被清空。`
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
        const index = teachers.value.findIndex(t => t.id === record.id)
        if (index !== -1) {
          teachers.value.splice(index, 1)
        }
        message.success('教师已删除')
      } catch (error) {
        console.error('删除教师错误:', error)
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
        message.error('删除教师失败: ' + errorDetails)
      }
    }
  })
}

// 重置密码
const handleResetPassword = (record) => {
  // 显示确认对话框
  Modal.confirm({
      title: '确认重置密码',
      content: `确定要将教师 ${record.name}（工号：${record.school_id}）的密码重置为默认密码吗？\n默认密码为：工号后六位字符`,
      okText: '确定',
      cancelText: '取消',
    onOk: async () => {
      try {
        // 调用API重置密码
        const response = await api.admin.resetPassword(record.id)
        
        // 显示成功消息并包含默认密码信息
        if (response.data?.default_password) {
          message.success(`密码重置成功！\n默认密码：${response.data.default_password}`)
        } else {
          message.success('密码重置成功！')
        }
      } catch (error) {
        console.error('密码重置失败:', error)
        message.error('密码重置失败: ' + (error.response?.data?.message || error.message))
      }
    }
  })
}

// 确认添加/编辑教师
const handleConfirmTeacher = async () => {
  if (!teacherFormRef.value) return
  
  try {
    await teacherFormRef.value.validate()
    
    // 找到选中的学院
    const selectedCollege = colleges.value.find(c => c.id === teacherForm.value.college)
    
    const data = {
      school_id: teacherForm.value.school_id,
      name: teacherForm.value.name,
      college: teacherForm.value.college, // 后端期望学院UUID
      user_type: 'teacher'
    }
    
    if (!selectedTeacherId.value) {
      // 添加教师时，使用表单中自动生成的密码
      data.password = teacherForm.value.password
      data.password_confirm = data.password // 确认密码与密码一致
    }
    
    let teacherId
    if (selectedTeacherId.value) {
      // 更新教师
      await api.admin.editUser(selectedTeacherId.value, data)
      teacherId = selectedTeacherId.value
      message.success('教师信息更新成功')
    } else {
      // 添加教师
      const response = await api.admin.addUser(data)
      teacherId = response.user?.id || response.id
      message.success('教师添加成功')
    }
    
    // 处理班级绑定
        if (teacherId) {
          try {
            // 获取教师当前的所有绑定
            const response = await api.admin.classBindings.getClassBindings({ teacher_id: teacherId })
            // 修复：响应拦截器已将 response 转换为 binding_list 数组
            const currentBindings = response || []
            
            // 提取当前绑定的班级ID数组
            // 修复：从 binding.class.id 中获取班级ID
            const currentClassIds = currentBindings.map(binding => binding.class.id)
            
            // 要绑定的班级ID数组（UUID格式，不需要转换）
            const newClassIds = teacherForm.value.class_ids || []
            
            // 找出需要删除的绑定（当前有但新列表没有的）
            // 修复：使用 binding.class.id 进行比较
            const bindingsToDelete = currentBindings.filter(binding => !newClassIds.includes(binding.class.id))
            
            // 找出需要新增的绑定（新列表有但当前没有的）
            const classIdsToAdd = newClassIds.filter(id => !currentClassIds.includes(id))
            
            // 先删除不需要的绑定
            for (const binding of bindingsToDelete) {
              // 修复：确保使用正确的 binding.id 字段
              await api.admin.classBindings.deleteClassBinding(binding.id)
            }
            
            // 再添加新的绑定
            for (const classId of classIdsToAdd) {
              await api.admin.classBindings.createClassBinding({
                teacher_id: teacherId,
                class_id: classId
              })
            }
            
            message.success('班级绑定更新成功')
          } catch (error) {
            message.error('班级绑定更新失败: ' + (error.response?.data?.message || error.message))
          }
        }
    
    // 关闭模态框并刷新列表
    teacherModalVisible.value = false
    fetchTeachers()
  } catch (error) {
    if (error.errorFields) {
      // 表单验证错误，已由Ant Design处理
      return
    }
    message.error('操作失败: ' + (error.response?.data?.message || error.message))
  }
}

// 取消添加/编辑教师
const handleCancelTeacher = () => {
  teacherModalVisible.value = false
  resetTeacherForm()
}

// 确认重置密码 - 已改为直接调用API，此方法保留以避免引用错误
const handleConfirmResetPassword = async () => {
  if (!resetPasswordFormRef.value || !selectedTeacherId.value) return
  
  try {
    // 调用API重置密码
    message.success('密码重置成功')
    resetPasswordModalVisible.value = false
    resetResetPasswordForm()
  } catch (error) {
    message.error('密码重置失败: ' + (error.response?.data?.message || error.message))
  }
}

// 取消重置密码
const handleCancelResetPassword = () => {
  resetPasswordModalVisible.value = false
  resetResetPasswordForm()
}

// 重置添加/编辑教师表单
const resetTeacherForm = () => {
  teacherForm.value = {
    school_id: '',
    name: '',
    college: '',
    collegeName: '',
    password: '',
    class_ids: []
  }
  if (teacherFormRef.value) {
    teacherFormRef.value.resetFields()
  }
}

// 重置重置密码表单
const resetResetPasswordForm = () => {
  resetPasswordForm.value = {
    password: '',
    confirmPassword: ''
  }
  if (resetPasswordFormRef.value) {
    resetPasswordFormRef.value.resetFields()
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

// 页面加载时获取教师列表、学院列表和班级列表
onMounted(async () => {
  await fetchColleges()
  await fetchClasses()
  await fetchTeachers()
})
</script>

<style scoped>
.admin-teachers {
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

.teachers-list {
  margin-bottom: 20px;
  min-height: 300px;
  position: relative;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

/* 教师详情样式 */
.teacher-detail {
  padding: 10px 0;
}

.detail-row {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.detail-label {
  width: 100px;
  font-weight: bold;
  margin-right: 10px;
  text-align: right;
  padding-top: 4px;
}

.detail-value {
  flex: 1;
  word-break: break-word;
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
</style>