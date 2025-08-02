import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.headers.common['Authorization'] = `Bearer ${localStorage.getItem('token')}`

const app = createApp(App)

app.use(ElementPlus)
app.use(router)
app.use(store)

app.mount('#app') 