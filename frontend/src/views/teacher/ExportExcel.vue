<template>
  <div class="export-excel">
    <h2>数据导出</h2>
    
    <a-card style="margin-top: 20px;">
      <div class="export-options">
        <h3>导出选项</h3>
        <a-radio-group v-model:value="exportType" style="margin-bottom: 20px;">
          <a-radio value="students">学生信息</a-radio>
          <a-radio value="applications">申请数据</a-radio>
        </a-radio-group>
        
        <!-- 学生信息导出选项 -->
        <div v-if="exportType === 'students'" class="export-content">
          <a-form :model="studentExportForm" layout="vertical">
            <a-form-item label="班级">
              <a-select v-model:value="studentExportForm.class" placeholder="选择班级">
                <a-select-option value="">全部班级</a-select-option>
                <a-select-option value="计算机科学与技术1班">计算机科学与技术1班</a-select-option>
                <a-select-option value="软件工程2班">软件工程2班</a-select-option>
                <a-select-option value="网络工程3班">网络工程3班</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="导出字段">
              <a-checkbox-group v-model:value="studentExportForm.fields">
                <a-checkbox value="studentId">学号</a-checkbox>
                <a-checkbox value="name">姓名</a-checkbox>
                <a-checkbox value="class">班级</a-checkbox>
                <a-checkbox value="department">院系</a-checkbox>
                <a-checkbox value="phone">联系方式</a-checkbox>
                <a-checkbox value="email">邮箱</a-checkbox>
                <a-checkbox value="totalScore">总加分</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
          </a-form>
        </div>
        
        <!-- 申请数据导出选项 -->
        <div v-else-if="exportType === 'applications'" class="export-content">
          <a-form :model="applicationExportForm" layout="vertical">
            <a-form-item label="申请状态">
              <a-select v-model:value="applicationExportForm.status" placeholder="选择状态">
                <a-select-option value="">全部状态</a-select-option>
                <a-select-option value="pending">等待审核</a-select-option>
                <a-select-option value="approved">审核通过</a-select-option>
                <a-select-option value="rejected">未通过</a-select-option>
                <a-select-option value="withdrawn">已撤回</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="项目类型">
              <a-select v-model:value="applicationExportForm.projectType" placeholder="选择项目类型">
                <a-select-option value="">全部类型</a-select-option>
                <!-- 英语成绩类 -->
                <a-select-option value="english_cet4">大学英语四级</a-select-option>
                <a-select-option value="english_cet6">大学英语六级</a-select-option>
                <!-- 学术专长类 -->
                <a-select-option value="academic_paper">学术论文</a-select-option>
                <a-select-option value="patent_work">专利著作</a-select-option>
                <a-select-option value="academic_competition">学业竞赛</a-select-option>
                <a-select-option value="innovation_project">大创项目</a-select-option>
                <a-select-option value="ccf_csp">CCF CSP认证</a-select-option>
                <!-- 综合表现类 -->
                <a-select-option value="international_internship">国际组织实习</a-select-option>
                <a-select-option value="military_service">参军入伍</a-select-option>
                <a-select-option value="volunteer_service">志愿服务</a-select-option>
                <a-select-option value="honorary_title">荣誉称号</a-select-option>
                <a-select-option value="social_work">社会工作</a-select-option>
                <a-select-option value="sports_competition">体育比赛</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="时间范围">
              <a-range-picker v-model:value="applicationExportForm.dateRange" style="width: 100%;" />
            </a-form-item>
          </a-form>
        </div>
        
        <div class="export-actions">
          <a-button type="primary" @click="handleExport">导出Excel</a-button>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import * as ExcelJS from 'exceljs'
import { saveAs } from 'file-saver'
import dayjs from 'dayjs'

// 导出类型
const exportType = ref('students')

// 学生信息导出表单
const studentExportForm = ref({
  class: '',
  fields: ['studentId', 'name', 'class', 'department', 'totalScore']
})

// 申请数据导出表单
const applicationExportForm = ref({
  status: '',
  projectType: '',
  dateRange: null
})

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '等待审核',
    approved: '审核通过',
    rejected: '未通过',
    withdrawn: '已撤回'
  }
  return statusMap[status] || status
}

// 获取项目类型文本
const getProjectTypeText = (type) => {
  // 健壮性处理：确保输入是字符串类型
  const typeStr = String(type || '')
  if (!typeStr.trim()) return '未知类型'
  
  // 检查是否已经是中文（包含中文字符）
  if (/[\u4e00-\u9fa5]/.test(typeStr)) {
    return typeStr
  }
  
  // 基础项目类型映射
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
    'ccf': 'CCF CSP认证',
    'ccf_csp': 'CCF CSP认证',
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
    'english_proficiency': '英语成绩'
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

// 导出学生信息
const exportStudents = async () => {
  try {
    // 创建工作簿
    const workbook = new ExcelJS.Workbook()
    workbook.creator = '教师端导出'
    workbook.created = new Date()
    workbook.modified = new Date()
    
    // 创建工作表
    const worksheet = workbook.addWorksheet('学生信息')
    
    // 设置列标题
    const columns = [
      { header: '学号', key: 'studentId', width: 15 },
      { header: '姓名', key: 'name', width: 10 },
      { header: '班级', key: 'class', width: 20 },
      { header: '院系', key: 'department', width: 20 },
      { header: '联系方式', key: 'phone', width: 15 },
      { header: '邮箱', key: 'email', width: 30 },
      { header: '总加分', key: 'totalScore', width: 10 }
    ]
    
    // 根据选择的字段过滤列
    const filteredColumns = columns.filter(col => studentExportForm.value.fields.includes(col.key))
    worksheet.columns = filteredColumns
    
    // 模拟学生数据
    const students = [
      {
        studentId: '202001001',
        name: '张三',
        class: '计算机科学与技术1班',
        department: '计算机科学与技术学院',
        phone: '13800138001',
        email: 'zhangsan@example.com',
        totalScore: 21
      },
      {
        studentId: '202001002',
        name: '李四',
        class: '软件工程2班',
        department: '计算机科学与技术学院',
        phone: '13800138002',
        email: 'lisi@example.com',
        totalScore: 15
      },
      {
        studentId: '202001003',
        name: '王五',
        class: '计算机科学与技术1班',
        department: '计算机科学与技术学院',
        phone: '13800138003',
        email: 'wangwu@example.com',
        totalScore: 0
      }
    ]
    
    // 过滤数据
    let filteredStudents = students
    if (studentExportForm.value.class) {
      filteredStudents = students.filter(s => s.class === studentExportForm.value.class)
    }
    
    // 添加数据行
    filteredStudents.forEach(student => {
      const rowData = {}
      filteredColumns.forEach(col => {
        rowData[col.key] = student[col.key]
      })
      worksheet.addRow(rowData)
    })
    
    // 设置表头样式
    worksheet.getRow(1).font = { bold: true }
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFCCCCCC' }
    }
    
    // 生成Excel文件
    const buffer = await workbook.xlsx.writeBuffer()
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    
    // 保存文件
    const fileName = `学生信息_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`
    saveAs(blob, fileName)
    
    message.success('学生信息导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    message.error('导出失败，请稍后重试')
  }
}

// 导出申请数据
const exportApplications = async () => {
  try {
    // 创建工作簿
    const workbook = new ExcelJS.Workbook()
    workbook.creator = '教师端导出'
    workbook.created = new Date()
    workbook.modified = new Date()
    
    // 创建工作表
    const worksheet = workbook.addWorksheet('申请数据')
    
    // 设置列
    worksheet.columns = [
      { header: '学生姓名', key: 'studentName', width: 15 },
      { header: '学号', key: 'studentId', width: 15 },
      { header: '班级', key: 'class', width: 20 },
      { header: '项目类型', key: 'projectType', width: 15 },
      { header: '项目名称', key: 'projectName', width: 30 },
      { header: '申请时间', key: 'applyTime', width: 20 },
      { header: '状态', key: 'status', width: 10 },
      { header: '加分', key: 'expectedScore', width: 10 },
      { header: '审核意见', key: 'comment', width: 30 }
    ]
    
    // 模拟申请数据
    const applications = [
      {
        studentName: '张三',
        studentId: '202001001',
        class: '计算机科学与技术1班',
        projectType: '科研成果',
        projectName: '基于深度学习的图像识别研究',
        applyTime: '2023-10-15 14:30:00',
        status: '审核通过',
        expectedScore: 6,
        comment: '表现优秀，同意加分'
      },
      {
        studentName: '李四',
        studentId: '202001002',
        class: '软件工程2班',
        projectType: '学业竞赛',
        projectName: '全国大学生数学建模竞赛',
        applyTime: '2023-10-10 09:15:00',
        status: '审核通过',
        expectedScore: 15,
        comment: '表现优秀，同意加分'
      },
      {
        studentName: '王五',
        studentId: '202001003',
        class: '计算机科学与技术1班',
        projectType: '创新创业训练',
        projectName: '智能校园导航系统',
        applyTime: '2023-10-05 16:45:00',
        status: '未通过',
        expectedScore: 1,
        comment: '项目创新性不足，不符合加分条件'
      }
    ]
    
    // 过滤数据
    let filteredApplications = applications
    if (applicationExportForm.value.status) {
      filteredApplications = filteredApplications.filter(app => app.status === applicationExportForm.value.status)
    }
    if (applicationExportForm.value.projectType) {
      filteredApplications = filteredApplications.filter(app => app.projectType === applicationExportForm.value.projectType)
    }
    
    // 添加数据行
    filteredApplications.forEach(app => {
      worksheet.addRow({
        studentName: app.studentName,
        studentId: app.studentId,
        class: app.class,
        projectType: getProjectTypeText(app.projectType),
        projectName: app.projectName,
        applyTime: app.applyTime,
        status: app.status,
        expectedScore: `${app.expectedScore}分`,
        comment: app.comment || ''
      })
    })
    
    // 设置表头样式
    worksheet.getRow(1).font = { bold: true }
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFCCCCCC' }
    }
    
    // 生成Excel文件
    const buffer = await workbook.xlsx.writeBuffer()
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    
    // 保存文件
    const fileName = `申请数据_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`
    saveAs(blob, fileName)
    
    message.success('申请数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    message.error('导出失败，请稍后重试')
  }
}

// 处理导出
const handleExport = () => {
  if (exportType.value === 'students') {
    exportStudents()
  } else if (exportType.value === 'applications') {
    exportApplications()
  }
}
</script>

<style scoped>
.export-excel {
  padding: 20px;
}

.export-options {
  padding: 20px 0;
}

.export-content {
  margin-bottom: 20px;
}

.export-actions {
  text-align: right;
}
</style>