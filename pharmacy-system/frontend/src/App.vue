<template>
  <div id="app">
    <el-container v-if="isLoggedIn">
      <el-aside width="200px">
        <el-menu
          :router="true"
          :default-active="$route.path"
          class="el-menu-vertical">
          <el-menu-item index="/dashboard">
            <el-icon><el-icon-menu /></el-icon>
            <span>概况</span>
          </el-menu-item>
          <el-menu-item index="/medicines" v-if="canAccessMedicines">
            <el-icon><el-icon-medicine-box /></el-icon>
            <span>药品管理</span>
          </el-menu-item>
          <el-menu-item index="/sales" v-if="canAccessSales">
            <el-icon><el-icon-shopping-cart /></el-icon>
            <span>销售记录</span>
          </el-menu-item>
          <el-menu-item index="/users" v-if="canAccessUsers">
            <el-icon><el-icon-user /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-content">
            <h2>药店管理系统</h2>
            <el-button type="danger" @click="logout">退出登录</el-button>
          </div>
        </el-header>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
    <router-view v-else></router-view>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    const router = useRouter()

    const isLoggedIn = computed(() => store.state.auth.token)
    const userRole = computed(() => store.state.auth.user?.role)

    const canAccessMedicines = computed(() => {
      return ['admin', 'pharmacy_admin', 'salesperson'].includes(userRole.value)
    })

    const canAccessSales = computed(() => {
      return ['admin', 'pharmacy_admin', 'salesperson'].includes(userRole.value)
    })

    const canAccessUsers = computed(() => {
      return ['admin', 'pharmacy_admin'].includes(userRole.value)
    })

    const logout = () => {
      store.dispatch('auth/logout')
      router.push('/login')
    }

    return {
      isLoggedIn,
      canAccessMedicines,
      canAccessSales,
      canAccessUsers,
      logout
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-aside {
  background-color: #545c64;
}

.el-menu {
  border-right: none;
}
</style> 