<template>
  <div class="admin-settings">
    <h2>系统设置</h2>
    
    <div class="settings-container">
      <!-- TOTP身份验证设置 -->
      <a-card class="settings-card" title="TOTP身份验证">
        <div class="totp-settings">
          <div class="setting-item">
            <div class="setting-label">
              <span>TOTP验证状态</span>
              <a-tooltip title="开启后登录时需要输入TOTP验证码">
                <InfoCircleOutlined style="margin-left: 8px; color: #1890ff;" />
              </a-tooltip>
            </div>
            <div class="setting-value">
              <a-switch 
                v-model:checked="totpSettings.enabled" 
                @change="handleToggleTOTP" 
                :disabled="totpSettings.binding || totpSettings.unbinding"
              />
              <span class="status-text">
                {{ totpSettings.enabled ? '已开启' : '已关闭' }}
              </span>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-label">绑定状态</div>
            <div class="setting-value">
              <a-tag :color="totpSettings.bound ? 'green' : 'red'">
                {{ totpSettings.bound ? '已绑定' : '未绑定' }}
              </a-tag>
            </div>
          </div>
          
          <div class="setting-actions">
            <a-button 
              type="primary" 
              @click="handleBindTOTP" 
              v-if="!totpSettings.bound && totpSettings.enabled"
              :loading="totpSettings.binding"
            >
              绑定TOTP
            </a-button>
            <a-button 
              danger 
              @click="handleUnbindTOTP" 
              v-if="totpSettings.bound"
              :loading="totpSettings.unbinding"
            >
              解除绑定
            </a-button>
          </div>
        </div>
      </a-card>

      <!-- 密码修改 -->
      <a-card class="settings-card" title="密码修改">
        <a-form :model="passwordForm" layout="vertical" :rules="passwordRules" ref="passwordFormRef">
          <a-form-item label="当前密码" name="currentPassword">
            <a-input-password v-model:value="passwordForm.currentPassword" placeholder="请输入当前密码" />
          </a-form-item>
          <a-form-item label="新密码" name="newPassword">
            <a-input-password v-model:value="passwordForm.newPassword" placeholder="请输入新密码" />
            <div class="password-hint">密码长度至少为6位，建议包含字母、数字和特殊字符</div>
          </a-form-item>
          <a-form-item label="确认新密码" name="confirmPassword">
            <a-input-password v-model:value="passwordForm.confirmPassword" placeholder="请确认新密码" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
              确认修改
            </a-button>
          </a-form-item>
        </a-form>
      </a-card>

      <!-- 账号安全信息 -->
      <a-card class="settings-card" title="账号安全信息">
        <div class="security-info">
          <div class="info-item">
            <span class="info-label">账号名称:</span>
            <span class="info-value">{{ currentUser.username }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">用户角色:</span>
            <a-tag color="blue">{{ currentUser.role === 'admin' ? '超级管理员' : currentUser.role }}</a-tag>
          </div>
          <div class="info-item">
            <span class="info-label">最后登录时间:</span>
            <span class="info-value">{{ currentUser.lastLoginAt || '首次登录' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">密码修改时间:</span>
            <span class="info-value">{{ currentUser.passwordUpdatedAt || '未修改' }}</span>
          </div>
        </div>
      </a-card>
    </div>

    <!-- TOTP绑定模态框 -->
    <a-modal
      v-model:open="totpModalVisible"
      title="绑定TOTP身份验证"
      @ok="handleConfirmBindTOTP"
      @cancel="resetTOTPForm"
      width="500px"
    >
      <div class="totp-modal-content">
        <div class="totp-intro">
          <p>请使用Google Authenticator或其他TOTP认证应用扫描以下二维码：</p>
        </div>
        <div class="qrcode-container">
          <img v-if="totpSettings.qrCode" :src="totpSettings.qrCode" alt="TOTP QR Code" class="qrcode" />
          <div v-else class="qrcode-placeholder">
            <LoadingOutlined spin style="font-size: 48px; color: #1890ff;" />
          </div>
        </div>
        <div class="totp-secret">
          <p class="secret-label">备用密钥 (如果无法扫描二维码):</p>
          <div class="secret-code">{{ totpSettings.secretKey || '生成中...' }}</div>
          <a-button type="link" size="small" @click="copySecretKey" style="margin-top: 8px;">
            复制密钥
          </a-button>
        </div>
        <a-form :model="totpForm" layout="vertical" :rules="totpRules" ref="totpFormRef">
          <a-form-item label="验证码" name="code">
            <a-input-number 
              v-model:value="totpForm.code" 
              placeholder="请输入6位验证码" 
              :min="100000" 
              :max="999999" 
              style="width: 100%" 
              :disabled="!totpSettings.secretKey"
            />
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- TOTP解绑确认模态框 -->
    <a-modal
      v-model:open="unbindModalVisible"
      title="确认解除绑定"
      @ok="handleConfirmUnbindTOTP"
      @cancel="unbindModalVisible = false"
    >
      <p>确定要解除TOTP身份验证绑定吗？解除后将不再需要TOTP验证码登录，但账号安全性会降低。</p>
      <a-form :model="unbindForm" layout="vertical" :rules="unbindRules" ref="unbindFormRef">
        <a-form-item label="当前密码" name="password">
          <a-input-password v-model:value="unbindForm.password" placeholder="请输入当前密码以确认" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { InfoCircleOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import api from '../../utils/api'

// 当前用户信息
const currentUser = ref({
  username: 'admin',
  role: 'admin',
  lastLoginAt: '2023-10-10 14:30:00',
  passwordUpdatedAt: '2023-09-01 08:00:00'
})

// TOTP设置
const totpSettings = reactive({
  enabled: true,
  bound: false,
  secretKey: '',
  qrCode: '',
  binding: false,
  unbinding: false
})

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码表单规则
const passwordRules = {
  currentPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
    ({ getFieldValue }) => ({
      validator(_, value) {
        if (!value || getFieldValue('currentPassword') !== value) {
          return Promise.resolve()
        }
        return Promise.reject(new Error('新密码不能与当前密码相同'))
      },
      trigger: 'blur'
    })
  ],
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

// 密码表单引用
const passwordFormRef = ref(null)
const passwordLoading = ref(false)

// TOTP绑定模态框
const totpModalVisible = ref(false)
const totpForm = reactive({
  code: null
})

// TOTP表单规则
const totpRules = {
  code: [{ required: true, message: '请输入6位验证码', trigger: 'blur' }]
}

// TOTP表单引用
const totpFormRef = ref(null)

// 解绑确认模态框
const unbindModalVisible = ref(false)
const unbindForm = reactive({
  password: ''
})

// 解绑表单规则
const unbindRules = {
  password: [{ required: true, message: '请输入当前密码以确认', trigger: 'blur' }]
}

// 解绑表单引用
const unbindFormRef = ref(null)

// 切换TOTP状态
const handleToggleTOTP = async (checked) => {
  try {
    // 调用API更新TOTP状态
    message.success(`TOTP验证已${checked ? '开启' : '关闭'}`)
  } catch (error) {
    // 恢复原状
    totpSettings.enabled = !checked
    message.error(`操作失败: ${error.response?.data?.message || error.message}`)
  }
}

// 绑定TOTP
const handleBindTOTP = async () => {
  totpSettings.binding = true
  try {
    // 调用API生成TOTP密钥和二维码
    // 模拟API响应
    totpSettings.secretKey = 'JBSWY3DPEHPK3PXP'
    totpSettings.qrCode = 'https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=otpauth%3A%2F%2Ftotp%2FAdmin%3Aadmin%40example.com%3Fsecret%3DJBSWY3DPEHPK3PXP%26issuer%3DAdmin'
    
    totpModalVisible.value = true
  } catch (error) {
    message.error(`生成TOTP密钥失败: ${error.response?.data?.message || error.message}`)
  } finally {
    totpSettings.binding = false
  }
}

// 确认绑定TOTP
const handleConfirmBindTOTP = async () => {
  if (!totpFormRef.value) return
  
  try {
    await totpFormRef.value.validate()
    
    // 调用API验证TOTP代码
    // 模拟API验证通过
    totpSettings.bound = true
    totpModalVisible.value = false
    resetTOTPForm()
    message.success('TOTP绑定成功')
  } catch (error) {
    message.error(`绑定失败: ${error.response?.data?.message || error.message}`)
  }
}

// 解除绑定TOTP
const handleUnbindTOTP = () => {
  unbindForm.password = ''
  unbindModalVisible.value = true
}

// 确认解除绑定TOTP
const handleConfirmUnbindTOTP = async () => {
  if (!unbindFormRef.value) return
  
  try {
    await unbindFormRef.value.validate()
    
    totpSettings.unbinding = true
    // 调用API解除TOTP绑定
    // 模拟API响应
    totpSettings.bound = false
    unbindModalVisible.value = false
    message.success('TOTP解绑成功')
  } catch (error) {
    message.error(`解绑失败: ${error.response?.data?.message || error.message}`)
  } finally {
    totpSettings.unbinding = false
  }
}

// 复制密钥
const copySecretKey = () => {
  if (!totpSettings.secretKey) return
  
  navigator.clipboard.writeText(totpSettings.secretKey)
    .then(() => {
      message.success('密钥已复制到剪贴板')
    })
    .catch(() => {
      message.error('复制失败，请手动复制')
    })
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    
    passwordLoading.value = true
    // 调用API修改密码
    // 模拟API响应
    currentUser.value.passwordUpdatedAt = new Date().toISOString().slice(0, 19).replace('T', ' ')
    message.success('密码修改成功')
    
    // 重置表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    if (passwordFormRef.value) {
      passwordFormRef.value.resetFields()
    }
  } catch (error) {
    message.error(`密码修改失败: ${error.response?.data?.message || error.message}`)
  } finally {
    passwordLoading.value = false
  }
}

// 重置TOTP表单
const resetTOTPForm = () => {
  totpForm.code = null
  if (totpFormRef.value) {
    totpFormRef.value.resetFields()
  }
}

// 获取TOTP设置
const fetchTOTPSettings = () => {
  // 模拟API数据
  totpSettings.enabled = true
  totpSettings.bound = false
  totpSettings.secretKey = ''
  totpSettings.qrCode = ''
}

// 获取当前用户信息
const fetchCurrentUser = () => {
  // 模拟API数据
  currentUser.value = {
    username: 'admin',
    role: 'admin',
    lastLoginAt: '2023-10-10 14:30:00',
    passwordUpdatedAt: '2023-09-01 08:00:00'
  }
}

onMounted(() => {
  fetchCurrentUser()
  fetchTOTPSettings()
})
</script>

<style scoped>
.admin-settings {
  padding: 0;
}

.settings-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.settings-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.totp-settings {
  padding: 20px 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.setting-label {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #333;
}

.setting-value {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-text {
  color: #666;
}

.setting-actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
}

.password-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.security-info {
  padding: 20px 0;
}

.info-item {
  display: flex;
  margin-bottom: 16px;
  line-height: 1.8;
}

.info-label {
  width: 120px;
  font-weight: 500;
  color: #666;
}

.info-value {
  color: #333;
}

/* TOTP Modal */
.totp-modal-content {
  padding: 20px 0;
}

.totp-intro {
  margin-bottom: 20px;
  text-align: center;
  color: #666;
}

.qrcode-container {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.qrcode {
  width: 200px;
  height: 200px;
  border: 1px solid #eee;
  padding: 10px;
}

.qrcode-placeholder {
  width: 200px;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
  border: 1px solid #eee;
}

.totp-secret {
  margin-bottom: 24px;
  text-align: center;
}

.secret-label {
  display: block;
  margin-bottom: 8px;
  color: #666;
}

.secret-code {
  display: inline-block;
  padding: 12px 20px;
  background: #f5f5f5;
  border: 1px solid #eee;
  border-radius: 4px;
  font-family: monospace;
  font-size: 16px;
  letter-spacing: 2px;
  color: #333;
  margin-bottom: 8px;
}

/* Responsive Design */
@media (max-width: 576px) {
  .settings-container {
    grid-template-columns: 1fr;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>