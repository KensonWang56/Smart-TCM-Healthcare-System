import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 1000000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 对于特定的接口，返回完整响应
    if (response.config.url.includes('/tongue/analyze/')) {
      console.log('舌苔分析接口原始响应:', response);
      // 尝试解析响应
      try {
        if (response.data) {
          return response.data;
        }
      } catch (e) {
        console.error('解析舌苔分析响应错误:', e);
      }
      return response;
    }
    
    // 其他接口返回data部分
    return response.data
  },
  error => {
    let message = '未知错误'
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = error.response.data.error || '请求参数错误'
          break
        case 401:
          message = error.response.data.error || '未授权，请重新登录'
          localStorage.removeItem('token')
          localStorage.removeItem('username')
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data.error || '未知错误'
      }
    } else if (error.request) {
      message = '服务器无响应'
    } else {
      message = error.message
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api 