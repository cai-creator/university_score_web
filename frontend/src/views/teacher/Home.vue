<template>
  <div class="teacher-home-container">
    <a-card title="教师控制台" class="welcome-card">
      <div class="welcome-info">
        <h3>欢迎，{{ userInfo?.name }}老师</h3>
        <p>您可以在这里管理学生的加分申请</p>
      </div>
    </a-card>

    <!-- 整合信息概览区域 -->
    <a-card title="信息概览" class="overview-card">
      <div class="overview-content">
        <!-- 核心统计信息 -->
        <div class="core-stats">
          <div class="stat-item-highlight">
            <div class="stat-icon">
              <ClockCircleOutlined style="font-size: 32px; color: #1890ff;" />
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ pendingCount }}</div>
              <div class="stat-label">待审批申请</div>
            </div>
            <a-button type="primary" @click="navigateToApplications" class="quick-action-btn">
              立即审批
            </a-button>
          </div>
          
          <div class="stat-item-highlight">
            <div class="stat-icon">
              <UserOutlined style="font-size: 32px; color: #52c41a;" />
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalStudents }}</div>
              <div class="stat-label">管理学生数</div>
            </div>
            <a-button type="primary" @click="navigateToStudents" class="quick-action-btn">
              管理学生
            </a-button>
          </div>
        </div>
        
        <!-- 快速操作区域 -->
        <div class="integrated-actions">
          <a-button type="primary" size="large" @click="navigateToApplications" class="action-btn">
            <AppstoreOutlined /> 查看申请列表
          </a-button>
          <a-button type="primary" size="large" @click="navigateToStudents" class="action-btn">
            <UserOutlined /> 学生管理
          </a-button>
          <a-button type="primary" size="large" @click="navigateToExport" class="action-btn">
            <ExportOutlined /> 导出Excel
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 辅助统计信息 -->
    <div class="secondary-stats-container">
      <a-card class="stat-card">
        <div class="stat-item">
          <div class="stat-number approved">{{ approvedCount }}</div>
          <div class="stat-label">已通过申请</div>
        </div>
      </a-card>
      <a-card class="stat-card">
        <div class="stat-item">
          <div class="stat-number rejected">{{ rejectedCount }}</div>
          <div class="stat-label">已拒绝申请</div>
        </div>
      </a-card>
    </div>

    <div class="recent-applications">
      <a-card title="最近申请" :bordered="false">
        <a-table
          :columns="recentAppColumns"
          :data-source="recentApplications"
          :pagination="false"
          row-key="id"
          @row-click="handleApplicationClick"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <a-tag
                :color="record.status === 'pending' ? 'blue' : record.status === 'approved' ? 'green' : 'red'"
              >
                {{ record.status === 'pending' ? '待审批' : record.status === 'approved' ? '已通过' : '已拒绝' }}
              </a-tag>
            </template>
            <template v-if="column.key === 'score'">
              {{ record.score }}分
            </template>
          </template>
        </a-table>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AppstoreOutlined, UserOutlined, ExportOutlined, ClockCircleOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import api from '../../utils/api'

const router = useRouter()
const userInfo = ref(JSON.parse(localStorage.getItem('user')))

// 统计数据
const pendingCount = ref(0)
const approvedCount = ref(0)
const rejectedCount = ref(0)
const totalStudents = ref(0)

// 最近申请
const recentApplications = ref([])

// 最近申请列配置
const recentAppColumns = [
  { title: '学生姓名', dataIndex: 'studentName', key: 'studentName' },
  { title: '项目名称', dataIndex: 'projectName', key: 'projectName' },
  { title: '申请分数', dataIndex: 'score', key: 'score' },
  { title: '申请时间', dataIndex: 'applyTime', key: 'applyTime' },
  { title: '状态', dataIndex: 'status', key: 'status' }
]

// 获取统计数据
const fetchStats = async () => {
  try {
    // 先尝试从统计API获取数据
    let response = null
    try {
      response = await api.teacher.getStats()
      
      // 健壮的数据处理：尝试多种可能的数据格式
      // 注意：后端返回的统计数据嵌套在 data 字段中
      const statsData = response.data || response;
      
      // 适配不同的数据结构：直接的stats对象或嵌套在data中的对象
      const finalStats = statsData.pending !== undefined ? statsData : (statsData.data || {});
      
      // 适配不同的字段命名
      pendingCount.value = finalStats.pending || finalStats.pendingCount || finalStats.pending_count || 0
      approvedCount.value = finalStats.approved || finalStats.approvedCount || finalStats.approved_count || 0
      rejectedCount.value = finalStats.rejected || finalStats.rejectedCount || finalStats.rejected_count || 0
      totalStudents.value = finalStats.total || finalStats.totalStudents || finalStats.total_students || 0
      
      console.log('处理后的统计数据:', { pendingCount: pendingCount.value, approvedCount: approvedCount.value, rejectedCount: rejectedCount.value, totalStudents: totalStudents.value });
    } catch (statsError) {
      console.warn('从统计API获取数据失败，使用默认值:', statsError);
      console.error('获取统计数据失败详情:', statsError.response?.data || statsError.message);
    }
    
    // 关键改进：直接从学生列表API获取准确的学生数量作为后备
    try {
      // 获取学生列表，使用足够大的page_size获取所有学生
      const studentsResponse = await api.teacher.getStudents({ page_size: 1000 })
      
      // 适配多种可能的返回格式
      if (studentsResponse) {
        // 情况1：返回格式为 { results: [], count: total }（标准分页格式）
        if (studentsResponse.count !== undefined) {
          totalStudents.value = studentsResponse.count
          console.log('使用学生列表API的count字段获取准确学生数量:', totalStudents.value)
        }
        // 情况2：返回格式为 { results: [] }（无count字段）
        else if (studentsResponse.results && Array.isArray(studentsResponse.results)) {
          totalStudents.value = studentsResponse.results.length
          console.log('使用学生列表API的results.length获取学生数量:', totalStudents.value)
        }
        // 情况3：直接返回数组
        else if (Array.isArray(studentsResponse)) {
          totalStudents.value = studentsResponse.length
          console.log('使用学生列表API的数组长度获取学生数量:', totalStudents.value)
        }
        // 情况4：返回格式为 { data: { results: [], count: total } }
        else if (studentsResponse.data) {
          if (studentsResponse.data.count !== undefined) {
            totalStudents.value = studentsResponse.data.count
            console.log('使用学生列表API的data.count字段获取准确学生数量:', totalStudents.value)
          } else if (studentsResponse.data.results && Array.isArray(studentsResponse.data.results)) {
            totalStudents.value = studentsResponse.data.results.length
            console.log('使用学生列表API的data.results.length获取学生数量:', totalStudents.value)
          }
        }
      }
    } catch (studentsError) {
      console.warn('获取学生列表作为后备数据失败:', studentsError)
      // 保留已有的值，不影响其他统计
    }
    
    // 日志记录响应数据，便于调试
    console.log('统计数据响应：', response)
    console.log('最终显示的学生数量:', totalStudents.value)
  } catch (error) {
    console.error('获取统计数据失败：', error)
    // 错误处理：确保UI不会因为数据加载失败而崩溃
    pendingCount.value = 0
    approvedCount.value = 0
    rejectedCount.value = 0
    totalStudents.value = 0
    
    // 显示友好的错误提示
    message.error('获取统计数据失败：' + (error.message || '未知错误'))
  }
}

// 获取最近申请
  const fetchRecentApplications = async () => {
    try {
      console.log('正在请求最近申请数据');
      // 传递正确的参数格式：对象包含page_size
      const response = await api.teacher.getRecentApplications({ page_size: 5 });
      
      console.log('最近申请API响应:', response);
      
      // 首先检查响应是否有效
      if (!response) {
        console.error('API返回空响应');
        recentApplications.value = [];
        message.error('获取最近申请失败：服务器未返回数据');
        return;
      }
      
      // 处理不同的数据结构
      let applicationList = [];
      
      // 检查多种可能的数据格式：
      // 1. response.results (标准分页格式)
      if (response.results && Array.isArray(response.results)) {
        applicationList = response.results;
      }
      // 2. response.data.results (嵌套在data中的分页格式)
      else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        applicationList = response.data.results;
      }
      // 3. response.data (直接返回数据数组)
      else if (response.data && Array.isArray(response.data)) {
        applicationList = response.data;
      }
      // 4. 直接返回数组
      else if (Array.isArray(response)) {
        applicationList = response;
      }
      
      // 过滤掉已拒绝的申请
      const filteredApplications = applicationList.filter(app => 
        app.review_status && !['rejected', 'first_rejected', 'second_rejected', 'third_rejected'].includes(app.review_status)
      );
      
      // 映射后端数据到前端期望的格式
      const mappedApplications = filteredApplications.map(app => {
        // 状态映射
        let statusDisplay = '未知';
        if (['pending', 'first_reviewing', 'second_reviewing', 'third_reviewing'].includes(app.review_status)) {
          statusDisplay = 'pending';
        } else if (['first_approved', 'second_approved', 'approved'].includes(app.review_status)) {
          statusDisplay = 'approved';
        } else if (['first_rejected', 'second_rejected', 'third_rejected', 'rejected'].includes(app.review_status)) {
          statusDisplay = 'rejected';
        }
        
        // 日期格式化
        const applyTime = new Date(app.created_at).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
        
        return {
          id: app.id,
          studentName: app.student_name || '未知',
          projectName: app.title || '未知',
          score: app.score || 0,
          applyTime: applyTime,
          status: statusDisplay
        };
      });
      
      recentApplications.value = mappedApplications;
      console.log('过滤后的最近申请:', filteredApplications);
      
      // 如果没有数据，显示提示信息
      if (filteredApplications.length === 0) {
        console.log('没有符合条件的申请');
      }
    } catch (error) {
      console.error('获取最近申请失败:', error);
      recentApplications.value = [];
      
      // 区分不同类型的错误并提供更具体的错误信息
      let errorMessage = '获取最近申请失败：';
      
      if (error.response) {
        // 服务器返回了错误状态码
        const status = error.response.status;
        
        switch (status) {
          case 401:
            errorMessage += '请重新登录';
            break;
          case 403:
            errorMessage += '权限不足';
            break;
          case 404:
            errorMessage += '请求的资源不存在';
            break;
          case 500:
            const serverError = error.response.data?.error || error.response.data?.message || '服务器内部错误';
            errorMessage += `服务器内部错误 (${serverError})`;
            break;
          default:
            errorMessage += `服务器错误 (状态码: ${status})`;
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        errorMessage += '网络连接失败，请检查网络';
      } else {
        // 其他错误
        errorMessage += error.message || '未知错误';
        
        // 处理特定的错误消息
        if (error.message && error.message.includes('timeout')) {
          errorMessage = '获取最近申请失败：请求超时，请检查网络连接';
        } else if (error.message && error.message.includes('Network Error')) {
          errorMessage = '获取最近申请失败：网络错误，请检查网络连接';
        }
      }
      
      message.error(errorMessage);
    }
  };

// 导航到申请列表
const navigateToApplications = () => {
  router.push('/teacher/applications')
}

// 导航到学生管理
const navigateToStudents = () => {
  router.push('/teacher/students')
}

// 导航到导出Excel
const navigateToExport = () => {
  router.push('/teacher/export-excel')
}

// 处理最近申请列表行点击事件
const handleApplicationClick = (record) => {
  // 导航到教师端申请列表页面
  router.push('/teacher/applications')
}

onMounted(() => {
  fetchStats()
  fetchRecentApplications()
})
</script>

<style scoped>
.teacher-home-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-info h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
}

.welcome-info p {
  margin: 0;
  color: #666;
}

/* 整合信息概览样式 */
.overview-card {
  margin-bottom: 20px;
}

.overview-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.core-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item-highlight {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  flex: 1;
  min-width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-item-highlight:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #1890ff;
  line-height: 1.2;
}

.stat-number.approved {
  color: #52c41a;
}

.stat-number.rejected {
  color: #ff4d4f;
}

.stat-label {
  font-size: 16px;
  color: #666;
  margin-top: 5px;
}

.quick-action-btn {
  white-space: nowrap;
}

/* 快速操作区域样式 */
.integrated-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.action-btn {
  flex: 1;
  min-width: 160px;
  max-width: 220px;
  justify-content: center;
}

/* 辅助统计信息样式 */
.secondary-stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 200px;
}

.stat-item {
  text-align: center;
  padding: 16px;
}

/* 最近申请样式 */
.recent-applications {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .core-stats {
    flex-direction: column;
  }
  
  .stat-item-highlight {
    min-width: 100%;
  }
  
  .integrated-actions {
    flex-direction: column;
  }
  
  .action-btn {
    min-width: 100%;
    max-width: 100%;
  }
  
  .secondary-stats-container {
    flex-direction: column;
  }
}
</style>