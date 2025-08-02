<template>
  <div class="medicines-container">
    <div class="header">
      <h2>药品管理</h2>
      <el-button type="primary" @click="showAddDialog" v-if="canAddMedicine">
        <el-icon><el-icon-plus /></el-icon> 添加药品
      </el-button>
      <el-input v-model="search" placeholder="搜索药品名称" style="width: 240px; margin-left: 20px;" clearable @input="filterMedicines" />
    </div>
    <el-table
      v-loading="loading"
      :data="filteredMedicines"
      style="width: 100%">
      <el-table-column prop="name" label="药品名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="price" label="价格">
        <template #default="scope">
          ¥{{ scope.row.price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" />
      <el-table-column prop="manufacturer" label="生产厂家" />
      <el-table-column label="操作" width="180" v-if="canEditMedicine">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)"><el-icon><el-icon-edit /></el-icon> 编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)"><el-icon><el-icon-delete /></el-icon> 删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
      <el-form :model="medicineForm" :rules="rules" ref="medicineFormRef" label-width="100px">
        <el-form-item label="药品名称" prop="name">
          <el-input v-model="medicineForm.name" placeholder="请输入药品名称" clearable />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="medicineForm.description" placeholder="请输入药品描述" :rows="3" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="medicineForm.price" :precision="2" :step="0.1" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="medicineForm.stock" :min="0" :precision="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生产厂家" prop="manufacturer">
          <el-input v-model="medicineForm.manufacturer" placeholder="请输入生产厂家" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

export default {
  name: 'Medicines',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const submitLoading = ref(false)
    const search = ref('')
    const medicineForm = ref({
      name: '',
      description: '',
      price: 0,
      stock: 0,
      manufacturer: ''
    })

    const rules = {
      name: [
        { required: true, message: '请输入药品名称', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入描述', trigger: 'blur' }
      ],
      price: [
        { required: true, message: '请输入价格', trigger: 'blur' }
      ],
      stock: [
        { required: true, message: '请输入库存', trigger: 'blur' }
      ],
      manufacturer: [
        { required: true, message: '请输入生产厂家', trigger: 'blur' }
      ]
    }

    const medicines = computed(() => store.state.medicines.list)
    const filteredMedicines = ref([])
    const userRole = computed(() => store.state.auth.user?.role)

    const canAddMedicine = computed(() => {
      return ['admin', 'pharmacy_admin'].includes(userRole.value)
    })

    const canEditMedicine = computed(() => {
      return ['admin', 'pharmacy_admin'].includes(userRole.value)
    })

    const dialogTitle = computed(() => {
      return isEdit.value ? '编辑药品' : '添加药品'
    })

    const filterMedicines = () => {
      if (!search.value) {
        filteredMedicines.value = medicines.value
      } else {
        filteredMedicines.value = medicines.value.filter(m => m.name.includes(search.value))
      }
    }

    const fetchMedicines = async () => {
      try {
        loading.value = true
        await store.dispatch('medicines/fetchMedicines')
        filterMedicines()
      } catch (error) {
        ElMessage.error(error.message)
      } finally {
        loading.value = false
      }
    }

    const showAddDialog = () => {
      isEdit.value = false
      medicineForm.value = {
        name: '',
        description: '',
        price: 0,
        stock: 0,
        manufacturer: ''
      }
      dialogVisible.value = true
    }

    const handleEdit = (row) => {
      isEdit.value = true
      medicineForm.value = { ...row }
      dialogVisible.value = true
    }

    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm('确定要删除这个药品吗？', '警告', {
          type: 'warning'
        })
        await axios.delete(`http://localhost:5000/api/medicines/${row.id}`)
        ElMessage.success('删除成功')
        fetchMedicines()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || '删除失败')
        }
      }
    }

    const medicineFormRef = ref(null)

    const handleSubmit = async () => {
      if (!medicineFormRef.value) return
      
      try {
        // 验证表单
        const isValid = await medicineFormRef.value.validate()
        if (!isValid) return
        
        submitLoading.value = true
        
        // 设置请求头
        const token = store.state.auth.token
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
        
        if (isEdit.value) {
          await axios.put(`http://localhost:5000/api/medicines/${medicineForm.value.id}`, medicineForm.value, config)
          ElMessage.success('更新成功')
        } else {
          await axios.post('http://localhost:5000/api/medicines', medicineForm.value, config)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchMedicines()
      } catch (error) {
        console.error('提交错误:', error)
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitLoading.value = false
      }
    }

    onMounted(() => {
      fetchMedicines()
    })

    return {
      loading,
      medicines,
      filteredMedicines,
      dialogVisible,
      dialogTitle,
      medicineForm,
      medicineFormRef,
      rules,
      canAddMedicine,
      canEditMedicine,
      showAddDialog,
      handleEdit,
      handleDelete,
      handleSubmit,
      submitLoading,
      search,
      filterMedicines
    }
  }
}
</script>

<style scoped>
.medicines-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 