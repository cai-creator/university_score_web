import { createRouter, createWebHistory } from 'vue-router'
import { message } from 'ant-design-vue'

// 路由配置
const routes = [
  // 公共路由
  {
    path: '/',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  // 学生端路由
  {
    path: '/student',
    name: 'StudentLayout',
    component: () => import('../layouts/StudentLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: 'home',
        name: 'StudentHome',
        component: () => import('../views/student/Home.vue')
      },
      {
        path: 'applications',
        name: 'StudentApplications',
        component: () => import('../views/student/MyApplications.vue')
      },
      {
        path: 'add-application',
        name: 'AddApplication',
        component: () => import('../views/student/UploadMaterial.vue')
      },

      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('../views/student/Profile.vue')
      }
    ]
  },
  // 教师端路由
  {
    path: '/teacher',
    name: 'TeacherLayout',
    component: () => import('../layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      {
        path: 'home',
        name: 'TeacherHome',
        component: () => import('../views/teacher/Home.vue')
      },
      {
        path: 'applications',
        name: 'TeacherApplications',
        component: () => import('../views/teacher/Applications.vue')
      },
      {
        path: 'students',
        name: 'TeacherStudents',
        component: () => import('../views/teacher/Students.vue')
      },
      {
        path: 'export-excel',
        name: 'ExportExcel',
        component: () => import('../views/teacher/ExportExcel.vue')
      },
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: () => import('../views/teacher/Profile.vue')
      }
    ]
  },
  // 超管端路由
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'home',
        name: 'AdminHome',
        component: () => import('../views/admin/AdminHome.vue')
      },
      {
        path: 'colleges',
        name: 'AdminColleges',
        component: () => import('../views/admin/Colleges.vue')
      },
      {
        path: 'accounts',
        name: 'AdminAccounts',
        redirect: '/admin/accounts/all',
        children: [
          {
            path: 'students',
            name: 'AdminStudents',
            component: () => import('../views/admin/Students.vue')
          },
          {
            path: 'teachers',
            name: 'AdminTeachers',
            component: () => import('../views/admin/Teachers.vue')
          },
          {
            path: 'all',
            name: 'AdminUsers',
            component: () => import('../views/admin/Users.vue')
          }
        ]
      },
      {
        path: 'classes',
        name: 'AdminClasses',
        component: () => import('../views/admin/Classes.vue')
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/admin/Settings.vue')
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  try {
    // 获取当前用户信息 - 增加错误处理
    let user = null
    const userStr = localStorage.getItem('user')
    if (userStr) {
      user = JSON.parse(userStr)
    }
    
    // 检查是否需要认证
    if (to.meta.requiresAuth) {
      if (!user) {
        message.error('请先登录')
        next({ name: 'Login' })
        return
      }
      
      // 为了兼容性，同时支持role和user_type字段
      // 处理数字类型的用户类型(0/1/2)转换为字符串类型
      const userTypeMap = {
        0: 'student',
        1: 'teacher', 
        2: 'admin'
      }
      
      let userRole = user.role || user.user_type
      // 如果是数字类型，进行转换
      if (typeof userRole === 'number') {
        userRole = userTypeMap[userRole] || userRole
      }
      
      // 检查用户角色
      if (to.meta.role && userRole !== to.meta.role) {
        message.error('没有权限访问该页面')
        // 根据用户角色重定向到对应首页
        if (userRole === 'student') {
          next({ name: 'StudentHome' })
        } else if (userRole === 'teacher') {
          next({ name: 'TeacherHome' })
        } else if (userRole === 'admin') {
          next({ name: 'AdminHome' })
        }
        return
      }
    }
    
    next()
  } catch (error) {
    console.error('路由守卫错误:', error)
    // 清除可能损坏的本地存储
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    // 重定向到登录页
    next({ name: 'Login' })
  }
})

export default router