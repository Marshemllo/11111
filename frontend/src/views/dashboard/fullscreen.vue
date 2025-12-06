<template>
  <div class="fullscreen-dashboard">
    <!-- 顶部标题 -->
    <div class="dashboard-header">
      <h1>智能数据分析平台</h1>
      <div class="header-right">
        <span class="current-time">{{ currentTime }}</span>
        <el-button type="primary" link @click="exitFullscreen">
          <el-icon><Close /></el-icon>
          退出
        </el-button>
      </div>
    </div>
    
    <!-- 主内容区 -->
    <div class="dashboard-content">
      <!-- 左侧 -->
      <div class="left-panel">
        <div class="panel-item">
          <div class="panel-title">数据概览</div>
          <div class="stat-grid">
            <div class="stat-item">
              <div class="stat-value">{{ summary.total_reports || 0 }}</div>
              <div class="stat-label">报告总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ summary.total_spiders || 0 }}</div>
              <div class="stat-label">爬虫数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ summary.today_reports || 0 }}</div>
              <div class="stat-label">今日报告</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ summary.active_spiders || 0 }}</div>
              <div class="stat-label">运行中</div>
            </div>
          </div>
        </div>
        
        <div class="panel-item">
          <div class="panel-title">行业分布</div>
          <div ref="pieChartRef" class="chart-box"></div>
        </div>
        
        <div class="panel-item">
          <div class="panel-title">实时动态</div>
          <div class="activity-list">
            <div v-for="(item, index) in activities" :key="index" class="activity-item">
              <span class="activity-time">{{ item.time }}</span>
              <span class="activity-text">{{ item.text }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 中间 -->
      <div class="center-panel">
        <div class="panel-item map-panel">
          <div class="panel-title">数据地图</div>
          <div ref="mapChartRef" class="chart-box"></div>
        </div>
        
        <div class="panel-item">
          <div class="panel-title">数据趋势</div>
          <div ref="trendChartRef" class="chart-box"></div>
        </div>
      </div>
      
      <!-- 右侧 -->
      <div class="right-panel">
        <div class="panel-item">
          <div class="panel-title">排行榜</div>
          <div class="ranking-list">
            <div v-for="(item, index) in rankings" :key="index" class="ranking-item">
              <span class="ranking-index" :class="'top-' + (index + 1)">{{ index + 1 }}</span>
              <span class="ranking-name">{{ item.name }}</span>
              <span class="ranking-value">{{ item.value }}</span>
            </div>
          </div>
        </div>
        
        <div class="panel-item">
          <div class="panel-title">数据统计</div>
          <div ref="barChartRef" class="chart-box"></div>
        </div>
        
        <div class="panel-item">
          <div class="panel-title">AI分析</div>
          <div class="ai-panel">
            <el-input
              v-model="aiQuery"
              placeholder="输入分析需求..."
              @keyup.enter="handleAIQuery"
            />
            <div v-if="aiResponse" class="ai-response">{{ aiResponse }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

const currentTime = ref('')
const summary = ref({
  total_reports: 1234,
  total_spiders: 56,
  today_reports: 23,
  active_spiders: 8
})

const activities = ref([
  { time: '10:30', text: '新增报告《2024年行业分析》' },
  { time: '10:25', text: '爬虫任务完成，获取数据1000条' },
  { time: '10:20', text: '用户张三登录系统' },
  { time: '10:15', text: 'AI生成报告完成' },
  { time: '10:10', text: '新增数据源：新闻网站' }
])

const rankings = ref([
  { name: '科技行业', value: 2345 },
  { name: '金融行业', value: 1890 },
  { name: '医疗行业', value: 1567 },
  { name: '教育行业', value: 1234 },
  { name: '制造行业', value: 987 }
])

const aiQuery = ref('')
const aiResponse = ref('')

const pieChartRef = ref(null)
const mapChartRef = ref(null)
const trendChartRef = ref(null)
const barChartRef = ref(null)

let charts = []
let timeInterval = null

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 初始化图表
const initCharts = () => {
  // 饼图
  if (pieChartRef.value) {
    const pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 1048, name: '科技', itemStyle: { color: '#5470c6' } },
          { value: 735, name: '金融', itemStyle: { color: '#91cc75' } },
          { value: 580, name: '医疗', itemStyle: { color: '#fac858' } },
          { value: 484, name: '教育', itemStyle: { color: '#ee6666' } },
          { value: 300, name: '其他', itemStyle: { color: '#73c0de' } }
        ]
      }]
    })
    charts.push(pieChart)
  }
  
  // 趋势图
  if (trendChartRef.value) {
    const trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月'],
        axisLine: { lineStyle: { color: '#fff' } }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#fff' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      series: [{
        data: [820, 932, 901, 934, 1290, 1330],
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        }
      }]
    })
    charts.push(trendChart)
  }
  
  // 柱状图
  if (barChartRef.value) {
    const barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['报告', '爬虫', '用户', '数据源'],
        axisLine: { lineStyle: { color: '#fff' } }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#fff' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      series: [{
        data: [120, 56, 89, 34],
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }]
    })
    charts.push(barChart)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  charts.forEach(chart => chart?.resize())
}

// 退出全屏
const exitFullscreen = () => {
  router.push('/dashboard')
}

// AI查询
const handleAIQuery = () => {
  if (!aiQuery.value.trim()) return
  aiResponse.value = `正在分析: ${aiQuery.value}...`
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  setTimeout(initCharts, 100)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(timeInterval)
  window.removeEventListener('resize', handleResize)
  charts.forEach(chart => chart?.dispose())
})
</script>

<style lang="scss" scoped>
.fullscreen-dashboard {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  overflow: hidden;
  
  .dashboard-header {
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 30px;
    background: rgba(0, 0, 0, 0.3);
    
    h1 {
      font-size: 24px;
      background: linear-gradient(90deg, #00d2ff, #3a7bd5);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .current-time {
        font-size: 16px;
        color: #00d2ff;
      }
    }
  }
  
  .dashboard-content {
    display: flex;
    height: calc(100vh - 60px);
    padding: 20px;
    gap: 20px;
    
    .left-panel, .right-panel {
      width: 25%;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    
    .center-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    
    .panel-item {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 16px;
      flex: 1;
      display: flex;
      flex-direction: column;
      
      &.map-panel {
        flex: 2;
      }
      
      .panel-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 12px;
        color: #00d2ff;
        border-left: 3px solid #00d2ff;
        padding-left: 10px;
      }
      
      .chart-box {
        flex: 1;
        min-height: 150px;
      }
    }
    
    .stat-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      
      .stat-item {
        text-align: center;
        padding: 16px;
        background: rgba(0, 210, 255, 0.1);
        border-radius: 8px;
        
        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #00d2ff;
        }
        
        .stat-label {
          font-size: 12px;
          color: #aaa;
          margin-top: 4px;
        }
      }
    }
    
    .activity-list {
      .activity-item {
        display: flex;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 12px;
        
        .activity-time {
          color: #00d2ff;
          margin-right: 10px;
        }
        
        .activity-text {
          color: #ccc;
        }
      }
    }
    
    .ranking-list {
      .ranking-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        
        .ranking-index {
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          margin-right: 10px;
          font-size: 12px;
          background: rgba(255, 255, 255, 0.1);
          
          &.top-1 { background: #f5a623; color: #fff; }
          &.top-2 { background: #c0c0c0; color: #fff; }
          &.top-3 { background: #cd7f32; color: #fff; }
        }
        
        .ranking-name {
          flex: 1;
          color: #ccc;
        }
        
        .ranking-value {
          color: #00d2ff;
        }
      }
    }
    
    .ai-panel {
      .ai-response {
        margin-top: 12px;
        padding: 12px;
        background: rgba(0, 210, 255, 0.1);
        border-radius: 8px;
        font-size: 14px;
        color: #ccc;
      }
    }
  }
}
</style>
