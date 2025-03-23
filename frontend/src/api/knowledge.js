import api from './config'

export const getKnowledgeDetail = (category) => {
  return api.get(`/knowledge/${category}/`)
} 