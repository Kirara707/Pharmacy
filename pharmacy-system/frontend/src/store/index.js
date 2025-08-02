import { createStore } from 'vuex'
import axios from 'axios'
import router from '../router'

const store = createStore({
  modules: {
    auth: {
      namespaced: true,
      state: {
        token: localStorage.getItem('token') || null,
        user: JSON.parse(localStorage.getItem('user')) || null
      },
      mutations: {
        SET_TOKEN(state, token) {
          state.token = token
          localStorage.setItem('token', token)
        },
        SET_USER(state, user) {
          state.user = user
          localStorage.setItem('user', JSON.stringify(user))
        },
        CLEAR_AUTH(state) {
          state.token = null
          state.user = null
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        }
      },
      actions: {
        async login({ commit }, credentials) {
          try {
            if (!credentials.username || !credentials.password) {
              throw new Error('请提供用户名和密码')
            }

            const response = await axios.post('http://localhost:5000/api/login', {
              username: credentials.username.trim(),
              password: credentials.password
            })

            const { access_token, user } = response.data
            if (!access_token || !user) {
              throw new Error('登录响应数据格式错误')
            }

            commit('SET_TOKEN', access_token)
            commit('SET_USER', user)
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          } catch (error) {
            if (error.response) {
              // 服务器返回错误响应
              const message = error.response.data?.message || '登录失败'
              throw new Error(message)
            } else if (error.request) {
              // 请求发送失败
              throw new Error('无法连接到服务器，请检查网络连接')
            } else {
              // 其他错误
              throw error
            }
          }
        },
        logout({ commit }) {
          commit('CLEAR_AUTH')
          delete axios.defaults.headers.common['Authorization']
        }
      }
    },
    medicines: {
      namespaced: true,
      state: {
        list: [],
        loading: false
      },
      mutations: {
        SET_MEDICINES(state, medicines) {
          state.list = medicines
        },
        SET_LOADING(state, loading) {
          state.loading = loading
        }
      },
      actions: {
        async fetchMedicines({ commit }) {
          commit('SET_LOADING', true)
          try {
            const response = await axios.get('http://localhost:5000/api/medicines')
            commit('SET_MEDICINES', response.data)
          } catch (error) {
            if (error.response?.status === 401) {
              store.dispatch('auth/logout')
              router.push('/login')
            }
            throw new Error(error.response?.data?.message || '获取药品列表失败')
          } finally {
            commit('SET_LOADING', false)
          }
        }
      }
    },
    sales: {
      namespaced: true,
      state: {
        list: [],
        loading: false
      },
      mutations: {
        SET_SALES(state, sales) {
          state.list = sales
        },
        SET_LOADING(state, loading) {
          state.loading = loading
        }
      },
      actions: {
        async fetchSales({ commit }) {
          commit('SET_LOADING', true)
          try {
            const response = await axios.get('http://localhost:5000/api/sales')
            commit('SET_SALES', response.data)
          } catch (error) {
            if (error.response?.status === 401) {
              store.dispatch('auth/logout')
              router.push('/login')
            }
            throw new Error(error.response?.data?.message || '获取销售记录失败')
          } finally {
            commit('SET_LOADING', false)
          }
        }
      }
    },
    users: {
      namespaced: true,
      state: {
        list: [],
        loading: false
      },
      mutations: {
        SET_USERS(state, users) {
          state.list = users
        },
        SET_LOADING(state, loading) {
          state.loading = loading
        }
      },
      actions: {
        async fetchUsers({ commit }) {
          commit('SET_LOADING', true)
          try {
            const response = await axios.get('http://localhost:5000/api/users')
            commit('SET_USERS', response.data)
          } catch (error) {
            if (error.response?.status === 401) {
              store.dispatch('auth/logout')
              router.push('/login')
            }
            throw new Error(error.response?.data?.message || '获取用户列表失败')
          } finally {
            commit('SET_LOADING', false)
          }
        }
      }
    }
  }
})

export default store 