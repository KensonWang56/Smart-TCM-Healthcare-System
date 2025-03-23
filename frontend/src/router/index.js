import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import HerbIdentification from '../views/HerbIdentification.vue'
import TongueDiagnosis from '../views/TongueDiagnosis.vue'
import AIChat from '../views/AIChat.vue'
import Knowledge from '../views/Knowledge.vue'
import Setting from '../views/setting.vue'

// 安全获取localStorage数据的方法
const getLocalStorageItem = (key) => {
  try {
    return window.localStorage.getItem(key)
  } catch (e) {
    console.error('无法访问localStorage:', e)
    return null
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/herbs',
      name: 'herbs',
      component: HerbIdentification,
      meta: { requiresAuth: true }
    },
    {
      path: '/tongue',
      name: 'tongue',
      component: TongueDiagnosis,
      meta: { requiresAuth: true }
    },
    {
      path: '/ai-chat',
      name: 'ai-chat',
      component: AIChat,
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: Knowledge,
      meta: { requiresAuth: true }
    },
    {
      path: '/setting',
      name: 'setting',
      component: Setting,
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

let isRedirectingToLogin = false;

router.beforeEach((to, from, next) => {
  if (from.path === '/setting' && to.path !== '/setting' && to.path !== '/login') {
    console.log('检测到从设置页面跳转失败，尝试手动导航');
    next();
    return;
  }

  if (to.path === '/login') {
    isRedirectingToLogin = false;
    next();
    return;
  }
  
  const token = getLocalStorageItem('token');
  
  if (!token && !isRedirectingToLogin) {
    isRedirectingToLogin = true;
    next('/login');
    return;
  }
  
  next();
})

export default router 