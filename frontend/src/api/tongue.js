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
    
    if (!response) {
      throw new Error('服务器响应数据格式错误')
    }
    
    // 直接返回响应数据
    return response
    
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
} 