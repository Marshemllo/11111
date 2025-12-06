import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          // 登录过期只显示提示，不自动跳转
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          // 权限不足只显示提示，不跳转
          ElMessage.error('权限不足，无法访问该功能')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 405:
          ElMessage.error('请求方法不允许')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        case 501:
          ElMessage.warning('该功能正在开发中，敬请期待')
          break
        default:
          ElMessage.error(response.data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    
    return Promise.reject(error)
  }
)

export default request
