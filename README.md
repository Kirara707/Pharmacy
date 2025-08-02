# 药店管理系统

这是一个基于Vue.js和Flask的药店管理系统，用于管理药品、销售记录和用户。

## 技术栈

### 前端
- Vue.js 3
- Element Plus
- Vuex
- Vue Router
- Axios

### 后端
- Python Flask
- SQLAlchemy
- JWT认证
- openGauss数据库

## 功能特性

- 用户认证和授权
- 药品管理（增删改查）
- 销售记录管理
- 库存管理
- 用户管理
- 数据统计和展示

## 安装和运行

### 1. 启动数据库

```bash
docker run --name opengauss --privileged=true -d -e GS_PASSWORD=Lzw20050815@ -p 8888:5432 opengauss/opengauss-server:latest
```

### 2. 后端设置

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. 前端设置

```bash
cd frontend
npm install
npm run serve
```

## 访问系统

前端应用将在 http://localhost:8080 运行
后端API将在 http://localhost:5000 运行

## 默认用户

系统初始化时会创建一个管理员账户：
- 用户名：admin
- 密码：admin123

## 权限说明

### 系统管理员（admin）
- 可以管理所有用户
- 可以管理所有药品
- 可以管理所有销售记录

### 药店管理员（pharmacy_admin）
- 可以管理销售人员
- 可以管理药品
- 可以查看销售记录

### 销售人员（salesperson）
- 可以查看药品信息
- 可以管理销售记录

## 开发说明

### 目录结构

```
pharmacy-system/
├── backend/
│   ├── app.py
│   ├── models.py
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   ├── views/
    │   ├── store/
    │   ├── router/
    │   ├── App.vue
    │   └── main.js
    └── package.json
```

### API文档

#### 认证
- POST /api/login - 用户登录

#### 用户管理
- GET /api/users - 获取用户列表
- POST /api/users - 创建新用户
- DELETE /api/users/:id - 删除用户

#### 药品管理
- GET /api/medicines - 获取药品列表
- POST /api/medicines - 添加新药品
- PUT /api/medicines/:id - 更新药品信息
- DELETE /api/medicines/:id - 删除药品

#### 销售记录
- GET /api/sales - 获取销售记录
- POST /api/sales - 创建销售记录
- DELETE /api/sales/:id - 删除销售记录 
