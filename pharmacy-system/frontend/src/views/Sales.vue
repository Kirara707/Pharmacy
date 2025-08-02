<template>
  <div class="sales-container">
    <div class="header">
      <h2>销售记录</h2>
      <el-button type="primary" @click="showAddDialog" v-if="canAddSale">
        新增销售记录
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="sales"
      style="width: 100%">
      <el-table-column prop="id" label="记录ID" width="100" />
      <el-table-column prop="medicine_name" label="药品名称" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column prop="total_price" label="总价">
        <template #default="scope">
          ¥{{ scope.row.total_price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="销售时间">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" v-if="canEditSale">
        <template #default="scope">
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加销售记录对话框 -->
    <el-dialog
      title="新增销售记录"
      v-model="dialogVisible"
      width="500px">
      <el-form
        :model="saleForm"
        :rules="rules"
        ref="saleFormRef"
        label-width="100px">
        <el-form-item label="药品" prop="medicine_id">
          <el-select
            v-model="saleForm.medicine_id"
            placeholder="请选择药品"
            style="width: 100%"
            filterable
            clearable>
            <el-option
              v-for="medicine in medicines"
              :key="medicine.id"
              :label="medicine.name"
              :value="medicine.id"
              :disabled="medicine.stock === 0">
              <span>{{ medicine.name }}</span>
              <span style="float: right; font-size: 13px" 
                    :style="{ color: medicine.stock > 0 ? '#67C23A' : '#F56C6C' }">
                库存: {{ medicine.stock }}{{ medicine.stock === 0 ? ' (缺货)' : '' }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number
            v-model="saleForm.quantity"
            :min="1"
            :max="Math.max(1, getMaxQuantity)"
            :precision="0"
            :disabled="!selectedMedicine || getMaxQuantity === 0"
            style="width: 100%"
            :placeholder="selectedMedicine ? '请输入销售数量' : '请先选择药品'" />
          <div v-if="!selectedMedicine" style="color: #909399; font-size: 12px; margin-top: 4px;">
            请先选择要销售的药品
          </div>
          <div v-else-if="getMaxQuantity === 0" style="color: #F56C6C; font-size: 12px; margin-top: 4px;">
            该药品库存不足，无法销售
          </div>
        </el-form-item>
        <el-form-item label="库存信息" v-if="selectedMedicine">
          <div style="margin-bottom: 8px;">
            <span style="color: #909399;">当前库存: </span>
            <span :style="{ color: getMaxQuantity > 0 ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
              {{ getMaxQuantity }} 件
            </span>
          </div>
        </el-form-item>
        <el-form-item label="预计总价" v-if="selectedMedicine && saleForm.quantity > 0">
          <div style="font-size: 16px; color: #409EFF; font-weight: bold;">
            ¥{{ (selectedMedicine.price * saleForm.quantity).toFixed(2) }}
          </div>
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
import axios from 'axios'

export default {
  name: 'Sales',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const dialogVisible = ref(false)
    const submitLoading = ref(false)
    const saleFormRef = ref(null)
    const saleForm = reactive({
      medicine_id: '',
      quantity: 1
    })

    const rules = {
      medicine_id: [
        { required: true, message: '请选择药品', trigger: 'change' }
      ],
      quantity: [
        { required: true, message: '请输入数量', trigger: 'blur' },
        { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }
      ]
    }

    const sales = computed(() => store.state.sales.list)
    const medicines = computed(() => store.state.medicines.list)
    const userRole = computed(() => store.state.auth.user?.role)

    const canAddSale = computed(() => {
      return ['admin', 'salesperson', 'pharmacy_admin'].includes(userRole.value)
    })

    const canEditSale = computed(() => {
      return ['admin', 'salesperson', 'pharmacy_admin'].includes(userRole.value)
    })

    const selectedMedicine = computed(() => {
      return medicines.value.find(m => m.id === saleForm.medicine_id)
    })

    const getMaxQuantity = computed(() => {
      return selectedMedicine.value ? selectedMedicine.value.stock : 0
    })

    const fetchSales = async () => {
      try {
        loading.value = true
        await store.dispatch('sales/fetchSales')
      } catch (error) {
        ElMessage.error(error.message)
      } finally {
        loading.value = false
      }
    }

    const fetchMedicines = async () => {
      try {
        await store.dispatch('medicines/fetchMedicines')
      } catch (error) {
        ElMessage.error(error.message)
      }
    }

    const showAddDialog = () => {
      console.log('显示添加销售记录对话框')
      console.log('当前用户角色:', userRole.value)
      console.log('可添加销售记录:', canAddSale.value)
      console.log('药品列表:', medicines.value)
      
      // 重置表单数据
      Object.assign(saleForm, {
        medicine_id: '',
        quantity: 1
      })
      dialogVisible.value = true
      // 清除表单验证
      setTimeout(() => {
        if (saleFormRef.value) {
          saleFormRef.value.clearValidate()
        }
      }, 100)
    }

    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm('确定要删除这条销售记录吗？删除后将恢复对应的药品库存。', '警告', {
          type: 'warning'
        })
        
        const token = store.state.auth.token
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
        
        await axios.delete(`http://localhost:5000/api/sales/${row.id}`, config)
        ElMessage.success('删除成功，库存已恢复')
        fetchSales()
        fetchMedicines() // 刷新药品库存
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || '删除失败')
        }
      }
    }

    const handleSubmit = async () => {
      if (!saleFormRef.value) {
        ElMessage.error('表单引用不存在')
        return
      }
      
      try {
        // 验证表单
        await saleFormRef.value.validate()
        
        // 检查必要数据
        if (!saleForm.medicine_id) {
          ElMessage.error('请选择药品')
          return
        }
        
        if (!saleForm.quantity || saleForm.quantity <= 0) {
          ElMessage.error('请输入有效的数量')
          return
        }
        
        console.log('提交销售记录:', saleForm)
        submitLoading.value = true
        
        // 设置请求头
        const token = store.state.auth.token
        if (!token) {
          ElMessage.error('用户未登录')
          return
        }
        
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
        
        const response = await axios.post('http://localhost:5000/api/sales', saleForm, config)
        console.log('销售记录创建响应:', response.data)
        
        ElMessage.success('销售记录添加成功')
        dialogVisible.value = false
        await fetchSales()
        await fetchMedicines() // 刷新药品库存
      } catch (error) {
        console.error('提交错误:', error)
        if (error.response) {
          console.error('错误响应:', error.response.data)
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
      fetchSales()
      fetchMedicines()
    })

    return {
      loading,
      sales,
      medicines,
      dialogVisible,
      saleForm,
      saleFormRef,
      rules,
      canAddSale,
      canEditSale,
      selectedMedicine,
      getMaxQuantity,
      showAddDialog,
      handleDelete,
      handleSubmit,
      submitLoading
    }
  }
}
</script>

<style scoped>
.sales-container {
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

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-form-item__error) {
  padding-top: 4px;
}

:deep(.el-select-dropdown__item.is-disabled) {
  color: #c0c4cc;
  cursor: not-allowed;
}
</style> 