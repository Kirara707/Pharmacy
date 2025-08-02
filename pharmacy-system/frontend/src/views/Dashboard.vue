<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>药品总数</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ medicines.length }}</h2>
            <p>种药品</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>今日销售额</span>
            </div>
          </template>
          <div class="card-content">
            <h2>¥{{ todaySales.toFixed(2) }}</h2>
            <p>元</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>库存预警</span>
            </div>
          </template>
          <div class="card-content">
            <h2>{{ lowStockCount }}</h2>
            <p>种药品库存不足</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>最近销售记录</span>
            </div>
          </template>
          <el-table :data="recentSales" style="width: 100%">
            <el-table-column prop="medicine.name" label="药品名称" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="total_price" label="金额" width="120">
              <template #default="scope">
                ¥{{ scope.row.total_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>库存预警药品</span>
            </div>
          </template>
          <el-table :data="lowStockMedicines" style="width: 100%">
            <el-table-column prop="name" label="药品名称" />
            <el-table-column prop="stock" label="当前库存" width="100" />
            <el-table-column prop="price" label="单价" width="120">
              <template #default="scope">
                ¥{{ scope.row.price.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const medicines = computed(() => store.state.medicines.list)
    const sales = computed(() => store.state.sales.list)

    const todaySales = computed(() => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return sales.value
        .filter(sale => new Date(sale.created_at) >= today)
        .reduce((sum, sale) => sum + sale.total_price, 0)
    })

    const lowStockMedicines = computed(() => {
      return medicines.value.filter(medicine => medicine.stock < 10)
    })

    const lowStockCount = computed(() => {
      return lowStockMedicines.value.length
    })

    const recentSales = computed(() => {
      return [...sales.value]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5)
    })

    onMounted(async () => {
      await Promise.all([
        store.dispatch('medicines/fetchMedicines'),
        store.dispatch('sales/fetchSales')
      ])
    })

    return {
      medicines,
      todaySales,
      lowStockMedicines,
      lowStockCount,
      recentSales
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.card-content h2 {
  font-size: 28px;
  margin: 0;
  color: #409EFF;
}

.card-content p {
  margin: 10px 0 0;
  color: #909399;
}
</style> 