# 学生综合素质加分系统

## 项目简介

学生综合素质加分系统是一个用于管理和计算学生综合素质加分的Web应用，支持学生提交申请、教师审批、管理员管理等功能，旨在提高学生综合素质评价的公平性和透明度。

## 功能特性

### 学生端
- 查看个人信息和当前总分数
- 查看各分类加分详情（科研成果、学业竞赛、创新创业等）
- 查看审核通过的加分项目
- 提交加分申请
- 查看申请状态和审批进度

### 教师端
- 查看待审批申请列表
- 审批学生提交的加分申请
- 查看已审批申请记录
- 查看学生加分统计信息

### 管理员端
- 管理学生信息
- 管理教师信息
- 管理学院和班级信息
- 管理申请类型和加分规则
- 查看系统统计信息

## 技术栈

### 前端
- Vue 3 + Composition API
- Ant Design Vue
- Axios
- Vite

### 后端
- Django 4.x
- Django REST Framework
- MySQL
- Redis

## 安装部署

### 前端部署

1. 克隆项目
```bash
git clone <repository-url>
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env
# 修改.env文件中的配置
```

4. 启动开发服务器
```bash
npm run dev
```

5. 构建生产版本
```bash
npm run build
```

### 后端部署

1. 克隆项目
```bash
git clone <repository-url>
cd team_back
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
```bash
# 修改settings.py中的数据库配置
```

4. 执行数据库迁移
```bash
python manage.py migrate
```

5. 创建超级管理员
```bash
python xmu_app/create_superuser.py
```

6. 启动开发服务器
```bash
python manage.py runserver 0.0.0.0:8000
```

## 项目结构

### 前端项目结构
```
frontend/
├── public/              # 静态资源
├── src/                 # 源代码
│   ├── assets/          # 资源文件
│   ├── components/      # 组件
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── router/          # 路由配置
│   ├── store/           # 状态管理
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── .env.example         # 环境变量模板
├── vite.config.js       # Vite配置
└── package.json         # 项目依赖
```

### 后端项目结构
```
team_back/
├── xmu_app/             # 主应用
├── material/            # 材料申请模块
├── score/               # 分数计算模块
├── user/                # 用户管理模块
├── settings.py          # 项目配置
├── urls.py              # 路由配置
└── manage.py            # 管理脚本
```

## 使用说明

### 学生提交加分申请
1. 登录学生端系统
2. 点击"提交申请"按钮
3. 选择申请类型
4. 填写申请信息并上传相关材料
5. 提交申请

### 教师审批加分申请
1. 登录教师端系统
2. 查看待审批申请列表
3. 点击申请详情，查看申请信息和材料
4. 输入审批分数和审批意见
5. 点击"通过"或"拒绝"按钮完成审批

### 管理员管理系统
1. 登录管理员端系统
2. 管理学生、教师、学院和班级信息
3. 配置申请类型和加分规则
4. 查看系统统计信息

## 开发指南

### 前端开发
1. 安装依赖
```bash
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 代码风格检查
```bash
npm run lint
```

### 后端开发
1. 安装依赖
```bash
cd team_back
pip install -r requirements.txt
```

2. 启动开发服务器
```bash
python manage.py runserver
```

3. 创建超级管理员
```bash
python xmu_app/create_superuser.py
```

4. 执行测试
```bash
python manage.py test
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
```bash
git checkout -b feature/your-feature
```

3. 提交更改
```bash
git commit -m 'Add some feature'
```

4. 推送到分支
```bash
git push origin feature/your-feature
```

5. 提交 Pull Request

