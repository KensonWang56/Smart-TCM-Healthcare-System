import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '', // API的基础URL，留空表示使用相对路径
  timeout: 15000 // 请求超时时间
})

// 是否正在显示网络错误提示
let isShowingNetworkError = false;

// 安全获取localStorage数据的方法
const getLocalStorageItem = (key) => {
  try {
    return window.localStorage.getItem(key)
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return null
  }
}

// 安全移除localStorage数据的方法
const removeLocalStorageItem = (key) => {
  try {
    window.localStorage.removeItem(key)
    return true
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return false
  }
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做一些处理
    const token = getLocalStorageItem('token')
    if (token) {
      // 让每个请求携带token
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    // 处理请求错误
    console.log(error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果状态码不是200，则判断为错误
    if (res.code !== 200 && res.code !== 300) {
      // 避免多次显示相同的错误消息
      if (!isShowingNetworkError) {
        ElMessage({
          message: res.message || '请求错误',
          type: 'error',
          duration: 5 * 1000,
          onClose: () => {
            isShowingNetworkError = false;
          }
        })
        isShowingNetworkError = true;
      }
      
      // 未授权，需要重新登录
      if (res.code === 401 || res.code === 403) {
        // 可以在这里处理登出和重新登录逻辑
        removeLocalStorageItem('token')
        removeLocalStorageItem('username')
        
        // 延迟跳转，避免同时触发多个跳转
        setTimeout(() => {
          window.location.href = '/login'
        }, 500);
      }
      
      return Promise.reject(new Error(res.message || '请求错误'))
    } else {
      return res
    }
  },
  error => {
    console.log('请求错误', error)
    let message = error.message
    
    // 检查是否有响应，如果没有响应说明是网络问题
    if (!error.response) {
      if (error.message.includes('timeout')) {
        message = '请求超时，请检查网络连接'
      } else if (error.message.includes('Network Error')) {
        message = '网络错误，请检查网络连接'
      } else {
        message = '无法连接到服务器，请稍后再试'
      }
      
      // 避免频繁显示网络错误
      if (!isShowingNetworkError) {
        ElMessage({
          message: message,
          type: 'error',
          duration: 5 * 1000,
          onClose: () => {
            isShowingNetworkError = false;
          }
        })
        isShowingNetworkError = true;
      }
      
      // 对于网络错误，我们返回一个特殊的对象，而不是reject
      return Promise.resolve({
        code: 500,
        message: message,
        data: null
      });
    }
    
    // 对于有响应的错误，我们可以根据状态码处理
    if (error.response) {
      // 处理400错误，通常包含表单验证错误
      if (error.response.status === 400) {
        // 尝试获取后端返回的错误详情
        const responseData = error.response.data;
        
        // 返回结构化的错误对象
        return Promise.resolve({
          code: 400,
          message: responseData.message || '请求参数错误',
          errors: responseData.errors || {}
        });
      }
      
      // 处理401错误，通常是登录认证失败
      if (error.response.status === 401) {
        const responseData = error.response.data;
        // 获取请求路径
        const url = error.config.url;
        
        // 如果是登录请求，不需要跳转，只需要显示错误信息
        if (url && (url.includes('/api/auth/login/') || url.includes('/api/auth/register/'))) {
          return Promise.resolve({
            code: 401,
            message: responseData.message || '用户名或密码错误',
            errors: responseData.errors || {}
          });
        }
        
        // 其他请求的401错误，表示token过期或无效，需要重新登录
        message = '未授权，请重新登录'
        removeLocalStorageItem('token')
        removeLocalStorageItem('username')
        
        setTimeout(() => {
          window.location.href = '/login'
        }, 500);
      } else {
        switch (error.response.status) {
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
            message = `连接错误 ${error.response.status}`
        }
      }
      
      // 避免频繁显示网络错误
      if (!isShowingNetworkError) {
        ElMessage({
          message: message,
          type: 'error',
          duration: 5 * 1000,
          onClose: () => {
            isShowingNetworkError = false;
          }
        })
        isShowingNetworkError = true;
      }
    }
    
    return Promise.reject(error)
  }
)

export default service 