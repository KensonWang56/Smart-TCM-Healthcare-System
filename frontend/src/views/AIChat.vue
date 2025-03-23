<template>
  <div class="ai-chat">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="menu-card">
          <template #header>
            <div class="card-header">
              <h3>常见症状</h3>
            </div>
          </template>
          <el-menu
            class="symptoms-menu"
            @select="handleSymptomSelect">
            <el-menu-item 
              v-for="symptom in commonSymptoms" 
              :key="symptom.value"
              :index="symptom.value">
              {{ symptom.label }}
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card class="chat-card">
          <template #header>
            <div class="card-header">
              <h3>智能问诊</h3>
            </div>
          </template>
          <div class="chat-container" ref="chatContainer">
            <div 
              v-for="(message, index) in chatMessages" 
              :key="index"
              :class="['message', message.role]">
              <el-avatar 
                :size="40"
                :src="message.role === 'user' ? userAvatar : doctorAvatar" />
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>
            <div v-if="isLoading" class="message assistant loading">
              <el-avatar :size="40" :src="doctorAvatar" />
              <div class="message-content">
                <div class="message-text">
                  <span class="loading-dots">
                    <i></i><i></i><i></i>
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="input-area">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="3"
              placeholder="请描述您的症状或健康问题..."
              @keyup.enter.prevent="handleSendMessage"
              :disabled="isLoading" />
            <div class="button-group">
              <el-button 
                type="primary" 
                @click="handleSendMessage" 
                :disabled="!userInput.trim() || isLoading"
                :loading="isLoading">
                发送
              </el-button>
              <el-button @click="userInput = ''" :disabled="isLoading">清空</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { sendMessage as sendMessageAPI } from '@/api/chat'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import SparkAIIcon from '@/img/SparkAI.png'

const userInput = ref('')
const chatMessages = ref([])
const chatContainer = ref(null)
const isLoading = ref(false)
const md = new MarkdownIt({
  breaks: true,
  linkify: true,
  typographer: true
})

const userAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
const doctorAvatar = SparkAIIcon

const commonSymptoms = [
  { label: '头痛', value: 'headache' },
  { label: '失眠', value: 'insomnia' },
  { label: '咳嗽', value: 'cough' },
  { label: '胃痛', value: 'stomachache' },
  { label: '关节疼痛', value: 'joint-pain' },
  { label: '焦虑', value: 'anxiety' }
]

const handleSymptomSelect = (symptom) => {
  const selectedSymptom = commonSymptoms.find(s => s.value === symptom)
  userInput.value = `我最近出现${selectedSymptom.label}的症状，请问可能是什么原因？应该如何缓解？`
}

const handleSendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMessage = {
    role: 'user',
    content: userInput.value,
    time: new Date().toLocaleTimeString()
  }
  chatMessages.value.push(userMessage)
  const currentInput = userInput.value
  userInput.value = ''
  isLoading.value = true

  try {
    scrollToBottom()
    const { response } = await sendMessageAPI(currentInput)
    chatMessages.value.push({
      role: 'assistant',
      content: response,
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    ElMessage.error('发送失败：' + (error.message || '未知错误'))
    // 回滚消息
    chatMessages.value.pop()
    userInput.value = currentInput
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const generateResponse = (message) => {
  // 模拟AI回复逻辑
  if (message.includes('头痛')) {
    return `根据您描述的症状，可能有以下几种情况：
    1. 紧张性头痛：常见于工作压力大、精神紧张的情况
    2. 偏头痛：可能与内分泌变化、饮食不规律有关
    3. 颈椎病引起的头痛：长期伏案工作可能导致
    
    建议：
    - 保持作息规律，适当运动放松
    - 可以服用川芎茶调散缓解症状
    - 如果症状持续，建议到医院进行详细检查`
  }
  return '抱歉，我需要更多信息来帮助您进行诊断。请详细描述您的症状，包括：\n1. 症状持续时间\n2. 是否有其他不适\n3. 是否有相关病史'
}

const formatMessage = (message) => {
  // 检测是否包含Markdown格式的内容
  if (message.includes('**') || message.includes('#') || 
      message.includes('-') || message.includes('1.')) {
    
    // 配置 markdown-it 选项
    const mdOptions = {
      breaks: true,
      linkify: true,
      typographer: true,
      html: true
    }
    const md = new MarkdownIt(mdOptions)
    
    // 添加自定义渲染规则以控制间距
    md.renderer.rules.paragraph_open = () => '<p class="md-paragraph">';
    md.renderer.rules.heading_open = (tokens, idx) => {
      const token = tokens[idx];
      return `<${token.tag} class="md-heading">`;
    };
    md.renderer.rules.list_item_open = () => '<li class="md-list-item">';
    
    // 渲染Markdown
    return md.render(message);
  }
  
  // 普通文本处理
  return message.replace(/\n/g, '<br>');
}

const clearChat = () => {
  chatMessages.value = []
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

onMounted(() => {
  // 添加欢迎消息
  chatMessages.value.push({
    role: 'assistant',
    content: '您好！我是由讯飞星火大模型驱动的中医智能助手，请描述您的症状，我会为您提供专业的建议。',
    time: new Date().toLocaleTimeString()
  })
})
</script>

<style>
@import '@/assets/AIChat.css';
</style>