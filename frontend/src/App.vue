<template>
  <div v-if="$route.path === '/login'">
    <router-view></router-view>
  </div>
  <el-container v-else class="layout-container">
    <el-aside width="200px">
      <el-menu
        :router="true"
        class="el-menu-vertical"
        :background-color="'#545c64'"
        :text-color="'#fff'"
        :active-text-color="'#ffd04b'">
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/herbs">
          <el-icon><Monitor /></el-icon>
          <span>中药材识别</span>
        </el-menu-item>
        <el-menu-item index="/tongue">
          <el-icon><PictureRounded /></el-icon>
          <span>舌诊系统</span>
        </el-menu-item>
        <el-menu-item index="/ai-chat">
          <el-icon><ChatRound /></el-icon>
          <span>智能问诊</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Document /></el-icon>
          <span>中医知识库</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>中医药综合服务平台</h2>
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ displayUsername }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed, onErrorCaptured, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  House,
  Monitor,
  PictureRounded,
  ChatRound,
  Document,
  User
} from '@element-plus/icons-vue'

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

const router = useRouter()
const route = useRoute()

// 用户登录状态和信息
const isLoggedIn = ref(false)
const currentUsername = ref('')
// 页面错误状态
const hasError = ref(false)

// 监听路由变化，处理导航问题
watch(() => route.path, (newPath, oldPath) => {
  if (oldPath === '/setting' && newPath !== '/login') {
    console.log('检测到设置页面导航变化，从', oldPath, '到', newPath);
  }
})

// 计算属性：显示的用户名
const displayUsername = computed(() => {
  return currentUsername.value || '用户'
})

const handleCommand = async (command) => {
  try {
    switch (command) {
      case 'profile':
        router.push('/setting')
        break
      case 'logout':
        // 不再调用后端的登出接口，直接清除本地存储
        removeLocalStorageItem('token')
        removeLocalStorageItem('username')
        ElMessage.success('退出登录成功')
        router.push('/login')
        break
    }
  } catch (error) {
    console.error('处理命令失败:', error)
    // 如果是登出命令，确保清除本地存储
    if (command === 'logout') {
      removeLocalStorageItem('token')
      removeLocalStorageItem('username')
      router.push('/login')
    }
  }
}

// 全局错误处理
onErrorCaptured((err, instance, info) => {
  console.error('捕获到错误:', err, info);
  hasError.value = true;
  
  // 显示友好的错误消息
  ElMessage.error('应用发生错误，请刷新页面重试');
  
  // 阻止错误继续传播
  return false;
});

onMounted(() => {
  checkLoginStatus()
  
  // 添加全局点击事件处理，解决导航无响应问题
  document.addEventListener('click', (e) => {
    // 检查是否点击了菜单项
    const menuItem = e.target.closest('.el-menu-item');
    if (menuItem && hasError.value) {
      const href = menuItem.getAttribute('href');
      if (href) {
        e.preventDefault();
        console.log('检测到菜单点击，手动导航到:', href);
        window.location.href = href;
      }
    }
  });
})

// 检查登录状态
const checkLoginStatus = () => {
  const token = getLocalStorageItem('token')
  const username = getLocalStorageItem('username')
  
  if (token && username) {
    isLoggedIn.value = true
    currentUsername.value = username
  } else {
    isLoggedIn.value = false
    currentUsername.value = ''
    // 如果未登录且当前不在登录页面，则重定向到登录页
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-content {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  color: #4CAF50;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  color: #666;
}

.el-aside {
  background-color: #545c64;
}

.el-menu {
  border-right: none;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style> 