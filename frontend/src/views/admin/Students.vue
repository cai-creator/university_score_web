<template>
  <div class="admin-students">
    <h2>学生信息管理</h2>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <a-button type="primary" @click="handleAddStudent">添加学生</a-button>
      <a-upload
        name="file"
        :multiple="false"
        :before-upload="handleBeforeUpload"
        accept=".xlsx, .xls"
        style="margin-left: 10px"
      >
        <a-button>导入Excel</a-button>
      </a-upload>
      <a-button @click="handleExport" style="margin-left: 10px">导出Excel</a-button>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-section">
      <a-row :gutter="[16, 16]">
        <a-col :span="12">
          <a-input
            v-model:value="searchKeyword"
            placeholder="搜索学号、姓名或班级"
            prefix="🔍"
            @pressEnter="handleSearch"
          />
        </a-col>
        <a-col :span="12" style="text-align: right;">
          <a-button @click="handleSearch">搜索</a-button>
          <a-button @click="handleReset" style="margin-left: 8px">重置</a-button>
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
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'gender'">
            {{ record.gender === 'male' ? '男' : '女' }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-button type="link" @click="handleViewStudent(record)">查看</a-button>
            <a-button type="link" @click="handleEditStudent(record)">编辑</a-button>
            <a-button type="link" @click="handleResetPassword(record)" danger>重置密码</a-button>
            <a-button type="link" @click="handleDeleteStudent(record)" danger>删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑学生模态框 -->
    <a-modal
      v-model:open="studentModalVisible"
      :title="studentModalTitle"
      @ok="handleSubmitStudent"
      @cancel="handleCancelStudent"
      width="600px"
    >
      <a-form :model="studentForm" layout="vertical" :rules="studentRules" ref="studentFormRef">
        <a-form-item label="学号（账号）" name="studentId">
          <a-input v-model:value="studentForm.studentId" placeholder="请输入学号" />
        </a-form-item>
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="studentForm.name" placeholder="请输入姓名" />
        </a-form-item>
        <a-form-item label="性别" name="gender">
          <a-select v-model:value="studentForm.gender" placeholder="请选择性别">
            <a-select-option value="male">男</a-select-option>
            <a-select-option value="female">女</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="所在学院" name="college">
          <div style="display: flex; gap: 8px;">
            <a-select
              v-model:value="studentForm.college"
              placeholder="请选择学院"
              :disabled="!colleges.length"
              style="flex: 1;"
            >
              <a-select-option
                v-for="college in colleges"
                :key="college.id"
                :value="college.id"
              >
                {{ college.name }}
              </a-select-option>
            </a-select>
            <a-button type="primary" size="small" @click="handleAddCollegeModal">
              添加学院
            </a-button>
          </div>
        </a-form-item>
        <a-form-item label="所在班级" name="class_name">
          <a-select
            v-model:value="studentForm.class_name"
            placeholder="请选择班级"
            :disabled="!filteredClasses.length"
          >
            <a-select-option
              v-for="cls in filteredClasses"
              :key="cls.id"
              :value="cls.id"
            >
              {{ cls.name }} ({{ cls.grade }})
            </a-select-option>
          </a-select>
          <div style="display: flex; gap: 8px; margin-top: 8px;">
            <a-button type="link" size="small" @click="handleAddClassModal">添加班级</a-button>
          </div>
        </a-form-item>
        <a-form-item label="平均绩点" name="gpa">
          <a-input-number v-model:value="studentForm.gpa" :min="0" :max="5" :step="0.1" placeholder="请输入平均绩点" />
        </a-form-item>
        <a-form-item v-if="!selectedStudentId" class="password-tip">
          <p style="color: #999;">密码将自动设置为学号后六位</p>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 学生详情模态框 -->
    <a-modal
      v-model:open="viewModalVisible"
      title="学生详情"
      @cancel="handleCloseViewModal"
      :footer="null"
      width="600px"
    >
      <div v-if="selectedStudent" class="student-detail">
        <a-descriptions :column="2" bordered>
<a-descriptions-item label="学号（账号）">{{ selectedStudent.studentId }}</a-descriptions-item>
<a-descriptions-item label="姓名">{{ selectedStudent.name }}</a-descriptions-item>
<a-descriptions-item label="性别">{{ selectedStudent.gender === 'male' ? '男' : '女' }}</a-descriptions-item>
<a-descriptions-item label="所在学院">{{ selectedStudent.college }}</a-descriptions-item>
<a-descriptions-item label="所在班级">{{ selectedStudent.class_obj?.name || selectedStudent.class_name }}</a-descriptions-item>
<a-descriptions-item label="辅导员老师">{{ selectedStudent.advisor || '未分配' }}</a-descriptions-item>
<a-descriptions-item label="平均绩点">{{ selectedStudent.gpa }}</a-descriptions-item>
<a-descriptions-item label="综测分数">{{ selectedStudent.total_score || 0 }}</a-descriptions-item>
<a-descriptions-item label="年级">{{ selectedStudent.grade || '未设置' }}</a-descriptions-item>
<a-descriptions-item label="联系方式">{{ selectedStudent.contact || '未设置' }}</a-descriptions-item>
<a-descriptions-item label="邮箱">{{ selectedStudent.email || '未设置' }}</a-descriptions-item>
<a-descriptions-item label="上一次登录">{{ selectedStudent.last_login ? new Date(selectedStudent.last_login).toLocaleString() : '未登录过' }}</a-descriptions-item>
</a-descriptions>
      </div>
    </a-modal>

    <!-- 重置密码确认模态框 -->
    <a-modal
      v-model:open="resetPasswordModalVisible"
      title="重置密码"
      @ok="handleConfirmResetPassword"
      @cancel="handleCancelResetPassword"
    >
      <p>确定要将学号为 <strong>{{ selectedStudentForReset?.studentId }}</strong> 的学生
        {{ selectedStudentForReset?.name }} 的密码重置为学号后六位吗？</p>
    </a-modal>

    <!-- 删除确认模态框 -->
    <a-modal
      v-model:open="deleteModalVisible"
      title="删除确认"
      @ok="handleConfirmDelete"
      @cancel="handleCancelDelete"
      okText="确认删除"
      okType="danger"
      cancelText="取消"
    >
      <p>确定要删除学号为 <strong>{{ selectedStudentForDelete?.studentId }}</strong> 的学生
        {{ selectedStudentForDelete?.name }} 吗？此操作不可撤销。</p>
    </a-modal>

    <!-- 添加学院模态框 -->
    <a-modal
      v-model:open="collegeModalVisible"
      title="添加学院"
      @ok="handleAddCollege"
      @cancel="handleCancelCollege"
    >
      <a-form
        :model="collegeForm"
        :rules="{ name: [{ required: true, message: '请输入学院名称', trigger: 'blur' }] }"
        ref="collegeFormRef"
        layout="vertical"
      >
        <a-form-item label="学院名称" name="name">
          <a-input v-model:value="collegeForm.name" placeholder="请输入学院名称" />
        </a-form-item>
        <a-form-item label="学院代码（选填）" name="code">
          <a-input v-model:value="collegeForm.code" placeholder="请输入学院代码" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 添加班级模态框 -->
    <a-modal
      v-model:open="classModalVisible"
      title="添加班级"
      @ok="handleAddClass"
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
        <a-form-item label="所属学院" name="college_id">
          <a-select 
            v-model:value="classForm.college_id" 
            placeholder="请选择学院"
          >
            <a-select-option 
              v-for="college in colleges" 
              :key="college.id" 
              :value="college.id"
            >
              {{ college.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import api from '@/utils/api.js'

// 状态管理
const students = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const colleges = ref([])
const classes = ref([]) // 班级列表

// 学院相关模态框
const collegeModalVisible = ref(false)
const collegeForm = reactive({ name: '', code: '' })
const collegeFormRef = ref()

// 班级相关模态框
const classModalVisible = ref(false)
const classForm = reactive({ name: '', grade: '', college_id: '' })
const classFormRef = ref()
const classFormRules = reactive({
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  college_id: [{ required: true, message: '请选择学院', trigger: 'change' }]
})

// 模态框状态
const studentModalVisible = ref(false)
const studentModalTitle = ref('添加学生')
const viewModalVisible = ref(false)
const resetPasswordModalVisible = ref(false)
const deleteModalVisible = ref(false)

// 表单引用
const studentFormRef = ref()

// 选中的学生信息
const selectedStudentId = ref(null)
const selectedStudent = ref(null)
const selectedStudentForReset = ref(null)
const selectedStudentForDelete = ref(null)

// 学生表单
const studentForm = reactive({
  studentId: '',
  name: '',
  gender: '',
  college: '',
  class_name: '',
  gpa: 0
})

// 表单验证规则
const studentRules = {
  studentId: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { min: 6, max: 20, message: '学号长度应在6-20个字符之间', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 20, message: '姓名长度应在1-20个字符之间', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  college: [
    { required: true, message: '请选择所在学院', trigger: 'change' }
  ],
  class_name: [
    { required: true, message: '请输入所在班级', trigger: 'blur' }
  ],
  gpa: [
    { required: true, message: '请输入平均绩点', trigger: 'blur' },
    { type: 'number', min: 0, max: 5, message: '平均绩点应在0-5之间', trigger: 'blur' }
  ]
}

// 表格列配置
const columns = [
  { title: '学号', dataIndex: 'studentId', key: 'studentId' },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '性别', dataIndex: 'gender', key: 'gender' },
  { title: '所在学院', dataIndex: 'college', key: 'college' },
  { title: '所在班级', dataIndex: 'class_name', key: 'class_name' },
  { title: '平均绩点', dataIndex: 'gpa', key: 'gpa' },
  { title: '综测分数', dataIndex: 'total_score', key: 'total_score' },
  { title: '操作', key: 'actions' }
]

// 计算属性：过滤后的学生列表
const filteredStudents = computed(() => {
  if (!searchKeyword.value) {
    return students.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return students.value.filter(student => 
    student.studentId.toLowerCase().includes(keyword) ||
    student.name.toLowerCase().includes(keyword) ||
    (student.class_name && student.class_name.toLowerCase().includes(keyword))
  )
})

// 根据选择的学院过滤班级
const filteredClasses = computed(() => {
  if (!studentForm.college) {
    return classes.value
  }
  return classes.value.filter(cls => 
    // 适配不同的班级数据结构
    cls.college_id === studentForm.college || 
    cls.college === studentForm.college || 
    (cls.college && cls.college.id === studentForm.college)
  )
})

// 监听学院变化，清空班级选择
watch(
  () => studentForm.college,
  (newCollege, oldCollege) => {
    if (newCollege !== oldCollege) {
      // 当学院变化时，清空班级选择
      studentForm.class_name = ''
    }
  }
)

// 获取年级选项
const getGradeOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  // 生成最近10年的年级选项
  for (let i = 0; i < 10; i++) {
    years.push(currentYear - i)
  }
  return years
})

// 获取学生列表
const fetchStudents = async () => {
  try {
    loading.value = true
    const response = await api.admin.getStudents()
    console.log('学生列表API响应:', response); // 调试日志
    
    // 直接使用后端返回的数据结构
    let studentData = []
    // 根据api.js的响应处理逻辑，适配多种可能的响应格式
    if (response && response.results && Array.isArray(response.results)) {
      // 适配新的分页响应格式 {results: [...], count: total, page: page, page_size: page_size}
      studentData = response.results || []
      console.log('解析后的学生数据(新分页格式):', studentData); // 调试日志
    } else if (response && response.users && Array.isArray(response.users)) {
      // 兼容旧的{users: [...]}格式
      studentData = response.users || []
      console.log('解析后的学生数据(旧格式):', studentData); // 调试日志
    } else if (response && response.data && response.data.users) {
      // 兼容更旧的响应格式
      studentData = response.data.users || []
      console.log('解析后的学生数据(兼容旧格式):', studentData); // 调试日志
    } else if (Array.isArray(response)) {
      // 兼容直接返回数组的情况
      studentData = response
      console.log('解析后的学生数据(数组格式):', studentData); // 调试日志
    } else if (response && Array.isArray(response.data)) {
      // 兼容{data: [...]}格式
      studentData = response.data || []
      console.log('解析后的学生数据(data数组格式):', studentData); // 调试日志
    }
    
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

    // 字段映射，确保数据结构一致
    students.value = studentData.map(student => {
      // 保存原始数据的引用
      const college_obj = student.college;
      const class_obj = student.class;
      
      // 优先使用后端返回的total_score，如果不存在则使用前端计算的分数
      // 确保使用正确的加分数据：bonus_score字段是审核通过的申请分数
      const gpa = student.gpa || 0;
      const bonusScore = student.bonus_score || student.total_bonus || 0;
      const calculatedScore = calculateTotalScore(gpa, bonusScore);
      
      // 先展开原始数据，再处理需要转换的字段
      const mappedStudent = {
        ...student,
        id: student.id || '',
        studentId: student.school_id || student.student_id || student.studentId || '',
        name: student.name || '',
        gender: student.gender || '',
        // 处理college对象，只显示学院名称
        college: student.college?.name || student.college || '',
        // 处理class对象或class_name字段，只显示班级名称
        class_name: student.class?.name || student.class_name || student.class || '',
        gpa: student.gpa || 0,
        // 优先使用后端返回的total_score，始终信任后端计算的分数
        total_score: student.total_score !== undefined ? student.total_score : calculatedScore,
        // 保存加分数据
        bonus_score: bonusScore,
        // 保存前端计算的综测分数，用于显示
        calculated_total_score: calculatedScore,
        // 处理辅导老师，优先使用 counselor_names（新字段），兼容旧的 advisor_name 字段
        advisor: student.counselor_names && Array.isArray(student.counselor_names) ? student.counselor_names.join(', ') : 
                 student.advisor_name || '',
        grade: student.grade || '',
        contact: student.contact || student.phone || '',
        email: student.email || '',
        last_login: student.last_login || '',
        // 保存原始的college和class对象，用于编辑时获取ID
        _original_college: college_obj, // 保存原始学院对象
        _original_class: class_obj // 保存原始班级对象
      };
      
      return mappedStudent;
    })
    console.log('映射后的学生数据:', students.value); // 调试日志
  } catch (error) {
    console.error('获取学生列表失败:', error)
    message.error('获取学生列表失败: ' + (error.response?.data?.error || error.message))
    students.value = []
  } finally {
    loading.value = false
  }
}

// 获取学院列表
const fetchColleges = async () => {
  try {
    const response = await api.admin.getColleges()
    // 处理不同的数据结构
    colleges.value = Array.isArray(response) ? response : 
                    response?.colleges || 
                    response?.data || 
                    response?.results || []
  } catch (error) {
    console.error('获取学院列表失败:', error)
    message.error('获取学院列表失败: ' + (error.response?.data?.message || error.message))
    colleges.value = []
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await api.admin.classes.getClasses()
    // 处理不同的数据结构
    classes.value = Array.isArray(response) ? response : 
                   response?.classes || 
                   response?.data || 
                   response?.results || []
    console.log('班级数据结构:', classes.value)
  } catch (error) {
    console.error('获取班级列表失败:', error)
    message.error('获取班级列表失败: ' + (error.response?.data?.message || error.message))
    classes.value = []
  }
}

// 搜索
const handleSearch = () => {
  // 搜索功能已通过计算属性实现，这里可以添加额外的搜索逻辑
  console.log('搜索关键词:', searchKeyword.value)
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
}

// 添加学生
const handleAddStudent = () => {
  studentModalTitle.value = '添加学生'
  selectedStudentId.value = null
  resetStudentForm()
  studentModalVisible.value = true
}

// 编辑学生
const handleEditStudent = (record) => {
  studentModalTitle.value = '编辑学生'
  selectedStudentId.value = record.id
  // 填充表单
  studentForm.studentId = record.studentId
  studentForm.name = record.name
  studentForm.gender = record.gender
  studentForm.gpa = record.gpa || 0
  
  // 通过学院名称查找学院ID - 支持对象格式和直接名称格式
  let collegeName = ''
  if (record.college && typeof record.college === 'object') {
    collegeName = record.college.name
  } else {
    collegeName = record.college
  }
  const collegeObj = colleges.value.find(c => c.name === collegeName)
  studentForm.college = collegeObj ? collegeObj.id : ''
  
  // 使用nextTick确保college设置后，filteredClasses更新
  nextTick(() => {
    // 优化班级信息获取逻辑 - 支持多种数据格式
    let classId = ''
    // 优先使用保存的原始班级对象
    if (record._original_class && record._original_class.id) {
      classId = record._original_class.id
    } else if (record.class && record.class.id) {
      // 兼容直接包含class对象的情况
      classId = record.class.id
    } else if (record.class_name) {
      // 通过班级名称查找班级ID - 优先使用filteredClasses
      const classObj = filteredClasses.value.find(c => c.name === record.class_name)
      // 如果在filteredClasses中找不到，尝试在所有班级中查找
      const fallbackClassObj = classObj || classes.value.find(c => c.name === record.class_name)
      classId = fallbackClassObj ? fallbackClassObj.id : ''
    }
    studentForm.class_name = classId
  })
  
  studentModalVisible.value = true
}

// 查看学生详情
const handleViewStudent = (record) => {
  selectedStudent.value = record
  viewModalVisible.value = true
}

// 重置学生密码
const handleResetPassword = (record) => {
  selectedStudentForReset.value = record
  resetPasswordModalVisible.value = true
}

// 删除学生
const handleDeleteStudent = (record) => {
  selectedStudentForDelete.value = record
  deleteModalVisible.value = true
}

// 提交学生表单（添加/编辑）
const handleSubmitStudent = async () => {
  if (!studentFormRef.value) return
  
  try {
    await studentFormRef.value.validate()
    
    // 查找选择的班级信息，获取年级
    const selectedClass = classes.value.find(cls => cls.id === studentForm.class_name)
    
    // 构建提交数据
    const submitData = {
      school_id: studentForm.studentId, // 映射到后端的school_id字段
      password: studentForm.studentId.slice(-6), // 密码设置为学号后六位
      name: studentForm.name,
      gender: studentForm.gender,
      college: studentForm.college,
      class_id: studentForm.class_name, // 直接使用班级ID
      grade: selectedClass ? selectedClass.grade : '', // 从选择的班级中获取年级
      gpa: studentForm.gpa,
      user_type: 'student'
    }
    
    if (selectedStudentId.value) {
      // 编辑学生
      await api.admin.updateUser(selectedStudentId.value, submitData)
      message.success('学生信息更新成功')
    } else {
      // 添加学生
      await api.admin.addUser(submitData)
      message.success('学生添加成功，密码已设置为学号后六位')
    }
    
    // 关闭模态框、重置表单并刷新列表
    studentModalVisible.value = false
    resetStudentForm()
    await fetchStudents()
  } catch (error) {
    console.error('保存学生信息失败:', error)
    message.error('保存失败: ' + (error.response?.data?.message || error.message))
  }
}

// 确认重置密码
const handleConfirmResetPassword = async () => {
  if (!selectedStudentForReset.value) return
  
  try {
    await api.admin.resetPassword(selectedStudentForReset.value.id)
    message.success('密码重置成功，新密码为学号后六位')
    resetPasswordModalVisible.value = false
  } catch (error) {
    console.error('重置密码失败:', error)
    message.error('重置密码失败: ' + (error.response?.data?.message || error.message))
  }
}

// 确认删除学生
const handleConfirmDelete = async () => {
  if (!selectedStudentForDelete.value) return
  
  try {
    await api.admin.deleteUser(selectedStudentForDelete.value.id)
    message.success('学生删除成功')
    deleteModalVisible.value = false
    // 刷新列表
    await fetchStudents()
  } catch (error) {
    console.error('删除学生失败:', error)
    message.error('删除失败: ' + (error.response?.data?.message || error.message))
  }
}

// 取消学生表单
const handleCancelStudent = () => {
  studentModalVisible.value = false
  resetStudentForm()
}

// 关闭查看详情模态框
const handleCloseViewModal = () => {
  viewModalVisible.value = false
  selectedStudent.value = null
}

// 取消重置密码
const handleCancelResetPassword = () => {
  resetPasswordModalVisible.value = false
  selectedStudentForReset.value = null
}

// 取消删除
const handleCancelDelete = () => {
  deleteModalVisible.value = false
  selectedStudentForDelete.value = null
}

// 打开添加学院模态框
const handleAddCollegeModal = () => {
  collegeModalVisible.value = true
  collegeForm.name = ''
  collegeForm.code = ''
}

// 关闭添加学院模态框
const handleCancelCollege = () => {
  collegeModalVisible.value = false
  collegeForm.name = ''
  collegeForm.code = ''
}

// 添加学院
const handleAddCollege = async () => {
  if (!collegeFormRef.value) return
  
  try {
    await collegeFormRef.value.validate()
    
    await api.admin.createCollege(collegeForm)
    message.success('学院添加成功')
    
    // 刷新学院列表
    await fetchColleges()
    
    // 如果学生表单中没有选择学院，自动选中新添加的学院
    if (!studentForm.college) {
      const newCollege = colleges.value.find(c => c.name === collegeForm.name)
      if (newCollege) {
        studentForm.college = newCollege.name
      }
    }
    
    // 关闭模态框
    handleCancelCollege()
  } catch (error) {
    console.error('添加学院失败:', error)
    message.error('添加学院失败: ' + (error.response?.data?.message || error.message))
  }
}

// 打开添加班级模态框
const handleAddClassModal = () => {
  classModalVisible.value = true
  classForm.name = ''
  classForm.grade = ''
  classForm.college_id = ''
  
  // 如果学生表单中选择了学院，自动设置班级的学院
  if (studentForm.college) {
    const selectedCollege = colleges.value.find(c => c.name === studentForm.college)
    if (selectedCollege) {
      classForm.college_id = selectedCollege.id
    }
  }
}

// 关闭添加班级模态框
const handleCancelClass = () => {
  classModalVisible.value = false
  classForm.name = ''
  classForm.grade = ''
  classForm.college_id = ''
}

// 添加班级
const handleAddClass = async () => {
  if (!classFormRef.value) return
  
  try {
    await classFormRef.value.validate()
    
    // 构建提交数据，将college_id映射为college字段
    const submitData = {
      name: classForm.name,
      grade: classForm.grade,
      college: classForm.college_id  // 后端期望的字段名是college
    }
    
    await api.admin.classes.createClass(submitData)
    message.success('班级添加成功')
    
    // 刷新班级列表
    await fetchClasses()
    
    // 如果学生表单中没有选择班级，自动选中新添加的班级
    if (!studentForm.class_name) {
      const newClass = classes.value.find(cls => cls.name === classForm.name)
      if (newClass) {
        studentForm.class_name = newClass.name
      }
    }
    
    // 关闭模态框
    handleCancelClass()
  } catch (error) {
    console.error('添加班级失败:', error)
    message.error('添加班级失败: ' + (error.response?.data?.message || error.message))
  }
}

// 重置学生表单
const resetStudentForm = () => {
  studentForm.studentId = ''
  studentForm.name = ''
  studentForm.gender = ''
  studentForm.college = ''
  studentForm.class_name = ''
  studentForm.gpa = 0
  if (studentFormRef.value) {
    studentFormRef.value.resetFields()
  }
}

// 导入前处理
const handleBeforeUpload = async (file) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    await api.admin.student.importStudents(formData)
    message.success('学生导入成功')
    // 刷新列表
    await fetchStudents()
  } catch (error) {
    console.error('导入学生失败:', error)
    message.error('导入失败: ' + (error.response?.data?.message || error.message))
  }
  return false // 阻止默认上传
}

// 导出Excel
const handleExport = async () => {
  try {
    const response = await api.admin.student.exportScores()
    // 创建下载链接
    const blob = new Blob([response], { type: 'application/vnd.ms-excel' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `学生信息_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    console.error('导出学生信息失败:', error)
    message.error('导出失败: ' + (error.response?.data?.message || error.message))
  }
}

// 页面加载时获取数据
onMounted(async () => {
  await fetchColleges()
  await fetchClasses()
  await fetchStudents()
})
</script>

<style scoped>
.admin-students {
  padding: 20px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.search-section {
  margin-bottom: 20px;
}

.students-list {
  margin-top: 20px;
}

.student-detail {
  max-height: 600px;
  overflow-y: auto;
}

.password-tip {
  margin-bottom: 0;
}
</style>