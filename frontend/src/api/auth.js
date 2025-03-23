import request from '@/utils/request'

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @returns {Promise} 登录响应
 */
export function login(data) {
  return request({
    url: '/api/auth/login/',
    method: 'post',
    data
  })
}

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @returns {Promise} 注册响应
 */
export function register(data) {
  return request({
    url: '/api/auth/register/',
    method: 'post',
    data: {
      username: data.username,
      email: data.email,
      password: data.password,
      confirm_password: data.confirmPassword
    }
  })
}

/**
 * 人脸登录
 * @param {FormData} formData - 包含人脸图像的表单数据
 * @returns {Promise} 登录响应
 */
export function faceLogin(formData) {
  return request({
    url: '/api/auth/face-login/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).catch(error => {
    console.error('人脸登录请求失败:', error);
    
    // 记录详细的错误信息
    if (error.response) {
      console.log('错误响应状态:', error.response.status);
      console.log('错误响应数据:', error.response.data);
    }
    
    // 如果有响应数据，处理并返回错误响应
    if (error.response && error.response.data) {
      // 确保保留原始错误码和消息
      const errorData = error.response.data;
      // 如果后端返回的是字符串消息，转为对象格式
      if (typeof errorData === 'string') {
        return {
          code: error.response.status,
          message: errorData
        };
      }
      // 如果后端没有返回code，使用HTTP状态码
      if (!errorData.code) {
        errorData.code = error.response.status;
      }
      return errorData;
    }
    
    // 否则构造一个错误响应
    return {
      code: 500,
      message: error.message || '人脸登录失败，请稍后再试'
    };
  });
}

/**
 * 退出登录
 * @returns {Promise} 退出登录响应
 */
export function logout() {
  return request({
    url: '/api/auth/logout/',
    method: 'post'
  })
}

export const getUserInfo = () => {
  return request({
    url: '/api/auth/user/',
    method: 'get'
  })
} 