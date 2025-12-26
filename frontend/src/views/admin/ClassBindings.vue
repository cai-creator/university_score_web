<template>
  <div class="admin-class-bindings">
    <h2>班级绑定管理</h2>
    
    <!-- 绑定操作区 -->
    <a-card style="margin-bottom: 20px;">
      <h3>添加班级绑定</h3>
      <a-form :model="bindingForm" layout="vertical" style="margin-top: 20px;">
        <a-row :gutter="[16, 16]">
          <a-col :span="8">
            <a-form-item label="教师">
              <a-select v-model:value="bindingForm.teacherId" placeholder="选择教师">
                <a-select-option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                  {{ teacher.name }} - {{ teacher.department }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="班级">
              <a-select v-model:value="bindingForm.classId" placeholder="选择班级">
                <a-select-option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                  {{ classItem.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8" style="display: flex; align-items: flex-end;">
            <a-button type="primary" @click="handleAddBinding">添加绑定</a-button>
          </a-col>
        </a-row>
      </a-form>
    </a-card>

    <!-- 绑定关系列表 -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="bindings"
        :pagination="{ pageSize: 10 }"
        :row-key="record => record.id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <a-button type="link" danger @click="handleDeleteBinding(record)">解除绑定</a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import api from '../../utils/api'

// 绑定表单
const bindingForm = ref({
  teacherId: null,
  classId: null
})

// 教师列表
const teachers = ref([])

// 班级列表
const classes = ref([])

// 绑定关系列表
const bindings = ref([])

// 表格列配置
const columns = [
  { title: '教师姓名', dataIndex: 'teacherName', key: 'teacherName' },
  { title: '教师院系', dataIndex: 'teacherDepartment', key: 'teacherDepartment' },
  { title: '班级名称', dataIndex: 'className', key: 'className' },
  { title: '操作', key: 'actions', fixed: 'right', width: 100 }
]

// 添加绑定
const handleAddBinding = async () => {
  if (!bindingForm.value.teacherId || !bindingForm.value.classId) {
    message.error('请选择教师和班级')
    return
  }
  
  // 检查是否已存在绑定
  const existing = bindings.value.find(b => 
    b.teacherId === bindingForm.value.teacherId && 
    b.classId === bindingForm.value.classId
  )
  
  if (existing) {
    message.warning('该教师和班级已存在绑定关系')
    return
  }
  
  try {
    // 调用API添加绑定
    await api.admin.classBindings.createClassBinding({ 
      teacher_id: bindingForm.value.teacherId, 
      class_id: bindingForm.value.classId 
    })
    
    // 添加成功后刷新绑定列表
    await fetchBindings()
    
    // 重置表单
    bindingForm.value = {
      teacherId: null,
      classId: null
    }
    
    message.success('班级绑定添加成功')
  } catch (error) {
    console.error('添加班级绑定失败:', error)
    message.error('添加班级绑定失败，请稍后重试')
  }
}

// 删除绑定
const handleDeleteBinding = async (record) => {
  Modal.confirm({
    title: '确认解除绑定',
    content: `确定要解除教师 ${record.teacherName} 和班级 ${record.className} 的绑定关系吗？`,
    onOk: async () => {
      try {
        // 调用API删除绑定
        await api.admin.classBindings.deleteClassBinding(record.id)
        
        // 删除成功后刷新绑定列表
        await fetchBindings()
        
        message.success('绑定关系已解除')
      } catch (error) {
        console.error('解除班级绑定失败:', error)
        message.error('解除班级绑定失败，请稍后重试')
      }
    }
  })
}

// 获取教师列表
const fetchTeachers = async () => {
  try {
    const data = await api.admin.getTeachers()
    teachers.value = data || []
  } catch (error) {
    console.error('获取教师列表失败:', error)
    message.error('获取教师列表失败，请稍后重试')
    teachers.value = []
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await api.admin.classes.getClasses()
    classes.value = response?.classes || []
  } catch (error) {
    console.error('获取班级列表失败:', error)
    message.error('获取班级列表失败，请稍后重试')
    classes.value = []
  }
}

// 获取绑定关系列表
const fetchBindings = async () => {
  try {
    const response = await api.admin.classBindings.getClassBindings()
    // 适配不同的响应结构
    // 注意：后端返回的是 {code, message, data} 格式
    const bindingsData = response.data || response.bindings || response.results || response || []
    // 确保每个绑定都有必要的字段
    bindings.value = bindingsData.map(binding => ({
      id: binding.id,
      // 从teacher对象中提取信息
      teacherId: binding.teacher?.id || binding.teacher_id || binding.teacherId,
      teacherName: binding.teacher?.name || binding.teacher_name || binding.teacherName,
      teacherDepartment: binding.teacher?.college || binding.teacher_department || binding.teacherDepartment,
      // 从class对象中提取信息
      classId: binding.class?.id || binding.class_id || binding.classId,
      className: binding.class?.name || binding.class_name || binding.className
    }))
  } catch (error) {
    console.error('获取绑定关系列表失败:', error)
    message.error('获取绑定关系列表失败，请稍后重试')
    bindings.value = []
  }
}

onMounted(async () => {
  try {
    // 并行获取数据，提高性能
    await Promise.all([
      fetchTeachers(),
      fetchClasses(),
      fetchBindings()
    ])
  } catch (error) {
    console.error('页面初始化数据加载失败:', error)
  }
})
</script>

<style scoped>
.admin-class-bindings {
  padding: 20px;
}
</style>