<template>
  <div class="herb-identification">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="upload-section" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>中药材图片上传</h3>
            </div>
          </template>
          <div class="upload-content">
            <el-upload
              class="upload-demo"
              drag
              action="/api/herbs/identify"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleImageChange">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽中药材照片到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请上传清晰的中药材照片，建议在自然光下拍摄
                </div>
              </template>
            </el-upload>
            <div v-if="previewUrl" class="preview-container">
              <img :src="previewUrl" alt="中药材预览" class="preview-image">
              <el-button type="primary" @click="handleIdentify" class="analyze-btn">
                开始识别
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card v-if="identificationResult" class="result-section" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>识别结果</h3>
            </div>
          </template>
          <div class="analysis-result">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="药材名称">
                {{ identificationResult.name }}
              </el-descriptions-item>
              <el-descriptions-item label="功效">
                {{ identificationResult.effects }}
              </el-descriptions-item>
              <el-descriptions-item label="性味">
                {{ identificationResult.properties }}
              </el-descriptions-item>
              <el-descriptions-item label="归经">
                {{ identificationResult.meridians }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="usage-advice">
              <h4>使用方法</h4>
              <el-card class="advice-card" shadow="never">
                <div class="advice-item">
                  <el-icon><InfoFilled /></el-icon>
                  <span>{{ identificationResult.usage }}</span>
                </div>
              </el-card>
            </div>

            <div class="precautions">
              <h4>注意事项</h4>
              <el-card class="advice-card" shadow="never">
                <div class="advice-item">
                  <el-icon><InfoFilled /></el-icon>
                  <span>{{ identificationResult.precautions }}</span>
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { identifyHerb as identifyHerbAPI } from '@/api/herbs'

const previewUrl = ref('')
const identificationResult = ref(null)
const file = ref(null)

const handleImageChange = (uploadFile) => {
  file.value = uploadFile
  previewUrl.value = URL.createObjectURL(uploadFile.raw)
}

const handleIdentify = async () => {
  try {
    const formData = new FormData()
    formData.append('image', file.value.raw)
    
    const result = await identifyHerbAPI(formData)
    identificationResult.value = result
    ElMessage.success('识别成功！')
  } catch (error) {
    ElMessage.error('识别失败：' + (error.message || '未知错误'))
  }
}
</script>

<style>
@import '@/assets/Herbldentification.css';
</style>