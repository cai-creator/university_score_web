// API服务层
import axios from 'axios'
import router from '@/router'
import { message } from 'ant-design-vue'

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 15000, // 增加超时时间
  withCredentials: false,  // 禁用跨域凭证，避免跨域问题
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 增强的token处理
axiosInstance.interceptors.request.use(
  config => {
    const requestId = Math.random().toString(36).substring(2, 10)
    config.requestId = requestId
    console.log(`[${requestId}] 原始请求配置:`, config)
    let token = null
    
    try {
      // 尝试从localStorage获取token
      token = localStorage.getItem('token')
      console.log(`[${requestId}] 从localStorage获取的token:`, token ? '存在' : '不存在')
    } catch (e) {
      console.error(`[${requestId}] 无法从localStorage获取token:`, e)
    }
    
    // 如果localStorage没有token，尝试从sessionStorage获取
    if (!token) {
      try {
        token = sessionStorage.getItem('token')
        console.log(`[${requestId}] 从sessionStorage获取的token:`, token ? '存在' : '不存在')
      } catch (e) {
        console.error(`[${requestId}] 无法从sessionStorage获取token:`, e)
      }
    }
    
    // 如果localStorage和sessionStorage都没有token，尝试从cookie获取
    if (!token) {
      try {
        // 使用更可靠的cookie解析方法
        const cookies = document.cookie.split('; ')
        for (let cookie of cookies) {
          const [name, value] = cookie.split('=')
          if (name === 'token') {
            token = decodeURIComponent(value)
            console.log(`[${requestId}] 从cookie获取的token:`, token ? '存在' : '不存在')
            break
          }
        }
      } catch (e) {
        console.error(`[${requestId}] 无法从cookie获取token:`, e)
      }
    }
    
    // 检查是否是登录请求，如果是则不添加token
    if (token && config.url && !config.url.includes('/api/auth/login/')) {
      config.headers['Authorization'] = `Token ${token}`
      console.log(`[${requestId}] Authorization token added to request:`, token)
    } else {
      console.log(`[${requestId}] No token found, this is a login request, or config.url is undefined`)
    }
    console.log(`[${requestId}] API Request:`, config.method.toUpperCase(), config.url, config.data || 'No data')
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 增强错误处理，支持多种响应格式
axiosInstance.interceptors.response.use(
  response => {
    const requestId = response.config?.requestId || 'unknown'
    try {
      console.log(`[${requestId}] API Response:`, response.status, response.config.method.toUpperCase(), response.config.url)
      console.log(`[${requestId}] 响应数据:`, response.data)
      
      // 特殊处理204 No Content响应
      if (response.status === 204) {
        console.log(`[${requestId}] 处理204 No Content响应`)
        return {} // 返回空对象表示成功但无内容，避免前端检查失败
      }
      
      const responseData = response.data
      
      // 特殊处理登录请求响应，确保token不会被错误格式化
      if (response.config && response.config.url && response.config.url.includes('/api/auth/login/')) {
        console.log(`[${requestId}] 登录响应特殊处理:`, responseData)
        return responseData // 直接返回完整的登录响应，包括token
      }
      
      // 统一处理不同的响应格式
      // 格式1: {code, message, data} - API返回的标准格式
      if (responseData.code !== undefined) {
        // 检查code是否为200表示成功
        if (responseData.code === 200) {
          return responseData.data
        } else {
          // 如果code不是200，抛出错误
          const error = new Error(responseData.message || '请求失败')
          error.response = response
          return Promise.reject(error)
        }
      }
      // 格式2: {success, data} - 成功响应格式
      if (responseData.success !== undefined) {
        // 如果success为true，返回包含results字段的对象，符合前端预期
        if (responseData.success) {
          // 检查data是否为数组
          if (Array.isArray(responseData.data)) {
            // 直接返回包含results字段的对象，符合前端预期
            return { results: responseData.data }
          } else {
            // 如果data不是数组，直接返回，让调用方自行处理
            return responseData
          }
        } else {
          // 如果success为false，抛出错误
          const error = new Error(responseData.message || '请求失败')
          error.response = response
          return Promise.reject(error)
        }
      }
      // 格式3: {results, count} - 分页响应
      // 保留完整的分页响应对象，让调用方自行处理results和count
      if (responseData.results && Array.isArray(responseData.results)) {
        return responseData
      }
      // 格式4: {score_items} - 加分项目响应
      if (responseData.score_items && Array.isArray(responseData.score_items)) {
        return responseData.score_items
      }
      // 格式5: {data} - 列表类响应
      if (responseData.data !== undefined) {
        // 检查data是否为数组
        if (Array.isArray(responseData.data)) {
          // 返回包含results字段的对象，符合前端预期
          return { results: responseData.data }
        } else {
          // 如果data不是数组，直接返回
          return responseData
        }
      }
      
      // 其他格式直接返回
      return responseData
    } catch (parseError) {
      console.error(`[${requestId}] 响应数据解析错误:`, parseError)
      // 不再直接显示错误信息，让调用方处理
      return Promise.reject(parseError)
    }
  },
  async error => {
    const requestId = error.config?.requestId || 'unknown'
    // 处理响应错误
    const originalRequest = error.config
    
    // 增强网络错误的详细日志记录
    if (!error.response) {
      console.error(`[${requestId}] 网络错误详情:`, {
        url: error.config?.url,
        method: error.config?.method,
        params: error.config?.params,
        data: error.config?.data,
        headers: error.config?.headers,
        error: error.message,
        code: error.code,
        stack: error.stack
      });
      
      // 不再直接显示错误信息，而是将错误信息添加到error对象中，让调用方处理
      if (error.code === 'ECONNABORTED') {
        error.message = '请求超时，请检查网络连接或稍后重试';
      } else if (error.code === 'ERR_NETWORK') {
        error.message = `网络连接失败: ${error.message}，请检查网络设置`;
      } else if (error.code === 'ERR_BAD_REQUEST') {
        error.message = '请求参数错误，请检查输入信息';
      } else if (error.code === 'ERR_ABORTED') {
        error.message = '请求被取消';
      }
    } else {
      console.error(`[${requestId}] HTTP错误详情:`, {
        url: error.config.url,
        method: error.config.method,
        params: error.config.params,
        data: error.config.data,
        headers: error.config.headers,
        status: error.response.status,
        statusText: error.response.statusText,
        error: error.response.data
      });
    }
    
    console.error(`[${requestId}] API错误详情:`, error)
    
    // 为404错误添加更详细的日志，包括调用栈
    if (error.response && error.response.status === 404) {
      console.error(`[${requestId}] 404 Error Details:`, {
        url: error.config.url,
        method: error.config.method,
        params: error.config.params,
        data: error.config.data,
        headers: error.config.headers,
        error: error.response.data
      });
      
      // 打印调用栈，帮助定位错误来源
      console.error(`[${requestId}] 404 Error Stack:`, new Error().stack);
    }
    
    // 不再将登录请求的401错误转换为成功响应，应该正常抛出错误
    // 这样登录组件可以正确处理失败情况，避免存储无效token
    
    // 如果是401错误，但不是登录请求，才跳转到登录页
    if (error.response && error.response.status === 401) {
      console.log(`[${requestId}] 检测到401未授权错误`)
      
      // 检查是否是登录请求，如果是登录请求失败，不清除token
      if (!originalRequest || !originalRequest.url || !originalRequest.url.includes('/api/auth/login/')) {
        // 清除本地存储的token和用户信息
        try {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          sessionStorage.removeItem('token')
          sessionStorage.removeItem('user')
          // 清除cookie中的token
          document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
          console.log(`[${requestId}] 成功清除所有存储的token和用户信息`)
        } catch (e) {
          console.error(`[${requestId}] 清除token时出错:`, e)
        }
        
        // 提示用户登录已过期
        message.error('登录已过期，请重新登录')
        
        // 跳转到登录页
        router.push({ name: 'Login' })
      } else {
        console.log(`[${requestId}] 登录请求返回401，这是正常的认证失败，不进行页面跳转`)
      }
    }
    
    // 处理其他错误
    // 尝试从响应中获取错误信息
    let errorMessage = '网络请求失败'
    if (error.response && error.response.data) {
      if (error.response.data.message) {
        errorMessage = error.response.data.message
      } else if (error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else {
        errorMessage = JSON.stringify(error.response.data)
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    console.error(`[${requestId}] API错误消息:`, errorMessage)
    // 对于非401错误，显示错误消息但不跳转
    if (!error.response || error.response.status !== 401) {
      message.error(errorMessage)
    }
    // 将错误传递给调用方，确保调用方可以正确处理错误
    return Promise.reject(error)
  }
)

// 定义API方法
// 登录
axiosInstance.login = async (username, password, role, captchaText) => {
  // 调用后端API进行登录：POST /api/auth/login/
  try {
    console.log('Login API request:', {
      url: '/api/auth/login/',
      method: 'POST',
      data: {
        school_id: username,
        password: password
      }
    });
    
    const response = await axiosInstance.post('/api/auth/login/', {
      school_id: username,
      password: password
    })
    console.log('Login API response:', response)
    
    // 处理后端返回的响应格式
    const responseData = response.data || response;
    
    // 直接返回响应数据，便于前端处理
    return responseData;
  } catch (error) {
    console.error('Login API error:', {
      message: error.message,
      code: error.code,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config
    });
    // 抛出完整的错误对象，包括response数据
    throw error;
  }
}

// 提交申请
axiosInstance.submitApplication = async (data) => {
  try {
    // 调用后端API提交申请：POST /api/material/applications/
    
    // 验证必要参数
    if (!data || !data.application_type) {
      const error = new Error('缺少必要参数: application_type');
      console.error('提交申请失败:', error);
      throw error;
    }
    
    console.log('提交申请的application_type:', data.application_type);
    
    // 构建FormData以支持multipart/form-data格式
    const formData = new FormData();
    
    // 添加非文件字段，确保application_type被显式添加
    formData.append('application_type', data.application_type);
    
    // 调试：打印所有数据键，检查竞赛相关字段是否存在
    console.log('data keys:', Object.keys(data));
    
    // 添加所有非文件字段
    Object.keys(data).forEach(key => {
      if (key !== 'screenshot' && key !== 'fileList' && key !== 'application_type' && key !== 'attachments') { // 避免重复添加
        console.log(`添加字段: ${key}, 值: ${data[key]}`);
        formData.append(key, data[key]);
      }
    });
    
    // 确保estimated_score字段被添加，无论是否在data中
    if (data.estimated_score !== undefined) {
      console.log(`添加字段: estimated_score, 值: ${data.estimated_score}`);
      formData.append('estimated_score', data.estimated_score);
    }
    
    // 确保user_explanation字段存在，避免后端验证失败
    if (!formData.has('user_explanation')) {
      formData.append('user_explanation', '');
    }
    
    // 确保学术竞赛相关字段被正确添加
    if (data.application_type === '5' || data.application_type === 'academic_competition') {
      // 确保竞赛相关字段存在
      console.log('处理学术竞赛申请，确保竞赛相关字段存在');
      
      // 竞赛类型：必须添加
      if (!data.competition_name) {
        // 如果是CCF CSP认证，设置为'programming'（程序设计竞赛）
        // 如果是其他竞赛，也设置为'programming'作为默认值
        formData.append('competition_name', 'programming');
      } else {
        formData.append('competition_name', data.competition_name);
      }
      
      // 具体竞赛名称：如果是CCF CSP认证，设置为'CCF CSP'
      if (data.competition_specific_name) {
        formData.append('competition_specific_name', data.competition_specific_name);
      } else if (data.competition_type === 'csp') {
        formData.append('competition_specific_name', 'CCF CSP');
      }
      
      // 竞赛级别：必须添加，使用正确的选项
      if (data.competition_level) {
        formData.append('competition_level', data.competition_level);
      } else {
        // 对于CCF CSP认证，设置为'A-'（A-类竞赛）
        // 对于其他竞赛，设置为默认值'A-'
        formData.append('competition_level', 'A-');
      }
      
      // 竞赛类别：必须添加，使用正确的选项
      if (data.competition_category) {
        formData.append('competition_category', data.competition_category);
      } else {
        // 对于CCF CSP认证，设置为'a_minus'（A-类）
        // 对于其他竞赛，设置为默认值'a_minus'
        formData.append('competition_category', 'a_minus');
      }
      
      // 获奖等级：必须添加，根据csp_rank_percentage设置
      if (data.award_level) {
        formData.append('award_level', data.award_level);
      } else if (data.competition_type === 'csp') {
        // 根据CSP排名等级设置获奖等级
        if (data.csp_rank_percentage === '0.2') {
          formData.append('award_level', 'first_plus'); // 等同全国一等奖
        } else if (data.csp_rank_percentage === '1.5') {
          formData.append('award_level', 'second'); // 等同全国二等奖
        } else if (data.csp_rank_percentage === '3') {
          formData.append('award_level', 'third'); // 等同全国三等奖
        } else {
          formData.append('award_level', 'third'); // 默认三等奖
        }
      } else {
        formData.append('award_level', 'third'); // 默认三等奖
      }
    } else if (data.application_type === '11' || data.application_type === 'honorary_title') {
      // 确保荣誉称号相关字段被正确添加
      console.log('处理荣誉称号申请，确保相关字段存在');
      
      // 确保颁发机构字段非空
      if (!data.awarding_organization || data.awarding_organization === '') {
        // 如果为空，设置为默认值
        formData.append('awarding_organization', '未知');
      } else {
        formData.append('awarding_organization', data.awarding_organization);
      }
    }
    
    // 处理文件上传，支持多种文件来源：screenshot、attachments、fileList
    const processFiles = (files) => {
      if (!files || (!Array.isArray(files) && (!files.raw || !files.name))) {
        return;
      }
      
      // 统一处理单文件和多文件情况
      const fileArray = Array.isArray(files) ? files : [files];
      
      // 筛选出所有新文件（有raw属性且不是已存在的文件）
      const newFiles = fileArray.filter(file => file.raw && !file.existing);
      if (newFiles.length === 0) {
        return;
      }
      
      // 获取申请类型
      const applicationType = data.application_type;
      
      // 文件大小限制：10MB
      const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
      
      // 检查文件大小
      const oversizedFiles = newFiles.filter(file => file.raw.size > MAX_FILE_SIZE);
      if (oversizedFiles.length > 0) {
        const error = new Error(`文件大小超过限制（最大10MB）: ${oversizedFiles.map(f => f.name).join(', ')}`);
        console.error('提交申请失败:', error);
        throw error;
      }
      
      // 检查是否为英语成绩申请
      const isEnglishCET = applicationType === 'english_score' || // 后端期望的字符串类型
                          applicationType === 'english_cet4' || 
                          applicationType === 'english_cet6';
      
      // 检查是否为荣誉称号申请、学术竞赛申请、国际组织实习或参军入伍
      const useScreenshot = applicationType === 'honorary_title' ||
                          applicationType === 'academic_competition' ||
                          applicationType === 'international_internship' ||
                          applicationType === 'military_service';
      
      // 调试：打印文件处理信息
      console.log('处理文件上传:', {
        applicationType,
        isEnglishCET,
        useScreenshot,
        newFilesLength: newFiles.length
      });
      
      // 根据申请类型添加对应的文件字段
      if (newFiles.length > 0) {
        // 英语成绩申请：使用score_report字段
        if (isEnglishCET) {
          const file = newFiles[0];
          console.log('添加英语成绩文件:', file.name, '作为score_report');
          formData.append('score_report', file.raw, file.name);
        }
        // 荣誉称号、学术竞赛等申请：使用screenshot字段
        else if (useScreenshot) {
          const file = newFiles[0];
          console.log('添加截图文件:', file.name, '作为screenshot');
          formData.append('screenshot', file.raw, file.name);
        }
        // 其他类型的申请：根据类型添加对应的字段
        else {
          // 对于创新项目、CCF CSP等其他类型，使用screenshot字段
          const file = newFiles[0];
          console.log('添加文件:', file.name, '作为screenshot');
          formData.append('screenshot', file.raw, file.name);
        }
      }
    };
    
    // 处理多种可能的文件来源
    if (data.screenshot) {
      processFiles(data.screenshot);
    }
    if (data.attachments) {
      processFiles(data.attachments);
    }
    if (data.fileList) {
      processFiles(data.fileList);
    }
    
    // 调试：打印所有表单数据，特别关注application_type
    console.log('提交的表单数据:');
    console.log('application_type值:', formData.get('application_type'));
    
    for (const [key, value] of formData.entries()) {
      if (key !== 'screenshot' && key !== 'attachments') { // 避免打印大文件数据
        if (value instanceof File) {
          console.log(`${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
        } else {
          console.log(`${key}: ${value}`);
        }
      }
    }
    
    const response = await axiosInstance.post('/api/material/applications/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: data.onUploadProgress || function() {}
    });
    
    return response;
  } catch (error) {
    console.error('提交申请失败:', error);
    console.error('错误详情:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    console.error('错误头信息:', error.response?.headers);
    throw error;
  }
}

// 编辑申请
axiosInstance.editApplication = async (id, data) => {
  try {
    // 验证必要参数
    if (!data || !data.application_type) {
      const error = new Error('缺少必要参数: application_type');
      console.error('编辑申请失败:', error);
      throw error;
    }
    
    console.log('编辑申请的application_type:', data.application_type);
    
    // 构建FormData以支持multipart/form-data格式
    const formData = new FormData();
    
    // 添加非文件字段，确保application_type被显式添加
    formData.append('application_type', data.application_type);
    
    Object.keys(data).forEach(key => {
      if (key !== 'screenshot' && key !== 'fileList' && key !== 'application_type') { // 避免重复添加
        formData.append(key, data[key]);
      }
    });
    
    // 添加文件字段（如果有）
    if (data.screenshot && Array.isArray(data.screenshot)) {
      // 筛选出所有新文件（有raw属性的）
      // 编辑模式下，从后端获取的文件有existing属性但可能没有raw属性，这些文件不需要重新上传
      const newFiles = data.screenshot.filter(file => file.raw && !file.existing);
      
      // 获取申请类型
      const applicationType = data.application_type;
      
      // 文件大小限制：10MB
      const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
      
      // 检查文件大小
      const oversizedFiles = newFiles.filter(file => file.raw.size > MAX_FILE_SIZE);
      if (oversizedFiles.length > 0) {
        const error = new Error(`文件大小超过限制（最大10MB）: ${oversizedFiles.map(f => f.name).join(', ')}`);
        console.error('编辑申请失败:', error);
        throw error;
      }
      
      // 检查是否为英语成绩申请
      const isEnglishCET = applicationType === '1' || // 数字标识，对应english_cet4
                          applicationType === '2' || // 数字标识，对应english_cet6
                          applicationType === 'english_cet4' || 
                          applicationType === 'english_cet6';
      
      // 检查是否为荣誉称号申请、学术竞赛申请、国际组织实习或参军入伍
      const useScreenshot = applicationType === 'honorary_title' ||
                          applicationType === 'academic_competition' ||
                          applicationType === '5' || // 数字标识，对应academic_competition
                          applicationType === '8' || // 数字标识，对应international_internship
                          applicationType === '9'; // 数字标识，对应military_service;
      
      // 处理新上传的文件
      if (newFiles.length > 0) {
        if (isEnglishCET) {
          // 英语成绩申请：使用score_report字段
          const file = newFiles[0];
          formData.append('score_report', file.raw, file.name);
        } else if (useScreenshot) {
          // 荣誉称号、学术竞赛等申请：使用screenshot字段
          const file = newFiles[0];
          formData.append('screenshot', file.raw, file.name);
        } else {
          // 其他类型的申请：使用screenshot字段
          const file = newFiles[0];
          formData.append('screenshot', file.raw, file.name);
        }
      }
      
      // 确保user_explanation字段存在，避免后端验证失败
      if (!formData.has('user_explanation')) {
        formData.append('user_explanation', '');
      }
    }
    
    // 调试：打印所有表单数据，特别关注application_type
    console.log('编辑的表单数据:');
    console.log('application_type值:', formData.get('application_type'));
    
    for (const [key, value] of formData.entries()) {
      if (key !== 'screenshot' && key !== 'attachments') { // 避免打印大文件数据
        if (value instanceof File) {
          console.log(`${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
        } else {
          console.log(`${key}: ${value}`);
        }
      }
    }

    // 使用正确的URL：指向StudentApplicationViewSet的update方法
    const response = await axiosInstance.put(`/api/material/student/applications/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response;
  } catch (error) {
    console.error('编辑申请失败:', error);
    console.error('错误详情:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    console.error('错误头信息:', error.response?.headers);
    throw error;
  }
}

// 获取申请详情
axiosInstance.getApplicationDetail = async (id) => {
  try {
    const response = await axiosInstance.get(`/api/material/student/applications/${id}/`);
    // 处理不同的返回格式
    if (response.data) {
      return response.data;
    } else {
      return response;
    }
  } catch (error) {
    console.error('获取申请详情失败:', error);
    throw error;
  }
}

// 获取申请列表
axiosInstance.getApplications = async () => {
  try {
    const res = await axiosInstance.get('/api/material/student/applications/');
    // 处理不同的返回格式，注意：由于响应拦截器的处理，res已经是处理后的数据
    console.log('getApplications响应:', res);
    if (res.results) {
      return res;
    } else if (res.applications) {
      // 后端返回applications字段（符合openapi规范）
      return { results: res.applications };
    } else if (Array.isArray(res)) {
      return { results: res };
    }
    return { results: [] };
  } catch (error) {
    console.error('获取申请列表失败:', error);
    // 确保即使请求失败，也返回一个包含results属性的对象
    return { results: [] };
  }
}

// 获取申请类型列表
axiosInstance.getApplicationTypes = async () => {
  return await axiosInstance.get('/api/material/applications/types/')
}

// 获取用户信息
axiosInstance.getUserInfo = async () => {
  try {
    const response = await axiosInstance.get('/api/auth/info/')
    
    console.log('用户信息API原始响应:', response)
    
    // 检查响应数据
    if (!response) {
      console.error('获取用户信息失败: 响应为空', response);
      throw new Error('获取用户信息失败: 响应为空');
    }
    
    // 处理用户类型，确保转换为字符串格式
    const userTypeMap = {
      0: 'student',
      1: 'teacher', 
      2: 'admin'
    }
    
    // 创建一个新对象，确保包含所有必要字段
    let userData = { ...response };
    
    // 检查响应结构，处理{errorcode, message, user}格式
    if (response.user) {
      // 如果响应直接包含user对象（后端返回格式），使用这个对象
      userData = { ...response.user };
    } else if (response.data && response.data.user) {
      // 如果user对象在data中，提取它
      userData = { ...response.data.user };
    } else if (response.data) {
      // 否则使用整个data对象
      userData = { ...response.data };
    }
    
    // 确保用户类型是字符串格式
    let userType = userData.user_type || userData.role;
    if (userType !== undefined) {
      if (typeof userType === 'number') {
        userData.user_type = userTypeMap[userType] || userType;
      } else {
        userData.user_type = userType;
      }
      // 同时设置role字段，确保与路由守卫的兼容性
      userData.role = userData.user_type;
    }
    
    console.log('处理后的用户信息:', userData)
    return userData
  } catch (error) {
    console.error('获取用户信息失败:', error)
    console.error('错误详情:', error.response?.data)
    throw error
  }
}

// 为保持兼容性，添加student API方法
axiosInstance.student = {
  getCurrentUser: () => axiosInstance.getUserInfo(),
  getApplications: async (params) => {
    try {
      const res = await axiosInstance.get('/api/material/student/applications/', { params });
      // 调试：打印响应数据
      console.log('getApplications响应:', res);
      // 处理不同的返回格式，注意：由于响应拦截器的处理，res可能已经是处理后的数据
      if (res.results) {
        return res;
      } else if (Array.isArray(res)) {
        // 如果响应拦截器直接返回了数组，包装为{ results: res }
        return { results: res };
      }
      return { results: [] };
    } catch (error) {
      console.error('获取申请列表失败:', error);
      // 确保即使请求失败，也返回一个包含results属性的对象
      return { results: [] };
    }
  },
  getScoreItems: async () => {
    return await axiosInstance.get('/api/score/student/score-items/');
  },
  updateProfile: async (data) => {
        return await axiosInstance.put('/api/auth/info/', data);
      },
  withdrawApplication: async (id) => {
    return await axiosInstance.post(`/api/material/applications/withdraw/${id}/`);
  },
  deleteApplication: async (id) => {
    return await axiosInstance.delete(`/api/material/student/applications/${id}/`);
  }
};

// 直接添加撤回申请的方法
axiosInstance.withdrawApplication = async (id) => {
  return await axiosInstance.student.withdrawApplication(id);
};

// 直接添加删除申请的方法
axiosInstance.deleteApplication = async (id) => {
  return await axiosInstance.student.deleteApplication(id);
};

// 在student对象中添加withdrawApplication方法
axiosInstance.student.withdrawApplication = async (id) => {
  return await axiosInstance.post(`/api/material/applications/withdraw/${id}/`);
};

// 在student对象中添加deleteApplication方法
axiosInstance.student.deleteApplication = async (id) => {
  return await axiosInstance.delete(`/api/material/student/applications/${id}/`);
};

// 为保持兼容性，添加teacher API方法
axiosInstance.teacher = {
  getCurrentUser: () => axiosInstance.getUserInfo(),
  getStats: async () => {
    return await axiosInstance.get('/api/material/applications/application-stats/');
  },
  getRecentApplications: async (params) => {
    return await axiosInstance.get('/api/material/reviews/recent-applications/', { params });
  },
  getApplications: async (params = {}) => {
        // 使用正确的接口URL，指向AdminMaterialApplicationViewSet的list方法
        // 该方法已经支持status和search参数，并且返回所有状态的申请
        const baseUrl = '/api/material/admin/applications/';
        
        console.log('getApplications params:', params);
        
        // 如果请求所有状态，删除status参数
        if (params.status === 'all') {
          delete params.status;
        }
        
        // 添加足够大的page_size以获取所有申请
        const allParams = {
          ...params,
          page_size: 100 // 设置一个足够大的值，确保获取所有申请
        };
        
        try {
          const response = await axiosInstance.get(baseUrl, { params: allParams });
          console.log('getApplications response:', response);
          
          // 返回处理后的响应数据
          return response;
        } catch (error) {
          console.error('获取申请列表失败:', error);
          // 保留原始错误信息
          throw error;
        }
      },
  approveApplication: async (id, data = {}) => {
      try {
        console.log('Approving application:', id);
        console.log('Approval data:', data);
        const response = await axiosInstance.post(`/api/material/admin/applications/${id}/approve/`, {
          ...data,
          score: data.score
        });
        console.log('Application approved successfully:', response);
        return response;
      } catch (error) {
        console.error('Error approving application:', error);
        throw error;
      }
    },
  rejectApplication: async (id, data) => {
    try {
      console.log('Rejecting application:', id);
      console.log('Rejection data:', data);
      const response = await axiosInstance.post(`/api/material/admin/applications/${id}/reject/`, {
        ...data,
        reason: data.reason || ''
      });
      console.log('Application rejected successfully:', response);
      return response;
    } catch (error) {
      console.error('Error rejecting application:', error);
      throw error;
    }
  },
  updateApplication: async (id, data) => {
    return await axiosInstance.put(`/api/material/student/applications/${id}/`, data);
  },
  getApplicationReviewHistory: async (id) => {
    return await axiosInstance.get(`/api/material/reviews/application_history/${id}/`);
  },
  getStudents: async (params) => {
    return await axiosInstance.get('/api/auth/admin/students/', { params });
  },
  updateProfile: async (data) => {
        return await axiosInstance.put('/api/auth/info/', data);
      }
};

// 为保持兼容性，添加admin API方法
axiosInstance.admin = {
    // 获取学院列表
    getColleges: async () => {
      return await axiosInstance.get('/api/auth/admin/colleges/');
    },
    // 添加学院
    createCollege: async (data) => {
      return await axiosInstance.post('/api/auth/admin/colleges/', data);
    },
    // 删除学院
    deleteCollege: async (id) => {
      // 确保ID有效
      if (!id) throw new Error('无效的学院ID');
      // 直接使用原始ID，不再尝试转换为整数，因为后端数据库使用UUID格式
      return await axiosInstance.delete(`/api/auth/admin/colleges/${encodeURIComponent(id)}/`);
    },
    // 更新学院信息
    updateCollege: async (id, data) => {
      // 确保ID有效
      if (!id) throw new Error('无效的学院ID');
      // 不再强制要求ID必须是数字，保留原始ID格式
      return await axiosInstance.put(`/api/auth/admin/colleges/${id}/`, data);
    },
  getCurrentUser: () => axiosInstance.getUserInfo(),
  // 重置用户密码
  resetPassword: async (userId, options = {}) => {
    // 支持传递自定义密码
    const data = options.password ? { password: options.password } : {};
    return await axiosInstance.post(`/api/auth/admin/reset_password/${userId}/`, data);
  },
  getStatistics: async () => {
    return await axiosInstance.get('/api/auth/admin/statistics/');
  },
  getApplications: async (params) => {
      return await axiosInstance.get('/api/student/material/admin/applications/', { params });
    },
  getReviewStatistics: async () => {
    return await axiosInstance.get('/api/material/reviews/review_statistics/');
  },
  getUsers: async (params) => {
    return await axiosInstance.get('/api/auth/admin/list/', { params });
  },
  getStudents: async (params) => {
    return await axiosInstance.get('/api/auth/admin/list/', { params: { ...params, type: 'student' } });
  },
  student: {
    importStudents: (formData) => {
      return axiosInstance.post('/api/auth/admin/students/import/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    },
    exportScores: () => {
      return axiosInstance.get('/api/auth/admin/students/export-scores/', {
        responseType: 'blob'
      });
    }
  },
  getTeachers: async (params) => {
    return await axiosInstance.get('/api/auth/admin/list/', { params: { ...params, type: 'teacher' } });
  },
  addUser: async (data) => {
    return await axiosInstance.post('/api/auth/admin/create/', data);
  },
  deleteUser: async (id) => {
    return await axiosInstance.delete(`/api/auth/admin/destroy/${id}/`);
  },
  updateUser: async (id, data) => {
    // 注意：后端API使用POST方法，且将user_id放在请求体中
    return await axiosInstance.post('/api/auth/admin/update/', { ...data, user_id: id });
  },
  // 添加editUser作为updateUser的别名，保持向后兼容
  editUser: async (id, data) => {
    return await axiosInstance.admin.updateUser(id, data);
  },
  importUsers: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return await axiosInstance.post('/api/auth/admin/import-users/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  classes: {
    getClasses: async () => {
      return await axiosInstance.get('/api/auth/admin/classes/');
    },
    getClassDetail: async (classId) => {
      return await axiosInstance.get(`/api/auth/admin/classes/${classId}/`);
    },
    createClass: async (data) => {
      return await axiosInstance.post('/api/auth/admin/classes/', data);
    },
    getClassStudents: async (classId) => {
      return await axiosInstance.get(`/api/auth/admin/classes/${classId}/students/`);
    },
    updateClass: async (classId, data) => {
      return await axiosInstance.put(`/api/auth/admin/classes/${classId}/`, data);
    },
    deleteClass: async (classId) => {
      return await axiosInstance.delete(`/api/auth/admin/classes/delete/${classId}/`);
    }
  },
  classBindings: {
        getClassBindings: async (params) => {
          return await axiosInstance.get('/api/auth/admin/class_bindings/', { params });
        },
        createClassBinding: async (data) => {
          return await axiosInstance.post('/api/auth/admin/class_bindings/', data);
        },
        deleteClassBinding: async (id) => {
          return await axiosInstance.delete(`/api/auth/admin/class_bindings/${id}/`);
        }
      },
      // 教师-学院绑定相关API
      teacherCollegeBindings: {
        getBindings: async (params) => {
          return await axiosInstance.get('/api/auth/admin/teacher_college_bindings/', { params });
        },
        createBinding: async (data) => {
          return await axiosInstance.post('/api/auth/admin/teacher_college_bindings/', data);
        },
        deleteBinding: async (id) => {
          return await axiosInstance.delete(`/api/auth/admin/teacher_college_bindings/${id}/`);
        },
        getTeacherBindings: async (teacherId) => {
          return await axiosInstance.get('/api/auth/admin/teacher_college_bindings/teacher_bindings/', { params: { teacher_id: teacherId } });
        }
      }
};

// 创建并导出api对象，确保所有组件都能正确访问API方法
const api = {
  ...axiosInstance,
  admin: axiosInstance.admin,
  teacher: axiosInstance.teacher,
  student: axiosInstance.student
}

export default api