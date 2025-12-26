<template>
  <div class="admin-home">
    <h2>系统管理首页</h2>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <a-card hoverable @click="navigateTo('/admin/accounts/students')" class="stat-card">
        <div class="stat-item">
          <h3>学生总数</h3>
          <div class="stat-value">{{ stats.studentCount }}</div>
        </div>
      </a-card>
      
      <a-card hoverable @click="navigateTo('/admin/accounts/teachers')" class="stat-card">
        <div class="stat-item">
          <h3>教师总数</h3>
          <div class="stat-value">{{ stats.teacherCount }}</div>
        </div>
      </a-card>
      
      <a-card hoverable @click="navigateTo('/admin/applications?status=pending')" class="stat-card">
        <div class="stat-item">
          <h3>待审批申请</h3>
          <div class="stat-value pending">{{ stats.pendingApplications }}</div>
        </div>
      </a-card>
      
      <a-card hoverable @click="navigateTo('/admin/applications?status=approved')" class="stat-card">
        <div class="stat-item">
          <h3>已审批申请</h3>
          <div class="stat-value approved">{{ stats.approvedApplications }}</div>
        </div>
      </a-card>
    </div>
    
    <!-- 系统功能入口 -->
    <a-card style="margin-top: 20px;">
      <h3>系统功能</h3>
      <div class="function-grid">
        <a-card hoverable @click="navigateTo('/admin/accounts/all')">
          <div class="function-item">
            <div class="function-icon">👥</div>
            <div class="function-text">用户管理</div>
          </div>
        </a-card>
        
        <a-card hoverable @click="navigateTo('/admin/classes')">
          <div class="function-item">
            <div class="function-icon">📋</div>
            <div class="function-text">班级绑定</div>
          </div>
        </a-card>
      </div>
    </a-card>
    
    <!-- 最近活动 -->
    <a-card style="margin-top: 20px;">
      <h3>最近活动</h3>
      <a-list
        :data-source="recentActivities"
        :pagination="{ pageSize: 5 }"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta
              :title="item.title"
              :description="item.description"
            />
            <span>{{ item.time }}</span>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import api from '../../utils/api'

const router = useRouter()

// 统计数据 - 使用更安全的默认值
const stats = ref({
  studentCount: 0,
  teacherCount: 0,
  pendingApplications: 0,
  approvedApplications: 0
})

// 最近活动 - 使用更安全的默认值
const recentActivities = ref([])

// 导航到指定路由
const navigateTo = (path) => {
  router.push(path)
}

// 获取统计数据
const fetchStats = async () => {
  try {
    // 调用用户统计API
    const userStatsData = await api.admin.getStatistics()
    
    // 更安全的数据处理，添加额外的空值检查
    stats.value = {
      // 用户统计数据
      studentCount: userStatsData && userStatsData.user_type_stats && typeof userStatsData.user_type_stats.students !== 'undefined' 
        ? Number(userStatsData.user_type_stats.students) 
        : 0,
      teacherCount: userStatsData && userStatsData.user_type_stats && typeof userStatsData.user_type_stats.teachers !== 'undefined'
        ? Number(userStatsData.user_type_stats.teachers)
        : 0,
      // 审核统计数据
      pendingApplications: userStatsData && typeof userStatsData.pending_applications !== 'undefined' 
        ? Number(userStatsData.pending_applications)
        : 0,
      approvedApplications: userStatsData && typeof userStatsData.approved_applications !== 'undefined' 
        ? Number(userStatsData.approved_applications)
        : 0
    }
  } catch (error) {
    console.error('获取统计数据失败：', error)
    message.error('获取统计数据失败，使用缓存数据')
    // 发生错误时确保使用默认值
    stats.value = {
      studentCount: 0,
      teacherCount: 0,
      pendingApplications: 0,
      approvedApplications: 0
    }
  }
}

// 获取最近活动
const fetchRecentActivities = () => {
  // 注意：暂时没有找到获取最近活动的API接口
  // 保留空数组作为默认值，等待后端提供接口后替换
  recentActivities.value = []
}

onMounted(async () => {
  // 使用async/await确保异步操作的错误能被捕获
  try {
    await fetchStats()
    fetchRecentActivities()
  } catch (error) {
    console.error('页面初始化失败：', error)
    message.error('页面初始化失败')
  }
})
</script>

<style scoped>
.admin-home {
  padding: 20px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-item {
  text-align: center;
}

.stat-item h3 {
  margin-bottom: 10px;
  color: #666;
  font-size: 16px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #1890ff;
}

.stat-value.pending {
  color: #faad14;
}

.stat-value.approved {
  color: #52c41a;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.function-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  cursor: pointer;
}

.function-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.function-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}
</style>