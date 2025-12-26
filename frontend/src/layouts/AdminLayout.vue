<template>
  <div class="admin-layout">
    <header class="header">
      <div class="header-content">
        <h1 class="title">学生综合素质加分系统 - 超级管理员</h1>
        <a-dropdown :trigger="['click']">
          <div class="user-info" @click="e => e.preventDefault()">
            <div class="user-avatar">
              {{ userInfo?.username?.charAt(0) || 'A' }}
            </div>
            <span>{{ userInfo?.username }}</span>
            <DownOutlined />
          </div>
          <template #overlay>
            <a-menu>
              <a-menu-item @click="handleSettings">
                <SettingOutlined />
                设置
              </a-menu-item>
              <a-menu-item @click="logout">
                <LogoutOutlined />
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </header>
    <div class="main">
      <aside class="sidebar">
        <a-menu 
          mode="inline" 
          :selectedKeys="[selectedMenuKey]" 
          class="menu"
        >
          <a-menu-item key="home">
            <template #icon>
              <HomeOutlined />
            </template>
            <router-link to="/admin/home">首页</router-link>
          </a-menu-item>
          <a-menu-item key="classes">
            <template #icon>
              <TeamOutlined />
            </template>
            <router-link to="/admin/classes">班级管理</router-link>
          </a-menu-item>
          <a-menu-item key="colleges">
            <template #icon>
              <BankOutlined />
            </template>
            <router-link to="/admin/colleges">学院管理</router-link>
          </a-menu-item>
          <a-sub-menu key="accounts">
            <template #title>
              <span>
                <UserSwitchOutlined />
                账号管理
              </span>
            </template>
            <a-menu-item key="accounts/students">
              <router-link to="/admin/accounts/students">学生信息管理</router-link>
            </a-menu-item>
            <a-menu-item key="accounts/teachers">
              <router-link to="/admin/accounts/teachers">教师信息管理</router-link>
            </a-menu-item>
            <a-menu-item key="accounts/all">
              <router-link to="/admin/accounts/all">全部账号管理</router-link>
            </a-menu-item>
          </a-sub-menu>
        </a-menu>
      </aside>
      <main class="content">
        <div class="content-inner">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { 
  HomeOutlined, 
  UserOutlined, 
  FileDoneOutlined,
  UserSwitchOutlined,
  SettingOutlined,
  LogoutOutlined,
  DownOutlined,
  TeamOutlined,
  BankOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const userInfo = ref(null)

// 获取当前选中的菜单项
const selectedMenuKey = computed(() => {
  const path = router.currentRoute.value.path
  const segments = path.split('/')
  if (segments[2] === 'accounts') {
    // 对于账号管理的嵌套路由，使用完整路径作为key
    return `accounts/${segments[3]}`
  }
  return segments[segments.length - 1]
})

// 获取用户信息
const getUserInfo = () => {
  const info = localStorage.getItem('user')
  if (info) {
    userInfo.value = JSON.parse(info)
  }
}

// 退出登录
const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  message.success('退出登录成功')
  router.push('/')
}

// 跳转到设置页面
const handleSettings = () => {
  router.push('/admin/settings')
}

onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 16px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 18px;
  color: #ff4d4f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: rgba(102, 126, 234, 0.1);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.main {
  flex: 1;
  display: flex;
  width: 100%;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #ffffff 0%, #f5f7fa 100%);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.sidebar:hover {
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.12);
}

.menu {
  height: 100%;
  border-right: none;
  padding: 16px 0;
}

.menu .ant-menu-item {
  padding: 12px 24px;
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.menu .ant-menu-item:hover {
  background-color: rgba(102, 126, 234, 0.1);
}

.menu .ant-menu-item-selected {
  background-color: rgba(102, 126, 234, 0.2) !important;
  border-left: 4px solid #667eea;
}

.menu .ant-menu-item-selected .ant-menu-item-icon,
.menu .ant-menu-item-selected span {
  color: #667eea !important;
}

.content {
  flex: 1;
  padding: 24px;
  background-color: #f5f7fa;
  overflow: auto;
}

.content-inner {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 12px;
  }
  
  .title {
    font-size: 16px;
  }
  
  .main {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
  
  .menu {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .content {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 8px;
  }
  
  .title {
    font-size: 14px;
  }
  
  .user-info {
    gap: 8px;
  }
  
  .content {
    padding: 12px;
  }
}
</style>