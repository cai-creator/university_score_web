<template>
  <div class="colleges-container">
    <h1 class="page-title">学院管理</h1>
    
    <!-- 操作栏 -->
    <div class="operation-bar">
      <a-button type="primary" @click="showAddModal">
        <plus-outlined /> 添加学院
      </a-button>
    </div>
    
    <!-- 表格 -->
    <a-table
      :columns="columns"
      :data-source="colleges"
      :pagination="false"
      row-key="id"
      :row-selection="rowSelection"
    >
      <!-- 操作列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-button size="small" @click="showEditModal(record)">编辑</a-button>
          <a-button size="small" @click="showTeacherManagement(record)">老师管理</a-button>
          <a-button size="small" @click="showClassManagement(record)">班级管理</a-button>
          <a-popconfirm
            title="确定要删除这个学院吗？"
            description="删除后将无法恢复"
            ok-text="确定"
            cancel-text="取消"
            @confirm="deleteCollege(record.id)"
          >
            <a-button size="small" danger>删除</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>
    
    <!-- 添加学院模态框 -->
    <a-modal
      v-model:open="addModalVisible"
      title="添加学院"
      ok-text="确定"
      cancel-text="取消"
      :loading="addFormLoading"
      @ok="handleAddCollege"
      @cancel="handleAddCancel"
    >
      <a-form
        ref="addFormRef"
        :model="addForm"
        layout="vertical"
      >
        <a-form-item name="name" label="学院名称" :rules="[{ required: true, message: '请输入学院名称', trigger: 'blur' }, { min: 2, message: '学院名称至少需要2个字符', trigger: 'blur' }]">
          <a-input v-model:value="addForm.name" placeholder="请输入学院名称" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 编辑学院模态框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑学院"
      ok-text="确定"
      cancel-text="取消"
      @ok="handleEditCollege"
      @cancel="handleEditCancel"
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        layout="vertical"
      >
        <a-form-item name="name" label="学院名称" :rules="[{ required: true, message: '请输入学院名称', trigger: 'blur' }, { min: 2, message: '学院名称至少需要2个字符', trigger: 'blur' }]">
          <a-input v-model:value="editForm.name" placeholder="请输入学院名称" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 批量操作模态框 -->
    <a-modal
      v-model:open="batchModalVisible"
      title="批量操作"
      ok-text="确定"
      cancel-text="取消"
      @ok="handleBatchDelete"
    >
      <p>确定要删除选中的 {{ selectedColleges.length }} 个学院吗？</p>
    </a-modal>

    <!-- 班级管理模态框 -->
    <a-modal
      v-model:open="classManagementModalVisible"
      title="学院班级管理"
      width="800px"
      :footer="null"
    >
      <div class="class-management">
        <div class="class-header">
          <h3>{{ currentCollege?.name }} - 班级列表</h3>
          <a-button type="primary" @click="showClassSelectionModal">添加班级</a-button>
        </div>
        
        <a-table
          :columns="classColumns"
          :data-source="selectedClasses || []"
          :pagination="false"
          row-key="id"
          :loading="loadingClasses"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-button size="small" @click="showEditClassModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除这个班级吗？"
                :description="`删除后将无法恢复，班级ID: ${record.id}`"
                ok-text="确定"
                cancel-text="取消"
                @confirm="deleteClass(record.id)"
              >
                <a-button size="small" danger>删除</a-button>
              </a-popconfirm>
            </template>
          </template>
          <template #empty>
            <div style="padding: 40px 0; text-align: center;">
              <a-empty description="当前学院下没有班级">
                <a-button type="primary" @click="showClassSelectionModal">
                  添加班级
                </a-button>
              </a-empty>
            </div>
          </template>
        </a-table>
      </div>
    </a-modal>

    <!-- 班级选择模态框 -->
    <a-modal
      v-model:open="classModalVisible"
      title="选择班级"
      ok-text="确定"
      cancel-text="取消"
      @ok="handleSaveClass"
    >
      <div class="class-selection">
        <p class="selection-hint">请从以下班级列表中选择要添加到 {{ currentCollege?.name }} 的班级：</p>
        
        <!-- 班级多选列表 -->
        <a-select
          v-model:value="classSelection.selectedClassIds"
          mode="multiple"
          placeholder="选择班级"
          class="class-select"
          option-filter-prop="children"
        >
          <a-select-option
            v-for="cls in availableClasses"
            :key="cls.id"
            :value="cls.id"
          >
            {{ cls.name }} ({{ cls.grade }})
          </a-select-option>
        </a-select>
        
        <p v-if="availableClasses.length === 0" class="no-classes">
          当前没有可添加的班级
        </p>
      </div>
    </a-modal>
    
    <!-- 老师管理模态框 -->
    <a-modal
      v-model:open="teacherManagementModalVisible"
      title="学院老师管理"
      width="800px"
      :footer="null"
    >
      <div class="teacher-management">
        <div class="teacher-header">
          <h3>{{ currentCollege?.name }} - 老师列表</h3>
        </div>
        
        <a-table
          :columns="teacherColumns"
          :data-source="currentCollegeTeachers"
          :pagination="false"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-button size="small" @click="showEditTeacherModal(record)">编辑</a-button>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import api from '@/utils/api'

// 学院数据
const colleges = ref([])
const selectedColleges = ref([])
const currentCollege = ref(null)

// 老师数据
const teachers = ref([])
const currentCollegeTeachers = ref([])

// 班级数据
const classes = ref([]) // 所有班级列表
const availableClasses = ref([]) // 可选择的班级列表（未绑定到当前学院的）
const selectedClasses = ref([]) // 已选择的班级
const searchKeyword = ref('')
const currentClass = ref(null)
const loadingClasses = ref(false) // 班级数据加载状态

// 模态框状态
const addModalVisible = ref(false)
const editModalVisible = ref(false)
const batchModalVisible = ref(false)
const classManagementModalVisible = ref(false)
const classModalVisible = ref(false)
const classModalTitle = ref('')
const teacherManagementModalVisible = ref(false)

// 表单引用
const addFormRef = ref(null)
const editFormRef = ref()
const classFormRef = ref()

// 添加表单数据
const addForm = reactive({
  name: ''
})

// 加载状态
const addFormLoading = ref(false)

// 编辑表单数据
const editForm = reactive({
  id: '',
  name: ''
})

// 班级选择数据
const classSelection = reactive({
  selectedClassIds: [] // 存储选中的班级ID数组
})

// 表单验证已在方法中通过手动方式实现

// 表格列配置
const columns = [
  {
    title: '学院名称',
    dataIndex: 'name',
    key: 'name'
  },

  {
    title: '操作',
    key: 'action',
    width: 250
  }
]

// 老师表格列配置
const teacherColumns = [
  {
    title: '老师姓名',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '工号',
    dataIndex: 'teacher_id',
    key: 'teacher_id'
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email'
  },
  {
    title: '操作',
    key: 'action',
    width: 80
  }
]

// 班级表格列配置
const classColumns = [
  {
    title: '班级ID',
    dataIndex: 'id',
    key: 'id',
    width: 80
  },
  {
    title: '班级名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '年级',
    dataIndex: 'grade',
    key: 'grade'
  },
  {
    title: '操作',
    key: 'action',
    width: 150
  }
]

// 行选择配置
const rowSelection = {
  selectedRowKeys: selectedColleges,
  onChange: (selectedRowKeys) => {
    selectedColleges.value = selectedRowKeys
  }
}

// 获取年级选项（当前年份及前后5年）
const getGradeOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 5; i <= currentYear + 5; i++) {
    years.push(i)
  }
  return years
})

// 筛选后的班级列表
const filteredClasses = computed(() => {
  if (!classes.value || !currentCollege.value) return []
  
  let result = classes.value.filter(cls => {
    // 处理college字段可能是对象或id的情况
    const collegeId = cls.college?.id || cls.college
    return collegeId === currentCollege.value.id
  })
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(cls => cls.name.toLowerCase().includes(keyword))
  }
  
  return result
})

// 获取学院列表
const fetchColleges = async () => {
  try {
    const response = await api.admin.getColleges()
    console.log('获取学院列表响应:', response);
    
    // 更健壮的响应处理逻辑，支持多种可能的响应格式
    // 根据axios拦截器的实现，成功时response可能直接是data部分
    if (Array.isArray(response)) {
      // 直接是数组的情况
      colleges.value = response;
    } else if (response && Array.isArray(response.data)) {
      // 包含data字段且为数组的情况
      colleges.value = response.data;
    } else if (response && Array.isArray(response.list)) {
      // 包含list字段且为数组的情况（某些后端API常用格式）
      colleges.value = response.list;
    } else {
      console.warn('获取的学院列表格式异常:', response);
      // 尝试提取可能的数据
      if (typeof response === 'object' && response !== null) {
        // 检查是否有其他可能包含学院数据的字段
        const dataKeys = ['items', 'colleges', 'results'];
        for (const key of dataKeys) {
          if (Array.isArray(response[key])) {
            console.log(`从${key}字段获取学院数据`);
            colleges.value = response[key];
            return;
          }
        }
      }
      
      // 如果都不符合期望格式，设置为空数组
      colleges.value = [];
    }
    
    // 确保数据规范化，添加缺失的id或其他必要字段
    colleges.value = colleges.value.map((item, index) => ({
      ...item,
      id: item.id || item._id || `temp_${Date.now()}_${index}` // 确保每项都有id
    }));
    
    console.log('最终处理后的学院列表:', colleges.value);
  } catch (error) {
    console.error('获取学院列表失败:', error);
    console.error('错误详情:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    
    // 更全面的错误类型处理
    let errorMsg = '获取学院列表失败，请重试';
    
    // 检查响应格式异常
    if (error.response?.data && typeof error.response.data === 'object') {
      console.warn('响应数据格式异常:', error.response.data);
    }
    
    // 根据错误类型和状态码提供更具体的提示
    if (error.response?.status === 403) {
      errorMsg = '权限不足，无法获取学院列表';
    } else if (error.response?.status === 500) {
      errorMsg = '服务器错误，请稍后再试';
    } else if (error.response?.status === 429) {
      // 处理请求频率限制
      errorMsg = '请求过于频繁，请稍后再试';
    } else if (error.response?.status === 404) {
      // 处理资源不存在
      errorMsg = '无法获取学院列表数据';
    } else if (!error.response) {
      // 网络错误
      if (error.message && error.message.includes('timeout')) {
        errorMsg = '请求超时，请检查网络后重试';
      } else {
        errorMsg = '网络连接失败，请检查网络后重试';
      }
    }
    
    // 使用更长的显示时间，让用户有足够时间阅读错误信息
    message.error(errorMsg, 3);
    
    // 出错时的容错处理，优先保留现有数据以保证用户体验
    // 这可以确保即使API调用失败，用户仍然可以查看之前加载的数据
    if (!colleges.value || colleges.value.length === 0) {
      console.log('首次加载失败，设置空数组避免渲染错误');
      colleges.value = []; // 避免首次加载失败时渲染错误
    } else {
      // 保留上次成功获取的数据，提供更好的用户体验
      console.log('保留上次成功获取的学院数据，提升用户体验');
    }
  }
}

// 获取老师列表
const fetchTeachers = async () => {
  try {
    const response = await api.admin.getTeachers()
    // 正确处理API响应格式
    let teacherData = response
    // 支持 { results: [] } 格式
    if (teacherData && Array.isArray(teacherData.results)) {
      teacherData = teacherData.results
    }
    // 确保teachers始终是数组
    teachers.value = Array.isArray(teacherData) ? teacherData : []
    
    // 过滤出当前学院的老师
    if (currentCollege.value) {
      currentCollegeTeachers.value = teachers.value.filter(teacher => {
        // 处理college字段可能是对象或id的情况
        const collegeId = teacher.college?.id || teacher.college
        return collegeId === currentCollege.value.id
      })
    }
  } catch (error) {
    console.error('获取老师列表失败:', error)
    message.error('获取老师列表失败')
    // 出错时设置为空数组，避免渲染错误
    teachers.value = []
    currentCollegeTeachers.value = []
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await api.admin.classes.getClasses()
    // 正确处理API响应格式
    let classData = response
    // 支持 { classes: [] } 格式
    if (classData && Array.isArray(classData.classes)) {
      classData = classData.classes
    }
    // 支持 { results: [] } 格式
    else if (classData && Array.isArray(classData.results)) {
      classData = classData.results
    }
    // 确保classes始终是数组
    classes.value = Array.isArray(classData) ? classData : []
  } catch (error) {
    console.error('获取班级列表失败:', error)
    message.error('获取班级列表失败')
    // 出错时设置为空数组，避免渲染错误
    classes.value = []
  }
}

// 重置表单
const resetForm = () => {
  // 重置表单数据
  addForm.name = '';
  // 注意：addForm中没有code字段，移除不必要的重置
  
  // 清除表单验证状态
  if (addFormRef.value) {
    addFormRef.value.resetFields();
  }
};

// 显示添加模态框
const showAddModal = () => {
  // 重置表单
  resetForm();
  addModalVisible.value = true;
};

// 处理添加模态框取消
const handleAddCancel = () => {
  // 先隐藏模态框
  addModalVisible.value = false;
  
  // 使用setTimeout确保模态框完全关闭后再重置，避免渲染冲突
  setTimeout(() => {
    // 重置表单并清除验证状态
    resetForm();
  }, 300);
};

// 处理编辑模态框取消
const handleEditCancel = () => {
  // 先隐藏模态框
  editModalVisible.value = false;
  
  // 使用setTimeout确保模态框完全关闭后再重置
  setTimeout(() => {
    // 重置编辑表单并清除验证状态
    if (editFormRef.value) {
      editFormRef.value.resetFields();
    }
    // 重置表单数据
    editForm.id = '';
    editForm.name = '';
  }, 300);
};

// 显示编辑模态框
const showEditModal = (record) => {
  // 先重置表单验证状态
  if (editFormRef.value) {
    editFormRef.value.resetFields();
  }
  // 填充表单数据
  editForm.id = record.id
  editForm.name = record.name
  editModalVisible.value = true
}

// 显示老师管理
const showTeacherManagement = async (record) => {
  currentCollege.value = record
  await fetchTeachers()
  teacherManagementModalVisible.value = true
}

// 显示班级管理
const showClassManagement = async (record) => {
  console.log('=== 打开班级管理模态框 ===');
  console.log('选择的学院:', record);
  
  // 初始化selectedClasses为空数组
  selectedClasses.value = [];
  
  currentCollege.value = record
  console.log('设置当前学院后，调用loadClassData()...');
  
  await loadClassData()
  
  console.log('loadClassData()执行完成，selectedClasses状态:', selectedClasses.value);
  console.log('selectedClasses数量:', selectedClasses.value.length);
  
  // 确保selectedClasses始终是数组
  if (!Array.isArray(selectedClasses.value)) {
    console.error('selectedClasses不是数组，重新初始化为空数组');
    selectedClasses.value = [];
  }
  
  console.log('打开班级管理模态框');
  classManagementModalVisible.value = true
}

// 显示添加班级模态框函数已在文件后面重构实现

// 显示编辑班级模态框
const showEditClassModal = (record) => {
  classModalTitle.value = '编辑班级'
  currentClass.value = record
  classForm.name = record.name
  classForm.grade = record.grade || new Date().getFullYear()
  classModalVisible.value = true
}

// 显示编辑老师模态框
const showEditTeacherModal = (record) => {
  // 这里可以根据需要实现老师编辑功能
  message.info('老师编辑功能待实现')
}

// 添加学院
const handleAddCollege = async () => {
  // 设置加载状态
  addFormLoading.value = true
  try {
    // 使用表单验证API进行验证
    try {
      await addFormRef.value.validate();
    } catch (errorInfo) {
      console.error('表单验证失败:', errorInfo);
      // 表单组件会自动显示验证错误，不需要抛出异常
      // 直接返回，避免继续执行
      return;
    }

    const nameTrimmed = addForm.name.trim();
    
    if (nameTrimmed.length > 50) {
      // 使用表单验证API显示错误
      if (addFormRef.value && typeof addFormRef.value.setFields === 'function') {
        addFormRef.value.setFields([{
          name: 'name',
          errors: ['学院名称不能超过50个字符']
        }]);
      } else {
        message.error('学院名称不能超过50个字符');
      }
      return
    }
    
    // 验证名称不重复
    const isDuplicateName = colleges.value.some(college => 
      college.name.toLowerCase() === nameTrimmed.toLowerCase()
    );
    
    if (isDuplicateName) {
      console.log('名称重复:', nameTrimmed);
      // 使用表单验证API显示错误
      if (addFormRef.value && typeof addFormRef.value.setFields === 'function') {
        addFormRef.value.setFields([{
          name: 'name',
          errors: ['该学院名称已存在，请使用其他名称']
        }]);
      } else {
        message.error('该学院名称已存在，请使用其他名称');
      }
      return
    }
    
    // 验证名称中不包含特殊字符（只允许中文、英文、数字、空格、括号和连字符）
    const validNamePattern = /^[\u4e00-\u9fa5a-zA-Z0-9\s\(\)\-]+$/;
    if (!validNamePattern.test(nameTrimmed)) {
      message.error('学院名称只能包含中文、英文、数字、空格、括号和连字符')
      return
    }
    
    // 准备请求数据，确保使用trimmed的名称
    // 根据后端要求，为学院名称生成一个简单的代码（取名称的前几个字母大写）
    // 生成简单的代码：取名称中的汉字/字母，转换为大写，最多取8个字符
    const generateCode = (name) => {
      // 移除所有空格并取前8个字符
      const cleanName = name.replace(/\s+/g, '');
      // 如果名称以中文开头，取前两个汉字的拼音首字母；如果是英文，直接取前几个字母
      // 这里采用简单实现，直接取前2-4个字符的大写作为代码
      if (/^[\u4e00-\u9fa5]/.test(cleanName)) {
        // 中文名称处理 - 简单起见，使用学院名称的拼音首字母缩写作为代码
        // 这里使用简化实现，取学院名称的前两个字的拼音首字母
        // 例如：计算机科学与技术学院 -> JSJ
        const pinyinMap = {
          '计算机': 'JSJ',
          '电子': 'DZ',
          '机械': 'JX',
          '化学': 'HX',
          '数学': 'SX',
          '物理': 'WL',
          '生物': 'SW',
          '医学': 'YX',
          '管理': 'GL',
          '经济': 'JJ',
          '法学': 'FX',
          '文学': 'WX',
          '外语': 'WY',
          '艺术': 'YS',
          '体育': 'TY',
          '建筑': 'JZ',
          '环境': 'HJ',
          '材料': 'CL',
          '能源': 'NY',
          '土木': 'TM'
        };
        
        // 尝试匹配常用学院名称
        for (const [key, value] of Object.entries(pinyinMap)) {
          if (cleanName.includes(key)) {
            return value;
          }
        }
        
        // 如果没有匹配到，使用默认的简化实现
        return 'XY' + Math.floor(Math.random() * 100).toString().padStart(2, '0');
      } else {
        // 英文或其他字符，直接取前3个字符
        return cleanName.substring(0, Math.min(3, cleanName.length)).toUpperCase();
      }
    };
    
    const requestData = {
      name: nameTrimmed,
      code: generateCode(nameTrimmed) // 添加code字段
    }
    console.log('发送到API的数据:', requestData);
    
    // 调用API创建学院
    console.log('准备发送请求到API...');
    console.log('API路径:', '/api/auth/admin/colleges/');
    console.log('请求数据:', requestData);
    
    // 调用API创建学院
    const response = await api.admin.createCollege(requestData);
    console.log('API响应:', response);
      
    // 处理响应 - 根据axios拦截器的处理，成功时直接返回data部分
    // 检查响应格式并处理成功情况
    if (response) {
      // 使用成功类型的消息提示，提供更友好的视觉反馈
      message.success(`学院「${nameTrimmed}」添加成功`, 2, () => {
        // 消息关闭后的回调，可以执行一些后续操作
        console.log(`学院${nameTrimmed}添加成功后的后续处理`);
      })
      
      // 确保模态框关闭并重置表单
      addModalVisible.value = false
      
      // 使用setTimeout确保模态框完全关闭后再重置，避免渲染冲突
      setTimeout(() => {
        addForm.name = ''
        // 清除可能的验证状态
        if (addFormRef.value) {
          addFormRef.value.clearValidate();
          addFormRef.value.resetFields();
        }
      }, 300)
      
      // 刷新学院列表，确保新添加的学院显示
      await fetchColleges()
    } else {
      // 更具体的错误提示，使用error类型的消息
      const errorMsg = '学院添加失败，请重试';
      console.error('API返回错误:', errorMsg, response);
      message.error(errorMsg, 3) // 错误消息显示时间稍长，便于用户阅读
    }
  } catch (error) {
    // 更详细的错误处理
    console.error('添加学院时发生错误:', error);
    console.error('错误详情:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    
    // 提供更具体的错误提示
    let errorMsg = '添加学院失败，请重试';
    
    // 根据错误类型提供不同的提示，更全面地覆盖各种边界情况
    if (error.message && error.message.includes('timeout')) {
      // 网络超时处理
      errorMsg = '请求超时，请检查网络后重试';
    } else if (!error.response) {
      // 网络错误处理
      errorMsg = '网络连接失败，请检查网络和后端服务是否正常运行';
      console.log('请确认后端服务是否可以访问');
    } else if (error.response?.status === 403) {
      // 权限错误处理
      errorMsg = '权限不足，无法添加学院';
    } else if (error.response?.status === 409) {
      // 冲突错误处理（可能是名称重复）
      errorMsg = '学院名称已存在，请使用其他名称';
      // 在表单上显示错误，提供更直接的反馈
      if (addFormRef.value && typeof addFormRef.value.setFields === 'function') {
        addFormRef.value.setFields([{
          name: 'name',
          errors: [errorMsg]
        }]);
      }
    } else if (error.response?.status === 400) {
      // 请求参数错误处理
      errorMsg = '请求参数错误，请检查输入';
      // 解析后端返回的具体错误信息
      if (error.response.data?.error) {
        errorMsg = error.response.data.error;
      } else if (error.response.data?.name) {
        errorMsg = `学院名称错误: ${error.response.data.name[0]}`;
        if (addFormRef.value && typeof addFormRef.value.setFields === 'function') {
          addFormRef.value.setFields([{
            name: 'name',
            errors: [errorMsg]
          }]);
        }
      } else if (error.response.data?.code) {
        errorMsg = `学院代码错误: ${error.response.data.code[0]}`;
      }
    } else if (error.response?.status === 500) {
      // 服务器错误处理
      errorMsg = '服务器内部错误，请稍后再试';
    } else if (error.response?.status === 429) {
      // 请求频率限制处理
      errorMsg = '操作过于频繁，请稍后再试';
    }
    
    // 显示错误消息，延长显示时间
    message.error(errorMsg, 3);
  } finally {
    // 确保无论成功失败都重置加载状态
    addFormLoading.value = false;
  }
}
const handleEditCollege = async () => {
  try {
    // 确保id存在且有效
    if (!editForm.id) {
      message.error('学院ID无效');
      return;
    }
    
    // 使用表单验证API进行验证
    if (editFormRef.value) {
      try {
        await editFormRef.value.validate();
      } catch (errorInfo) {
        console.error('表单验证失败:', errorInfo);
        // 不抛出异常，让组件自己显示错误信息
        return;
      }
    }
    
    // 获取修剪后的名称
    const trimmedName = editForm.name.trim();
    
    // 发送请求编辑学院
    await api.admin.updateCollege(editForm.id, { name: trimmedName })
    
    message.success('学院编辑成功')
    editModalVisible.value = false
    fetchColleges() // 重新获取列表
    
    // 重置表单
    if (editFormRef.value) {
      editFormRef.value.resetFields()
    }
  } catch (error) {
    console.error('编辑学院失败:', error);
    
    // 处理不同类型的错误
    if (error.code === 'ECONNABORTED' || error.message.includes('Network Error')) {
      message.error('网络连接失败，请检查网络后重试');
    } else if (error.response?.status === 403) {
      message.error('您没有权限执行此操作');
    } else if (error.response?.status === 409) {
      message.error('该学院信息已存在，请检查后重试');
    } else if (error.response?.status === 400) {
      message.error('请求参数错误，请检查后重试');
    } else if (error.response?.status === 500) {
      message.error('服务器内部错误，请稍后重试');
    } else if (error.response?.status === 429) {
      message.error('操作过于频繁，请稍后重试');
    } else if (error.message === '学院ID无效') {
      message.error(error.message);
    } else if (error.message && error.message.includes('validate')) {
      message.error('请检查表单输入是否正确');
    } else if (error.message === 'api.admin.updateCollege is not a function') {
      message.error('系统功能异常，请刷新页面后重试');
    } else {
      message.error(error.response?.data?.detail || '编辑学院失败');
    }
  }
}

// 删除学院
const deleteCollege = async (id) => {
  try {
    // 检查是否为临时ID（以'temp_'开头）
    if (typeof id === 'string' && id.startsWith('temp_')) {
      // 对于临时ID，直接在前端从列表中移除，不调用后端API
      colleges.value = colleges.value.filter(item => item.id !== id);
      message.success('学院删除成功');
      console.log('前端临时学院已删除，ID:', id);
    } else {
      // 立即从本地列表中移除被删除的项目，提供即时反馈
      const collegeToDelete = colleges.value.find(item => item.id === id);
      if (collegeToDelete) {
        colleges.value = colleges.value.filter(item => item.id !== id);
        console.log('已从本地列表移除学院，准备调用API:', id);
      }
      
      // 真实ID，调用后端API删除
      // 注意：后端删除API返回204 No Content，api.js拦截器会将其转换为null
      const result = await api.admin.deleteCollege(id);
      
      // 即使返回null（因为204 No Content），也认为成功
      // 这确保了无论后端返回什么格式，只要不抛出异常，就显示成功
      console.log('API删除学院成功，结果:', result);
      message.success('学院删除成功');
      
      // 仍然调用fetchColleges确保数据一致性，但使用try-catch避免刷新失败影响用户体验
      try {
        await fetchColleges();
      } catch (fetchError) {
        console.warn('刷新学院列表时出现警告，但删除操作已成功:', fetchError);
        // 不显示错误，因为删除已经成功并且本地列表已经更新
      }
    }
  } catch (error) {
    console.error('删除学院失败:', error);
    console.error('错误响应:', error.response);
    
    // 恢复本地列表，因为API调用失败了
    try {
      await fetchColleges();
    } catch (recoverError) {
      console.error('恢复学院列表失败:', recoverError);
    }
    
    // 更友好的错误提示，处理各种可能的错误格式
    let errorMessage = '删除学院失败';
    if (error.response) {
      // 处理HTTP错误响应
      if (error.response.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.response.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response.status === 403) {
        errorMessage = '权限不足，无法删除学院';
      } else if (error.response.status === 404) {
        errorMessage = '学院不存在';
      } else if (error.response.status === 400) {
        errorMessage = '学院已被使用，无法删除';
      } else if (error.response.status === 500) {
        errorMessage = '服务器内部错误，请稍后再试';
      }
    } else if (error.message) {
      // 处理网络错误或其他JavaScript错误
      if (error.message.includes('Network Error')) {
        errorMessage = '网络连接错误，请检查您的网络连接';
      } else {
        errorMessage = error.message;
      }
    }
    
    message.error(errorMessage);
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    // 保存要删除的学院ID列表
    const collegesToDelete = [...selectedColleges.value];
    if (collegesToDelete.length === 0) {
      message.warning('请选择要删除的学院');
      return;
    }
    
    // 立即从本地列表中移除被删除的项目，提供即时反馈
    colleges.value = colleges.value.filter(item => !collegesToDelete.includes(item.id));
    console.log('已从本地列表移除学院，准备批量调用API:', collegesToDelete);
    
    // 遍历选中的ID，依次调用删除接口
    let successCount = 0;
    let errorCount = 0;
    const errors = [];
    
    for (const id of collegesToDelete) {
      try {
        await api.admin.deleteCollege(id);
        successCount++;
        console.log('成功删除学院ID:', id);
      } catch (individualError) {
        errorCount++;
        console.error('删除单个学院失败:', id, individualError);
        // 收集错误信息
        let errorMsg = `学院 ${id} 删除失败`;
        if (individualError.response) {
          if (individualError.response.data?.error) {
            errorMsg = individualError.response.data.error;
          } else if (individualError.response.data?.detail) {
            errorMsg = individualError.response.data.detail;
          }
        }
        errors.push(errorMsg);
      }
    }
    
    // 显示适当的消息
    if (successCount > 0 && errorCount === 0) {
      message.success(`成功删除 ${successCount} 个学院`);
    } else if (successCount > 0 && errorCount > 0) {
      message.success(`部分成功：${successCount} 个学院删除成功，${errorCount} 个失败`);
      // 记录错误详情
      console.warn('批量删除部分失败，错误详情:', errors);
    } else {
      message.error(`所有 ${errorCount} 个学院删除失败`);
      // 恢复本地列表，因为所有删除都失败了
      try {
        await fetchColleges();
      } catch (recoverError) {
        console.error('恢复学院列表失败:', recoverError);
      }
    }
    
    // 关闭模态框并清空选择
    batchModalVisible.value = false;
    selectedColleges.value = [];
    
    // 仍然调用fetchColleges确保数据一致性，但使用try-catch避免刷新失败影响用户体验
    try {
      await fetchColleges();
    } catch (fetchError) {
      console.warn('刷新学院列表时出现警告:', fetchError);
    }
  } catch (error) {
    console.error('批量删除学院过程中发生异常:', error);
    
    // 尝试恢复数据
    try {
      await fetchColleges();
    } catch (recoverError) {
      console.error('恢复学院列表失败:', recoverError);
    }
    
    // 提供更友好的错误提示
    let errorMessage = '批量删除失败';
    if (error.message) {
      errorMessage = error.message;
    }
    message.error(errorMessage);
  }
}

// 加载所有班级和当前学院已绑定的班级
const loadClassData = async () => {
  if (!currentCollege.value) return;
  
  console.log('=== 开始加载班级数据 ===');
  console.log('当前学院信息:', currentCollege.value);
  
  // 设置加载状态为true
  loadingClasses.value = true;
  
  try {
    // 获取所有班级列表
    console.log('1. 调用班级列表API...');
    const classesResponse = await api.admin.classes.getClasses();
    console.log('班级列表API响应:', classesResponse);
    
    let classData = classesResponse;
    // 支持 { classes: [] } 格式
    if (classData && Array.isArray(classData.classes)) {
      console.log('2. 解析 { classes: [] } 格式');
      classData = classData.classes;
    }
    // 支持 { results: [] } 格式
    else if (classData && Array.isArray(classData.results)) {
      console.log('2. 解析 { results: [] } 格式');
      classData = classData.results;
    }
    // 支持 { data: [] } 格式
    else if (classData && Array.isArray(classData.data)) {
      console.log('2. 解析 { data: [] } 格式');
      classData = classData.data;
    }
    const allClasses = Array.isArray(classData) ? classData : [];
    console.log('3. 处理后的所有班级数据:', allClasses);
    console.log('   班级数量:', allClasses.length);
    allClasses.forEach((cls, index) => {
      console.log(`   班级${index + 1}:`, { 
        id: cls.id, 
        name: cls.name, 
        college: cls.college, 
        collegeType: typeof cls.college 
      });
    });
    
    // 获取当前学院已绑定的班级
    console.log('4. 调用班级绑定关系API...');
    const classBindingsResponse = await api.admin.classBindings.getClassBindings({
      college_id: currentCollege.value.id
    });
    console.log('班级绑定关系API响应:', classBindingsResponse);
    
    let bindingData = classBindingsResponse;
    // 支持 { data: [] } 格式
    if (bindingData && Array.isArray(bindingData.data)) {
      console.log('5. 解析绑定关系 { data: [] } 格式');
      bindingData = bindingData.data;
    }
    // 支持 { results: [] } 格式
    else if (bindingData && Array.isArray(bindingData.results)) {
      console.log('5. 解析绑定关系 { results: [] } 格式');
      bindingData = bindingData.results;
    }
    const collegeClassBindings = Array.isArray(bindingData) ? bindingData : [];
    console.log('6. 处理后的班级绑定关系:', collegeClassBindings);
    console.log('   绑定关系数量:', collegeClassBindings.length);
    
    // 提取当前学院已绑定的班级ID列表
    const collegeClassIds = collegeClassBindings.map(binding => {
      // 确保class_id是字符串类型，便于后续比较
      return String(binding.class_id || '');
    });
    console.log('7. 提取的班级ID列表:', collegeClassIds);
    
    // 更新已选择的班级列表
    let selectedFromBindings = allClasses.filter(cls => {
      // 确保班级ID是字符串类型，便于比较
      const classId = String(cls.id || '');
      return collegeClassIds.includes(classId);
    });
    console.log('8. 通过绑定关系获取的班级:', selectedFromBindings);
    console.log('   通过绑定关系获取的班级数量:', selectedFromBindings.length);
    
    // =================================
    // 备用逻辑：当绑定关系获取的班级为空时，直接从班级数据中根据college字段过滤
    // =================================
    let finalSelectedClasses = selectedFromBindings;
    
    if (finalSelectedClasses.length === 0) {
      console.log('9. 通过绑定关系获取的班级为空，使用备用逻辑：根据班级的college字段过滤...');
      console.log('   当前学院ID:', currentCollege.value.id);
      console.log('   当前学院名称:', currentCollege.value.name);
      
      finalSelectedClasses = allClasses.filter(cls => {
        // 处理college字段可能的多种格式
        const classCollege = cls.college;
        let isMatch = false;
        
        if (!classCollege) {
          console.log(`   班级 ${cls.name} (ID: ${cls.id}) 的college字段为空，不匹配`);
          return false;
        }
        
        // 情况1: college是对象 { id: 'xxx', name: 'xxx' }
        if (typeof classCollege === 'object' && classCollege.id) {
          isMatch = String(classCollege.id) === String(currentCollege.value.id);
          console.log(`   班级 ${cls.name} (ID: ${cls.id}) - college是对象: ${classCollege.id} === ${currentCollege.value.id} ? ${isMatch}`);
        }
        // 情况2: college是字符串ID
        else if (typeof classCollege === 'string') {
          // 先尝试ID匹配
          isMatch = classCollege === currentCollege.value.id;
          console.log(`   班级 ${cls.name} (ID: ${cls.id}) - college是字符串: ${classCollege} === ${currentCollege.value.id} ? ${isMatch}`);
          
          // 如果ID不匹配，尝试名称匹配
          if (!isMatch) {
            isMatch = classCollege === currentCollege.value.name;
            console.log(`   班级 ${cls.name} (ID: ${cls.id}) - college是字符串: ${classCollege} === ${currentCollege.value.name} ? ${isMatch}`);
          }
        }
        
        return isMatch;
      });
      
      console.log('10. 通过备用逻辑获取的班级:', finalSelectedClasses);
      console.log('    通过备用逻辑获取的班级数量:', finalSelectedClasses.length);
    }
    
    // 更新已选择的班级列表
    selectedClasses.value = finalSelectedClasses;
    console.log('11. 最终已选择的班级列表:', selectedClasses.value);
    console.log('    最终已选择班级数量:', selectedClasses.value.length);
    selectedClasses.value.forEach((cls, index) => {
      console.log(`    已选班级${index + 1}:`, { id: cls.id, name: cls.name });
    });
    
    // 计算可选择的班级（未绑定到当前学院的）
    availableClasses.value = allClasses.filter(cls => {
      // 确保班级ID是字符串类型，便于比较
      const classId = String(cls.id || '');
      // 检查班级是否已在最终选择列表中
      const isSelected = finalSelectedClasses.some(selected => String(selected.id) === classId);
      console.log(`   检查班级 ${cls.name} (ID: ${classId}): ${isSelected ? '已绑定' : '可选择'}`);
      return !isSelected;
    });
    console.log('12. 可选择的班级列表:', availableClasses.value);
    console.log('    可选择班级数量:', availableClasses.value.length);
    
    // 确保classes.value也被正确更新，保持数据一致性
    classes.value = allClasses;
    console.log('13. 班级数据加载完成');
  } catch (error) {
    console.error('加载班级数据失败:', error);
    console.error('错误详情:', error.response?.data);
    console.error('错误状态:', error.response?.status);
    
    // 根据错误类型显示不同的错误信息
    let errorMsg = '加载班级数据失败';
    if (error.response?.status === 403) {
      errorMsg = '权限不足，无法获取班级数据';
    } else if (error.response?.status === 404) {
      errorMsg = '无法找到班级数据';
    } else if (error.response?.status === 500) {
      errorMsg = '服务器错误，请稍后再试';
    } else if (error.message.includes('Network Error')) {
      errorMsg = '网络连接失败，请检查网络';
    }
    message.error(errorMsg);
  } finally {
    // 设置加载状态为false
    loadingClasses.value = false;
    console.log('设置loadingClasses为false');
  }
  console.log('=== 班级数据加载结束 ===');
};

// 打开班级选择模态框（重构版本）
const showClassSelectionModal = () => {
  // 清空之前的选择
  classSelection.selectedClassIds = [];
  // 加载最新的班级数据
  loadClassData();
  // 显示模态框
  classModalVisible.value = true;
};

// 保存班级（从列表中选择添加）
const handleSaveClass = async () => {
  if (!currentCollege.value) return;
  
  try {
    // 检查是否有选择班级
    if (!classSelection.selectedClassIds || classSelection.selectedClassIds.length === 0) {
      message.error('请至少选择一个班级');
      return;
    }
    
    // 为每个选择的班级创建绑定关系
    const bindingPromises = classSelection.selectedClassIds.map(classId => {
      return api.admin.classBindings.createClassBinding({
        college_id: currentCollege.value.id,
        class_id: classId
      });
    });
    
    // 并行执行所有绑定操作
    await Promise.all(bindingPromises);
    
    message.success(`成功添加 ${classSelection.selectedClassIds.length} 个班级`);
    classModalVisible.value = false;
    
    // 重新加载班级数据
    await loadClassData();
  } catch (error) {
    console.error('添加班级失败:', error);
    message.error(error.response?.data?.detail || '添加班级失败');
  }
};

// 删除班级（解除绑定关系）
const deleteClass = async (id) => {
  try {
    if (!currentCollege.value) throw new Error('学院信息不存在');
    
    // 获取班级绑定关系
    const bindingsResponse = await api.admin.classBindings.getClassBindings({
      college_id: currentCollege.value.id,
      class_id: id
    });
    let bindingData = bindingsResponse;
    // 支持 { data: [] } 格式
    if (bindingData && Array.isArray(bindingData.data)) {
      bindingData = bindingData.data;
    }
    // 支持 { results: [] } 格式
    else if (bindingData && Array.isArray(bindingData.results)) {
      bindingData = bindingData.results;
    }
    const bindings = Array.isArray(bindingData) ? bindingData : [];
    if (bindings.length === 0) {
      throw new Error('班级绑定关系不存在');
    }
    
    // 删除绑定关系
    await api.admin.classBindings.deleteClassBinding(bindings[0].id);
    
    message.success('班级移除成功');
    await loadClassData(); // 重新加载班级数据
  } catch (error) {
    console.error('移除班级失败:', error);
    message.error(error.response?.data?.detail || error.message || '移除班级失败');
  }
};

// 生命周期钩子
onMounted(() => {
  fetchColleges()
})
</script>

<style scoped>
.colleges-container {
  padding: 24px;
  background: #fff;
  min-height: 80vh;
}

.page-title {
  font-size: 24px;
  margin-bottom: 24px;
  color: #1890ff;
}

.class-selection {
  padding: 10px 0;
}

.selection-hint {
  margin-bottom: 16px;
  color: #666;
}

.class-select {
  width: 100%;
  min-height: 100px;
}

.no-classes {
  color: #999;
  text-align: center;
  padding: 20px;
  margin-top: 10px;
}

.operation-bar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-management {
  padding: 10px 0;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.class-header h3 {
  margin: 0;
  color: #333;
}

.teacher-management {
  padding: 10px 0;
}

.teacher-header {
  margin-bottom: 16px;
}

.teacher-header h3 {
  margin: 0;
  color: #333;
}
</style>