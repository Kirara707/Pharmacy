<template>
  <div class="users-container">
    <div class="header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showAddDialog" v-if="canAddUser">
        添加用户
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="users"
      style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色">
        <template #default="scope">
          <el-tag :type="getRoleType(scope.row.role)">
            {{ getRoleName(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" v-if="canEditUser">
        <template #default="scope">
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row)"
            v-if="canDeleteUser(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加用户对话框 -->
    <el-dialog
      title="添加用户"
      v-model="dialogVisible"
      width="500px">
      <el-form
        :model="userForm"
        :rules="rules"
        ref="userFormRef"
        label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="userForm.username" 
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
            clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select 
            v-model="userForm.role" 
            placeholder="请选择角色"
            size="large"
            style="width: 100%">
            <el-option
              v-for="role in availableRoles"
              :key="role.value"
              :label="role.label"
              :value="role.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'Users',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const dialogVisible = ref(false)
    const submitLoading = ref(false)
    const userFormRef = ref(null)
    const userForm = reactive({
      username: '',
      password: '',
      role: ''
    })

    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    }

    const users = computed(() => store.state.users.list)
    const userRole = computed(() => store.state.auth.user?.role)

    const canAddUser = computed(() => {
      return ['admin', 'pharmacy_admin'].includes(userRole.value)
    })

    const canEditUser = computed(() => {
      return ['admin', 'pharmacy_admin'].includes(userRole.value)
    })

    const availableRoles = computed(() => {
      if (userRole.value === 'admin') {
        return [
          { value: 'admin', label: '系统管理员' },
          { value: 'pharmacy_admin', label: '药店管理员' },
          { value: 'salesperson', label: '销售人员' }
        ]
      } else if (userRole.value === 'pharmacy_admin') {
        return [
          { value: 'salesperson', label: '销售人员' }
        ]
      }
      return []
    })

    const getRoleType = (role) => {
      const types = {
        admin: 'danger',
        pharmacy_admin: 'warning',
        salesperson: 'success'
      }
      return types[role] || 'info'
    }

    const getRoleName = (role) => {
      const names = {
        admin: '系统管理员',
        pharmacy_admin: '药店管理员',
        salesperson: '销售人员'
      }
      return names[role] || role
    }

    const canDeleteUser = (user) => {
      if (userRole.value === 'admin') {
        return true
      }
      if (userRole.value === 'pharmacy_admin') {
        return user.role === 'salesperson'
      }
      return false
    }

    const fetchUsers = async () => {
      try {
        loading.value = true
        await store.dispatch('users/fetchUsers')
      } catch (error) {
        ElMessage.error(error.message)
      } finally {
        loading.value = false
      }
    }

    const showAddDialog = () => {
      // 重置表单数据
      Object.assign(userForm, {
        username: '',
        password: '',
        role: ''
      })
      dialogVisible.value = true
      // 清除表单验证
      setTimeout(() => {
        if (userFormRef.value) {
          userFormRef.value.clearValidate()
        }
      }, 100)
    }

    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm('确定要删除这个用户吗？', '警告', {
          type: 'warning'
        })
        
        const token = store.state.auth.token
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
        
        await axios.delete(`http://localhost:5000/api/users/${row.id}`, config)
        ElMessage.success('删除成功')
        fetchUsers()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || '删除失败')
        }
      }
    }

    const handleSubmit = async () => {
      if (!userFormRef.value) return
      
      try {
        // 验证表单
        await userFormRef.value.validate()
        
        submitLoading.value = true
        
        // 设置请求头
        const token = store.state.auth.token
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
        
        await axios.post('http://localhost:5000/api/users', userForm, config)
        ElMessage.success('用户添加成功')
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        console.error('提交错误:', error)
        if (error.response) {
          ElMessage.error(error.response.data?.message || '操作失败')
        } else if (error.message) {
          ElMessage.error(error.message)
        } else {
          ElMessage.error('请检查输入是否正确')
        }
      } finally {
        submitLoading.value = false
      }
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      loading,
      users,
      dialogVisible,
      userForm,
      userFormRef,
      rules,
      canAddUser,
      canEditUser,
      availableRoles,
      getRoleType,
      getRoleName,
      canDeleteUser,
      showAddDialog,
      handleDelete,
      handleSubmit,
      submitLoading,
      User,
      Lock
    }
  }
}
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-input__wrapper) {
  height: 44px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-select .el-input__wrapper) {
  height: 44px;
}

:deep(.el-form-item__error) {
  padding-top: 4px;
}

:deep(.el-input__inner) {
  font-size: 14px;
}
</style> 