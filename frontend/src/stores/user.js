import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserInfo } from '@/api/user'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const menus = ref([])
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '')
  const avatar = computed(() => userInfo.value?.avatar || '')
  const role = computed(() => userInfo.value?.role || 'user')
  
  // 登录
  async function loginAction(loginForm) {
    try {
      const res = await login(loginForm)
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }
  
  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      userInfo.value = res
      return res
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }
  
  // 登出
  async function logoutAction(redirect = true) {
    try {
      await logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 清除本地状态
      token.value = ''
      userInfo.value = null
      menus.value = []
      localStorage.removeItem('token')
      if (redirect) {
        router.push('/login')
      }
    }
  }
  
  // 清除状态（不跳转）
  function clearState() {
    token.value = ''
    userInfo.value = null
    menus.value = []
    localStorage.removeItem('token')
  }
  
  // 设置菜单
  function setMenus(menuList) {
    menus.value = menuList
  }
  
  return {
    token,
    userInfo,
    menus,
    isLoggedIn,
    username,
    avatar,
    role,
    loginAction,
    fetchUserInfo,
    logoutAction,
    setMenus,
    clearState
  }
})
