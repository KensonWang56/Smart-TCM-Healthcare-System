import api from './config'

export const sendMessage = (message) => {
  return api.post('/chat/message/', { message })
}