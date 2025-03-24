<template>
  <div class="tongue-diagnosis">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="upload-section" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>舌诊图片上传</h3>
            </div>
          </template>
          <div class="upload-content">
            <el-upload
              class="upload-demo"
              drag
              :action="'/api/tongue/analyze/'"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleImageChange">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽要诊断的舌苔图片到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请上传清晰的舌苔图片，建议在自然光下拍摄
                </div>
              </template>
            </el-upload>
            <div v-if="isUploaded" class="upload-success">
              <div class="success-icon">
                <img 
                  :src="gifSrc" 
                  alt="成功" 
                  class="success-gif"
                  @load="handleGifLoad"
                  ref="successGif"
                />
              </div>
              <div class="success-text">
                <p>图片成功上传</p>
                <p class="file-name">图片名称：{{ fileName }}</p>
              </div>
              <el-button 
                type="primary" 
                @click="handleAnalyze" 
                class="analyze-btn"
                :loading="isAnalyzing">
                {{ isAnalyzing ? '分析中...' : '开始分析' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card v-if="analysisResult" class="result-section">
          <template #header>
            <div class="card-header">
              <h3>诊断结果</h3>
            </div>
          </template>
          <div class="analysis-result">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="舌苔性状">
                {{ analysisResult.tongueCoating }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div v-if="analysisResult.aiSuggestions" class="ai-suggestions">
              <el-divider>
                <el-icon><star-filled /></el-icon>
                讯飞星火AI建议
              </el-divider>
              <div class="ai-content" v-html="formatMarkdown(analysisResult.aiSuggestions)"></div>
            </div>
          </div>
        </el-card>
        <div v-else-if="isAnalyzing" class="analyzing-placeholder">
          <div class="analyzing-content">
            <el-icon class="analyzing-icon" :size="48"><Loading /></el-icon>
            <p>正在诊断舌苔图片，请稍候...</p>
            <div class="loading-dots">
              <i></i><i></i><i></i>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled, Loading, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { analyzeTongue } from '@/api/tongue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const isUploaded = ref(false)
const isAnalyzing = ref(false)
const file = ref(null)
const fileName = ref('')
const analysisResult = ref(null)
const successGif = ref(null)
const gifSrc = ref('/src/img/success.gif')

const handleImageChange = (uploadFile) => {
  file.value = uploadFile
  fileName.value = uploadFile.name
  isUploaded.value = true
  gifSrc.value = '/src/img/success.gif'
  // 重置分析结果
  analysisResult.value = null
}

const handleGifLoad = () => {
  if (successGif.value) {
    setTimeout(() => {
      gifSrc.value = '/src/img/success.jpg'
    }, 1700)
  }
}

const formatMarkdown = (text) => {
  if (!text) return ''
  try {
    // 预处理文本，确保建议和推荐中药部分正确显示
    const formattedText = text
      .replace(/建议：/, '### 建议：\n')
      .replace(/推荐中药：/, '### 推荐中药：\n')
      .replace(/(\d+\. )/g, '\n$1') // 确保每个建议项都在新行
      .replace(/、/g, '、\n') // 让每个中药名字都在新行
    return md.render(formattedText)
  } catch (error) {
    console.error('Markdown渲染错误:', error)
    return text
  }
}

const handleAnalyze = async () => {
  if (!file.value) {
    ElMessage.warning('请先上传图片')
    return
  }
  
  isAnalyzing.value = true
  analysisResult.value = null
  
  try {
    const formData = new FormData()
    formData.append('image', file.value.raw)
    console.log('准备上传文件:', file.value.name, '大小:', file.value.size)
    
    const response = await analyzeTongue(formData)
    console.log('API 原始响应:', response) // 添加调试日志
    
    // 确保响应数据有效
    if (!response) {
      throw new Error('未接收到有效的分析结果')
    }
    
    // 尝试处理可能的不同响应格式
    let responseData = response
    
    console.log('处理的响应数据:', responseData)
    
    // 处理分析结果
    analysisResult.value = {
      tongueCoating: responseData.tongueCoating || '未检测到',
      aiSuggestions: responseData.aiSuggestions || ''
    }
    
    console.log('最终处理后的分析结果:', analysisResult.value)
    
    ElMessage.success('舌苔分析完成！')
  } catch (error) {
    console.error('分析错误:', error)
    ElMessage.error(typeof error === 'string' ? error : '舌苔分析失败，请重试')
    analysisResult.value = null
  } finally {
    isAnalyzing.value = false
  }
}
</script>

<style>
@import '@/assets/TongueDiagnosis.css';
</style>