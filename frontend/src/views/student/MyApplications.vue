<template>
  <div class="applications-container">
    <h2 class="page-title">我的申请</h2>
    
    <!-- 加载状态 -->
    <a-spin v-if="loading" tip="加载中..." class="loading-spin">
      <a-card class="applications-card" style="min-height: 300px;"></a-card>
    </a-spin>
    
    <!-- 网络错误提示 -->
    <a-card v-else-if="networkError" class="applications-card error-card">
      <a-empty>
        <template #description>
          <div>
            <p>{{ networkError }}</p>
            <a-button type="primary" @click="fetchApplications" style="margin-top: 16px">重试</a-button>
          </div>
        </template>
      </a-empty>
    </a-card>
    
    <!-- 正常显示 -->
    <a-card v-else class="applications-card">
      <a-tabs v-model:activeKey="activeTab" type="card">
        <a-tab-pane key="all" tab="全部申请">
          <application-list :applications="filteredApplications.all" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
        <a-tab-pane key="pending" tab="一审中">
          <application-list :applications="filteredApplications.pending" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
        <a-tab-pane key="second_reviewing" tab="二审中">
          <application-list :applications="filteredApplications.second_reviewing" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
        <a-tab-pane key="third_reviewing" tab="三审中">
          <application-list :applications="filteredApplications.third_reviewing" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
        <a-tab-pane key="approved" tab="审核通过">
          <application-list :applications="filteredApplications.approved" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
        <a-tab-pane key="rejected" tab="审核未通过">
          <application-list :applications="filteredApplications.rejected" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
        <a-tab-pane key="withdrawn" tab="已撤回">
          <application-list :applications="filteredApplications.withdrawn" @refresh="refreshApplications" :key="refreshKey" />
        </a-tab-pane>
      </a-tabs>
    </a-card>
    
    <a-float-button
      type="primary"
      icon="PlusOutlined"
      @click="navigateToUpload"
      :tooltip="{ title: '添加申请' }"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import ApplicationList from '../../components/ApplicationList.vue'
import api from '../../utils/api'
// 组件数据
const router = useRouter()
const activeTab = ref('all')
const applications = ref([])
// 用于强制刷新组件的key
const refreshKey = ref(0)
// 加载状态
const loading = ref(false)
// 网络错误信息
const networkError = ref('')

// 过滤后的申请列表（按状态分类）
const filteredApplications = computed(() => {
  return {
    all: applications.value,
    // 一审中：pending, first_reviewing
    pending: applications.value.filter(app => 
      ['pending', 'first_reviewing'].includes(app.review_status)
    ),
    // 二审中：first_approved, second_reviewing
    second_reviewing: applications.value.filter(app => 
      ['first_approved', 'second_reviewing'].includes(app.review_status)
    ),
    // 三审中：second_approved, third_reviewing
    third_reviewing: applications.value.filter(app => 
      ['second_approved', 'third_reviewing'].includes(app.review_status)
    ),
    // 审核通过：approved
    approved: applications.value.filter(app => app.review_status === 'approved'),
    // 审核未通过：rejected, first_rejected, second_rejected, third_rejected
    rejected: applications.value.filter(app => 
      ['rejected', 'first_rejected', 'second_rejected', 'third_rejected'].includes(app.review_status)
    ),
    // 已撤回：withdrawn
    withdrawn: applications.value.filter(app => app.review_status === 'withdrawn')
  }
})

// 获取申请列表
const fetchApplications = async () => {
  // 开始加载，清空错误信息
  loading.value = true
  networkError.value = ''
  
  try {
      const data = await api.student.getApplications()
      // 调试：打印从API获取的原始数据
      console.log('从API获取的原始数据:', data)
      
      // 确保data是对象
      if (!data || typeof data !== 'object') {
        console.error('API返回的数据格式错误:', data)
        applications.value = []
        return
      }
      
      // 获取申请列表数据，支持多种格式
      let rawApplications = []
      if (data.results) {
        // 格式1: { results: [] }
        rawApplications = data.results
      } else if (data.data && Array.isArray(data.data)) {
        // 格式2: { data: [] }
        rawApplications = data.data
      } else if (Array.isArray(data)) {
        // 格式3: []
        rawApplications = data
      }
      
      // 直接在获取数据后处理项目类型为中文
      const processedApplications = (rawApplications || []).map(application => {
        if (application.category && typeof application.category === 'string' && !/[\u4e00-\u9fa5]/.test(application.category)) {
          console.log('处理前的项目类型:', application.category)
          
          // 项目类型中英文映射
          const typeMap = {
            // 后端返回的所有category值映射
            'english': '英语成绩',
            'academic_paper': '学术论文',
            'patent_work': '发明专利',
            'academic_competition': '学业竞赛',
            'innovation': '创新创业训练',
            'ccf_csp': 'CCF CSP认证',
            'internship': '国际组织实习',
            'military': '参军入伍服兵役',
            'volunteer_service': '志愿服务',
            'honor': '荣誉称号',
            'social': '社会工作',
            'sports_competition': '体育比赛',
            
            // 其他可能的类型映射
            'scientific': '科研成果',
            'academic': '科研成果',
            'competition': '学业竞赛',
            'volunteer': '志愿服务',
            'sports': '体育比赛',
            'ccf': 'CCF CSP认证',
            
            // 大写版本映射
            'ENGLISH': '英语成绩',
            'ACADEMIC_PAPER': '学术论文',
            'PATENT_WORK': '发明专利',
            'ACADEMIC_COMPETITION': '学业竞赛',
            'INNOVATION': '创新创业训练',
            'CCF_CSP': 'CCF CSP认证',
            'INTERNSHIP': '国际组织实习',
            'MILITARY': '参军入伍服兵役',
            'VOLUNTEER_SERVICE': '志愿服务',
            'HONOR': '荣誉称号',
            'SOCIAL': '社会工作',
            'SPORTS_COMPETITION': '体育比赛',
            'SCIENTIFIC': '科研成果',
            'ACADEMIC': '科研成果',
            'COMPETITION': '学业竞赛',
            'VOLUNTEER': '志愿服务',
            'SPORTS': '体育比赛',
            'CCF': 'CCF CSP认证'
          }
          
          // 进行类型转换
          const lowerType = application.category.toLowerCase()
          let translatedType = typeMap[application.category] || 
                              typeMap[lowerType] || 
                              typeMap[application.category.toUpperCase()]
          
          // 关键词匹配
          if (!translatedType) {
            if (lowerType.includes('scientific') || lowerType.includes('research')) {
              translatedType = '科研成果'
            } else if (lowerType.includes('competition') || lowerType.includes('contest')) {
              translatedType = '学业竞赛'
            } else if (lowerType.includes('innovation')) {
              translatedType = '创新创业训练'
            } else if (lowerType.includes('internship') || lowerType.includes('international')) {
              translatedType = '国际组织实习'
            } else if (lowerType.includes('military') || lowerType.includes('service')) {
              translatedType = '参军入伍服兵役'
            } else if (lowerType.includes('volunteer')) {
              translatedType = '志愿服务'
            } else if (lowerType.includes('honor') || lowerType.includes('award')) {
              translatedType = '荣誉称号'
            } else if (lowerType.includes('social')) {
              translatedType = '社会工作'
            } else if (lowerType.includes('sports') || lowerType.includes('athletic')) {
              translatedType = '体育比赛'
            } else if (lowerType.includes('english') || lowerType.includes('score')) {
              translatedType = '英语成绩'
            } else if (lowerType.includes('ccf')) {
              translatedType = 'CCF CSP认证'
            } else {
              translatedType = '未分类项目'
            }
          }
          
          console.log('处理后的项目类型:', translatedType)
          return { ...application, category: translatedType }
        }
        return application
      })
      
      // 调试：如果有数据，打印第一个申请的详细信息，特别是category字段和分数
      if (processedApplications.length > 0) {
        console.log('第一个申请的详细信息:', processedApplications[0])
        console.log('项目类型字段:', processedApplications[0].category, '类型:', typeof processedApplications[0].category)
        console.log('申请分数:', processedApplications[0].score, '类型:', typeof processedApplications[0].score)
        console.log('附件数量:', processedApplications[0].attachments?.length || 0)
      }
      
      // 使用处理后的数据，确保Vue能够检测到变化
      applications.value = [...processedApplications]
    } catch (error) {
      console.error('API请求错误:', error)
      // 设置网络错误信息
      networkError.value = error.message || '获取申请列表失败，请稍后重试'
      // 发生错误时将applications设为空数组，避免显示错误内容
      applications.value = []
    } finally {
      // 结束加载
      loading.value = false
    }
}

// 刷新申请列表
const refreshApplications = () => {
  fetchApplications()
  // 更新key值，强制组件重新渲染
  refreshKey.value++
}

// 跳转到材料上传页面
const navigateToUpload = () => {
  router.push('/student/add-application')
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.applications-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #1f2937;
  font-size: 24px;
  font-weight: 600;
}

.applications-card {
  margin-bottom: 20px;
}

.loading-spin {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-card {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.error-card .ant-empty {
  margin: 0;
}
</style>