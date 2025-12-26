<template>
  <div class="teacher-layout">
    <header class="header">
      <div class="header-content">
        <h1 class="title">学生综合素质加分系统</h1>
        <div class="user-info">
          <span>{{ userInfo?.username }}</span>
          <a-button type="text" @click="logout">退出登录</a-button>
        </div>
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
            <router-link to="/teacher/home">首页</router-link>
          </a-menu-item>
          <a-menu-item key="applications">
            <template #icon>
              <FileTextOutlined />
            </template>
            <router-link to="/teacher/applications">申请审批</router-link>
          </a-menu-item>
          <a-menu-item key="students">
            <template #icon>
              <UserOutlined />
            </template>
            <router-link to="/teacher/students">学生管理</router-link>
          </a-menu-item>
          <a-menu-item key="export-excel">
            <template #icon>
              <DownloadOutlined />
            </template>
            <router-link to="/teacher/export-excel">导出Excel</router-link>
          </a-menu-item>
          <a-menu-item key="profile">
            <template #icon>
              <UserOutlined />
            </template>
            <router-link to="/teacher/profile">个人信息</router-link>
          </a-menu-item>
        </a-menu>
      </aside>
      <main class="content">
        <router-view />
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
  FileTextOutlined, 
  UserOutlined, 
  DownloadOutlined 
} from '@ant-design/icons-vue'

const router = useRouter()
const userInfo = ref(null)

// 获取当前选中的菜单项
const selectedMenuKey = computed(() => {
  const path = router.currentRoute.value.path
  const segments = path.split('/')
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

onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.teacher-layout {
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
  color: #1890ff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main {
  flex: 1;
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.sidebar {
  width: 200px;
  background-color: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.menu {
  height: 100%;
  border-right: none;
}

.content {
  flex: 1;
  padding: 24px;
  background-color: #f5f5f5;
  overflow: auto;
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