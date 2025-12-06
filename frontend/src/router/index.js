import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/login/register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据大屏', icon: 'DataBoard' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/index.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'menus',
        name: 'Menus',
        component: () => import('@/views/menus/index.vue'),
        meta: { title: '菜单管理', icon: 'Menu' }
      },
      {
        path: 'spiders',
        name: 'Spiders',
        component: () => import('@/views/spiders/index.vue'),
        meta: { title: '爬虫管理', icon: 'Connection' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/reports/index.vue'),
        meta: { title: '报告管理', icon: 'Document' }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/chat/index.vue'),
        meta: { title: '在线聊天', icon: 'ChatDotRound' }
      }
    ]
  },
  {
    path: '/fullscreen-dashboard',
    name: 'FullscreenDashboard',
    component: () => import('@/views/dashboard/fullscreen.vue'),
    meta: { title: '数据大屏', requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 智能数据分析平台` : '智能数据分析平台'
  
  const userStore = useUserStore()
  const token = userStore.token
  
  // 不需要认证的页面
  if (to.meta.requiresAuth === false) {
    if (token && (to.name === 'Login' || to.name === 'Register')) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
    return
  }
  
  // 需要认证的页面
  if (!token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
