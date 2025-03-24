import api from './config'

export const analyzeTongue = async (formData) => {
  try {
    console.log('Sending request to analyze tongue...')
    const response = await api.post('/tongue/analyze/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000
    })
    
    console.log('Raw response:', response)
    
    // 检查响应格式
    if (!response) {
      throw new Error('服务器响应为空')
    }
    
    // 根据实际返回结构处理数据
    const data = response.data || response
    console.log('Processed data:', data)
    
    // 返回处理后的数据
    return data
    
  } catch (error) {
    console.error('API Error:', error)
    if (error.response && error.response.data) {
      throw error.response.data.error || error.response.data || '服务器错误'
    }
    throw error.message || '分析请求失败'
  }
} 