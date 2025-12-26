<template>
  <div class="teacher-applications">
    <h2>申请审批列表</h2>
    
    <!-- 筛选条件 -->
    <div class="filter-section">
      <a-row :gutter="[16, 16]">
        <a-col :span="6">
          <a-select v-model:value="filterForm.status" placeholder="申请状态">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="pending">等待审核</a-select-option>
            <a-select-option value="approved">审核通过</a-select-option>
            <a-select-option value="rejected">未通过</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="12">
          <a-input v-model:value="filterForm.searchText" placeholder="搜索学生姓名或项目名称" @pressEnter="handleSearch" />
        </a-col>
        <a-col :span="6">
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-col>
      </a-row>
    </div>

    <!-- 状态分类筛选 -->
    <div class="status-filter" style="margin: 16px 0;">
      <h3 style="margin-bottom: 8px;">状态分类：</h3>
      <div class="filter-tags">
        <a-tag
          v-for="status in statusCategories"
          :key="status.value"
          :color="filterForm.statusCategories.includes(status.value) ? 'blue' : 'default'"
          @click="toggleStatusCategory(status.value)"
          style="cursor: pointer; margin: 4px;"
        >
          {{ status.label }} ({{ statusCounts[status.value] || 0 }})
        </a-tag>
      </div>
    </div>

    <!-- 项目类型分类筛选 -->
    <div class="project-type-filter" style="margin: 16px 0;">
      <h3 style="margin-bottom: 8px;">项目类型分类：</h3>
      <div class="filter-tags">
        <a-tag
          v-for="type in projectTypes"
          :key="type.value"
          :color="filterForm.projectTypes.includes(type.value) ? 'blue' : 'default'"
          @click="toggleProjectType(type.value)"
          style="cursor: pointer; margin: 4px;"
        >
          {{ type.label }} ({{ projectTypeCounts[type.value] || 0 }})
        </a-tag>
      </div>
    </div>

    <!-- 直接展示筛选结果表格 -->
    <a-table
      :columns="columns"
      :data-source="filteredApplications"
      :pagination="false"
      :row-key="record => record.id"
      :loading="loading"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'actions'">
          <div class="action-buttons">
            <a-button type="link" @click="handleView(record)">查看</a-button>
          </div>
        </template>
      </template>
    </a-table>
    
    <!-- 如果没有符合条件的申请 -->
    <div v-if="filteredApplications.length === 0 && !loading" class="no-data">
      <a-empty description="暂无符合条件的申请" />
    </div>
    
    <!-- 如果没有任何申请 -->
    <a-card v-if="applications.length === 0" style="margin-top: 20px;">
      <a-empty description="暂无符合条件的申请" />
    </a-card>
  </div>
    <!-- 申请详情模态框 -->
    <a-modal
      v-model:open="viewModalVisible"
      title="申请详情"
      width="800px"
      :footer="footerButtons"
    >
      <div v-if="selectedApplication" class="application-detail">
        <a-descriptions bordered :column="2">
          <a-descriptions-item label="学生姓名">{{ selectedApplication.studentName }}</a-descriptions-item>
          <a-descriptions-item label="学号">{{ selectedApplication.studentId }}</a-descriptions-item>
          <a-descriptions-item label="班级">{{ selectedApplication.className }}</a-descriptions-item>
          <a-descriptions-item label="项目类型">{{ getProjectTypeText(selectedApplication.projectType) }}</a-descriptions-item>
          <a-descriptions-item label="项目名称">{{ selectedApplication.projectName }}</a-descriptions-item>
          <a-descriptions-item label="申请时间">{{ formatDate(selectedApplication.applyTime) }}</a-descriptions-item>
          <a-descriptions-item label="当前状态">
            <a-tag :color="getStatusColor(selectedApplication.status)">
              {{ getStatusText(selectedApplication.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="申请分数">{{ selectedApplication.score }}分</a-descriptions-item>
          <a-descriptions-item label="详细描述" :span="2">{{ selectedApplication.description }}</a-descriptions-item>
          <a-descriptions-item label="证明材料" :span="2">
            <div class="proof-materials">
              <div v-for="(material, index) in selectedApplication.proofMaterials" :key="index" class="material-item">
                <a-typography-text strong>{{ material.name }}</a-typography-text>
                <a-button type="link" @click="handlePreview(material)">预览</a-button>
                <a-button type="link" @click="handleDownload(material.url)">下载</a-button>
              </div>
              <div v-if="!selectedApplication.proofMaterials || selectedApplication.proofMaterials.length === 0" class="no-materials">
                暂无证明材料
              </div>
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>

  <!-- 通过申请模态框 -->
  <a-modal
    v-model:open="approveModalVisible"
    title="通过申请"
    @ok="handleConfirmApprove"
    @cancel="approveModalVisible = false"
  >
    <div v-if="selectedApplication" class="approval-form">
      <a-descriptions bordered :column="1" size="small" style="margin-bottom: 16px;">
        <a-descriptions-item label="学生姓名">{{ selectedApplication.studentName }}</a-descriptions-item>
        <a-descriptions-item label="项目名称">{{ selectedApplication.projectName }}</a-descriptions-item>
      </a-descriptions>
      
      <a-form layout="vertical">
        <a-form-item label="审批分数" required>
          <a-input-number 
            v-model:value="approveForm.score" 
            :min="0" 
            :max="100" 
            style="width: 100%" 
            placeholder="请输入审批分数"
          />
        </a-form-item>
      </a-form>
    </div>
  </a-modal>

  <!-- 拒绝申请模态框 -->
  <a-modal
    v-model:open="rejectModalVisible"
    title="拒绝申请"
    @ok="handleConfirmReject"
    @cancel="() => { rejectModalVisible.value = false }"
    :footer="[
      h('a-button', {
        onClick: () => { rejectModalVisible.value = false },
        class: 'approval-button cancel-button'
      }, '取消'),
      h('a-button', {
        type: 'primary',
        onClick: handleConfirmReject,
        class: 'approval-button reject-button'
      }, '确认拒绝')
    ]"
  >
    <div v-if="selectedApplication" class="approval-form">
      <a-descriptions bordered :column="1" size="small" style="margin-bottom: 16px;">
        <a-descriptions-item label="学生姓名">{{ selectedApplication.studentName }}</a-descriptions-item>
        <a-descriptions-item label="项目名称">{{ selectedApplication.projectName }}</a-descriptions-item>
      </a-descriptions>
      
      <a-form layout="vertical">
        <a-form-item label="拒绝理由" required>
          <a-textarea 
            v-model:value="rejectForm.reason" 
            :rows="4" 
            placeholder="请详细说明拒绝理由"
          />
        </a-form-item>
      </a-form>
    </div>
  </a-modal>
  
  <!-- 证明材料预览模态框 -->
  <a-modal
    v-model:open="previewModalVisible"
    title="材料预览"
    width="800px"
    @cancel="closePreviewModal"
    :footer="[
      h('a-button', {
        onClick: closePreviewModal
      }, '关闭')
    ]"
  >
    <div v-if="selectedMaterial" class="material-preview">
      <!-- 图片预览 -->
      <div v-if="isImageFile(selectedMaterial)" class="image-preview">
        <img :src="selectedMaterial.url" alt="Preview" style="max-width: 100%; max-height: 600px; object-fit: contain;" />
      </div>
      <!-- 其他文件类型，提供下载链接 -->
      <div v-else class="other-preview">
        <a-empty description="无法直接预览此文件类型" />
        <a-button type="primary" style="margin-top: 16px;" @click="handleDownload(selectedMaterial)">
          下载文件
        </a-button>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { message } from 'ant-design-vue'
import api from '@/utils/api'

// 筛选条件
const filterForm = ref({
  status: '',
  searchText: '',
  projectTypes: [],
  statusCategories: []
})

// 项目类型
const projectTypes = [
  // 英语成绩类
  { label: '大学英语四级', value: 'english_cet4' },
  { label: '大学英语六级', value: 'english_cet6' },
  // 学术专长类
  { label: '学术论文', value: 'academic_paper' },
  { label: '专利著作', value: 'patent_work' },
  { label: '学业竞赛', value: 'academic_competition' },
  { label: '大创项目', value: 'innovation_project' },
  { label: 'CCF CSP认证', value: 'ccf_csp' },
  // 综合表现类
  { label: '国际组织实习', value: 'international_internship' },
  { label: '参军入伍', value: 'military_service' },
  { label: '志愿服务', value: 'volunteer_service' },
  { label: '荣誉称号', value: 'honorary_title' },
  { label: '社会工作', value: 'social_work' },
  { label: '体育比赛', value: 'sports_competition' }
]

// 状态分类
const statusCategories = [
  { label: '未审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' }
]

// 表格列
const columns = [
  { title: '项目名称', dataIndex: 'projectName', key: 'projectName', width: 200 },
  { title: '学生姓名', dataIndex: 'studentName', key: 'studentName', width: 120 },
  { title: '学号', dataIndex: 'studentId', key: 'studentId', width: 120 },
  { title: '班级', dataIndex: 'className', key: 'className', width: 150 },
  { title: '项目类型', dataIndex: 'projectType', key: 'projectType', width: 120, render: (_, record) => getProjectTypeText(record.projectType) },
  { title: '申请时间', dataIndex: 'applyTime', key: 'applyTime', width: 180, render: (_, record) => formatDate(record.applyTime) },
  { title: '申请分数', dataIndex: 'score', key: 'score', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', dataIndex: 'actions', key: 'actions', width: 120, fixed: 'right' }
]

// 申请列表
const applications = ref([])
const loading = ref(false)
const currentUser = ref(null)

// 按状态分组的申请列表
const applicationsByStatus = computed(() => {
  const result = {}
  applications.value.forEach(app => {
    if (!result[app.status]) {
      result[app.status] = []
    }
    result[app.status].push(app)
  })
  return result
})

// 按项目类型分组的申请列表
const getApplicationsByProjectType = (apps) => {
  const result = {}
  apps.forEach(app => {
    if (!result[app.projectType]) {
      result[app.projectType] = []
    }
    result[app.projectType].push(app)
  })
  return result
}

// 统计每种状态下的申请数量
const statusCounts = computed(() => {
  const counts = {
    pending: 0,
    approved: 0,
    rejected: 0,
    withdrawn: 0
  }
  
  applications.value.forEach(app => {
    const mainStatus = getMainStatusCategory(app.status)
    if (counts[mainStatus] !== undefined) {
      counts[mainStatus]++
    }
  })
  
  return counts
})

// 统计每种项目类型下的申请数量
const projectTypeCounts = computed(() => {
  const counts = {}
  // 初始化所有前端项目类型的计数为0
  projectTypes.forEach(type => {
    counts[type.value] = 0
  })
  
  applications.value.forEach(app => {
    // 获取原始英文项目类型
    const originalType = app.originalProjectType || app.application_type || app.type || 'unknown'
    
    // 找到对应的前端项目类型值
    const frontendTypes = getFrontendTypesByProjectType(originalType)
    
    // 增加每个匹配的前端项目类型的计数
    frontendTypes.forEach(frontendType => {
      if (counts[frontendType] !== undefined) {
        counts[frontendType]++
      }
    })
  })
  
  return counts
})

// 获取申请列表
const fetchApplications = async () => {
  loading.value = true
  try {
    // 构建查询参数，处理状态参数
    const params = {
      status: filterForm.value.status === 'all' ? '' : filterForm.value.status,
      search: filterForm.value.searchText,
      project_types: filterForm.value.projectTypes
    }
    
    const response = await api.teacher.getApplications(params)
    
    // 打印API返回的数据结构
    console.log('API Response:', response)
    console.log('First Application Data:', response.results ? response.results[0] : response[0])
    
    // 根据API返回格式处理数据
    let data = []
    if (response.results && Array.isArray(response.results)) {
      data = response.results
    } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
      data = response.data.results
    } else if (response.data && Array.isArray(response.data)) {
      data = response.data
    } else if (Array.isArray(response)) {
      data = response
    }
    
    // 添加调试日志，查看完整的数据结构
    console.log('完整数据列表:', data);
    if (data.length > 0) {
      console.log('第一个申请的完整数据:', data[0]);
      console.log('第一个申请的所有字段:', Object.keys(data[0]));
    }
    
    // 映射后端数据到前端期望的格式
    const mappedData = data.map(app => {
      // 状态映射
      let status = app.review_status || app.status || 'unknown';
      
      // 日期格式化
      const applyTime = new Date(app.created_at).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // 项目类型处理：使用与学生端相同的逻辑，确保显示中文
      let projectType = app.application_type || app.type || 'unknown';
      // 检查是否已经是中文
      if (!/[\u4e00-\u9fa5]/.test(projectType)) {
        // 使用全局定义的typeMap进行映射
        projectType = typeMap[projectType] || projectType;
      }
      
      // 尝试从不同字段获取分数
      let score = 0;
      // 英语成绩申请不加分，直接显示0
      if (app.type === 'english_score') {
        score = 0;
      } else {
        // 其他类型申请尝试多种可能的分数字段名
        if (app.score && app.score > 0) {
          score = app.score;
        } else if (app.estimated_score && app.estimated_score > 0) {
          score = app.estimated_score;
        } else if (app.bonus_points && app.bonus_points > 0) {
          score = app.bonus_points;
        } else if (app.exam_score && app.exam_score > 0) {
          score = app.exam_score;
        }
      }
      
      // 尝试从不同字段获取证明材料
      let proofMaterials = [];
      
      // 1. 首先处理后端collect_attachments函数返回的attachments字段
      // 该字段包含name、url和original_name字段的对象数组
      if (app.attachments && Array.isArray(app.attachments)) {
        console.log(`处理attachments字段，数组长度: ${app.attachments.length}`);
        app.attachments.forEach((attachment, index) => {
          if (attachment && attachment.url && typeof attachment.url === 'string' && attachment.url.trim()) {
            const fileName = attachment.original_name || attachment.name || attachment.url.split('/').pop() || `附件${index + 1}`;
            proofMaterials.push({ 
              url: attachment.url, 
              name: fileName 
            });
            console.log(`添加材料: ${fileName}, URL: ${attachment.url}`);
          }
        });
      }
      
      // 2. 处理其他可能的证明材料字段名
      const materialFields = [
        'screenshot', 'score_report', 'proof_materials',
        'materials', 'documents', 'file', 'files',
        'proof_files', 'evidence_files', 'supporting_documents'
      ];
      
      // 添加详细的调试日志，查看每个应用的类型和材料字段
      console.log(`处理申请类型: ${app.type || app.application_type}, ID: ${app.id}`);
      console.log('可用的材料字段:', Object.keys(app).filter(key => materialFields.includes(key)));
      
      // 遍历所有可能的材料字段
      for (const field of materialFields) {
        // 确保即使字段值为0或false也能被处理，只跳过undefined和null
        if (app[field] === undefined || app[field] === null) continue;
        
        console.log(`处理字段: ${field}, 值:`, app[field]);
        
        if (Array.isArray(app[field])) {
          // 数组类型的证明材料
          console.log(`字段 ${field} 是数组，长度: ${app[field].length}`);
          
          // 处理数组中的每个项，可能是URL字符串或对象
          app[field].forEach((item, index) => {
            if (typeof item === 'string' && item.trim()) {
              // 直接是URL字符串
              const fileName = item.split('/').pop() || `附件${index + 1}`;
              proofMaterials.push({ url: item, name: fileName });
              console.log(`添加材料: ${fileName}, URL: ${item}`);
            } else if (typeof item === 'object' && item.url) {
              // 是包含url字段的对象
              const fileName = item.name || item.original_name || item.url.split('/').pop() || `附件${index + 1}`;
              proofMaterials.push({ url: item.url, name: fileName });
              console.log(`添加材料: ${fileName}, URL: ${item.url}`);
            }
          });
        } else if (typeof app[field] === 'string') {
          // 单个字符串URL类型的证明材料
          if (app[field].trim()) {
            const fileName = app[field].split('/').pop() || '附件';
            proofMaterials.push({ url: app[field], name: fileName });
            console.log(`添加材料: ${fileName}, URL: ${app[field]}`);
          }
        } else if (typeof app[field] === 'object') {
          // 单个对象类型的证明材料
          const url = app[field].url || app[field].file_url || app[field].path;
          if (url && typeof url === 'string' && url.trim()) {
            const fileName = app[field].name || app[field].file_name || app[field].original_name || url.split('/').pop() || '附件';
            proofMaterials.push({ url, name: fileName });
            console.log(`添加材料: ${fileName}, URL: ${url}`);
          }
        }
      }
      
      // 添加最终的材料数量日志
      console.log(`申请 ${app.id} 最终材料数量: ${proofMaterials.length}`);
      
      // 2. 特殊处理英语成绩相关材料
      if (app.type && (app.type === 'english_score' || app.type.includes('english'))) {
        // 处理英语成绩报告
        if (app.cet4_report) {
          const fileName = app.cet4_report.split('/').pop() || '英语四级成绩报告';
          proofMaterials.push({ url: app.cet4_report, name: fileName });
        }
        if (app.cet6_report) {
          const fileName = app.cet6_report.split('/').pop() || '英语六级成绩报告';
          proofMaterials.push({ url: app.cet6_report, name: fileName });
        }
        // 处理其他可能的英语成绩报告字段
        if (app.english_report) {
          const fileName = app.english_report.split('/').pop() || '英语成绩报告';
          proofMaterials.push({ url: app.english_report, name: fileName });
        }
      }
      
      // 3. 特殊处理学术论文、专利等材料
      if (app.type && (app.type === 'academic_paper' || app.type === 'patent_work' || app.type.includes('research'))) {
        if (app.paper_pdf) {
          const fileName = app.paper_pdf.split('/').pop() || '论文文件';
          proofMaterials.push({ url: app.paper_pdf, name: fileName });
        }
        if (app.patent_certificate) {
          const fileName = app.patent_certificate.split('/').pop() || '专利证书';
          proofMaterials.push({ url: app.patent_certificate, name: fileName });
        }
      }
      
      // 4. 特殊处理竞赛获奖材料
      if (app.type && (app.type === 'academic_competition' || app.type.includes('competition'))) {
        if (app.award_certificate) {
          const fileName = app.award_certificate.split('/').pop() || '获奖证书';
          proofMaterials.push({ url: app.award_certificate, name: fileName });
        }
        if (app.competition_evidence) {
          const fileName = app.competition_evidence.split('/').pop() || '竞赛证明';
          proofMaterials.push({ url: app.competition_evidence, name: fileName });
        }
      }
      
      // 5. 去重处理，避免重复的证明材料
      const uniqueMaterials = [];
      const seenUrls = new Set();
      for (const material of proofMaterials) {
        if (material.url && !seenUrls.has(material.url)) {
          seenUrls.add(material.url);
          uniqueMaterials.push(material);
        }
      }
      proofMaterials = uniqueMaterials;
      
      // 获取原始英文项目类型
      const originalProjectType = app.application_type || app.type || app.project_type || app.category || 'unknown';
      
      // 判断当前教师是否已经审批过该申请
      let reviewedByCurrentTeacher = false;
      if (currentUser.value) {
        // 检查是否是当前教师审批的
        const currentUserId = currentUser.value.id;
        const reviewerIds = [
          app.first_reviewer?.id,
          app.second_reviewer?.id,
          app.third_reviewer?.id,
          app.first_reviewer_id,
          app.second_reviewer_id,
          app.third_reviewer_id
        ];
        
        reviewedByCurrentTeacher = reviewerIds.includes(currentUserId);
      }
      
      return {
        id: app.id,
        studentName: app.student_name || '未知',
        studentId: app.student_id || '未知',
        className: app.class_name || app.clazz_name || '未知',
        projectType: projectType,
        originalProjectType: originalProjectType,
        projectName: app.title || '未知',
        applyTime: applyTime,
        status: status,
        score: score,
        description: app.description || '无',
        proofMaterials: proofMaterials,
        reviewedByCurrentTeacher: reviewedByCurrentTeacher
      };
    });
    
    // 默认过滤掉已撤回状态的数据，除非用户明确选择了已撤回分类
    if (filterForm.value.statusCategories && filterForm.value.statusCategories.includes('withdrawn')) {
      applications.value = mappedData
    } else {
      applications.value = mappedData.filter(app => getMainStatusCategory(app.status) !== 'withdrawn')
    }
  } catch (error) {
    console.error('获取申请列表失败：', error)
    message.error('获取申请列表失败：' + (error.message || '未知错误'))
    applications.value = []
  } finally {
    loading.value = false
  }
}

// 折叠面板
const activeCategories = ref([])
const activeSubCategories = ref([])

// 处理搜索
const handleSearch = () => {
  fetchApplications()
}

// 处理重置
const handleReset = () => {
  filterForm.value = {
    status: '',
    searchText: '',
    projectTypes: []
  }
  fetchApplications()
}

// 切换项目类型筛选
const toggleProjectType = (type) => {
  const index = filterForm.value.projectTypes.indexOf(type)
  if (index === -1) {
    filterForm.value.projectTypes.push(type)
  } else {
    filterForm.value.projectTypes.splice(index, 1)
  }
}

// 切换状态分类筛选
const toggleStatusCategory = (category) => {
  // 确保statusCategories存在
  if (!filterForm.value.statusCategories) {
    filterForm.value.statusCategories = []
  }
  
  const index = filterForm.value.statusCategories.indexOf(category)
  if (index === -1) {
    filterForm.value.statusCategories.push(category)
  } else {
    filterForm.value.statusCategories.splice(index, 1)
  }
}

// 项目类型映射：前端项目类型值 -> 后端项目类型
const frontendToBackendProjectType = {
  'english_cet4': 'english_scores',
  'english_cet6': 'english_scores',
  'academic_paper': 'academic_papers',
  'patent_work': 'patent_works',
  'academic_competition': 'academic_competitions',
  'innovation_project': 'innovation_projects',
  'ccf_csp': 'ccf_csp_certifications',
  'international_internship': 'international_internships',
  'military_service': 'military_services',
  'volunteer_service': 'volunteer_services',
  'honorary_title': 'honorary_titles',
  'social_work': 'social_works',
  'sports_competition': 'sports_competitions'
}

// 创建反向映射：后端项目类型 -> 前端项目类型值列表
const backendToFrontendProjectTypes = {};
Object.entries(frontendToBackendProjectType).forEach(([frontendType, backendType]) => {
  if (!backendToFrontendProjectTypes[backendType]) {
    backendToFrontendProjectTypes[backendType] = [];
  }
  backendToFrontendProjectTypes[backendType].push(frontendType);
});

// 创建项目类型中英文映射（用于显示）
const typeMap = {
  // 基础核心类型
  'english_scores': '英语成绩',
  'academic_papers': '学术论文',
  'patent_works': '专利著作',
  'academic_competitions': '学业竞赛',
  'innovation_projects': '大创项目',
  'ccf_csp_certifications': 'CCF CSP认证',
  'international_internships': '国际组织实习',
  'military_services': '参军入伍',
  'volunteer_services': '志愿服务',
  'honorary_titles': '荣誉称号',
  'social_works': '社会工作',
  'sports_competitions': '体育比赛',
  // 旧类型兼容
  'english_score': '英语成绩',
  'academic_paper': '学术论文',
  'patent_work': '发明专利',
  'academic_competition': '学术竞赛',
  'innovation_project': '创新项目',
  'ccf_csp': 'CCF-CSP认证',
  'international_internship': '国际实习',
  'military_service': '服兵役',
  'volunteer_service': '志愿服务',
  'honorary_title': '荣誉称号',
  'social_work': '社会工作',
  'sports_competition': '体育竞赛'
};

// 创建反向映射：中文显示名称 -> 后端项目类型 -> 前端项目类型值
const chineseToFrontendProjectTypes = {};
Object.entries(typeMap).forEach(([backendType, chineseName]) => {
  if (!chineseToFrontendProjectTypes[chineseName]) {
    chineseToFrontendProjectTypes[chineseName] = [];
  }
  // 找到对应的前端项目类型值
  const frontendTypes = backendToFrontendProjectTypes[backendType] || [];
  chineseToFrontendProjectTypes[chineseName] = [...new Set([...chineseToFrontendProjectTypes[chineseName], ...frontendTypes])];
});

// 为了简化处理，创建一个直接映射：项目类型标识（后端或中文） -> 前端项目类型值列表
const getFrontendTypesByProjectType = (projectType) => {
  // 如果是前端项目类型值，直接返回
  if (frontendToBackendProjectType[projectType]) {
    return [projectType];
  }
  // 如果是后端项目类型，返回对应的前端项目类型值列表
  if (backendToFrontendProjectTypes[projectType]) {
    return backendToFrontendProjectTypes[projectType];
  }
  // 如果是中文显示名称，返回对应的前端项目类型值列表
  if (chineseToFrontendProjectTypes[projectType]) {
    return chineseToFrontendProjectTypes[projectType];
  }
  // 其他情况，返回空列表
  return [];
};

// 过滤后的申请列表（基于状态和项目类型）
const filteredApplications = computed(() => {
  let filtered = applications.value
  
  // 按状态分类筛选
  if (filterForm.value.statusCategories && filterForm.value.statusCategories.length > 0) {
    filtered = filtered.filter(app => {
      const mainStatus = getMainStatusCategory(app.status)
      return filterForm.value.statusCategories.includes(mainStatus)
    })
  }
  
  // 按项目类型筛选
  if (filterForm.value.projectTypes && filterForm.value.projectTypes.length > 0) {
    filtered = filtered.filter(app => {
      // 获取后端返回的原始英文项目类型
      const backendType = app.originalProjectType || ''
      
      // 检查是否与任何筛选的项目类型匹配
      return filterForm.value.projectTypes.some(frontendType => {
        const mappedBackendType = frontendToBackendProjectType[frontendType] || frontendType
        return backendType.includes(mappedBackendType)
      })
    })
  }
  
  // 按搜索文本筛选
  if (filterForm.value.searchText) {
    const searchText = filterForm.value.searchText.toLowerCase()
    filtered = filtered.filter(app => {
      return (
        app.studentName?.toLowerCase().includes(searchText) ||
        app.projectName?.toLowerCase().includes(searchText)
      )
    })
  }
  
  return filtered
})

// 获取项目类型文本
const getProjectTypeText = (type) => {
  // 健壮性处理：确保输入是字符串类型
  const typeStr = String(type || '')
  if (!typeStr.trim()) return '未知类型'
  
  // 检查是否已经是中文（包含中文字符）
  if (/[\u4e00-\u9fa5]/.test(typeStr)) {
    return typeStr
  }
  
  // 首先尝试使用projectTypes数组进行匹配
  const projectType = projectTypes.find(t => t.value === typeStr)
  if (projectType) {
    return projectType.label
  }
  
  // 项目类型中英文映射 - 确保覆盖所有可能的后端返回值
  const typeMap = {
    // 基础核心类型
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
    // CCF CSP认证支持
    'ccf': 'CCF CSP认证',
    'ccf_csp': 'CCF CSP认证'
  }
  
  // 尝试直接匹配
  if (typeMap[typeStr]) {
    return typeMap[typeStr]
  }
  
  // 尝试小写匹配
  const lowerType = typeStr.toLowerCase()
  if (typeMap[lowerType]) {
    return typeMap[lowerType]
  }
  
  // 对于未映射的类型，使用硬编码的映射来确保中文显示
  if (lowerType.includes('scientific') || lowerType.includes('research')) {
    return '科研成果'
  } else if (lowerType.includes('competition') || lowerType.includes('contest')) {
    return '学业竞赛'
  } else if (lowerType.includes('innovation')) {
    return '创新创业训练'
  } else if (lowerType.includes('internship') || lowerType.includes('international')) {
    return '国际组织实习'
  } else if (lowerType.includes('military') || lowerType.includes('service')) {
    return '参军入伍服兵役'
  } else if (lowerType.includes('volunteer')) {
    return '志愿服务'
  } else if (lowerType.includes('honor') || lowerType.includes('award')) {
    return '荣誉称号'
  } else if (lowerType.includes('social')) {
    return '社会工作'
  } else if (lowerType.includes('sports') || lowerType.includes('athletic')) {
    return '体育比赛'
  } else if (lowerType.includes('english') || lowerType.includes('score')) {
    return '英语成绩'
  } else if (lowerType.includes('ccf')) {
    return 'CCF CSP认证'
  }
  
  // 作为最后的手段，返回中文默认值
  return '未分类项目'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取状态颜色
const getStatusColor = (status) => {
  // 主要状态类别的颜色映射 - 规范为五种状态
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
  };
  return colorMap[status] || 'default';
};

// 获取主要状态类别（用于筛选）
const getMainStatusCategory = (status) => {
  if (!status) return 'unknown';
  const statusMap = {
    pending: 'pending',
    first_reviewing: 'pending',
    second_reviewing: 'pending',
    third_reviewing: 'pending',
    approved: 'approved',
    first_approved: 'approved',
    second_approved: 'approved',
    third_approved: 'approved',
    rejected: 'rejected',
    first_rejected: 'rejected',
    second_rejected: 'rejected',
    third_rejected: 'rejected',
    withdrawn: 'withdrawn'
  };
  return statusMap[status] || 'unknown';
};

// 获取状态文本
const getStatusText = (status) => {
  if (!status) return '未知状态';
  // 将细分状态归为主要状态类别 - 规范为五种状态
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
  };
  return statusMap[status] || '未知状态';
};

// 处理编辑
const handleEdit = (record) => {
  console.log('编辑申请:', record)
}

// 详情模态框相关
const viewModalVisible = ref(false)
const selectedApplication = ref(null)

// 处理查看详情
const handleView = (record) => {
  selectedApplication.value = record
  viewModalVisible.value = true
}

// 预览模态框相关
const previewModalVisible = ref(false)
const selectedMaterial = ref({})

// 关闭预览模态框
const closePreviewModal = () => {
  previewModalVisible.value = false
  selectedMaterial.value = {}
}

// 处理证明材料下载
const handleDownload = (material) => {
  console.log('下载材料:', material)
  // 从material对象或URL字符串中获取URL
  const url = typeof material === 'string' ? material : material.url
  if (url) {
    // 创建下载链接，确保文件正确下载而非在浏览器中打开
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.download = typeof material === 'string' ? url.split('/').pop() || '附件' : material.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

// 检查是否为图片文件
const isImageFile = (material) => {
  if (!material || !material.name) return false;
  const url = material.url || '';
  const name = material.name || url;
  const lowerName = name.toLowerCase();
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'];
  return imageExtensions.some(ext => lowerName.endsWith(ext));
}



// 处理证明材料预览
const handlePreview = (material) => {
  console.log('预览材料:', material)
  // 确保material是对象格式
  if (typeof material === 'string') {
    const fileName = material.split('/').pop() || '附件';
    selectedMaterial.value = { url: material, name: fileName };
  } else {
    selectedMaterial.value = material;
  }
  previewModalVisible.value = true;
}

// 审批模态框状态
const approveModalVisible = ref(false)
const rejectModalVisible = ref(false)

// 审批表单
const approveForm = ref({
  score: null,
  remark: ''
})

// 拒绝表单
const rejectForm = ref({
  reason: ''
})

// 审批按钮配置
const footerButtons = computed(() => {
  if (!selectedApplication.value) return null
  
  // 检查当前教师是否已经审批过该申请
  const hasReviewed = selectedApplication.value.reviewedByCurrentTeacher
  
  if (hasReviewed) {
    // 已审批的申请只显示关闭按钮
    return [
      h('a-button', {
        type: 'default',
        onClick: () => { viewModalVisible.value = false },
        class: 'approval-button close-button'
      }, '关闭')
    ]
  } else {
    // 未审批的申请显示审批按钮，无论当前状态
    return [
      h('a-button', {
        type: 'default',
        onClick: () => { viewModalVisible.value = false },
        class: 'approval-button cancel-button'
      }, '取消'),
      h('a-button', {
        type: 'default',
        onClick: () => {
          viewModalVisible.value = false
          rejectModalVisible.value = true
        },
        class: 'approval-button reject-button'
      }, '拒绝'),
      h('a-button', {
        type: 'primary',
        onClick: () => {
          viewModalVisible.value = false
          approveModalVisible.value = true
        },
        class: 'approval-button approve-button'
      }, '同意')
    ]
  }
})

// 打开通过申请模态框
const handleApprove = (application) => {
  selectedApplication.value = application
  console.log('完整Application对象:', JSON.stringify(application))
  console.log('Application对象所有键:', Object.keys(application))
  
  // 尝试从所有可能的字段获取分数
  let defaultScore = 0
  
  // 列出所有可能的分数字段名
  const scoreFields = [
    'score', 'estimated_score', 'bonus_points', 'exam_score',
    'estimatedScore', 'bonusPoints', 'examScore', 'apply_score', 'applyScore',
    'total_score', 'totalScore', 'final_score', 'finalScore'
  ]
  
  for (const field of scoreFields) {
    if (application[field] !== undefined && application[field] !== null) {
      defaultScore = application[field]
      console.log(`Found score from field '${field}': ${defaultScore}`)
      break
    }
  }
  
  // 如果还是没找到，尝试从嵌套对象中获取
  if (defaultScore === 0 && application.data) {
    console.log('Checking application.data for score...')
    for (const field of scoreFields) {
      if (application.data[field] !== undefined && application.data[field] !== null) {
        defaultScore = application.data[field]
        console.log(`Found score from field 'data.${field}': ${defaultScore}`)
        break
      }
    }
  }
  
  console.log('最终Default score:', defaultScore)
  
  approveForm.value = {
    score: defaultScore, // 默认填写申请的分数
    remark: ''
  }
  
  console.log('approveForm after setting:', approveForm.value)
  
  approveModalVisible.value = true
}

// 确认通过申请
const handleConfirmApprove = async () => {
  try {
    if (!selectedApplication.value) return
    
    // 验证表单数据
    if (!approveForm.value.score) {
      message.error('请输入审批分数')
      return
    }
    
    // 调用API通过申请
    await api.teacher.approveApplication(selectedApplication.value.id, {
      score: approveForm.value.score
    })
    
    message.success('申请已通过')
    approveModalVisible.value = false
    fetchApplications() // 刷新申请列表
  } catch (error) {
    console.error('通过申请失败:', error)
    message.error('通过申请失败: ' + (error.message || '未知错误'))
  }
}

// 打开拒绝申请模态框
const handleReject = (application) => {
  selectedApplication.value = application
  rejectForm.value = {
    reason: ''
  }
  rejectModalVisible.value = true
}

// 确认拒绝申请
const handleConfirmReject = async () => {
  try {
    if (!selectedApplication.value) return
    
    // 验证表单数据
    if (!rejectForm.value.reason) {
      message.error('请输入拒绝理由')
      return
    }
    
    // 调用API拒绝申请
    await api.teacher.rejectApplication(selectedApplication.value.id, {
      reason: rejectForm.value.reason
    })
    
    message.success('申请已拒绝')
    rejectModalVisible.value = false
    fetchApplications() // 刷新申请列表
  } catch (error) {
    console.error('拒绝申请失败:', error)
    message.error('拒绝申请失败: ' + (error.message || '未知错误'))
  }
}

// 获取当前教师信息
const fetchCurrentUser = async () => {
  try {
    const user = await api.teacher.getCurrentUser()
    currentUser.value = user
    console.log('Current user info:', user)
  } catch (error) {
    console.error('Failed to fetch current user:', error)
  }
}

// 页面加载时获取数据
onMounted(async () => {
  await fetchCurrentUser()
  fetchApplications()
})
</script>

<style scoped>
.teacher-applications {
  padding: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.project-type-filter {
  margin-bottom: 20px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
}

.no-data {
  text-align: center;
  padding: 20px;
}

.approval-form {
  max-height: 400px;
  overflow-y: auto;
}

/* 审批按钮样式优化 */
.approval-button {
  padding: 8px 20px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
  margin-left: 8px;
  min-width: 80px;
}

.approval-button:first-child {
  margin-left: 0;
}

/* 取消按钮样式 */
.cancel-button {
  background-color: #f0f0f0;
  border-color: #d9d9d9;
  color: #666;
}

.cancel-button:hover {
  background-color: #e6e6e6;
  border-color: #bfbfbf;
  color: #333;
}

/* 拒绝按钮样式 */
.reject-button {
  background-color: #ff4d4f;
  border-color: #ff4d4f;
  color: white;
}

.reject-button:hover {
  background-color: #ff7875;
  border-color: #ff7875;
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.25);
}

.reject-button:active {
  background-color: #cf1322;
  border-color: #cf1322;
}

/* 通过按钮样式 */
.approve-button {
  background-color: #52c41a;
  border-color: #52c41a;
  color: white;
}

.approve-button:hover {
  background-color: #73d13d;
  border-color: #73d13d;
  box-shadow: 0 2px 8px rgba(82, 196, 26, 0.25);
}

.approve-button:active {
  background-color: #389e0d;
  border-color: #389e0d;
}

/* 关闭按钮样式 */
.close-button {
  background-color: #f0f0f0;
  border-color: #d9d9d9;
  color: #666;
}

.close-button:hover {
  background-color: #e6e6e6;
  border-color: #bfbfbf;
  color: #333;
}

/* 确保按钮文字居中 */
.approval-button span {
  display: inline-block;
  text-align: center;
  width: 100%;
}
</style>