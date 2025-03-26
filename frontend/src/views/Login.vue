<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>中医药综合服务平台</h2>
        <div class="auth-type-switch">
          <el-button 
            :class="['switch-btn', { active: activeForm === 'login' }]"
            @click="activeForm = 'login'"
            text>
            登录
          </el-button>
          <el-button 
            :class="['switch-btn', { active: activeForm === 'register' }]"
            @click="activeForm = 'register'"
            text>
            注册
          </el-button>
          <div class="switch-slider" :class="{ 'slide-right': activeForm === 'register' }"></div>
        </div>
      </div>

      <div class="forms-container">
        <!-- 登录表单 -->
        <el-form
          v-show="activeForm === 'login'"
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form">
          <div v-if="loginError" class="form-error-message">{{ loginError }}</div>
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              prefix-icon="User"
              placeholder="请输入用户名">
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              ref="passwordInput"
              v-model="loginForm.password"
              prefix-icon="Lock"
              type="password"
              placeholder="请输入密码"
              show-password>
            </el-input>
          </el-form-item>
          <div class="form-buttons">
            <el-button 
              type="primary" 
              class="submit-button"
              :loading="loading"
              @click="handleLogin">
              登录
            </el-button>
            <el-button 
              type="success" 
              class="face-login-button"
              @click="startFaceLogin">
              <el-icon><VideoCameraFilled /></el-icon>
              人脸识别登录
            </el-button>
          </div>
        </el-form>

        <!-- 注册表单 -->
        <el-form
          v-show="activeForm === 'register'"
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form">
          <div v-if="registerErrors.general" class="form-error-message">{{ registerErrors.general }}</div>
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              prefix-icon="User"
              placeholder="请输入用户名">
            </el-input>
            <div v-if="registerErrors.username" class="field-error-message">{{ registerErrors.username }}</div>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              prefix-icon="Lock"
              type="password"
              placeholder="请输入密码"
              show-password>
            </el-input>
            <div v-if="registerErrors.password" class="field-error-message">{{ registerErrors.password }}</div>
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              prefix-icon="Lock"
              type="password"
              placeholder="请确认密码"
              show-password>
            </el-input>
            <div v-if="registerErrors.confirmPassword" class="field-error-message">{{ registerErrors.confirmPassword }}</div>
          </el-form-item>
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              prefix-icon="Message"
              placeholder="请输入邮箱">
            </el-input>
            <div v-if="registerErrors.email" class="field-error-message">{{ registerErrors.email }}</div>
          </el-form-item>
          <div class="form-buttons">
            <el-button 
              type="primary" 
              class="submit-button"
              :loading="loading"
              @click="handleRegister">
              注册
            </el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 人脸识别对话框 -->
    <el-dialog
      v-model="showFaceDialog"
      :show-close="false"
      :close-on-click-modal="false"
      width="400px"
      class="face-dialog">
      <div class="face-container">
        <div v-if="faceError" class="face-error-message">{{ faceError }}</div>
        <video ref="videoRef" class="face-video" autoplay playsinline></video>
        <div class="face-mask">
          <div class="face-circle"></div>
        </div>
        <div class="face-tips">
          {{ isFaceRegister ? '请录入您的面部信息' : '请将面部放入圆圈内' }}
        </div>
      </div>
      <div class="dialog-footer">
        <el-button @click="cancelFaceLogin">取消</el-button>
        <el-button type="primary" @click="confirmFaceLogin">
          {{ isFaceRegister ? '完成录入' : '确认' }}
        </el-button>
      </div>
    </el-dialog>

    <!-- 用户选择对话框 -->
    <el-dialog
      v-model="showUserSelectionDialog"
      title="选择用户"
      width="450px"
      :show-close="true"
      :close-on-click-modal="false"
      class="user-selection-dialog">
      <div class="user-selection-container">
        <p class="user-selection-tip" v-if="multipleUsers.length > 0">
          人脸匹配成功，请选择账户进行登录：
        </p>
        <div class="user-cards-container">
          <div
            v-for="user in multipleUsers"
            :key="user.username"
            class="user-card"
            :class="{ 'user-card-selected': selectedUsername === user.username }"
            @click="selectedUsername = user.username">
            <div class="user-card-content">
              <div class="user-avatar">
                <el-avatar :size="40">{{ user.username.substring(0, 1).toUpperCase() }}</el-avatar>
              </div>
              <div class="user-info">
                <div class="user-name">{{ user.username }}</div>
              </div>
              <div class="selection-indicator">
                <el-icon v-if="selectedUsername === user.username"><Check /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelUserSelection">取消</el-button>
          <el-button type="primary" @click="handleUserSelect(selectedUsername)" :disabled="!selectedUsername">
            确认登录
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoCameraFilled, Check } from '@element-plus/icons-vue'
import { login, register, faceLogin } from '@/api/auth'

const router = useRouter()
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)
const activeForm = ref('login')

// 监听表单切换，在切换时清除错误
watch(activeForm, (newForm) => {
  if (newForm === 'login') {
    if (loginFormRef.value) {
      loginFormRef.value.clearValidate()
    }
  } else if (newForm === 'register') {
    if (registerFormRef.value) {
      registerFormRef.value.clearValidate()
    }
  }
})

const loginForm = reactive({
  username: '',
  password: ''
})

// 为登录表单添加错误提示状态
const loginError = ref('')

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  // 清除之前的错误提示
  loginError.value = ''
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    const response = await login(loginForm)
    
    // 处理不同的响应状态
    if (response.code === 200 && response.data && response.data.token) {
      // 登录成功
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('username', response.data.username)
      ElMessage.success('登录成功')
      router.push('/')
    } else if (response.code === 401) {
      // 登录失败（用户名或密码错误）
      loginError.value = response.message || '用户名或密码错误，请重试'
      ElMessage.error(loginError.value)
    } else {
      // 其他错误情况
      loginError.value = response.message || '登录失败，请检查用户名和密码'
      ElMessage.error(loginError.value)
    }
  } catch (error) {
    console.error('登录错误:', error)
    loginError.value = error.message || '登录过程中发生错误，请稍后再试'
    ElMessage.error(loginError.value)
  } finally {
    loading.value = false
  }
}

// 注册表单数据
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

// 为注册表单添加字段错误提示状态
const registerErrors = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
  general: '' // 一般性错误
})

// 注册表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在 3 到 20 个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在 6 到 20 个字符之间', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]+$/, message: '密码只能包含英文字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 清除注册表单中的所有错误提示
const clearRegisterErrors = () => {
  Object.keys(registerErrors).forEach(key => {
    registerErrors[key] = ''
  })
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  // 清除之前的错误提示
  clearRegisterErrors()
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    // 调用注册API
    const response = await register(registerForm)
    
    if (response.code === 200) {
      ElMessage.success('注册成功')
      
      // 提示是否需要设置人脸识别
      try {
        await ElMessageBox.confirm('是否需要设置人脸识别登录？', '提示', {
          confirmButtonText: '设置',
          cancelButtonText: '暂不设置',
          type: 'info'
        })
        
        // 用户点击设置，打开人脸采集窗口
        isFaceRegister.value = true
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('username', response.data.username)
        startFaceCapture()
      } catch (err) {
        // 用户点击暂不设置，直接跳转到登录界面
        resetRegisterForm()
      }
    } else {
      // 检查具体错误类型，并更新对应字段的错误状态
      if (response.errors) {
        // 处理每个字段的错误
        Object.entries(response.errors).forEach(([field, error]) => {
          if (field in registerErrors) {
            if (typeof error === 'string') {
              registerErrors[field] = error
            } else if (Array.isArray(error) && error.length > 0) {
              registerErrors[field] = error[0]
            }
            
            // 针对特定字段的错误，直接在表单中显示
            if (field === 'username' && registerFormRef.value) {
              const usernameField = registerFormRef.value.fields.find(f => f.prop === 'username')
              if (usernameField) {
                usernameField.validateState = 'error'
                usernameField.validateMessage = registerErrors[field]
              }
              
              // 修改错误提示文本，简化为"用户名已存在"
              if (registerErrors[field].includes('已存在')) {
                registerErrors[field] = '用户名已存在'
                ElMessage.error('用户名已存在')
              }
            } else if (field === 'email' && registerFormRef.value) {
              const emailField = registerFormRef.value.fields.find(f => f.prop === 'email')
              if (emailField) {
                emailField.validateState = 'error'
                emailField.validateMessage = registerErrors[field]
              }
              
              // 修改错误提示文本，简化为"邮箱已被注册"
              if (registerErrors[field].includes('已存在') || registerErrors[field].includes('已被注册')) {
                registerErrors[field] = '邮箱已被注册'
                ElMessage.error('邮箱已被注册')
              }
            } else if (field === 'password' && registerFormRef.value) {
              const passwordField = registerFormRef.value.fields.find(f => f.prop === 'password')
              if (passwordField) {
                passwordField.validateState = 'error'
                passwordField.validateMessage = registerErrors[field]
              }
            } else if (field === 'confirmPassword' && registerFormRef.value) {
              const confirmPasswordField = registerFormRef.value.fields.find(f => f.prop === 'confirmPassword')
              if (confirmPasswordField) {
                confirmPasswordField.validateState = 'error'
                confirmPasswordField.validateMessage = registerErrors[field]
              }
            }
          }
        })
      } else if (response.message) {
        // 有具体的错误消息
        // 简化通用错误消息
        if (response.message.includes('用户名') && response.message.includes('已存在')) {
          registerErrors.general = '用户名已存在'
          ElMessage.error('用户名已存在')
        } else if (response.message.includes('邮箱') && (response.message.includes('已存在') || response.message.includes('已被注册'))) {
          registerErrors.general = '邮箱已被注册'
          ElMessage.error('邮箱已被注册')
        } else {
          registerErrors.general = response.message
          ElMessage.error(response.message)
        }
      } else {
        // 通用错误
        registerErrors.general = '注册失败，请检查输入信息'
        ElMessage.error('注册失败，请检查输入信息')
      }
    }
  } catch (error) {
    if (error.message) {
      registerErrors.general = error.message
      ElMessage.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

// 重置注册表单并切换到登录页
const resetRegisterForm = () => {
  activeForm.value = 'login'
  registerForm.username = ''
  registerForm.password = ''
  registerForm.confirmPassword = ''
  registerForm.email = ''
  clearRegisterErrors() // 清除所有错误提示
}

// 处理人脸识别错误信息
const handleFaceRecognitionError = (error, source = '操作') => {
  console.error(`${source}失败:`, error)
  
  // 如果是响应对象
  if (error && error.code) {
    if (error.code === 400) {
      if (error.message && error.message.includes('未检测到有效人脸')) {
        faceError.value = '未能检测到有效的人脸，请确保光线充足并正对摄像头'
      } else {
        faceError.value = error.message || '请求参数无效，请重试'
      }
    } else if (error.code === 404) {
      if (error.message && error.message.includes('未检测到人脸')) {
        faceError.value = '未能检测到有效的人脸，请确保光线充足并正对摄像头'
      } else if (error.message && error.message.includes('未找到匹配')) {
        faceError.value = '人脸信息不存在，请先注册或使用用户名密码登录'
      } else {
        faceError.value = error.message || '未找到相关资源'
      }
    } else if (error.code === 500) {
      // 检查消息内容，处理特定的500错误
      if (error.message && error.message.includes('未检测到人脸')) {
        faceError.value = '未能检测到有效的人脸，请确保光线充足并正对摄像头'
      } else if (error.message && error.message.includes('未找到匹配')) {
        faceError.value = '人脸信息不存在，请先注册或使用用户名密码登录'
      } else {
        faceError.value = error.message || '人脸识别服务暂时不可用，请稍后再试或使用其他登录方式'
      }
    } else {
      faceError.value = error.message || `${source}失败，请稍后再试`
    }
  } 
  // 如果是错误对象或其他格式
  else if (error.response && error.response.data) {
    handleFaceRecognitionError(error.response.data, source)
  } else if (error.message) {
    // 直接检查错误消息
    if (error.message.includes('未检测到人脸')) {
      faceError.value = '未能检测到有效的人脸，请确保光线充足并正对摄像头'
    } else if (error.message.includes('未找到匹配')) {
      faceError.value = '人脸信息不存在，请先注册或使用用户名密码登录'
    } else {
      faceError.value = `${source}失败: ${error.message}`
    }
  } else {
    faceError.value = `${source}失败，请稍后再试`
  }
  
  // 显示错误消息
  ElMessage.error(faceError.value)
  return faceError.value
}

// 人脸识别相关
const showFaceDialog = ref(false)
const videoRef = ref(null)
let stream = null
const isFaceRegister = ref(false)
const capturedImage = ref(null)
const multipleUsers = ref([])
const showUserSelectionDialog = ref(false)
const selectedUsername = ref('')
const faceError = ref('') // 添加人脸识别错误提示

const startFaceCapture = async () => {
  try {
    // 重置错误信息
    faceError.value = ''
    showFaceDialog.value = true
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user"
      }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.onloadedmetadata = () => {
        videoRef.value.play()
      }
    }
  } catch (error) {
    console.error('摄像头访问失败:', error)
    faceError.value = '无法访问摄像头，请检查设备权限'
    ElMessage.error('无法访问摄像头，请检查设备权限')
    showFaceDialog.value = false
    if (!isFaceRegister.value) {
      resetRegisterForm()
    }
  }
}

const startFaceLogin = async () => {
  isFaceRegister.value = false
  startFaceCapture()
}

const cancelFaceLogin = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  showFaceDialog.value = false
  
  // 如果是注册时的人脸设置，取消后需要切换到登录页
  if (isFaceRegister.value) {
    resetRegisterForm()
  }
}

const confirmFaceLogin = async () => {
  if (!videoRef.value) return

  try {
    // 清除之前的错误提示
    faceError.value = ''
    loading.value = true
    
    // 创建canvas捕获当前视频帧
    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth
    canvas.height = videoRef.value.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height)
    
    // 将canvas内容转为base64
    const imageData = canvas.toDataURL('image/jpeg')
    capturedImage.value = imageData
    
    if (isFaceRegister.value) {
      // 上传人脸照片进行注册
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          faceError.value = '未登录，无法设置人脸'
          ElMessage.error(faceError.value)
          throw new Error('未登录')
        }

        const formData = new FormData()
        // 将base64转为blob
        const blob = await fetch(imageData).then(res => res.blob())
        formData.append('file', blob, 'face.jpg')
        
        // 调用API上传人脸
        const response = await fetch('/api/user/face/', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        })
        
        // 记录详细的响应信息，用于调试
        console.log('人脸注册响应状态:', response.status, response.statusText)
        
        const result = await response.json()
        console.log('人脸注册响应数据:', result)
        
        if (result.code === 200) {
          ElMessage.success('人脸信息设置成功，请使用账号密码或人脸识别登录')
          cancelFaceLogin()
          resetRegisterForm()
        } else {
          // 使用统一的错误处理
          handleFaceRecognitionError(result, '人脸信息设置')
        }
      } catch (error) {
        handleFaceRecognitionError(error, '人脸信息设置')
      }
    } else {
      // 人脸登录
      try {
        // 将base64转为blob
        const blob = await fetch(imageData).then(res => res.blob())
        const formData = new FormData()
        formData.append('face_image', blob, 'face.jpg')
        
        // 调用人脸登录API
        const response = await faceLogin(formData)
        console.log('人脸登录响应:', response)
        
        if (response.code === 200) {
          // 登录成功
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('username', response.data.username)
          ElMessage.success('人脸登录成功')
          cancelFaceLogin()
          router.push('/')
        } else if (response.code === 300 && response.data && response.data.users) {
          // 多个用户匹配
          // 去重处理，防止出现同一用户多次
          const uniqueUsers = [];
          const usernames = new Set();
          
          // 对用户进行去重，相同用户名只保留相似度最高的一个
          response.data.users.forEach(user => {
            if (!usernames.has(user.username)) {
              usernames.add(user.username);
              uniqueUsers.push(user);
            } else {
              // 如果已存在相同用户名，比较相似度，保留相似度更高的
              const existingUserIndex = uniqueUsers.findIndex(u => u.username === user.username);
              if (existingUserIndex !== -1 && uniqueUsers[existingUserIndex].similarity < user.similarity) {
                uniqueUsers[existingUserIndex] = user;
              }
            }
          });
          
          // 按相似度降序排序
          uniqueUsers.sort((a, b) => b.similarity - a.similarity);
          
          multipleUsers.value = uniqueUsers;
          console.log('匹配到的用户(去重后):', uniqueUsers);
          
          // 确保总是显示用户选择对话框，不再自动登录单个用户
          if (uniqueUsers.length > 0) {
            showUserSelectionDialog.value = true
            // 预选第一个用户
            selectedUsername.value = uniqueUsers[0].username
          } else {
            faceError.value = '未找到匹配的用户，请先注册或使用用户名密码登录'
            ElMessage.error(faceError.value)
          }
          cancelFaceLogin()
        } else {
          // 使用统一的错误处理
          handleFaceRecognitionError(response, '人脸登录')
        }
      } catch (error) {
        handleFaceRecognitionError(error, '人脸登录')
      }
    }
  } catch (error) {
    console.error('处理人脸图像失败:', error)
    faceError.value = '处理人脸图像时出错'
    ElMessage.error('处理人脸图像时出错')
  } finally {
    loading.value = false
  }
}

// 根据选择的用户名进行登录
const handleUserSelect = async (username) => {
  if (!username) {
    ElMessage.warning('请选择一个用户')
    return
  }
  
  try {
    loading.value = true
    // 查找选中用户的详细信息
    const selectedUser = multipleUsers.value.find(user => user.username === username)
    
    if (!selectedUser) {
      ElMessage.error('用户信息获取失败')
      return
    }
    
    // 从匹配结果中获取token
    const token = selectedUser.token
    if (!token) {
      ElMessage.error('登录凭证获取失败')
      return
    }
    
    // 保存登录信息
    localStorage.setItem('token', token)
    localStorage.setItem('username', username)
    
    // 关闭对话框并提示
    showUserSelectionDialog.value = false
    ElMessage.success(`已成功以 ${username} 身份登录`)
    
    // 跳转到首页
    router.push('/')
  } catch (error) {
    console.error('用户选择登录失败:', error)
    ElMessage.error('登录失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

// 取消用户选择
const cancelUserSelection = () => {
  ElMessage({
    message: '已取消用户选择，请重新尝试登录或使用账号密码登录',
    type: 'info',
    duration: 3000,
    showClose: true
  })
  showUserSelectionDialog.value = false
  selectedUsername.value = ''
  multipleUsers.value = []
}
</script>

<style lang="scss" scoped>
@import '@/assets/Login.css';

// 错误消息样式
.form-error-message {
  background-color: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
  border-left: 3px solid #F56C6C;
}

.field-error-message {
  color: #F56C6C;
  font-size: 12px;
  padding: 4px 0;
  margin-top: 2px;
  line-height: 1.2;
  text-align: left;
  transition: all 0.3s;
}

// 人脸识别错误消息样式
.face-error-message {
  background-color: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
  border-left: 3px solid #F56C6C;
  text-align: center;
  position: relative;
  z-index: 10;
}

// 新增样式补充
.user-selection-container {
  margin-bottom: 15px;
}

.user-selection-tip {
  margin-bottom: 15px;
  color: #606266;
  font-size: 14px;
}

.user-cards-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 10px;
  padding-right: 5px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
}

.user-card {
  margin-bottom: 10px;
  width: 100%;
  transition: all 0.3s;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  padding: 10px 15px;
  cursor: pointer;
  
  &:hover {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    background-color: #f5f7fa;
  }
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &.user-card-selected {
    border-color: #409EFF;
    background-color: rgba(64, 158, 255, 0.1);
  }
}

.user-card-content {
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
}

.user-avatar {
  flex: 0 0 auto;
  margin-right: 15px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 16px;
  color: #303133;
}

.selection-indicator {
  flex: 0 0 auto;
  color: #409EFF;
  font-size: 20px;
  margin-left: 10px;
}

.dialog-footer {
  text-align: right;
  margin-top: 15px;
}

// 用户选择对话框样式
.user-selection-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
  }

  :deep(.el-dialog__header) {
    padding-bottom: 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
    
    .el-dialog__title {
      font-size: 18px;
      font-weight: bold;
      color: #303133;
    }
  }
}

// 添加全局样式
:deep(.el-progress) {
  &.is-success .el-progress-bar__inner {
    background-color: #67C23A;
  }
  
  &.is-warning .el-progress-bar__inner {
    background-color: #E6A23C;
  }
  
  &.is-exception .el-progress-bar__inner {
    background-color: #F56C6C;
  }
}
</style>