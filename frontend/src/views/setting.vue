<template>
  <div class="setting-container">
    <!-- 加载和错误处理 -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <div style="padding: 20px;">
            <el-skeleton-item variant="image" style="width: 120px; height: 120px; border-radius: 50%;" />
            <div style="padding: 20px 0;">
              <el-skeleton-item variant="p" style="width: 80%;" />
              <el-skeleton-item variant="text" style="width: 60%; margin-top: 10px;" />
              <el-skeleton-item variant="text" style="width: 70%; margin-top: 10px;" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <div v-else-if="hasError" class="error-container">
      <el-result
        icon="error"
        title="加载失败"
        sub-title="获取用户信息时发生错误，请刷新页面重试。">
        <template #extra>
          <el-button type="primary" @click="reloadPage">刷新页面</el-button>
          <el-button @click="router.push('/')">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <transition-group v-else name="card-fade" tag="div" class="transition-container">
      <el-row :gutter="30" key="row">
        <!-- 个人资料卡片 -->
        <el-col :span="8">
          <el-card class="profile-card">
            <template #header>
              <div class="card-header">
                <h3>个人资料</h3>
                <div>
                  <el-button v-if="!isEditing" type="primary" size="small" text @click="startEdit">
                    <el-icon><Edit /></el-icon> 编辑
                  </el-button>
                  <transition name="fade" mode="out-in">
                    <div v-if="isEditing" class="edit-actions">
                      <el-button type="success" size="small" text @click="saveProfile">
                        <el-icon><Check /></el-icon> 保存
                      </el-button>
                      <el-button type="info" size="small" text @click="cancelEdit">
                        <el-icon><Close /></el-icon> 取消
                      </el-button>
                    </div>
                  </transition>
                </div>
              </div>
            </template>
            <div class="profile-content">
              <div class="avatar-container">
                <el-upload
                  class="avatar-uploader"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :on-error="handleAvatarError"
                  :before-upload="beforeAvatarUpload"
                  action="/api/user/avatar/"
                  :headers="authHeaders">
                  <img v-if="userInfo.avatar" :src="userInfo.avatar" class="avatar" />
                  <img v-else :src="defaultAvatarImage" class="avatar" />
                  <div class="avatar-hover-mask">
                    <el-icon><Camera /></el-icon>
                    <span>更换头像</span>
                  </div>
                </el-upload>
              </div>
              <div class="info-container">
                <transition-group name="list" tag="div" class="info-list">
                  <div class="info-item" key="username">
                    <label>用户名：</label>
                    <transition name="fade" mode="out-in">
                      <template v-if="isEditing">
                        <el-input v-model="editForm.username" placeholder="请输入用户名" />
                      </template>
                      <span v-else>{{ userInfo.username || '未设置' }}</span>
                    </transition>
                  </div>
                  <div class="info-item" key="email">
                    <label>邮箱：</label>
                    <transition name="fade" mode="out-in">
                      <template v-if="isEditing">
                        <el-input v-model="editForm.email" placeholder="请输入邮箱" />
                      </template>
                      <span v-else>{{ userInfo.email || '未设置' }}</span>
                    </transition>
                  </div>
                  <div class="info-item" key="createTime">
                    <label>注册时间：</label>
                    <span>{{ formatDate(userInfo.create_time) }}</span>
                  </div>
                  <div class="info-item" v-if="userInfo.lastLoginTime" key="lastLoginTime">
                    <label>上次登录：</label>
                    <span>{{ formatDate(userInfo.lastLoginTime) }}</span>
                  </div>
                </transition-group>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 修改密码表单 -->
        <el-col :span="8">
          <el-card class="password-card">
            <template #header>
              <div class="card-header">
                <h3>修改密码</h3>
                <el-tag size="small" effect="dark" type="warning" v-if="needChangePassword">
                  建议修改初始密码
                </el-tag>
              </div>
            </template>
            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="100px">
              <el-form-item label="当前密码" prop="oldPassword">
                <el-input
                  v-model="passwordForm.oldPassword"
                  type="password"
                  show-password
                  placeholder="请输入当前密码">
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="passwordForm.newPassword"
                  type="password"
                  show-password
                  placeholder="请输入新密码">
                  <template #prefix>
                    <el-icon><Key /></el-icon>
                  </template>
                </el-input>
                <transition name="slide-fade">
                  <div class="password-strength" v-if="passwordForm.newPassword">
                    <div class="strength-label">密码强度:</div>
                    <div class="strength-bar">
                      <div class="strength-indicator" :class="passwordStrengthClass"></div>
                    </div>
                    <div class="strength-text" :class="passwordStrengthClass">{{ passwordStrengthText }}</div>
                  </div>
                </transition>
              </el-form-item>
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  show-password
                  placeholder="请再次输入新密码">
                  <template #prefix>
                    <el-icon><Check /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
                  <el-icon><Refresh /></el-icon> 确认修改
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 人脸识别设置 -->
        <el-col :span="8">
          <el-card class="face-card">
            <template #header>
              <div class="card-header">
                <h3>人脸识别设置</h3>
                <transition name="zoom" mode="out-in">
                  <el-tag v-if="hasFaceRecognition" key="enabled" size="small" effect="dark" type="success">已启用</el-tag>
                  <el-tag v-else key="disabled" size="small" effect="dark" type="info">未启用</el-tag>
                </transition>
              </div>
            </template>
            <div class="face-content">
              <div class="face-preview">
                <img :src="faceAnimationGif" class="face-animation" alt="人脸识别动画" />
                <el-image
                  v-if="hasFaceRecognition"
                  :src="faceImage"
                  fit="cover"
                  style="display: none;"
                  :preview-src-list="[faceImage]">
                </el-image>
              </div>
              <div class="face-actions">
                <el-button type="success" class="face-btn" @click="showUploadDialog" :disabled="faceLoading">
                  <el-icon><Upload /></el-icon>
                  {{ hasFaceRecognition ? '更新人脸数据' : '录入人脸' }}
                </el-button>
                <el-button type="danger" class="face-btn" @click="handleDeleteFace" 
                  :disabled="!hasFaceRecognition || faceLoading" :loading="deleteLoading">
                  <el-icon><Delete /></el-icon>
                  删除人脸数据
                </el-button>
              </div>
              <transition name="slide-fade">
                <div class="face-tips" v-if="!hasFaceRecognition">
                  <el-alert
                    title="人脸识别登录提示"
                    type="info"
                    :closable="false"
                    description="添加人脸识别可以让您的登录更加安全便捷，录入时请确保光线充足，面部正对摄像头。"
                    show-icon>
                  </el-alert>
                </div>
              </transition>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </transition-group>
    
    <!-- 选择上传方式的对话框 -->
    <transition name="fade">
      <el-dialog
        v-if="uploadDialogVisible"
        v-model="uploadDialogVisible"
        title="选择录入方式"
        width="350px"
        destroy-on-close
        center
        custom-class="upload-dialog"
        :modal="true"
        modal-class="upload-modal"
        append-to-body>
        <div class="upload-options">
          <el-button type="primary" class="upload-btn" @click="startCamera">
            <el-icon><Camera /></el-icon>
            使用摄像头拍照
          </el-button>
          <el-upload
            class="local-upload"
            action=""
            :http-request="handleLocalImageUpload"
            :show-file-list="false"
            :before-upload="beforeFaceUpload">
            <el-button type="primary" class="upload-btn">
              <el-icon><Picture /></el-icon>
              选择本地图片
            </el-button>
          </el-upload>
        </div>
      </el-dialog>
    </transition>

    <!-- 摄像头拍照对话框 - 使用完全独立的容器 -->
    <transition name="fade">
      <div v-if="cameraDialogVisible" class="camera-fullscreen-container">
        <div class="camera-popup">
          <div class="camera-popup-header">
            <h3>面部信息录入</h3>
            <el-button class="close-btn" type="text" @click="stopCamera">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <div class="camera-container">
            <video
              ref="videoRef"
              class="camera-video"
              autoplay
              playsinline
              style="transform: scaleX(-1);">
            </video>
            <canvas
              ref="canvasRef"
              class="camera-canvas"
              style="display: none;">
            </canvas>
            <div class="camera-overlay">
              <div class="face-frame">
                <span></span>
                <span></span>
                <div class="scan-line"></div>
              </div>
            </div>
          </div>
          <div class="camera-tips">
            请将面部置于框内，保持光线充足，面部正对摄像头
          </div>
          <div class="camera-popup-footer">
            <el-button @click="stopCamera">取消</el-button>
            <el-button type="primary" @click="takePhoto" :loading="captureLoading">
              <el-icon><Camera /></el-icon> 拍照
            </el-button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Lock,
  Key,
  Edit,
  Check,
  Close,
  Message,
  Phone,
  Calendar,
  Upload,
  Delete,
  Plus,
  Camera,
  Picture,
  Refresh
} from '@element-plus/icons-vue'
import { getUserInfo, updatePassword, updateFace, deleteFace, updateUserInfo, updateAvatar } from '@/api/user'
import { validatePassword } from '@/utils/validation'
import defaultFaceImage from '@/img/face.png'
import defaultAvatarImage from '@/img/user.jpg'
import faceAnimationGif from '@/img/face.gif'

// 安全获取localStorage数据的方法
const getLocalStorageItem = (key) => {
  try {
    return window.localStorage.getItem(key)
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return null
  }
}

// 安全设置localStorage数据的方法
const setLocalStorageItem = (key, value) => {
  try {
    window.localStorage.setItem(key, value)
    return true
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return false
  }
}

// 安全移除localStorage数据的方法
const removeLocalStorageItem = (key) => {
  try {
    window.localStorage.removeItem(key)
    return true
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return false
  }
}

// 验证头部
const authHeaders = computed(() => {
  const token = getLocalStorageItem('token')
  return {
    'Authorization': token ? `Bearer ${token}` : ''
  }
})

const router = useRouter();
// 加载状态
const isLoading = ref(true);
// 错误状态
const hasError = ref(false);
// 初始化完成标志
const initialized = ref(false);

// 用户信息
const userInfo = ref({
  username: '',
  role: '',
  email: '',
  phone: '',
  avatar: '',
  create_time: '',
  lastLoginTime: '',
  has_face: false
})

// 是否需要修改初始密码
const needChangePassword = ref(false)

// 密码表单
const passwordFormRef = ref(null)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordLoading = ref(false)

// 人脸相关
const faceImage = ref('')
const faceLoading = ref(false)
const deleteLoading = ref(false)
const captureLoading = ref(false)

// 计算属性：是否已设置人脸识别
const hasFaceRecognition = computed(() => {
  console.log('计算人脸状态:', userInfo.value?.has_face);
  return userInfo.value && userInfo.value.has_face === true;
})

// 观察人脸识别状态变化
watch(() => userInfo.value.has_face, (newVal) => {
  console.log('人脸状态变化:', newVal);
}, { immediate: true });

// 密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 计算密码强度
const passwordStrength = computed(() => {
  const password = passwordForm.value.newPassword
  if (!password) return 0
  
  let strength = 0
  // 长度检查
  if (password.length >= 8) strength += 1
  // 包含数字
  if (/\d/.test(password)) strength += 1
  // 包含小写字母
  if (/[a-z]/.test(password)) strength += 1
  // 包含大写字母
  if (/[A-Z]/.test(password)) strength += 1
  // 包含特殊字符
  if (/[^a-zA-Z0-9]/.test(password)) strength += 1
  
  return strength
})

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 1) return 'weak'
  if (strength <= 3) return 'medium'
  return 'strong'
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 1) return '弱'
  if (strength <= 3) return '中'
  return '强'
})

// 编辑状态
const isEditing = ref(false)
const editForm = ref({
  username: '',
  email: '',
  phone: ''
})

// 开始编辑
const startEdit = () => {
  isEditing.value = true
  editForm.value = {
    username: userInfo.value.username,
    email: userInfo.value.email,
    phone: userInfo.value.phone
  }
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  editForm.value = {
    username: '',
    email: '',
    phone: ''
  }
}

// 保存个人资料
const saveProfile = async () => {
  try {
    const res = await updateUserInfo(editForm.value)
    
    if (res.code === 200) {
      userInfo.value = {
        ...userInfo.value,
        ...editForm.value
      }
      isEditing.value = false
      ElMessage.success('个人资料更新成功')
    } else {
      ElMessage.error(res.message || '个人资料更新失败')
    }
  } catch (error) {
    console.error('个人资料更新失败:', error)
    ElMessage.error('个人资料更新失败')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  
  try {
    // 尝试直接转换日期字符串
    const date = new Date(dateString)
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('无效的日期格式:', dateString)
      return dateString || '未知'
    }
    
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '-')
  } catch (e) {
    console.error('日期格式化错误:', e)
    return dateString || '未知'
  }
}

// 处理头像URL的辅助函数
const processImageUrl = (url, addTimestamp = true) => {
  if (!url || url === defaultAvatarImage || url === defaultFaceImage) {
    return url;
  }
  
  console.log('处理前的URL:', url);
  
  // 确保URL以/开头
  if (url && !url.startsWith('http') && !url.startsWith('//') && !url.startsWith('/')) {
    url = '/' + url;
  }
  
  // 添加时间戳参数以避免缓存问题
  if (addTimestamp) {
    url = url.includes('?') 
      ? `${url}&t=${new Date().getTime()}` 
      : `${url}?t=${new Date().getTime()}`;
  }
  
  console.log('处理后的URL:', url);
  return url;
}

// 头像上传前的验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 头像上传成功的回调
const handleAvatarSuccess = (response) => {
  console.log('头像上传响应:', response);
  
  if (response.code === 200) {
    try {
      let avatarUrl = processImageUrl(response.data.avatarUrl);
      
      // 更新头像并显示成功消息
      userInfo.value.avatar = avatarUrl;
      
      // 强制刷新头像显示
      setTimeout(() => {
        const avatarEl = document.querySelector('.avatar');
        if (avatarEl) {
          avatarEl.src = avatarUrl;
        }
      }, 100);
      
      ElMessage.success('头像更新成功');
    } catch (error) {
      console.error('处理头像URL时出错:', error);
      ElMessage.warning('头像更新成功，但显示可能有问题');
    }
  } else {
    console.error('头像上传失败:', response);
    ElMessage.error(response.message || '头像更新失败');
  }
}

// 添加上传失败的钩子
const handleAvatarError = (error) => {
  console.error('头像上传失败:', error)
  ElMessage.error('头像上传失败，请稍后重试')
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    isLoading.value = true;
    hasError.value = false;
    
    const res = await getUserInfo();
    
    if (res.code === 200 && res.data) {
      console.log('获取到的用户信息:', res.data); // 调试输出
      
      // 处理头像URL
      const avatarUrl = processImageUrl(res.data.avatar);
      const faceImageUrl = processImageUrl(res.data.face_image);
      
      // 设置默认值，防止属性为undefined导致渲染错误
      userInfo.value = {
        username: res.data.username || getLocalStorageItem('username') || '用户',
        email: res.data.email || '',
        avatar: avatarUrl,
        create_time: res.data.create_time || new Date().toISOString(),
        lastLoginTime: res.data.last_login_time || new Date().toISOString(),
        has_face: res.data.has_face === true
      };
      
      // 判断是否使用了默认密码
      needChangePassword.value = res.data.need_change_password || false;
      
      // 设置人脸图像
      faceImage.value = faceImageUrl;
      console.log('人脸识别状态:', userInfo.value.has_face, '人脸图像:', faceImage.value);
      
      // 初始化编辑表单
      editForm.value = {
        username: userInfo.value.username || '',
        email: userInfo.value.email || '',
        phone: userInfo.value.phone || ''
      };
      
      initialized.value = true;
      
      // 手动检查人脸识别状态 (调试)
      setTimeout(() => {
        console.log('人脸状态检查 (延迟):', userInfo.value.has_face, hasFaceRecognition.value);
      }, 100);
    } else {
      console.error('获取用户信息失败:', res.message);
      hasError.value = true;
      ElMessage.error(res.message || '获取用户信息失败');
      
      // 设置默认值，防止渲染错误
      userInfo.value = {
        username: getLocalStorageItem('username') || '用户',
        email: '',
        avatar: defaultAvatarImage,
        create_time: new Date().toISOString(),
        lastLoginTime: new Date().toISOString(),
        has_face: false
      };
      
      // 初始化编辑表单
      editForm.value = {
        username: userInfo.value.username || '',
        email: userInfo.value.email || '',
        phone: userInfo.value.phone || ''
      };
      
      initialized.value = true;
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
    hasError.value = true;
    ElMessage.error('获取用户信息失败，请刷新页面重试');
    
    // 设置默认值，防止渲染错误
    userInfo.value = {
      username: getLocalStorageItem('username') || '用户',
      email: '',
      avatar: defaultAvatarImage,
      create_time: new Date().toISOString(),
      lastLoginTime: new Date().toISOString(),
      has_face: false
    };
      
    // 初始化编辑表单
    editForm.value = {
      username: userInfo.value.username || '',
      email: userInfo.value.email || '',
      phone: userInfo.value.phone || ''
    };
    
    initialized.value = true;
  } finally {
    isLoading.value = false;
  }
};

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        passwordLoading.value = true
        const res = await updatePassword(passwordForm.value)
        
        if (res.code === 200) {
          ElMessage.success('密码修改成功')
          passwordForm.value = {
            oldPassword: '',
            newPassword: '',
            confirmPassword: ''
          }
          // 更新密码修改提示状态
          needChangePassword.value = false
        } else {
          ElMessage.error(res.message || '密码修改失败')
        }
      } catch (error) {
        console.error('密码修改失败:', error)
        ElMessage.error('密码修改失败')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

// 上传对话框相关
const uploadDialogVisible = ref(false)
const cameraDialogVisible = ref(false)
const videoRef = ref(null)
const canvasRef = ref(null)
let stream = null

// 显示上传选择对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true
}

// 启动摄像头
const startCamera = async () => {
  try {
    uploadDialogVisible.value = false
    cameraDialogVisible.value = true
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: "user"
      }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.onloadeddata = () => {
        // 给父容器添加camera-ready类，触发就绪动画
        const container = videoRef.value.closest('.camera-container')
        if (container) {
          setTimeout(() => {
            container.classList.add('camera-ready')
          }, 300)
        }
      }
    }
  } catch (error) {
    ElMessage.error('无法访问摄像头，请检查设备权限')
    console.error('摄像头访问失败:', error)
    cameraDialogVisible.value = false
  }
}

// 停止摄像头
const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  cameraDialogVisible.value = false
}

// 拍照
const takePhoto = () => {
  if (!videoRef.value || !canvasRef.value) return
  
  captureLoading.value = true

  const video = videoRef.value
  const canvas = canvasRef.value
  const context = canvas.getContext('2d')

  // 设置canvas尺寸与视频一致
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  // 在canvas上绘制视频帧（需要水平翻转以匹配摄像头预览）
  context.translate(canvas.width, 0)
  context.scale(-1, 1)
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  // 恢复变换
  context.setTransform(1, 0, 0, 1, 0, 0)

  // 将canvas内容转换为blob
  canvas.toBlob(async (blob) => {
    try {
      // 创建表单数据
      const formData = new FormData()
      formData.append('file', blob, 'face.jpg')

      // 上传图片
      const response = await updateFace(formData)
      
      if (response.code === 200) {
        faceImage.value = response.data.faceImage
        // 更新用户信息中的人脸状态
        userInfo.value.has_face = true
        ElMessage.success('人脸录入成功')
        stopCamera()
      } else {
        ElMessage.error(response.message || '人脸录入失败')
      }
    } catch (error) {
      console.error('人脸录入失败:', error)
      ElMessage.error('人脸录入失败')
    } finally {
      captureLoading.value = false
    }
  }, 'image/jpeg', 0.95)
}

// 人脸上传相关方法
const beforeFaceUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  
  faceLoading.value = true
  return true
}

// 处理本地图片上传
const handleLocalImageUpload = async (options) => {
  try {
    faceLoading.value = true
    
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', options.file)
    
    // 上传图片
    const response = await updateFace(formData)
    
    if (response.code === 200) {
      faceImage.value = response.data.faceImage
      // 更新用户信息中的人脸状态
      userInfo.value.has_face = true
      ElMessage.success('人脸录入成功')
      uploadDialogVisible.value = false
    } else {
      ElMessage.error(response.message || '人脸录入失败')
    }
  } catch (error) {
    console.error('人脸录入失败:', error)
    ElMessage.error('人脸录入失败')
  } finally {
    faceLoading.value = false
  }
}

// 删除人脸数据
const handleDeleteFace = async () => {
  try {
    await ElMessageBox.confirm('确定要删除人脸识别数据吗？删除后将无法使用人脸登录。', '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    deleteLoading.value = true
    const res = await deleteFace()
    
    if (res.code === 200) {
      faceImage.value = defaultFaceImage
      // 更新用户信息中的人脸状态
      userInfo.value.has_face = false
      ElMessage.success('人脸数据删除成功')
    } else {
      ElMessage.error(res.message || '人脸数据删除失败')
    }
  } catch (error) {
    if (error !== 'cancel')
      ElMessage.error('人脸数据删除失败')
  } finally {
    deleteLoading.value = false
  }
}

// 重新加载页面
const reloadPage = () => {
  window.location.reload();
};

// 页面加载时获取用户信息
onMounted(() => {
  fetchUserInfo();
  
  // 设置页面可见性检测
  document.addEventListener('visibilitychange', handleVisibilityChange);
  
  // 如果5秒后还是加载状态，则尝试重新加载一次
  setTimeout(() => {
    if (isLoading.value) {
      console.log('页面加载超时，尝试重新获取数据');
      fetchUserInfo();
    }
  }, 5000);
});

// 页面卸载前清理
onBeforeUnmount(() => {
  // 停止摄像头
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  
  // 移除事件监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  
  // 清除可能存在的超时
  if (window._settingPageTimeout) {
    clearTimeout(window._settingPageTimeout);
    window._settingPageTimeout = null;
  }
});

// 处理页面可见性变化
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    // 页面变为可见时，重新加载用户信息
    if (initialized.value && hasError.value) {
      console.log('页面重新可见，尝试重新加载用户信息');
      fetchUserInfo();
    }
  }
};
</script>

<style>
@import '@/assets/setting.css';

.loading-container,
.error-container {
  width: 100%;
  min-height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.loading-container {
  padding: 30px;
}

.error-container {
  flex-direction: column;
}
</style>
