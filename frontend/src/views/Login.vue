<template>
  <div class="login-container">
    <a-card title="学生综合素质加分系统" class="login-card">
      <a-form
        :model="form"
        :rules="rules"
        ref="formRef"
        class="login-form"
        @finish="handleSubmit"
      >
        <a-form-item label="登录角色" name="role">
          <a-select
            v-model:value="form.role"
            placeholder="请选择登录角色"
          >
            <a-select-option value="student">学生</a-select-option>
            <a-select-option value="teacher">教师</a-select-option>
            <a-select-option value="admin">超管</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="用户名" name="username">
          <a-input
            v-model:value="form.username"
            placeholder="请输入用户名"
          >
            <template #prefix-icon>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item label="密码" name="password">
          <a-input-password
            v-model:value="form.password"
            placeholder="请输入密码"
            visibilityToggle
            autocomplete="current-password"
          >
            <template #prefix-icon>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>
        <a-form-item label="验证码" name="captcha">
          <a-input
            v-model:value="form.captcha"
            placeholder="请输入验证码"
            style="width: 60%"
          >
            <template #prefix-icon>
              <SafetyCertificateOutlined />
            </template>
          </a-input>
          <div class="captcha-image" @click="refreshCaptcha">
            <div v-html="captchaSvg"></div>
          </div>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            class="login-button"
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>

      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, SafetyCertificateOutlined } from '@ant-design/icons'
import api from '../utils/api'


const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  captcha: '',
  role: 'student' // 默认选择学生角色
})

const captchaText = ref('')
const captchaSvg = ref('')
const refreshCaptcha = () => {
  // 自定义浏览器兼容的SVG验证码生成 - 增加错误处理
  try {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // 排除容易混淆的字符
    const size = 4;
    let text = '';
    
    // 生成随机文本
    for (let i = 0; i < size; i++) {
      text += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    captchaText.value = text;
    
    // SVG验证码配置
    const width = 120;
    const height = 40;
    const fontSize = 24;
    const noiseLines = 3;
    
    // 生成随机颜色
    const getRandomColor = (min, max) => {
      const r = Math.floor(Math.random() * (max - min + 1)) + min;
      const g = Math.floor(Math.random() * (max - min + 1)) + min;
      const b = Math.floor(Math.random() * (max - min + 1)) + min;
      return `rgb(${r},${g},${b})`;
    };
    
    // 创建SVG元素
    let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg" style="background-color: #f0f0f0;">`;
    
    // 添加干扰线
    for (let i = 0; i < noiseLines; i++) {
      const x1 = Math.random() * width;
      const y1 = Math.random() * height;
      const x2 = Math.random() * width;
      const y2 = Math.random() * height;
      svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${getRandomColor(150, 200)}" stroke-width="1" />`;
    }
    
    // 添加验证码文本
    const textX = 20;
    const textY = height / 2 + fontSize / 3;
    
    for (let i = 0; i < text.length; i++) {
      const char = text.charAt(i);
      const x = textX + i * 24;
      const rotate = (Math.random() - 0.5) * 30; // -15到15度的旋转
      svg += `<text x="${x}" y="${textY}" font-size="${fontSize}" font-family="Arial, sans-serif" fill="${getRandomColor(50, 150)}" transform="rotate(${rotate} ${x} ${textY})" font-weight="bold">${char}</text>`;
    }
    
    svg += '</svg>';
    captchaSvg.value = svg;
  } catch (error) {
    console.error('验证码生成失败:', error);
    // 提供一个简单的文本验证码作为后备
    captchaSvg.value = `<div style="width: 120px; height: 40px; background-color: #f0f0f0; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 24px; color: #333; letter-spacing: 4px;">${captchaText.value}</div>`;
  }
}

const rules = {
  role: [
    { required: true, message: '请选择登录角色', trigger: 'change' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ],

}

// 登录提交
const handleSubmit = async (values) => {
  try {
    loading.value = true
    
    // 验证图形验证码
    if (values.captcha.toUpperCase() !== captchaText.value) {
      message.error('验证码错误，请重新输入')
      refreshCaptcha() // 刷新验证码
      loading.value = false
      return
    }
    
    console.log('准备登录，参数：', values)
    
    // 调用API进行登录，传递角色信息和验证码文本
    const response = await api.login(values.username, values.password, values.role, values.captcha)
    
    console.log('登录API响应：', response)
    
    // 提取token并存储
    let token = null;
    let userInfo = null;
    
    // 检查多种可能的响应格式
    const responseData = response.data || response;
    
    // 提取token
    if (responseData.token) {
      token = responseData.token;
      console.log('从响应中获取到token');
    } else if (responseData.access_token) {
      token = responseData.access_token;
      console.log('从响应中获取到access_token');
    } else {
      console.error('登录响应中未找到token:', responseData);
      throw new Error('登录成功但未获取到访问令牌');
    }
    
    // 提取用户信息
    if (responseData.user) {
      userInfo = responseData.user;
      console.log('从响应中直接获取到用户信息');
    } else if (responseData.data && responseData.data.user) {
      userInfo = responseData.data.user;
      console.log('从响应data.user中获取到用户信息');
    } else {
      // 直接使用responseData作为用户信息
      userInfo = responseData;
      console.log('使用响应数据作为用户信息');
    }
    
    // 三级存储token，提高可靠性
    if (token) {
      console.log('登录成功，获取到token:', token);
      
      // 本地存储
      try {
        localStorage.setItem('token', token);
        console.log('Token已存入localStorage');
      } catch (e) {
        console.error('localStorage存储token失败:', e);
      }
      
      // 会话存储
      try {
        sessionStorage.setItem('token', token);
        console.log('Token已存入sessionStorage');
      } catch (e) {
        console.error('sessionStorage存储token失败:', e);
      }
      
      // Cookie存储 - 使用更安全的方式
      try {
        // 设置24小时过期时间，与后端一致
        const expirationDate = new Date();
        expirationDate.setTime(expirationDate.getTime() + (24 * 60 * 60 * 1000));
        const expires = `expires=${expirationDate.toUTCString()}`;
        document.cookie = `token=${encodeURIComponent(token)}; path=/; ${expires}; SameSite=Lax`;
        console.log('Token已存入Cookie');
      } catch (e) {
        console.error('Cookie存储token失败:', e);
      }
    }
    
    // 处理用户信息，确保正确的角色映射
    const userTypeMap = {
      0: 'student',
      1: 'teacher', 
      2: 'admin'
    }
    
    // 安全地获取角色信息，兼容多种返回格式
    let userRole = userInfo.user_type || userInfo.role || values.role;
    
    // 确保user_type转换为正确的字符串格式
    if (typeof userRole === 'number') {
      userRole = userTypeMap[userRole] || values.role;
    } else if (!userRole || typeof userRole !== 'string') {
      userRole = values.role;
    }
    
    // 构建最终的用户信息
    const finalUserInfo = {
      ...userInfo,
      role: userRole,
      user_type: userRole,
      school_id: userInfo.school_id || values.username,
      name: userInfo.name || '未知用户'
    }
    
    console.log('最终的用户信息：', finalUserInfo)
    
    // 存储最终的用户信息
    try {
      localStorage.setItem('user', JSON.stringify(finalUserInfo))
      console.log('用户信息已存储到localStorage');
    } catch (storageError) {
      console.error('本地存储用户信息失败:', storageError);
    }
    
    message.success('登录成功！')
    
    // 根据用户角色跳转到对应首页
    try {
      if (finalUserInfo.role === 'student') {
        router.push({ name: 'StudentHome' })
      } else if (finalUserInfo.role === 'teacher') {
        router.push({ name: 'TeacherHome' })
      } else if (finalUserInfo.role === 'admin') {
        router.push({ name: 'AdminHome' })
      } else {
        message.error('未知用户角色，请联系管理员')
        router.push({ name: 'Login' })
      }
      console.log('已跳转到对应角色的首页');
    } catch (routerError) {
      console.error('路由跳转失败:', routerError)
      message.error('页面跳转失败，请手动刷新页面')
    }
  } catch (error) {
    loading.value = false
    console.error('登录失败错误详情：', error)
    console.error('错误响应数据：', error.response?.data || error.data)
    console.error('错误状态码：', error.response?.status || error.status)
    console.error('错误配置：', error.config)
    
    // 更加健壮的错误信息提取
    let errorMsg = '登录失败';
    
    try {
      // 检查错误对象中是否有响应数据
      const errorData = error.response?.data || error.data || error;
      
      if (errorData.error) {
        errorMsg = errorData.error;
      } else if (errorData.message) {
        errorMsg = errorData.message;
      } else if (errorData.detail) {
        errorMsg = errorData.detail;
      } else if (typeof errorData === 'string') {
        errorMsg = errorData;
      } else if (error.response?.status === 401) {
        errorMsg = '用户名或密码错误';
      } else if (typeof errorData === 'object') {
        // 处理可能的字段错误
        const fieldErrors = Object.entries(errorData)
          .map(([field, errors]) => `${field}：${Array.isArray(errors) ? errors.join('、') : errors}`)
          .join('\n');
        errorMsg += '：' + fieldErrors;
      } else {
        errorMsg += '：未知错误';
      }
    } catch (parseError) {
      console.error('解析错误信息失败:', parseError);
    } finally {
      // 确保在登录页面显示错误信息
      message.error(errorMsg);
    }
    
    // 刷新验证码
    refreshCaptcha();
  } finally {
    loading.value = false;
  }
}

// 初始化 - 增加错误处理，防止页面白屏
onMounted(() => {
  try {
    refreshCaptcha()
  } catch (error) {
    console.error('初始化验证码失败:', error)
    // 显示一个简单的文本验证码作为后备
    captchaText.value = 'TEST1'
    captchaSvg.value = `<div style="width: 120px; height: 40px; background-color: #f0f0f0; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 24px; color: #333; letter-spacing: 4px;">${captchaText.value}</div>`
    message.warning('验证码加载失败，使用默认验证码: TEST1')
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.login-form-wrapper {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 24px;
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
}

.login-title {
  text-align: center;
  margin-bottom: 20px;
  color: #1890ff;
  font-size: 20px;
}

.login-form {
  width: 100%;
}

.login-button {
  width: 100%;
  height: 40px;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 12px;
  }
  
  .login-form-wrapper {
    padding: 20px;
  }
  
  .login-title {
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .login-button {
    height: 36px;
  }
}

/* 注册功能已移除，相关样式已清理 */
</style>