<template>
  <div class="register-container">
    <div class="register-form-wrapper">
      <h2 class="register-title">学生综合素质加分系统</h2>
      <a-form
        :model="form"
        :rules="rules"
        ref="formRef"
        class="register-form"
      >
        <a-form-item label="用户名" name="username">
          <a-input
            v-model:value="form.username"
            placeholder="请输入用户名"
            prefix-icon="<UserOutlined />"
          />
        </a-form-item>

        <a-form-item label="真实姓名" name="realName">
          <a-input
            v-model:value="form.realName"
            placeholder="请输入真实姓名"
            prefix-icon="<UserOutlined />"
          />
        </a-form-item>

        <a-form-item label="密码" name="password">
          <a-input-password
            v-model:value="form.password"
            placeholder="请输入密码"
            prefix-icon="<LockOutlined />"
          />
        </a-form-item>

        <a-form-item label="确认密码" name="confirmPassword">
          <a-input-password
            v-model:value="form.confirmPassword"
            placeholder="请确认密码"
            prefix-icon="<LockOutlined />"
          />
        </a-form-item>

        <a-form-item label="角色" name="role">
          <a-select
            v-model:value="form.role"
            placeholder="请选择角色"
          >
            <a-select-option value="student">学生</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="班级/院系" name="classOrDept">
          <a-input
            v-model:value="form.classOrDept"
            placeholder="学生请输入班级，教师请输入院系"
            prefix-icon="<TeamOutlined />"
          />
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            class="register-button"
            :loading="loading"
          >
            注册
          </a-button>
        </a-form-item>

        <div class="register-footer">
          <a href="/" class="login-link">已有账号？立即登录</a>
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, TeamOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  realName: '',
  password: '',
  confirmPassword: '',
  role: 'student',
  classOrDept: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 20, message: '用户名长度在 4 到 20 个字符', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    ({ getFieldValue }) => ({
      validator(_, value) {
        if (!value || getFieldValue('password') === value) {
          return Promise.resolve()
        }
        return Promise.reject(new Error('两次输入的密码不一致'))
      },
      trigger: 'blur'
    })
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  classOrDept: [
    { required: true, message: '请输入班级或院系', trigger: 'blur' }
  ]
}

// 注册提交
const handleSubmit = async (values) => {
  try {
    loading.value = true
    
    // 这里模拟注册请求，实际项目中应该调用后端API
    // const response = await axios.post('/api/register', values)
    
    // 模拟注册成功
    setTimeout(() => {
      // 注册成功，保存临时用户信息
      const tempUserInfo = {
        username: values.username,
        name: values.realName,
        role: values.role,
        class: values.role === 'student' ? values.classOrDept : undefined,
        department: values.role === 'teacher' ? values.classOrDept : undefined
      }
      localStorage.setItem('tempUserInfo', JSON.stringify(tempUserInfo))
      
      message.success('注册成功！请设置TOTP验证码')
      router.push('/totp-setup')
      loading.value = false
    }, 1000)
    
  } catch (error) {
    loading.value = false
    message.error('注册失败：' + (error.message || '未知错误'))
  }
}

// 监听表单提交
if (formRef.value) {
  formRef.value.onFinish = handleSubmit
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.register-form-wrapper {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 32px;
  width: 100%;
  max-width: 400px;
}

.register-title {
  text-align: center;
  margin-bottom: 24px;
  color: #1890ff;
}

.register-form {
  width: 100%;
}

.register-button {
  width: 100%;
  height: 40px;
}

.register-footer {
  text-align: center;
  margin-top: 16px;
}

.login-link {
  color: #1890ff;
}
</style>