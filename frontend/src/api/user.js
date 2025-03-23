import request from '@/utils/request'

// 安全获取localStorage数据的方法
const getLocalStorageItem = (key) => {
  try {
    return window.localStorage.getItem(key)
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return null
  }
}

/**
 * 获取用户信息
 * @returns {Promise} 用户信息响应
 */
export function getUserInfo() {
  return request({
    url: '/api/user/info/',
    method: 'get'
  }).catch(error => {
    console.error('获取用户信息失败:', error);
    // 返回一个默认的响应，避免前端崩溃
    return {
      code: 200,
      message: '获取用户信息失败，显示默认值',
      data: {
        username: getLocalStorageItem('username') || '用户',
        email: '',
        create_time: new Date().toISOString(),
        last_login_time: new Date().toISOString(),
        has_face: false,
        avatar: ''
      }
    };
  });
}

/**
 * 更新用户信息
 * @param {Object} data - 用户信息数据
 * @returns {Promise} 更新响应
 */
export function updateUserInfo(data) {
  return request({
    url: '/api/user/info/',
    method: 'put',
    data
  }).catch(error => {
    console.error('更新用户信息失败:', error);
    return {
      code: 500,
      message: '更新用户信息失败，请稍后再试'
    };
  });
}

/**
 * 修改密码
 * @param {Object} data - 密码数据
 * @returns {Promise} 修改密码响应
 */
export function updatePassword(data) {
  return request({
    url: '/api/auth/password/',
    method: 'put',
    data: {
      old_password: data.oldPassword,
      new_password: data.newPassword,
      confirm_password: data.confirmPassword
    }
  }).catch(error => {
    console.error('修改密码失败:', error);
    return {
      code: 500,
      message: '修改密码失败，请稍后再试'
    };
  });
}

/**
 * 上传头像
 * @param {FormData} formData - 包含头像的表单数据
 * @returns {Promise} 上传响应
 */
export function updateAvatar(formData) {
  return request({
    url: '/api/user/avatar/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).catch(error => {
    console.error('上传头像失败:', error);
    return {
      code: 500,
      message: '上传头像失败，请稍后再试'
    };
  });
}

/**
 * 上传人脸照片
 * @param {FormData} formData - 包含人脸照片的表单数据
 * @returns {Promise} 上传响应
 */
export function updateFace(formData) {
  return request({
    url: '/api/user/face/',
    method: 'put',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).catch(error => {
    console.error('上传人脸照片失败:', error);
    return {
      code: 500,
      message: '上传人脸照片失败，请稍后再试'
    };
  });
}

/**
 * 删除人脸数据
 * @returns {Promise} 删除响应
 */
export function deleteFace() {
  return request({
    url: '/api/user/face/',
    method: 'delete'
  }).catch(error => {
    console.error('删除人脸数据失败:', error);
    return {
      code: 500,
      message: '删除人脸数据失败，请稍后再试'
    };
  });
} 