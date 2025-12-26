<template>
  <div class="applications-main">
    <div class="page-header">
      <h2>材料申请管理</h2>
      <p>管理学生提交的各类综合素质加分申请</p>
      <div v-if="statusFilter" class="status-filter-indicator">
        <a-tag :color="statusFilter === 'pending' ? 'orange' : 'green'" closable @close="clearStatusFilter">
          当前筛选: {{ statusFilter === 'pending' ? '待审批申请' : '已审批申请' }}
        </a-tag>
      </div>
    </div>
    
    <div class="category-grid">
      <a-card 
        v-for="category in projectCategories" 
        :key="category.value"
        :title="category.label"
        :extra="getCategoryStats(category.value)"
        class="category-card"
        @click="navigateToCategory(category.value)"
      >
        <div class="category-info">
          <div class="category-icon">
            <a-icon :type="getCategoryIcon(category.value)" />
          </div>
          <div class="category-description">
            <p>管理该分类下的所有申请</p>
            <p class="limit-info" v-if="category.limit">
              <a-tag color="blue">限制: {{ category.limit }}项</a-tag>
            </p>
            <p class="limit-info" v-else>
              <a-tag color="green">无限制</a-tag>
            </p>
          </div>
        </div>
      </a-card>
    </div>
    
    <a-card title="分类统计概览" class="stats-card">
      <a-row :gutter="[16, 16]">
        <a-col :span="8">
          <div class="stat-item">
            <div class="stat-number">{{ totalApplications }}</div>
            <div class="stat-label">总申请数</div>
          </div>
        </a-col>
        <a-col :span="8">
          <div class="stat-item">
            <div class="stat-number pending">{{ pendingApplications }}</div>
            <div class="stat-label">待审批</div>
          </div>
        </a-col>
        <a-col :span="8">
          <div class="stat-item">
            <div class="stat-number approved">{{ approvedApplications }}</div>
            <div class="stat-label">已通过</div>
          </div>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Card, Tag, Row, Col } from 'ant-design-vue'
import { 
  FileTextOutlined, TrophyOutlined, RocketOutlined, 
  GlobalOutlined, UserOutlined, HeartOutlined, 
  StarOutlined, TeamOutlined, AppstoreOutlined, 
  CloseCircleOutlined 
} from '@ant-design/icons-vue'
import api from '../../utils/api'

const router = useRouter()
const route = useRoute()
const applications = ref([])
const statusFilter = ref(null)

// 项目分类定义
const projectCategories = [
  { value: 'english', label: '英语成绩', limit: null },
  { value: 'academic', label: '科研成果', limit: null },
  { value: 'comprehensive', label: '综合项目', limit: null }
]

// 获取申请列表数据
const fetchApplications = async () => {
  try {
    const data = await api.admin.getApplications()
    applications.value = data.data || []
  } catch (error) {
    console.error('获取申请列表失败:', error)
    applications.value = []
  }
}

// 跳转到分类页面
const navigateToCategory = (category) => {
  const query = statusFilter.value ? { status: statusFilter.value } : {}
  router.push({
    name: 'ApplicationCategory',
    params: { category: category },
    query
  })
}

// 清除状态筛选
const clearStatusFilter = () => {
  router.push({ path: '/admin/applications', query: {} })
}

// 监听路由参数变化
watch(() => route.query.status, (newStatus) => {
  statusFilter.value = newStatus
})

// 获取分类图标
const getCategoryIcon = (category) => {
  const iconMap = {
    '科研成果': FileTextOutlined,
    '学业竞赛': TrophyOutlined,
    '创新创业训练': RocketOutlined,
    '国际组织实习': GlobalOutlined,
    '参军入伍服兵役': UserOutlined,
    '志愿服务': HeartOutlined,
    '荣誉称号': StarOutlined,
    '社会工作': TeamOutlined,
    '体育比赛': AppstoreOutlined
  }
  return iconMap[category] || FileTextOutlined
}

// 获取分类统计信息
const getCategoryStats = (category) => {
  const filtered = applications.value.filter(app => app.category === category)
  const pending = filtered.filter(app => app.status === 'pending').length
  const approved = filtered.filter(app => app.status === 'approved').length
  const rejected = filtered.filter(app => app.status === 'rejected').length
  return `${pending}待审批 / ${approved}已通过 / ${rejected}已拒绝`
}

// 计算总统计数据
const totalApplications = computed(() => applications.value.length)
const pendingApplications = computed(() => 
  applications.value.filter(app => app.status === 'pending').length
)
const approvedApplications = computed(() => 
  applications.value.filter(app => app.status === 'approved').length
)

onMounted(() => {
  fetchApplications()
  // 初始化状态筛选
  statusFilter.value = route.query.status
})
</script>

<style scoped>
.applications-main {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #262626;
}

.page-header p {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.category-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.category-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.category-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.category-icon {
  font-size: 48px;
  color: #667eea;
  padding: 16px;
  background-color: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
}

.category-description {
  flex: 1;
}

.category-description p {
  margin: 0 0 8px 0;
  color: #595959;
}

.limit-info {
  margin-top: 8px;
}

.stats-card {
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
  padding: 24px;
  background-color: #fafafa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background-color: #f0f0f0;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #262626;
}

.stat-number.pending {
  color: #faad14;
}

.stat-number.approved {
  color: #52c41a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
}
</style>