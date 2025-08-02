<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>药店管理系统</h1>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="welcome-card">
              <template #header>
                <div class="card-header">
                  <h2>欢迎使用药店管理系统</h2>
                </div>
              </template>
              <div class="card-content">
                <p>这是一个现代化的药店管理系统，提供以下功能：</p>
                <ul>
                  <li>药品库存管理</li>
                  <li>销售记录管理</li>
                  <li>用户权限管理</li>
                </ul>
                <el-button type="primary" @click="$router.push('/login')">立即登录</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 60px;
}

.welcome-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px;
}

.card-content ul {
  text-align: left;
  margin: 20px 0;
}

.el-button {
  margin-top: 20px;
}
</style> 