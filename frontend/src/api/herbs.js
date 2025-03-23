import api from './config'

export const identifyHerb = (formData) => {
  return api.post('/herbs/identify/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 