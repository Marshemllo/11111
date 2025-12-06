<template>
  <div class="login-page">
    <!-- 登录页面容器 -->
    <div class="login-container">
      <!-- 左侧数据可视化区域 -->
      <div class="left-panel">
        <div class="left-content">
          <!-- 标题区域 -->
          <div class="header-section">
            <div class="logo-wrapper">
              <div class="logo-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <h1 class="platform-title">智能数据分析平台</h1>
            </div>
            <h2 class="main-title">数据驱动决策<br>智慧引领未来</h2>
            <p class="description">集成数据采集、分析、可视化于一体的智能数据管理平台，助力科学决策与高效治理</p>
          </div>

          <!-- 数据可视化图表 -->
          <div class="charts-section">
            <!-- 数据增长趋势图 -->
            <div class="chart-card">
              <h3 class="chart-title"><i class="fas fa-chart-bar"></i> 数据增长趋势</h3>
              <div class="chart-container" ref="growthChartRef"></div>
            </div>
            <!-- 小图表 -->
            <div class="small-charts">
              <div class="chart-card small">
                <h3 class="chart-title"><i class="fas fa-chart-pie"></i> 数据分布</h3>
                <div class="chart-container" ref="distributionChartRef"></div>
              </div>
              <div class="chart-card small">
                <h3 class="chart-title"><i class="fas fa-chart-line"></i> 舆情指数</h3>
                <div class="chart-container" ref="sentimentChartRef"></div>
              </div>
            </div>
          </div>

          <!-- 底部版权 -->
          <div class="footer-section">
            <p>© 2024 智能数据分析平台. 保留所有权利.</p>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单区域 -->
      <div class="right-panel">
        <!-- 移动端标题 -->
        <div class="mobile-header">
          <div class="logo-icon small">
            <i class="fas fa-chart-line"></i>
          </div>
          <h1>智能数据分析平台</h1>
        </div>

        <!-- 登录表单 -->
        <div class="form-wrapper">
          <h2 class="form-title">欢迎登录</h2>
          <p class="form-subtitle">请输入您的账号信息以继续</p>

          <form class="login-form" @submit.prevent="handleLogin">
            <!-- 用户名 -->
            <div class="form-group">
              <label for="username">用户名</label>
              <div class="input-wrapper">
                <i class="fas fa-user input-icon"></i>
                <input
                  id="username"
                  v-model="loginForm.username"
                  type="text"
                  placeholder="请输入用户名"
                  required
                />
              </div>
            </div>

            <!-- 密码 -->
            <div class="form-group">
              <div class="label-row">
                <label for="password">密码</label>
                <a href="javascript:void(0);" class="forgot-link">忘记密码?</a>
              </div>
              <div class="input-wrapper">
                <i class="fas fa-lock input-icon"></i>
                <input
                  id="password"
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  required
                />
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  <i :class="showPassword ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
                </button>
              </div>
            </div>

            <!-- 记住我 -->
            <div class="remember-row">
              <label class="checkbox-wrapper">
                <input type="checkbox" v-model="rememberMe" />
                <span>记住我</span>
              </label>
            </div>

            <!-- 登录按钮 -->
            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="!loading">登录</span>
              <span v-else><i class="fas fa-spinner fa-spin"></i> 登录中...</span>
              <i v-if="!loading" class="fas fa-arrow-right btn-arrow"></i>
            </button>

            <!-- 其他登录方式 -->
            <div class="divider">
              <span>其他登录方式</span>
            </div>
            <div class="other-login">
              <button type="button" class="other-btn">
                <i class="fas fa-qrcode"></i>
              </button>
              <button type="button" class="other-btn">
                <i class="fas fa-id-card"></i>
              </button>
            </div>
          </form>

          <!-- 帮助信息 -->
          <div class="help-section">
            <p>如需账号请联系管理员</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div class="toast" :class="{ show: toast.visible }">
      <div class="toast-icon" :class="toast.type">
        <i :class="toast.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
      </div>
      <div class="toast-content">
        <h4>{{ toast.title }}</h4>
        <p>{{ toast.message }}</p>
      </div>
      <button class="toast-close" @click="toast.visible = false">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})
const showPassword = ref(false)
const rememberMe = ref(false)
const loading = ref(false)

// Toast 提示
const toast = reactive({
  visible: false,
  type: 'success',
  title: '',
  message: ''
})

// 图表引用
const growthChartRef = ref(null)
const distributionChartRef = ref(null)
const sentimentChartRef = ref(null)
let growthChart = null
let distributionChart = null
let sentimentChart = null

// 显示 Toast
const showToast = (title, message, type = 'success') => {
  toast.title = title
  toast.message = message
  toast.type = type
  toast.visible = true
  setTimeout(() => {
    toast.visible = false
  }, 3000)
}

// 登录处理
const handleLogin = async () => {
  if (!loginForm.username) {
    showToast('输入错误', '请输入用户名', 'error')
    return
  }
  if (!loginForm.password) {
    showToast('输入错误', '请输入密码', 'error')
    return
  }

  loading.value = true
  try {
    await userStore.loginAction(loginForm)
    showToast('登录成功', '正在跳转至系统首页...')
    setTimeout(() => {
      const redirect = route.query.redirect || '/dashboard'
      router.push(redirect)
    }, 1000)
  } catch (error) {
    showToast('登录失败', error.response?.data?.detail || '用户名或密码错误', 'error')
    loading.value = false
  }
}

// 初始化图表
const initCharts = () => {
  if (window.innerWidth < 1024) return

  // 数据增长趋势图
  if (growthChartRef.value) {
    growthChart = echarts.init(growthChartRef.value)
    growthChart.setOption({
      grid: { top: '10%', left: '5%', right: '5%', bottom: '15%', containLabel: true },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        textStyle: { color: '#fff' },
        borderColor: 'rgba(255, 255, 255, 0.3)'
      },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月'],
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.7)' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisLabel: { color: 'rgba(255, 255, 255, 0.7)', formatter: '{value}万' },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
      },
      series: [{
        type: 'bar',
        data: [120, 190, 150, 230, 290, 320],
        barWidth: '60%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 255, 255, 0.8)' },
            { offset: 1, color: 'rgba(255, 255, 255, 0.2)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }]
    })
  }

  // 数据分布饼图
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(255, 255, 255, 0.2)', textStyle: { color: '#fff' } },
      legend: { bottom: 0, textStyle: { color: 'rgba(255, 255, 255, 0.7)', fontSize: 10 }, itemWidth: 8, itemHeight: 8 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: { borderRadius: 4, borderColor: 'rgba(255, 255, 255, 0.1)', borderWidth: 2 },
        label: { show: false },
        data: [
          { value: 35, name: '结构化', itemStyle: { color: 'rgba(255, 255, 255, 0.8)' } },
          { value: 25, name: '非结构化', itemStyle: { color: 'rgba(255, 255, 255, 0.6)' } },
          { value: 20, name: '半结构化', itemStyle: { color: 'rgba(255, 255, 255, 0.4)' } },
          { value: 20, name: '实时流', itemStyle: { color: 'rgba(255, 255, 255, 0.2)' } }
        ]
      }]
    })
  }

  // 舆情指数折线图
  if (sentimentChartRef.value) {
    sentimentChart = echarts.init(sentimentChartRef.value)
    sentimentChart.setOption({
      grid: { top: '10%', left: '5%', right: '5%', bottom: '15%', containLabel: true },
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(255, 255, 255, 0.2)', textStyle: { color: '#fff' } },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.7)', fontSize: 10 }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLine: { show: false },
        axisLabel: { color: 'rgba(255, 255, 255, 0.7)', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
      },
      series: [{
        type: 'line',
        data: [65, 59, 80, 81, 56, 55, 72],
        smooth: true,
        lineStyle: { width: 3, color: 'rgba(255, 255, 255, 0.8)' },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#fff', borderWidth: 2, borderColor: 'rgba(255, 255, 255, 0.5)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 255, 255, 0.3)' },
            { offset: 1, color: 'rgba(255, 255, 255, 0)' }
          ])
        }
      }]
    })
  }
}

// 窗口大小变化时重新调整图表
const handleResize = () => {
  growthChart?.resize()
  distributionChart?.resize()
  sentimentChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  growthChart?.dispose()
  distributionChart?.dispose()
  sentimentChart?.dispose()
})
</script>

<style lang="scss" scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: #f3f4f6;
  font-family: 'Inter', system-ui, sans-serif;
}

.login-container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

// 左侧面板
.left-panel {
  width: 50%;
  background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);
  padding: 3rem;
  color: #fff;
  display: none;

  @media (min-width: 1024px) {
    display: block;
  }
}

.left-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.header-section {
  .logo-wrapper {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
  }

  .logo-icon {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    font-size: 1.25rem;

    &.small {
      width: 2.5rem;
      height: 2.5rem;
      background: #165DFF;
      color: #fff;
    }
  }

  .platform-title {
    font-size: 1.5rem;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .main-title {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1rem;
  }

  .description {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.125rem;
    max-width: 400px;
  }
}

.charts-section {
  margin-top: 2rem;
}

.chart-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }

  &.small {
    flex: 1;
  }

  .chart-title {
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;

    i {
      margin-right: 0.5rem;
    }
  }

  .chart-container {
    height: 180px;
  }
}

.small-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;

  .chart-container {
    height: 140px;
  }
}

.footer-section {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);

  p {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.875rem;
  }
}

// 右侧面板
.right-panel {
  width: 100%;
  padding: 2rem 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #f9fafb;

  @media (min-width: 1024px) {
    width: 50%;
  }
}

.mobile-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;

  @media (min-width: 1024px) {
    display: none;
  }

  h1 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1f2937;
    margin-left: 0.75rem;
  }
}

.form-wrapper {
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #6b7280;
  margin-bottom: 2rem;
}

.login-form {
  .form-group {
    margin-bottom: 1.5rem;

    label {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
      color: #374151;
      margin-bottom: 0.25rem;
    }

    .label-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.25rem;
    }

    .forgot-link {
      font-size: 0.875rem;
      color: #4A90E2;
      text-decoration: none;

      &:hover {
        color: #357ABD;
      }
    }
  }

  .input-wrapper {
    position: relative;

    .input-icon {
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      color: #9ca3af;
    }

    input {
      width: 100%;
      padding: 0.75rem 2.5rem;
      border: 1px solid #d1d5db;
      border-radius: 0.5rem;
      font-size: 1rem;
      transition: all 0.3s ease;
      background: #fff;

      &:focus {
        outline: none;
        border-color: #4A90E2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
      }

      &::placeholder {
        color: #9ca3af;
      }
    }

    .toggle-password {
      position: absolute;
      right: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: #9ca3af;
      cursor: pointer;

      &:hover {
        color: #6b7280;
      }
    }
  }

  .remember-row {
    margin-bottom: 1rem;

    .checkbox-wrapper {
      display: flex;
      align-items: center;
      cursor: pointer;

      input {
        width: 1rem;
        height: 1rem;
        margin-right: 0.5rem;
        accent-color: #4A90E2;
      }

      span {
        font-size: 0.875rem;
        color: #374151;
      }
    }
  }

  .login-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    background: #4A90E2;
    color: #fff;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;

    &:hover:not(:disabled) {
      background: #357ABD;
    }

    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .btn-arrow {
      margin-left: 0.5rem;
      transition: transform 0.3s ease;
    }

    &:hover .btn-arrow {
      transform: translateX(4px);
    }
  }

  .divider {
    position: relative;
    margin: 1.5rem 0;
    text-align: center;

    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: #d1d5db;
    }

    span {
      position: relative;
      padding: 0 0.5rem;
      background: #f9fafb;
      color: #6b7280;
      font-size: 0.875rem;
    }
  }

  .other-login {
    display: flex;
    justify-content: center;
    gap: 1rem;

    .other-btn {
      width: 3rem;
      height: 3rem;
      border-radius: 50%;
      border: 1px solid #d1d5db;
      background: #fff;
      color: #6b7280;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #E8F3FF;
        color: #4A90E2;
        border-color: rgba(74, 144, 226, 0.3);
      }
    }
  }
}

.help-section {
  margin-top: 2.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;

  a {
    color: #4A90E2;
    text-decoration: none;

    &:hover {
      color: #357ABD;
    }
  }
}

// Toast 提示
.toast {
  position: fixed;
  top: 1rem;
  right: 1rem;
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 1rem;
  display: flex;
  align-items: center;
  max-width: 350px;
  transform: translateX(120%);
  transition: transform 0.3s ease;
  z-index: 1000;

  &.show {
    transform: translateX(0);
  }

  .toast-icon {
    margin-right: 0.75rem;
    font-size: 1.25rem;

    &.success {
      color: #00B42A;
    }

    &.error {
      color: #F53F3F;
    }
  }

  .toast-content {
    flex: 1;

    h4 {
      font-weight: 500;
      color: #1f2937;
      margin-bottom: 0.25rem;
    }

    p {
      font-size: 0.875rem;
      color: #6b7280;
    }
  }

  .toast-close {
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    margin-left: 1rem;

    &:hover {
      color: #6b7280;
    }
  }
}
</style>
