<template>
  <div class="student-profile">
    <a-card title="个人信息" class="profile-card">
      <div class="profile-actions">
        <a-button 
          v-if="!isEditing" 
          type="primary" 
          @click="startEditing"
        >
          编辑信息
        </a-button>
      </div>
      <a-form
        :model="form"
        :rules="rules"
        ref="formRef"
        class="profile-form"
        @finish="handleSubmit"
      >
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="form.name" placeholder="请输入姓名" :disabled="!isEditing" />
        </a-form-item>
        <a-form-item label="学号" name="studentId">
          <a-input v-model:value="form.studentId" placeholder="请输入学号" disabled />
        </a-form-item>
        <a-form-item label="班级" name="className">
          <a-input v-model:value="form.className" placeholder="请输入班级" disabled />
        </a-form-item>
        <a-form-item label="学院" name="college">
          <a-input v-model:value="form.college" placeholder="请输入学院" disabled />
        </a-form-item>
        <a-form-item label="手机号" name="phone">
          <a-input v-model:value="form.phone" placeholder="请输入手机号" :disabled="!isEditing" />
        </a-form-item>
        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="form.email" placeholder="请输入邮箱" :disabled="!isEditing" />
        </a-form-item>
        <a-form-item label="性别" name="gender">
          <a-select v-model:value="form.gender" placeholder="请选择性别" :disabled="!isEditing">
            <a-select-option value="male">男</a-select-option>
            <a-select-option value="female">女</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="出生日期" name="birthDate">
          <a-date-picker v-model:value="form.birthDate" placeholder="请选择出生日期" style="width: 100%;" :disabled="!isEditing" />
        </a-form-item>
        <a-form-item label="上一次登录" name="lastLogin" style="color: #999;">
          <div>{{ lastLoginTime || '未登录过' }}</div>
        </a-form-item>
        <a-form-item v-if="isEditing">
          <a-button type="primary" html-type="submit" class="save-button" :loading="loading" style="margin-right: 8px;">
            保存信息
          </a-button>
          <a-button @click="cancelEditing">
            取消
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="修改密码" class="profile-card password-card">
      <a-collapse v-model:active-key="activeKey">
        <a-collapse-panel key="1" header="修改密码">
          <a-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            class="password-form"
            @finish="handlePasswordChange"
          >
            <a-form-item label="当前密码" name="oldPassword">
              <a-input-password v-model:value="passwordForm.oldPassword" placeholder="请输入当前密码" />
            </a-form-item>
            <a-form-item label="新密码" name="newPassword">
              <a-input-password v-model:value="passwordForm.newPassword" placeholder="请输入新密码" />
            </a-form-item>
            <a-form-item label="确认新密码" name="confirmPassword">
              <a-input-password v-model:value="passwordForm.confirmPassword" placeholder="请再次输入新密码" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="passwordLoading">
                修改密码
              </a-button>
            </a-form-item>
          </a-form>
        </a-collapse-panel>
      </a-collapse>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { message } from 'ant-design-vue'
import api from '../../utils/api'
import dayjs from 'dayjs'

const formRef = ref(null)
const loading = ref(false)

// 编辑状态管理
const isEditing = ref(false)
const originalForm = ref({})

// 密码修改相关变量
const passwordFormRef = ref(null)
const passwordLoading = ref(false)
const activeKey = ref([])

const form = reactive({
  name: '',
  studentId: '',
  className: '',
  college: '',
  phone: '',
  email: '',
  gender: '',
  birthDate: null
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 上一次登录时间
const lastLoginTime = ref('')

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        if (!value || passwordForm.newPassword === value) {
          return Promise.resolve()
        }
        return Promise.reject(new Error('两次输入的密码不一致'))
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await api.student.getCurrentUser()
    // 处理不同的返回格式
    const data = response.data || response
    
    console.log('获取到的用户信息:', data)
    
    // 填充表单数据，兼容后端API的字段名
    form.name = data.name || ''
    
    // 处理学号信息 - 后端返回的是school_id
    form.studentId = data.school_id || data.student_id || data.studentId || data.schoolId || ''
    
    // 处理班级信息 - 后端返回的是class_name
    form.className = data.class_name || data.className || ''
    
    // 处理学院信息 - 后端返回的是college_name
    form.college = data.college_name || data.department_name || data.department || ''
    
    form.phone = data.phone || data.mobile || ''
    form.email = data.email || ''
    form.gender = data.gender || ''
    form.birthDate = data.birth_date ? dayjs(data.birth_date) : null
    
    // 设置上一次登录时间
    if (data.last_login) {
      lastLoginTime.value = new Date(data.last_login).toLocaleString()
    }
    
    console.log('填充后的表单数据:', form)
  } catch (error) {
    console.error('获取用户信息失败:', error)
    message.error('获取用户信息失败: ' + (error.message || '未知错误'))
  }
}

// 开始编辑
const startEditing = () => {
  // 保存原始表单数据，用于取消编辑时恢复
  originalForm.value = {
    ...form
  }
  isEditing.value = true
}

// 取消编辑
const cancelEditing = () => {
  // 恢复原始表单数据
  Object.assign(form, originalForm.value)
  isEditing.value = false
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 保存用户信息
const handleSubmit = async (values) => {
  try {
    loading.value = true
    
    // 转换为后端API需要的数据格式
    const requestData = {
      name: values.name,
      phone: values.phone,
      email: values.email,
      gender: values.gender,
      birth_date: values.birthDate ? values.birthDate.format('YYYY-MM-DD') : null
    }
    
    // 调用API保存用户信息
    await api.student.updateProfile(requestData)
    
    // 更新本地存储的用户信息
    const userInfo = JSON.parse(localStorage.getItem('user'))
    localStorage.setItem('user', JSON.stringify({ ...userInfo, ...values }))
    
    // 更新form对象，确保页面显示最新信息
    form.name = values.name
    form.phone = values.phone
    form.email = values.email
    form.gender = values.gender
    form.birthDate = values.birthDate
    
    message.success('个人信息保存成功')
    loading.value = false
    
    // 保存成功后退出编辑状态
    isEditing.value = false
    
  } catch (error) {
    loading.value = false
    message.error('保存失败：' + (error.response?.data?.message || error.message || '未知错误'))
  }
}

// 修改密码
const handlePasswordChange = async (values) => {
  try {
    passwordLoading.value = true
    
    // 调用API修改密码
    await api.student.updateProfile({
      old_password: values.oldPassword,
      new_password: values.newPassword
    })
    
    message.success('密码修改成功')
    passwordLoading.value = false
    
    // 重置密码表单
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    if (passwordFormRef.value) {
      passwordFormRef.value.resetFields()
    }
    
  } catch (error) {
    passwordLoading.value = false
    message.error('密码修改失败：' + (error.response?.data?.message || error.message || '未知错误'))
  }
}

onMounted(() => {
  fetchUserInfo()
  
  // 添加页面离开前的确认提示
  window.addEventListener('beforeunload', handleBeforeUnload)
})

// 组件卸载前清理
onBeforeUnmount(() => {
  // 移除页面离开前的确认提示
  window.removeEventListener('beforeunload', handleBeforeUnload)
  
  // 重置编辑状态
  if (isEditing.value) {
    cancelEditing()
  }
})

// 页面离开前的确认提示
const handleBeforeUnload = (event) => {
  if (isEditing.value) {
    event.preventDefault()
    event.returnValue = '您有未保存的修改，确定要离开吗？'
  }
}
</script>

<style scoped>
.student-profile {
  padding: 20px;
}

.profile-card {
  max-width: 800px;
}

.profile-actions {
  text-align: right;
  margin-bottom: 16px;
}

.profile-form {
  max-width: 600px;
}

.save-button {
  width: 150px;
}
</style>