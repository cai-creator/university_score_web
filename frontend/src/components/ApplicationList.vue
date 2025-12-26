<template>
  <div class="application-list">
    <a-table
      :columns="columns"
      :data-source="sortedApplications"
      :row-key="record => record.id"
      :pagination="{ pageSize: 10 }"
      :loading="loading"
      :scroll="{ x: 1000 }"
      :row-class-name="record => record.review_status === 'withdrawn' ? 'withdrawn-row' : ''"
      :bordered="false"
      class="application-table"
      size="middle"
    >
      <template #bodyCell="{ column, record }">
        <!-- 状态列 -->
        <template v-if="column.key === 'status'">
          <a-tag
            :color="getStatusColor(record.review_status)"
            :key="record.review_status"
          >
            {{ getStatusText(record.review_status) }}
          </a-tag>
        </template>
        
        <!-- 操作列 -->
        <template v-if="column.key === 'actions'">
          <!-- 桌面端显示独立按钮 -->
          <div v-if="!isMobile" style="display: flex; gap: 8px; justify-content: center; align-items: center; flex-wrap: wrap;">
            <a-button type="link" @click="viewApplication(record)" size="small">
              查看
            </a-button>
            
            <!-- 根据状态显示不同操作 -->
            <template v-if="record.review_status === 'pending' || record.review_status.includes('reviewing')">
              <a-button type="link" danger @click="withdrawApplication(record)" size="small">
                撤回
              </a-button>
              <a-button type="link" @click="editApplication(record)" size="small">
                编辑
              </a-button>
            </template>
            
            <template v-else-if="record.review_status === 'rejected' || record.review_status === 'withdrawn'">
              <a-button type="link" @click="editApplication(record)" size="small">
                重新提交
              </a-button>
              
              <!-- 已撤回和审核未通过的申请都显示删除按钮 -->
              <template v-if="record.review_status === 'withdrawn' || record.review_status === 'rejected'">
                <a-button type="link" danger @click="deleteApplication(record)" size="small">
                  删除
                </a-button>
              </template>
            </template>
            
            <!-- 审核通过状态只显示查看按钮 -->
            <template v-else-if="record.review_status === 'approved'">
              <!-- 已移除"已通过"标签，只保留查看按钮 -->
            </template>
            
            <!-- 已撤回的申请不显示操作按钮 -->
            <template v-else-if="record.review_status === 'withdrawn'">
              <a-tag color="default" size="small">已撤回</a-tag>
            </template>
          </div>
          
          <!-- 移动端显示下拉菜单 -->
          <div v-else>
            <template v-if="record.review_status === 'approved'">
              <!-- 审核通过状态显示查看按钮 -->
              <a-button type="text" size="small" @click="viewApplication(record)">
                查看
              </a-button>
            </template>
            <template v-else-if="record.review_status === 'withdrawn'">
              <a-tag color="default" size="small">已撤回</a-tag>
            </template>
            <a-dropdown v-else>
              <a-button type="text" size="small">
                <EllipsisOutlined />
              </a-button>
              <template #overlay>
                <a-menu :items="getActionMenu(record)"></a-menu>
              </template>
            </a-dropdown>
          </div>
        </template>
        
        <!-- 材料列 -->
        <template v-if="column.key === 'attachments'">
          <div class="attachments-list">
            <!-- 图片直接显示 -->
            <div
              v-for="(attachment, index) in record.attachments"
              :key="index"
              class="attachment-item"
              @click="previewAttachment(attachment)"
            >
              <!-- 处理字符串URL和对象两种情况 -->
              <div 
                v-if="isImageAttachment(attachment)"
                class="image-attachment"
              >
                <img 
                  :src="getAttachmentUrl(attachment)" 
                  :alt="getAttachmentName(attachment)"
                  class="attachment-preview-image"
                />
                <div class="attachment-name">{{ getAttachmentName(attachment) }}</div>
              </div>
              <!-- 其他文件类型显示 -->
              <div 
                v-else
                class="other-attachment"
              >
                <div class="other-icon">文件</div>
                <div class="attachment-name">{{ getAttachmentName(attachment) }}</div>
              </div>
            </div>
            <span v-if="!record.attachments || record.attachments.length === 0">
              无
            </span>
          </div>
        </template>
        
        <!-- 拒绝理由列 -->
        <template v-if="column.key === 'reason'">
          <div v-if="record.reason">
            {{ record.reason }}
          </div>
          <span v-else>-</span>
        </template>
      </template>
    </a-table>
    
    <!-- 空数据提示 -->
    <div v-if="applications.length === 0 && !loading" class="empty-list">
      <a-empty description="暂无申请记录" />
    </div>
    
    <!-- 申请详情模态框 -->
    <a-modal
      v-model:open="detailModalVisible"
      :title="`申请详情 - ${selectedApplication.title || ''}`"
      width="800px"
      @cancel="closeDetailModal"
    >
      <div class="application-detail" v-if="selectedApplication">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="项目名称">{{ getProjectTitleText(selectedApplication.title) }}</a-descriptions-item>
          <a-descriptions-item label="项目类型">{{ getProjectTypeText(selectedApplication.category) }}</a-descriptions-item>
          <a-descriptions-item label="申请分数">{{ selectedApplication.score }}分</a-descriptions-item>
          <a-descriptions-item label="状态"><a-tag :color="getStatusColor(selectedApplication.review_status)">{{ getStatusText(selectedApplication.review_status) }}</a-tag></a-descriptions-item>
          <a-descriptions-item label="申请日期">{{ selectedApplication.applyDate }}</a-descriptions-item>
          <a-descriptions-item label="审核日期">{{ selectedApplication.reviewDate || '-' }}</a-descriptions-item>
          <a-descriptions-item label="审核人">{{ selectedApplication.reviewer || '-' }}</a-descriptions-item>
          <a-descriptions-item label="拒绝理由">{{ selectedApplication.reason || '-' }}</a-descriptions-item>
          <a-descriptions-item label="项目描述" span="2">{{ selectedApplication.description }}</a-descriptions-item>
          <a-descriptions-item label="材料附件" span="2">
            <div class="attachments-list">
              <!-- 图片直接显示 -->
              <div
                v-for="(attachment, index) in selectedApplication.attachments"
                :key="index"
                class="attachment-item"
                @click="previewAttachment(attachment)"
              >
                <!-- 处理字符串URL和对象两种情况 -->
                <div 
                  v-if="isImageAttachment(attachment)"
                  class="image-attachment"
                >
                  <img 
                    :src="getAttachmentUrl(attachment)" 
                    :alt="getAttachmentName(attachment)"
                    class="attachment-preview-image"
                  />
                  <div class="attachment-name">{{ getAttachmentName(attachment) }}</div>
                </div>
                <!-- PDF文件显示 -->
                <div 
                  v-else-if="isPdfAttachment(attachment)"
                  class="pdf-attachment"
                >
                  <div class="pdf-icon">PDF</div>
                  <div class="attachment-name">{{ getAttachmentName(attachment) }}</div>
                </div>
                <!-- 其他文件类型显示 -->
                <div 
                  v-else
                  class="other-attachment"
                >
                  <div class="other-icon">文件</div>
                  <div class="attachment-name">{{ getAttachmentName(attachment) }}</div>
                </div>
              </div>
              <span v-if="!selectedApplication.attachments || selectedApplication.attachments.length === 0">
                无
              </span>
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
    
    <!-- 文件预览模态框 -->
    <a-modal
      v-model:open="previewModalVisible"
      :title="selectedAttachment?.name || '文件预览'"
      width="90%"
      :footer="null"
      :maskClosable="true"
      @cancel="closePreviewModal"
    >
      <div class="preview-container">
        <!-- 图片预览 -->
        <div v-if="isImageFile(selectedAttachment)" class="image-preview">
          <img 
            :src="selectedAttachment?.url || ''" 
            alt="预览图片" 
            :style="{ maxWidth: '100%', maxHeight: '80vh' }" 
            @error="handleImageError" 
          />
          <div v-if="imageError" class="image-error">
            <p>图片加载失败: {{ imageError }}</p>
            <a-button type="primary" @click="downloadFile(selectedAttachment)">
              下载图片
            </a-button>
          </div>
        </div>
        
        <!-- 其他文件类型 -->
        <div v-else class="other-preview">
          <a-empty description="暂不支持该文件类型的预览" />
          <a-button type="primary" @click="downloadFile(selectedAttachment)" style="margin-top: 20px">
            下载文件
          </a-button>
        </div>
        
        <!-- 关闭按钮 -->
        <a-button
          type="text"
          icon="CloseOutlined"
          class="close-preview-btn"
          @click="closePreviewModal"
        >
          关闭预览
        </a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal, Descriptions, Tag, Button, Dropdown, Menu } from 'ant-design-vue'
import { DeleteOutlined, EditOutlined, EyeOutlined, FileTextOutlined, CloseOutlined, EllipsisOutlined, LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'
import api from '../utils/api'

const props = defineProps({
  applications: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// 处理申请数据，确保所有申请都有统一的attachments数组
const processApplication = (application) => {
  // 复制原始对象，避免修改props
  const processed = { ...application }
  
  // 初始化attachments数组
  const attachments = []
  
  // 直接使用后端返回的attachments字段，不进行额外处理
  // 确保attachments是数组
  if (application.attachments) {
    if (Array.isArray(application.attachments)) {
      application.attachments.forEach(attachment => {
        if (attachment) {
          // 支持多种附件字段名
          const attachmentUrl = attachment.url || attachment.file_url || attachment.path || attachment.file_path || attachment.attachment_url || ''
          if (attachmentUrl) {
            attachments.push({
              url: attachmentUrl,
              name: attachment.name || attachment.original_name || attachmentUrl.split('/').pop() || '附件'
            })
          }
        }
      })
    }
  } else if (application.data && application.data.attachments) {
    // 处理申请详情中的attachments字段
    if (Array.isArray(application.data.attachments)) {
      application.data.attachments.forEach(attachment => {
        if (attachment) {
          // 支持多种附件字段名
          const attachmentUrl = attachment.url || attachment.file_url || attachment.path || attachment.file_path || attachment.attachment_url || ''
          if (attachmentUrl) {
            attachments.push({
              url: attachmentUrl,
              name: attachment.name || attachment.original_name || attachmentUrl.split('/').pop() || '附件'
            })
          }
        }
      })
    }
  }
  
  // 移除重复的附件
  const uniqueAttachments = []
  const urlSet = new Set()
  
  attachments.forEach(attachment => {
    const url = typeof attachment === 'string' ? attachment : attachment.url
    if (url && !urlSet.has(url)) {
      urlSet.add(url)
      uniqueAttachments.push(attachment)
    }
  })
  
  // 将合并后的attachments赋值给processed对象
  processed.attachments = uniqueAttachments
  
  // 调试：记录处理结果
  console.log(`处理后的申请附件: id=${application.id}, attachmentsCount=${uniqueAttachments.length}`)
  if (uniqueAttachments.length > 0) {
    console.log('附件详情:', uniqueAttachments)
  }
  
  return processed
}

// 排序后的申请列表 - 已撤回的申请放在末尾
const sortedApplications = computed(() => {
  // 分离已撤回和未撤回的申请
  const withdrawnApplications = []
  const normalApplications = []
  
  props.applications.forEach(application => {
    // 处理申请数据，确保有统一的attachments数组
    const processedApplication = processApplication(application)
    
    if (processedApplication.review_status === 'withdrawn') {
      withdrawnApplications.push(processedApplication)
    } else {
      normalApplications.push(processedApplication)
    }
  })
  
  // 对已撤回申请按申请时间升序排序（保持原有顺序）
  withdrawnApplications.sort((a, b) => {
    return new Date(a.applyDate) - new Date(b.applyDate)
  })
  
  // 对未撤回申请按申请时间倒序排序（最新的在前面）
  normalApplications.sort((a, b) => {
    return new Date(b.applyDate) - new Date(a.applyDate)
  })
  
  // 合并列表：未撤回申请在前，已撤回申请在后
  return [...normalApplications, ...withdrawnApplications]
})

const emit = defineEmits(['refresh'])

const router = useRouter()

// 详情模态框相关
const detailModalVisible = ref(false)
const selectedApplication = ref({})

// 预览模态框相关
const previewModalVisible = ref(false)
const selectedAttachment = ref({})
const imageError = ref('')

// 处理图片加载错误
const handleImageError = (event) => {
  console.error('图片加载失败:', event)
  imageError.value = '图片加载失败，请尝试下载查看'
}

// 关闭预览模态框
const closePreviewModal = () => {
  previewModalVisible.value = false
  selectedAttachment.value = {}
  imageError.value = ''
}
  
  // 响应式设计 - 屏幕宽度检测
  const isMobile = ref(false)
  
  // 检测屏幕宽度
  const checkScreenWidth = () => {
    isMobile.value = window.innerWidth < 768
  }
  
  // 监听屏幕宽度变化
onMounted(() => {
  checkScreenWidth()
  window.addEventListener('resize', checkScreenWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenWidth)
})



// 表格列配置
const columns = [
  {
    title: '项目名称',
    dataIndex: 'title',
    key: 'title',
    ellipsis: true,
    width: 200,
    align: 'left',
    render: (text) => getProjectTitleText(text)
  },
  {
    title: '项目类型',
    dataIndex: 'category',
    key: 'category',
    width: 120,
    align: 'center',
    render: (text, record) => {
      // 调试：打印完整记录，查看category字段的值和类型
      console.log('完整申请记录:', record)
      console.log('项目类型字段值:', text, '类型:', typeof text)
      return getProjectTypeText(text)
    }
  },
  {
    title: '申请分数',
    dataIndex: 'score',
    key: 'score',
    width: 100,
    align: 'center',
    render: (text) => `${text}分`
  },
  {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 120,
        align: 'center',
        render: (text, record) => {
          // 处理状态显示 - 适配多种状态格式
          const status = record.review_status
          const statusText = getStatusText(status)
          const statusColor = getStatusColor(status)
          
          // 根据状态选择图标
          let statusIcon = null
          if (status === 'pending') {
            statusIcon = h(EyeOutlined)
          } else if (status.includes('reviewing')) {
            statusIcon = h(LoadingOutlined)
          } else if (status.includes('approved')) {
            statusIcon = h(CheckCircleOutlined)
          } else if (status === 'rejected' || status === 'withdrawn') {
            statusIcon = h(CloseCircleOutlined)
          }
          
          // 使用h函数创建标签组件
          return h(Tag, {
            color: statusColor,
            style: { display: 'inline-flex', alignItems: 'center', gap: '4px' }
          }, [
            statusIcon,
            statusText
          ])
        }
      },
  { title: '申请日期', dataIndex: 'applyDate', key: 'applyDate', width: 160, align: 'center', render: (text) => text ? new Date(text).toLocaleDateString('zh-CN') : '-' },
  {
    title: '审核日期',
    dataIndex: 'reviewDate',
    key: 'reviewDate',
    width: 160,
    align: 'center',
    render: (text) => text || '-'
  },
  {
    title: '审核人',
    dataIndex: 'reviewer',
    key: 'reviewer',
    width: 120,
    align: 'center',
    render: (text) => text || '-'
  },
  {
    title: '拒绝理由',
    dataIndex: 'reason',
    key: 'reason',
    ellipsis: true,
    width: 200,
    align: 'center',
    tooltip: (record) => record.reason
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    align: 'center',
    fixed: 'right',
    render: (_, record) => {
      // 桌面端显示按钮组
      if (!isMobile.value) {
        const actions = []
        
        // 查看按钮
        actions.push(
          h(Button, { 
            key: 'view', 
            type: 'text', 
            size: 'small', 
            onClick: () => viewApplication(record)
          }, '查看')
        )
        
        // 根据状态添加其他按钮
        if (record.review_status === 'pending' || record.review_status.includes('reviewing')) {
          actions.push(
            h(Button, { 
              key: 'withdraw', 
              type: 'text', 
              size: 'small', 
              danger: true, 
              onClick: () => withdrawApplication(record)
            }, '撤回')
          )
          actions.push(
            h(Button, { 
              key: 'edit', 
              type: 'text', 
              size: 'small', 
              onClick: () => editApplication(record)
            }, '编辑')
          )
        } else if (record.review_status === 'rejected' || record.review_status === 'withdrawn') {
          actions.push(
            h(Button, { 
              key: 'resubmit', 
              type: 'text', 
              size: 'small', 
              onClick: () => editApplication(record)
            }, '重新提交')
          )
          
          // 已撤回和审核未通过的申请都显示删除按钮
          if (record.review_status === 'withdrawn' || record.review_status === 'rejected') {
            actions.push(
              h(Button, { 
                key: 'delete', 
                type: 'text', 
                size: 'small', 
                danger: true, 
                onClick: () => deleteApplication(record)
              }, '删除')
            )
          }
        }
        
        return h('div', { class: 'action-buttons' }, actions)
      } else {
        // 移动端显示下拉菜单
        const menuItems = getActionMenu(record).map(item => {
          return h(Menu.Item, { 
            key: item.key, 
            danger: item.danger, 
            onClick: item.onClick
          }, item.label)
        })
        
        const menu = h(Menu, null, menuItems)
        
        return h(Dropdown, { 
          overlay: menu, 
          placement: 'bottomRight'
        }, {
          default: () => h(Button, { 
            type: 'text', 
            size: 'small'
          }, ['操作 ', h(EllipsisOutlined)])
        })
      }
    }
  }
]

// 获取状态文本
const getStatusText = (status) => {
  // 规范状态体系：仅保留五种状态
  const statusMap = {
    pending: '一审中',
    first_reviewing: '一审中',
    first_approved: '二审中',
    second_reviewing: '二审中',
    second_approved: '三审中',
    third_reviewing: '三审中',
    approved: '审核通过',
    rejected: '审核未通过',
    first_rejected: '审核未通过',
    second_rejected: '审核未通过',
    third_rejected: '审核未通过',
    withdrawn: '已撤回'
  }
  return statusMap[status] || status
}

// 获取状态颜色
const getStatusColor = (status) => {
  // 规范状态体系：仅保留五种状态
  const colorMap = {
    pending: 'blue',
    first_reviewing: 'blue',
    first_approved: 'blue',
    second_reviewing: 'blue',
    second_approved: 'blue',
    third_reviewing: 'blue',
    approved: 'green',
    rejected: 'red',
    first_rejected: 'red',
    second_rejected: 'red',
    third_rejected: 'red',
    withdrawn: 'gray'
  }
  return colorMap[status] || 'default'
}

// 获取状态图标
const getStatusIcon = (status) => {
  // 规范状态体系：仅保留五种状态
  const iconMap = {
    pending: 'loading',
    first_reviewing: 'loading',
    first_approved: 'loading',
    second_reviewing: 'loading',
    second_approved: 'loading',
    third_reviewing: 'loading',
    approved: 'check-circle',
    rejected: 'close-circle',
    first_rejected: 'close-circle',
    second_rejected: 'close-circle',
    third_rejected: 'close-circle',
    withdrawn: 'close-circle'
  }
  return iconMap[status] || 'info-circle'
}

// 获取项目类型中文文本
const getProjectTypeText = (type) => {
  // 调试：打印所有传入的类型值，以便找出未映射的类型
  console.log('getProjectTypeText被调用，原始值:', type, '类型:', typeof type)
  
  // 健壮性处理：确保输入是字符串类型
  const typeStr = String(type || '')
  console.log('转换为字符串后:', typeStr, '类型:', typeof typeStr)
  
  if (!typeStr.trim()) {
    console.log('输入为空或空白字符串，返回空字符串')
    return ''
  }
  
  // 检查是否已经是中文（包含中文字符）
  if (/[\u4e00-\u9fa5]/.test(typeStr)) {
    console.log('输入已经是中文，直接返回:', typeStr)
    return typeStr
  }
  
  // 特别处理学术论文类型
  if (typeStr === 'academic_paper') {
    return '学术论文'
  }
  
  // 项目类型中英文映射 - 扩展版本，确保覆盖所有可能的后端返回值
  const typeMap = {
    // 基础核心类型 - 确保完全覆盖后端可能的所有值
    'scientific': '科研成果',
    'academic': '科研成果',
    'competition': '学业竞赛',
    'innovation': '创新创业训练',
    'internship': '国际组织实习',
    'military': '参军入伍服兵役',
    'volunteer': '志愿服务',
    'honor': '荣誉称号',
    'social': '社会工作',
    'sports': '体育比赛',
    'english': '英语成绩',
    'ccf': 'CCF CSP认证',
    'ccf_csp': 'CCF CSP认证',
    'ccf_csp_certification': 'CCF CSP认证',
    
    // 新增扩展类型映射
    'research_result': '科研成果',
    'academic_excellence': '学术成果',
    'project_innovation': '创新创业训练',
    'international_intern': '国际组织实习',
    'military_service_experience': '参军入伍服兵役',
    'volunteer_activity': '志愿服务',
    'honor_award': '荣誉称号',
    'social_practice': '社会实践',
    'sports_game': '体育比赛',
    'english_proficiency': '英语成绩',
    
    // 补全更多可能的组合
    'scientific_achievement': '科研成果',
    'academic_competition': '学业竞赛',
    'innovation_project': '创新创业训练',
    'internship_experience': '国际组织实习',
    'military_experience': '参军入伍服兵役',
    'volunteer_work': '志愿服务',
    'honor_title': '荣誉称号',
    'social_activity': '社会工作',
    'sports_event': '体育比赛',
    'english_test_score': '英语成绩',
    
    // 英语成绩类 - 详细中文表述
    'english_cet4': '全国大学英语四级考试',
    'english_cet6': '全国大学英语六级考试',
    'english_other': '其他英语成绩',
    'cet4': '全国大学英语四级考试',
    'cet6': '全国大学英语六级考试',
    'english_test': '英语考试',
    'toefl': '托福考试',
    'ielts': '雅思考试',
    'gre': 'GRE考试',
    'gmat': 'GMAT考试',
    
    // 学术专长类 - 标准化中文表述
    'research': '科研成果',
    'academic_paper': '学术论文',
    'paper': '学术论文',
    'patent_work': '发明专利',
    'patent': '发明专利',
    'innovation_project': '创新创业训练项目',
    'innovation_entrepreneurship': '创新创业训练',
    'research_project': '研究项目',
    'project': '项目',
    
    // 综合表现类 - 完整规范表述
    'international_internship': '国际组织实习',
    'military_service': '参军入伍服兵役',
    'volunteer_service': '志愿服务',
    'honorary_title': '荣誉称号',
    'honor_award': '荣誉奖项',
    'social_work': '社会工作',
    'sports_competition': '体育比赛',
    'international': '国际组织实习',
    
    // 详细子类映射
    'A': 'A类期刊论文',
    'B': 'B类期刊论文',
    'C': 'C类期刊论文',
    'invention': '发明专利',
    'utility': '实用新型专利',
    'independent': '独立作者',
    'first': '第一作者',
    'other': '其他作者',
    'national': '国家级竞赛',
    'provincial': '省级竞赛',
    'A+': 'A+类学科竞赛',
    'A-': 'A-类学科竞赛',
    'individual': '个人参赛',
    'team2': '2人团队',
    'team3': '2-3人团队',
    'team4': '4-5人团队',
    
    // 扩展更多可能的类型
    'paper_publication': '论文发表',
    'professional_certification': '专业认证',
    'leadership_experience': '领导力经历',
    'academic_excellence': '学术优秀',
    'community_service': '社区服务',
    'international_exchange': '国际交流',
    'other_type': '其他',
    
    // 新增常见类型
    'scholarship': '奖学金',
    'national_scholarship': '国家奖学金',
    'provincial_scholarship': '省级奖学金',
    'school_scholarship': '校级奖学金',
    'excellent_student': '优秀学生',
    'excellent_student_leader': '优秀学生干部',
    'merit_student': '三好学生',
    'sports_meeting': '运动会',
    'basketball': '篮球比赛',
    'football': '足球比赛',
    'volleyball': '排球比赛',
    'cultural_activity': '文化活动',
    'art_performance': '文艺表演',
    'social_service': '社会服务',
    'field_work': '实地调研',
    'course_project': '课程项目',
    'team_project': '团队项目',
    'individual_project': '个人项目',
    'certificate': '证书',
    'skill_certificate': '技能证书',
    'professional_certificate': '职业证书',
    
    // 可能的后端返回值（小写版本）
    'a': 'A类期刊论文',
    'b': 'B类期刊论文',
    'c': 'C类期刊论文',
    'a+': 'A+类学科竞赛',
    'a-': 'A-类学科竞赛',
    
    // 数值类型转换（如果后端返回数字）
    '0': '其他',
    '1': '英语成绩',
    '2': '科研成果',
    '3': '学业竞赛',
    '4': '创新创业',
    '5': '社会实践',
    '6': '志愿服务',
    '7': '荣誉称号',
    '8': '体育比赛',
    '9': '国际交流',
    
    // 直接替换模式 - 确保即使是完整英文单词也能被翻译
    'Scientific Research': '科研成果',
    'Research Achievement': '科研成果',
    'Academic Competition': '学业竞赛',
    'Innovation Training': '创新创业训练',
    'International Internship': '国际组织实习',
    'Military Service': '参军入伍服兵役',
    'Volunteer Work': '志愿服务',
    'Honorary Title': '荣誉称号',
    'Social Work': '社会工作',
    'Sports Competition': '体育比赛',
    'English Score': '英语成绩',
    
    // 确保所有可能的核心类型都有映射
    'research_achievement': '科研成果',
    'academic_achievement': '学术成果',
    'contest': '竞赛',
    'innovation_training': '创新创业训练',
    'internship_international': '国际组织实习',
    'military_experience': '参军入伍服兵役',
    'volunteer_activity': '志愿服务',
    'award': '荣誉奖项',
    'practice': '实践',
    'competition_sports': '体育比赛',
    'english_exam': '英语成绩',
    
    // 新增可能的后端返回值
    'SCIENTIFIC': '科研成果',
    'ACADEMIC': '科研成果',
    'COMPETITION': '学业竞赛',
    'INNOVATION': '创新创业训练',
    'INTERNSHIP': '国际组织实习',
    'MILITARY': '参军入伍服兵役',
    'VOLUNTEER': '志愿服务',
    'HONOR': '荣誉称号',
    'SOCIAL': '社会工作',
    'SPORTS': '体育比赛',
    'ENGLISH': '英语成绩',
    'CCF': 'CCF CSP认证',
    'CCF_CSP': 'CCF CSP认证'
  }
  
  // 尝试直接匹配
  if (typeMap[typeStr]) {
    console.log('类型直接匹配成功:', typeStr, '->', typeMap[typeStr])
    return typeMap[typeStr]
  }
  
  // 尝试小写匹配
  const lowerType = typeStr.toLowerCase()
  if (typeMap[lowerType]) {
    console.log('小写类型匹配成功:', typeStr, '->', typeMap[lowerType])
    return typeMap[lowerType]
  }
  
  // 尝试大写匹配
  const upperType = typeStr.toUpperCase()
  if (typeMap[upperType]) {
    console.log('大写类型匹配成功:', typeStr, '->', typeMap[upperType])
    return typeMap[upperType]
  }
  
  // 尝试移除空格和特殊字符后的匹配
  const normalizedType = typeStr.replace(/[\s_-]/g, '').toLowerCase()
  if (typeMap[normalizedType]) {
    console.log('标准化类型匹配成功:', typeStr, '->', typeMap[normalizedType])
    return typeMap[normalizedType]
  }
  
  // 尝试移除空格和特殊字符后的大写匹配
  const normalizedUpperType = typeStr.replace(/[\s_-]/g, '').toUpperCase()
  if (typeMap[normalizedUpperType]) {
    console.log('标准化大写类型匹配成功:', typeStr, '->', typeMap[normalizedUpperType])
    return typeMap[normalizedUpperType]
  }
  
  // 调试：标记未映射的类型
  console.warn('未映射的项目类型:', typeStr)
  
  // 对于未映射的类型，使用硬编码的映射来确保中文显示
// 这是最后的保障机制
if (lowerType.includes('scientific') || lowerType.includes('research')) {
    console.log('包含scientific或research，返回科研成果')
    return '科研成果'
} else if (lowerType.includes('academic_paper') || lowerType.includes('academic_papers')) {
    console.log('包含academic_paper或academic_papers，返回学术论文')
    return '学术论文'
} else if (lowerType.includes('patent_work') || lowerType.includes('patent_works') || lowerType.includes('patent')) {
    console.log('包含patent_work或patent_works或patent，返回发明专利')
    return '发明专利'
} else if (lowerType.includes('competition') || lowerType.includes('contest')) {
    console.log('包含competition或contest，返回学业竞赛')
    return '学业竞赛'
} else if (lowerType.includes('innovation')) {
    console.log('包含innovation，返回创新创业训练')
    return '创新创业训练'
} else if (lowerType.includes('internship') || lowerType.includes('international')) {
    console.log('包含internship或international，返回国际组织实习')
    return '国际组织实习'
} else if (lowerType.includes('military')) {
    console.log('包含military，返回参军入伍服兵役')
    return '参军入伍服兵役'
} else if (lowerType.includes('volunteer')) {
    console.log('包含volunteer，返回志愿服务')
    return '志愿服务'
} else if (lowerType.includes('honor') || lowerType.includes('award')) {
    console.log('包含honor或award，返回荣誉称号')
    return '荣誉称号'
} else if (lowerType.includes('social')) {
    console.log('包含social，返回社会工作')
    return '社会工作'
} else if (lowerType.includes('sports') || lowerType.includes('athletic')) {
    console.log('包含sports或athletic，返回体育比赛')
    return '体育比赛'
} else if (lowerType.includes('english') || lowerType.includes('score')) {
    console.log('包含english或score，返回英语成绩')
    return '英语成绩'
} else if (lowerType.includes('ccf')) {
    console.log('包含ccf，返回CCF CSP认证')
    return 'CCF CSP认证'
}
  
  // 作为最后的手段，使用一个默认映射
  // 如果都不匹配，返回一个中文默认值，确保显示不是英文
  console.log('所有匹配都失败，返回未分类项目')
  return '未分类项目'
}

// 获取子类别中文文本
const getSubCategoryText = (subCategory) => {
  if (!subCategory) return ''
  // 检查是否已经是中文（包含中文字符）
  if (/[\u4e00-\u9fa5]/.test(subCategory)) {
    return subCategory
  }
  // 子类别中英文映射 - 专业术语标准翻译
  const subCategoryMap = {
    // 英语相关子类别（标准化翻译）
    'CET4': '全国大学英语四级',
    'CET6': '全国大学英语六级',
    'TOEFL': '托福考试',
    'IELTS': '雅思考试',
    'GRE': '美国研究生入学考试',
    'PETS': '全国公共英语等级考试',
    'BEC': '剑桥商务英语考试',
    'OTHER': '其他英语考试',
    
    // 科研相关子类别（学术规范）
    'Paper': '学术论文',
    'Journal Paper': '期刊论文',
    'Conference Paper': '会议论文',
    'Patent': '专利',
    'Invention Patent': '发明专利',
    'Utility Model Patent': '实用新型专利',
    'Design Patent': '外观设计专利',
    'Project': '研究项目',
    'Research Project': '研究项目',
    'Innovation Project': '创新项目',
    'A类论文': 'A类论文',
    'B类论文': 'B类论文',
    'C类论文': 'C类论文',
    'SCI论文': 'SCI收录论文',
    'EI论文': 'EI收录论文',
    'CSSCI论文': 'CSSCI来源期刊论文',
    'CSCD论文': 'CSCD来源期刊论文',
    '发明专利': '发明专利',
    '实用新型专利': '实用新型专利',
    '外观设计专利': '外观设计专利',
    
    // 竞赛相关子类别（官方分类）
    '国家级': '国家级',
    'National': '国家级',
    '省级': '省级',
    'Provincial': '省级',
    '市级': '市级',
    'Municipal': '市级',
    '校级': '校级',
    'University': '校级',
    '院级': '院级',
    'College': '院级',
    '国际级': '国际级',
    'International': '国际级',
    'CCF推荐': 'CCF推荐会议/期刊',
    'CCF Recommended': 'CCF推荐会议/期刊',
    '一等奖': '一等奖',
    'First Prize': '一等奖',
    '二等奖': '二等奖',
    'Second Prize': '二等奖',
    '三等奖': '三等奖',
    'Third Prize': '三等奖',
    '特等奖': '特等奖',
    'Special Prize': '特等奖',
    'Grand Prize': '特等奖',
    '金奖': '金奖',
    'Gold Medal': '金奖',
    '银奖': '银奖',
    'Silver Medal': '银奖',
    '铜奖': '铜奖',
    'Bronze Medal': '铜奖',
    
    // 志愿服务子类别（标准分类）
    '社区服务': '社区服务',
    'Community Service': '社区服务',
    '环保活动': '环境保护活动',
    'Environmental Protection': '环境保护活动',
    '教育支持': '教育支持服务',
    'Education Support': '教育支持服务',
    '国际志愿': '国际志愿服务',
    'International Volunteer': '国际志愿服务',
    '医疗服务': '医疗健康服务',
    'Medical Service': '医疗健康服务',
    '文化传承': '文化传承服务',
    'Cultural Heritage': '文化传承服务',
    
    // 组织形式（规范表述）
    '个人': '个人',
    'Individual': '个人',
    '团队': '团队',
    'Team': '团队',
    '小组': '小组',
    'Group': '小组',
    '集体': '集体',
    'Collective': '集体',
    
    // 奖学金类别（标准名称）
    '国家奖学金': '国家奖学金',
    'National Scholarship': '国家奖学金',
    '国家励志奖学金': '国家励志奖学金',
    'National Encouragement Scholarship': '国家励志奖学金',
    '校级一等奖学金': '校级一等奖学金',
    '校级二等奖学金': '校级二等奖学金',
    '校级三等奖学金': '校级三等奖学金',
    
    // 科研项目类别（规范名称）
    '大创项目': '大学生创新创业训练项目',
    'SRTP项目': '大学生科研训练计划项目',
    '省级大创': '省级大学生创新创业训练项目',
    '国家级大创': '国家级大学生创新创业训练项目'
  }
  
  // 尝试精确匹配
  if (subCategoryMap[subCategory]) {
    return subCategoryMap[subCategory]
  }
  
  // 尝试部分匹配，保持专业术语一致性
  let chineseSubCategory = subCategory
  const termMap = {
    // 个人/团队相关术语
    'Individual': '个人',
    'Team': '团队',
    'Group': '小组',
    'Collective': '集体',
    
    // 奖项等级术语
    'First': '第一',
    'Second': '第二',
    'Third': '第三',
    'Special': '特等',
    'Grand': '特别',
    'Gold': '金',
    'Silver': '银',
    'Bronze': '铜',
    'Champion': '冠军',
    'Runner-up': '亚军',
    'Third Place': '季军',
    
    // 级别术语
    'National': '国家',
    'Provincial': '省级',
    'Municipal': '市级',
    'University': '校级',
    'College': '院级',
    'Department': '系级',
    'International': '国际',
    
    // 服务类型术语
    'Community': '社区',
    'Environment': '环境',
    'Education': '教育',
    'Volunteer': '志愿',
    'Medical': '医疗',
    'Health': '健康',
    'Cultural': '文化',
    'Heritage': '传承',
    
    // 学术术语
    'Scholarship': '奖学金',
    'Research': '研究',
    'Innovation': '创新',
    'Project': '项目',
    'Paper': '论文',
    'Patent': '专利',
    
    // 活动类型术语
    'Competition': '竞赛',
    'Contest': '比赛',
    'Tournament': '锦标赛',
    'Challenge': '挑战赛',
    
    // 成果类型术语
    'Award': '奖项',
    'Prize': '奖',
    'Medal': '奖',
    'Certificate': '证书'
  }
  
  // 替换常见术语，使用边界匹配确保单词完整替换
  Object.entries(termMap).forEach(([english, chinese]) => {
    const regex = new RegExp(`\\b${english}\\b`, 'gi')
    chineseSubCategory = chineseSubCategory.replace(regex, chinese)
  })
  
  return chineseSubCategory
}

// 获取项目名称中文文本
const getProjectTitleText = (title) => {
  if (!title) return ''
  // 检查是否已经是中文（包含中文字符）
  if (/[\u4e00-\u9fa5]/.test(title)) {
    return title
  }
  // 项目名称中英文映射（常见英文项目名称转换）- 专业术语标准翻译
  const titleMap = {
    // 英语考试（标准化翻译）
    'CET4': '全国大学英语四级考试',
    'CET6': '全国大学英语六级考试',
    'TOEFL': '托福考试',
    'IELTS': '雅思考试',
    'GRE': '美国研究生入学考试',
    'PETS': '全国公共英语等级考试',
    'BEC': '剑桥商务英语考试',
    
    // 学科竞赛（官方名称）
    'ACM-ICPC': 'ACM国际大学生程序设计竞赛',
    'ICPC': '国际大学生程序设计竞赛',
    'CCPC': '中国大学生程序设计竞赛',
    '蓝桥杯': '蓝桥杯全国软件和信息技术专业人才大赛',
    'Lan Qiao Cup': '蓝桥杯全国软件和信息技术专业人才大赛',
    '互联网+': '互联网+大学生创新创业大赛',
    'Internet+': '互联网+大学生创新创业大赛',
    '挑战杯': '挑战杯全国大学生课外学术科技作品竞赛',
    'Challenge Cup': '挑战杯全国大学生课外学术科技作品竞赛',
    '创青春': '创青春全国大学生创业大赛',
    'Chuang Qingchun': '创青春全国大学生创业大赛',
    'CSP': '计算机软件能力认证',
    'CCF CSP': 'CCF CSP认证加分',
    'CCF-CSP': 'CCF CSP认证加分',
    'NOIP': '全国青少年信息学奥林匹克联赛',
    'NOI': '全国青少年信息学奥林匹克竞赛',
    
    // 专利类型（法律术语）
    'Invention Patent': '发明专利',
    'Utility Model Patent': '实用新型专利',
    'Design Patent': '外观设计专利',
    'Patent for Invention': '发明专利',
    
    // 科研项目（规范名称）
    'Innovation Project': '大学生创新训练项目',
    'Entrepreneurship Project': '大学生创业训练项目',
    'Innovation and Entrepreneurship Training Program': '大学生创新创业训练计划',
    'SRTP': '大学生科研训练计划',
    'Research Training Program': '科研训练计划',
    
    // 学术成果（标准术语）
    'Thesis': '学位论文',
    'Dissertation': '学位论文',
    'Academic Paper': '学术论文',
    'Journal Paper': '期刊论文',
    'Conference Paper': '会议论文',
    'EI': '工程索引',
    'SCI': '科学引文索引',
    'CSSCI': '中文社会科学引文索引',
    'CSCD': '中国科学引文数据库',
    
    // 志愿服务（官方表述）
    'Volunteer Service': '志愿服务',
    'Community Service': '社区服务',
    'Social Volunteer': '社会志愿者',
    'International Volunteer': '国际志愿者',
    
    // 荣誉称号（规范表述）
    'Merit Student': '三好学生',
    'Outstanding Student': '优秀学生',
    'Excellent Student Leader': '优秀学生干部',
    'National Scholarship': '国家奖学金',
    'Provincial Scholarship': '省级奖学金',
    'University Scholarship': '校级奖学金',
    
    // 社会实践（标准术语）
    'Social Practice': '社会实践',
    'Internship': '实习',
    'Professional Practice': '专业实习',
    'Field Work': '田野调查',
    
    // 体育竞赛（标准名称）
    'Sports Meeting': '运动会',
    'Athletics Meeting': '田径运动会',
    'Basketball Game': '篮球比赛',
    'Football Match': '足球比赛',
    'National Games': '全国运动会',
    
    // 其他专业术语
    'Leadership': '领导力',
    'Communication Skills': '沟通能力',
    'Teamwork': '团队协作',
    'Professional Skills': '专业技能',
    'Certification': '认证',
    'Qualification': '资格证书',
    'Training': '培训'
  }
  
  // 尝试精确匹配
  if (titleMap[title]) {
    return titleMap[title]
  }
  
  // 尝试部分匹配（转换常见英文术语，保持专业一致性）
  let chineseTitle = title
  const termMap = {
    // 等级术语（标准化翻译）
    'National': '国家级',
    'Provincial': '省级',
    'Municipal': '市级',
    'University': '校级',
    'College': '院级',
    'Department': '系级',
    
    // 奖项术语（规范表述）
    'First Prize': '一等奖',
    'Second Prize': '二等奖',
    'Third Prize': '三等奖',
    'Special Prize': '特等奖',
    'Grand Prize': '特等奖',
    'Gold Medal': '金奖',
    'Silver Medal': '银奖',
    'Bronze Medal': '铜奖',
    'Champion': '冠军',
    'Runner-up': '亚军',
    'Third Place': '季军',
    'Winner': '获奖者',
    'Finalist': '入围者',
    
    // 组织形式术语（标准表述）
    'Team': '团队',
    'Individual': '个人',
    'Group': '小组',
    'Collective': '集体',
    
    // 活动类型术语（专业术语）
    'Competition': '竞赛',
    'Contest': '比赛',
    'Tournament': '锦标赛',
    'Competition': '竞赛',
    'Match': '比赛',
    'Game': '比赛',
    'Challenge': '挑战赛',
    'Hackathon': '黑客马拉松',
    
    // 成果类型术语（学术规范）
    'Award': '奖项',
    'Scholarship': '奖学金',
    'Patent': '专利',
    'Paper': '论文',
    'Thesis': '论文',
    'Dissertation': '学位论文',
    
    // 项目类型术语（标准名称）
    'Project': '项目',
    'Research': '研究',
    'Innovation': '创新',
    'Entrepreneurship': '创业',
    'Training': '训练',
    'Program': '计划',
    
    // 服务类型术语（官方表述）
    'Volunteer': '志愿者',
    'Service': '服务',
    'Social': '社会',
    'Community': '社区',
    'Practice': '实践',
    'Internship': '实习',
    'Fieldwork': '实地工作',
    
    // 能力素质术语（专业表述）
    'Leadership': '领导力',
    'Communication': '沟通',
    'Organization': '组织',
    'Management': '管理',
    'Professional': '专业',
    'Technical': '技术',
    'Skill': '技能',
    'Ability': '能力'
  }
  
  // 替换常见术语，保持专业术语一致性
  Object.entries(termMap).forEach(([english, chinese]) => {
    // 使用边界匹配确保单词完整替换
    const regex = new RegExp(`\\b${english}\\b`, 'gi')
    chineseTitle = chineseTitle.replace(regex, chinese)
  })
  
  return chineseTitle
}

// 查看申请详情
const viewApplication = (record) => {
  // 处理申请数据，确保有统一的attachments数组
  const processedRecord = processApplication(record)
  selectedApplication.value = processedRecord
  detailModalVisible.value = true
}

// 关闭详情模态框
const closeDetailModal = () => {
  detailModalVisible.value = false
  selectedApplication.value = {}
}

// 编辑申请
const editApplication = (record) => {
  // 跳转到材料上传页面并传递完整的申请数据
  router.push({
    path: '/student/add-application',
    query: { ...record, isEdit: true }
  })
}

// 撤回申请
const withdrawApplication = async (record) => {
  Modal.confirm({
    title: '确认撤回',
    content: `确定要撤回申请「${record.title}」吗？`,
    onOk: async () => {
      try {
        await api.withdrawApplication(record.id)
        message.success('申请已成功撤回')
        emit('refresh')
      } catch (error) {
        message.error('撤回失败：' + (error.response?.data?.detail || error.message || '未知错误'))
      }
    }
  })
}

// 删除申请
const deleteApplication = async (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要彻底删除申请「${record.title}」吗？删除后不可恢复！`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await api.deleteApplication(record.id)
        message.success('申请已成功删除')
        emit('refresh')
      } catch (error) {
        message.error('删除失败：' + (error.response?.data?.detail || error.message || '未知错误'))
      }
    }
  })
}

// 预览附件
const previewAttachment = (file) => {
  console.log('预览附件:', file)
  try {
    // 直接获取附件URL
    let url = ''
    
    if (typeof file === 'string') {
      // 如果file是字符串URL
      url = file
    } else if (typeof file === 'object' && file !== null) {
      // 如果file是对象，获取URL
      url = file.url || file.file_url || file.path || file.file_path || file.attachment_url || file.screenshot || file.score_report || ''
      if (!url) {
        console.error('附件对象没有有效的URL字段:', file)
        message.error('附件对象没有有效的URL字段')
        return
      }
    } else {
      // 处理无效格式
      console.error('无效的附件格式:', file)
      message.error('无效的附件格式')
      return
    }
    
    // 所有文件都使用浏览器自带的预览功能，在新标签页中打开
    window.open(url, '_blank')
  } catch (error) {
    console.error('预览附件失败:', error)
    message.error('预览附件失败，请稍后重试')
  }
}





// 监听屏幕宽度变化
onMounted(() => {
  checkScreenWidth()
  window.addEventListener('resize', checkScreenWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenWidth)
})

// 生成操作菜单
const getActionMenu = (record) => {
  const items = []
  
  // 添加查看操作
  items.push({
    label: '查看',
    key: 'view',
    onClick: () => viewApplication(record)
  })
  
  // 根据状态添加其他操作
  if (record.review_status === 'pending' || record.review_status.includes('reviewing') || record.review_status.includes('approved')) {
    // 只有待审核和审核中状态可以撤回和编辑
    if (record.review_status === 'pending' || record.review_status.includes('reviewing')) {
      items.push({
        label: '撤回',
        key: 'withdraw',
        danger: true,
        onClick: () => withdrawApplication(record)
      })
      items.push({
        label: '编辑',
        key: 'edit',
        onClick: () => editApplication(record)
      })
    }
  } else if (record.review_status.includes('rejected') || record.review_status === 'withdrawn') {
    items.push({
      label: '重新提交',
      key: 'resubmit',
      onClick: () => editApplication(record)
    })
    
    // 已撤回和审核未通过的申请都显示删除选项
    if (record.review_status === 'withdrawn' || record.review_status.includes('rejected')) {
      items.push({
        label: '删除',
        key: 'delete',
        danger: true,
        onClick: () => deleteApplication(record)
      })
    }
  }
  
  return items
}

// 检查是否为图片文件
const isImageFile = (file) => {
  if (!file) return false
  // 优先从URL中提取扩展名，因为name字段可能不包含扩展名
  const url = file.url || ''
  // 移除URL中的查询参数
  const urlWithoutQuery = url.split('?')[0]
  const name = file.name || urlWithoutQuery
  const lowerName = name.toLowerCase()
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
  // 检查文件名或URL是否以图片扩展名结尾
  const isImage = imageExtensions.some(ext => lowerName.endsWith(ext))
  console.log(`检查文件是否为图片: name=${name}, url=${url}, urlWithoutQuery=${urlWithoutQuery}, isImage=${isImage}`)
  return isImage
}

// 检查附件是否为图片（用于材料列显示）
const isImageAttachment = (attachment) => {
  if (typeof attachment === 'string') {
    // 如果是字符串URL，直接检查扩展名
    return attachment.toLowerCase().endsWith('.jpg') || 
           attachment.toLowerCase().endsWith('.jpeg') || 
           attachment.toLowerCase().endsWith('.png') || 
           attachment.toLowerCase().endsWith('.gif') || 
           attachment.toLowerCase().endsWith('.bmp') || 
           attachment.toLowerCase().endsWith('.webp') || 
           attachment.toLowerCase().endsWith('.svg')
  } else if (typeof attachment === 'object' && attachment !== null) {
    // 如果是对象，使用isImageFile函数检查
    return isImageFile(attachment)
  }
  return false
}

// 检查附件是否为PDF（用于申请详情显示）
const isPdfAttachment = (attachment) => {
  if (typeof attachment === 'string') {
    // 如果是字符串URL，直接检查扩展名
    return attachment.toLowerCase().endsWith('.pdf')
  } else if (typeof attachment === 'object' && attachment !== null) {
    // 如果是对象，检查文件名或URL
    const url = attachment.url || attachment.file_url || attachment.path || attachment.file_path || attachment.attachment_url || ''
    const name = attachment.name || url.split('/').pop() || ''
    return name.toLowerCase().endsWith('.pdf')
  }
  return false
}

// 获取附件的URL（用于材料列显示）
const getAttachmentUrl = (attachment) => {
  if (typeof attachment === 'string') {
    // 如果是字符串URL，直接返回
    return attachment
  } else if (typeof attachment === 'object' && attachment !== null) {
    // 如果是对象，获取URL
    return attachment.url || attachment.file_url || attachment.path || attachment.file_path || attachment.attachment_url || ''
  }
  return ''
}

// 获取附件的名称（用于材料列显示）
const getAttachmentName = (attachment) => {
  if (typeof attachment === 'string') {
    // 如果是字符串URL，获取文件名
    return attachment.split('/').pop() || ''
  } else if (typeof attachment === 'object' && attachment !== null) {
    // 如果是对象，获取名称
    return attachment.name || attachment.original_name || attachment.split('/').pop() || ''
  }
  return ''
}

// 下载文件
const downloadFile = (file) => {
  if (!file || !file.url) {
    message.error('文件下载地址无效')
    return
  }
  
  // 创建下载链接
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name || 'download.pdf'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
/* 应用列表容器 */
.application-list {
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  transition: box-shadow 0.3s ease;
}

.application-list:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

/* 表格样式 */
.application-table {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
}

/* 行样式 */
.withdrawn-row {
  background-color: #f5f5f5;
  opacity: 0.7;
}

.withdrawn-row:hover {
  background-color: #e8e8e8 !important;
}

/* 状态标签样式 */
.status-tag {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 表格单元格样式 */
.application-table .ant-table-thead > tr > th,
.application-table .ant-table-tbody > tr > td {
  padding: 12px 16px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 表头样式 */
.application-table .ant-table-thead > tr > th {
  font-weight: 600;
  color: #262626;
  background-color: #fafafa;
  border-right: 1px solid #f0f0f0;
  font-size: 14px;
}

/* 内容区域样式 */
.application-table .ant-table-tbody > tr > td {
  color: #595959;
  border-right: 1px solid #f0f0f0;
}

/* 响应式设计 - 媒体查询 */
@media (max-width: 768px) {
  .application-list {
    padding: 10px;
  }
  
  .application-table {
    font-size: 12px;
  }
  
  .application-table .ant-table-thead > tr > th,
  .application-table .ant-table-tbody > tr > td {
    padding: 8px 4px;
    font-size: 12px;
  }
  
  /* 移动端隐藏部分列 */
  .application-table .ant-table-thead > tr > th:nth-child(3),
  .application-table .ant-table-tbody > tr > td:nth-child(3) {
    display: none;
  }
  
  /* 调整移动端列宽 */
  .application-table .ant-table-thead > tr > th:first-child,
  .application-table .ant-table-tbody > tr > td:first-child {
    min-width: 120px;
  }
}

@media (max-width: 480px) {
  /* 移动端隐藏更多列 */
  .application-table .ant-table-thead > tr > th:nth-child(4),
  .application-table .ant-table-tbody > tr > td:nth-child(4) {
    display: none;
  }
  
  /* 进一步调整移动端列宽 */
  .application-table .ant-table-thead > tr > th:first-child,
  .application-table .ant-table-tbody > tr > td:first-child {
    min-width: 100px;
  }
}

/* 操作按钮样式优化 */
.application-table .ant-btn-link {
  padding: 6px 16px;
  min-width: 70px;
  text-align: center;
  border-radius: 4px;
  transition: all 0.2s ease;
  font-size: 14px;
}

.application-table .ant-btn-small {
  padding: 4px 12px;
  font-size: 12px;
}

.application-table .ant-btn-link:hover {
  background-color: rgba(0, 0, 0, 0.02);
  color: #1890ff;
  text-decoration: none;
}

.application-table .ant-btn-link.danger:hover {
  color: #ff4d4f;
  background-color: rgba(255, 77, 79, 0.04);
}

/* 表格行悬停效果 */
.application-table .ant-table-tbody > tr:hover > td {
  background-color: #fafafa;
  transition: all 0.2s ease;
}

/* 已撤回状态标签样式 */
.withdrawn-tag {
  text-decoration: line-through;
}

/* 下拉菜单样式优化 */
.application-table .ant-dropdown-menu-item {
  padding: 8px 16px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.application-table .ant-dropdown-menu-item:hover {
  background-color: #e6f7ff;
  color: #1890ff;
}

.application-table .ant-dropdown-menu-item-danger:hover {
  background-color: #fff1f0;
  color: #ff4d4f;
}

/* 空列表样式 */
.empty-list {
  padding: 60px 0;
  text-align: center;
}

/* 附件列表样式 */
.attachments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-start;
  margin: 8px 0;
}

.attachment-tag {
  cursor: pointer;
}

.attachment-tag:hover {
  opacity: 0.8;
}

/* 材料附件项样式 */
.attachment-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 120px;
  height: 140px;
  background-color: #fafafa;
}

.attachment-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

/* 图片附件样式 */
.image-attachment {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.attachment-preview-image {
  max-width: 100%;
  max-height: 100px;
  object-fit: contain;
  border-radius: 4px;
  margin-bottom: 8px;
}

/* PDF附件样式 */
.pdf-attachment {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.pdf-icon {
  width: 80px;
  height: 100px;
  background-color: #ff5722;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  border-radius: 4px;
  margin-bottom: 8px;
}

/* 其他文件类型样式 */
.other-attachment {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.other-icon {
  width: 80px;
  height: 100px;
  background-color: #909399;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  border-radius: 4px;
  margin-bottom: 8px;
}

/* 附件名称样式 */
.attachment-name {
  font-size: 12px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
  color: #333;
}

/* 预览样式 */
.preview-container {
  position: relative;
  text-align: center;
  padding: 20px;
}

.close-preview-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 16px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  padding: 5px;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}

.pdf-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}

.other-preview {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
</style>

<style scoped>
.application-detail {
  margin-top: 10px;
}
</style>