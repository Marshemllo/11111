<template>
  <div class="bigscreen-container">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="header-left">
        <span class="logo">📊</span>
      </div>
      <div class="header-center">
        <h1>政企舆情大数据监控大屏</h1>
      </div>
      <div class="header-right">
        <span class="time">{{ currentTime }}</span>
        <el-button type="primary" link @click="toggleMapType" class="switch-btn">
          {{ mapType === '2d' ? '切换3D地球' : '切换2D地图' }}
        </el-button>
        <el-button type="primary" link @click="exitScreen">
          <el-icon><Close /></el-icon>
          退出
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧面板 -->
      <div class="left-panel">
        <!-- 全国舆情热力分布 -->
        <div class="panel-card map-card">
          <div class="panel-header">
            <span class="panel-title">全国舆情热力分布 (AI 驱动实时分析)</span>
          </div>
          <div class="panel-body">
            <!-- 2D地图 -->
            <div v-show="mapType === '2d'" ref="map2dRef" class="chart-container"></div>
            <!-- 3D地球 -->
            <div v-show="mapType === '3d'" ref="globe3dRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 底部图表区 -->
        <div class="bottom-charts">
          <!-- 行业分布饼图 -->
          <div class="panel-card">
            <div class="panel-header">
              <span class="panel-title">行业分布</span>
            </div>
            <div class="panel-body">
              <div ref="pieChartRef" class="chart-container"></div>
            </div>
          </div>

          <!-- 数据趋势柱状图 -->
          <div class="panel-card">
            <div class="panel-header">
              <span class="panel-title">数据趋势</span>
            </div>
            <div class="panel-body">
              <div ref="barChartRef" class="chart-container"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <!-- 实时采集资讯 Top 20 -->
        <div class="panel-card news-card">
          <div class="panel-header">
            <span class="panel-title">实时采集资讯 (Top 20)</span>
            <el-button type="primary" link size="small" @click="refreshLatestData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          <div class="panel-body">
            <div class="news-list" ref="newsListRef">
              <div 
                v-for="(item, index) in latestNews" 
                :key="item.id" 
                class="news-item"
                @click="openNews(item)"
              >
                <div class="news-title">{{ item.title }}</div>
                <div class="news-meta">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatTime(item.time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI分析面板 -->
        <div class="panel-card ai-card">
          <div class="panel-header">
            <span class="panel-title">AI 智能分析</span>
          </div>
          <div class="panel-body">
            <div class="ai-input">
              <el-input
                v-model="aiQuery"
                placeholder="输入分析需求，如：分析今日热点趋势..."
                @keyup.enter="handleAIAnalysis"
              >
                <template #append>
                  <el-button @click="handleAIAnalysis" :loading="aiLoading">
                    <el-icon><Search /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </div>
            <div v-if="aiResult" class="ai-result">
              <div class="ai-result-content">{{ aiResult }}</div>
            </div>
          </div>
        </div>

        <!-- 地区热度排行 -->
        <div class="panel-card ranking-card">
          <div class="panel-header">
            <span class="panel-title">地区热度排行</span>
          </div>
          <div class="panel-body">
            <div class="ranking-list">
              <div 
                v-for="(item, index) in regionRanking" 
                :key="item.name" 
                class="ranking-item"
              >
                <span class="ranking-index" :class="'top-' + (index + 1)">{{ index + 1 }}</span>
                <span class="ranking-name">{{ item.name }}</span>
                <div class="ranking-bar">
                  <div 
                    class="ranking-bar-inner" 
                    :style="{ width: (item.value / maxRankingValue * 100) + '%' }"
                  ></div>
                </div>
                <span class="ranking-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import 'echarts-gl'
import { Close, Refresh, Clock, Search } from '@element-plus/icons-vue'
import { 
  getHeatmapData, 
  getLatestData, 
  getIndustryDistribution, 
  getTrendData,
  getRankingData,
  aiDataAnalysis 
} from '@/api/dashboard'

const router = useRouter()

// 响应式数据
const currentTime = ref('')
const mapType = ref('2d')
const latestNews = ref([])
const regionRanking = ref([])
const aiQuery = ref('')
const aiResult = ref('')
const aiLoading = ref(false)
const heatmapData = ref([])

// DOM引用
const map2dRef = ref(null)
const globe3dRef = ref(null)
const pieChartRef = ref(null)
const barChartRef = ref(null)
const newsListRef = ref(null)

// 图表实例
let map2dChart = null
let globe3dChart = null
let pieChart = null
let barChart = null
let timeInterval = null
let scrollInterval = null

// 计算最大排行值
const maxRankingValue = computed(() => {
  if (regionRanking.value.length === 0) return 1
  return Math.max(...regionRanking.value.map(item => item.value))
})

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

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 切换地图类型
const toggleMapType = () => {
  mapType.value = mapType.value === '2d' ? '3d' : '2d'
  nextTick(() => {
    if (mapType.value === '2d') {
      map2dChart?.resize()
    } else {
      globe3dChart?.resize()
    }
  })
}

// 退出大屏
const exitScreen = () => {
  router.push('/dashboard')
}

// 打开新闻链接
const openNews = (item) => {
  if (item.url) {
    window.open(item.url, '_blank')
  }
}

// 加载热力数据
const loadHeatmapData = async () => {
  try {
    const res = await getHeatmapData()
    if (res.code === 200) {
      heatmapData.value = res.data.regions
      init2DMap()
      init3DGlobe()
    }
  } catch (error) {
    console.error('加载热力数据失败:', error)
    // 使用模拟数据
    generateMockHeatmapData()
  }
}

// 生成模拟热力数据
const generateMockHeatmapData = () => {
  const provinces = [
    { name: '北京', lng: 116.405285, lat: 39.904989 },
    { name: '上海', lng: 121.472644, lat: 31.231706 },
    { name: '广东', lng: 113.280637, lat: 23.125178 },
    { name: '浙江', lng: 120.153576, lat: 30.287459 },
    { name: '江苏', lng: 118.767413, lat: 32.041544 },
    { name: '四川', lng: 104.065735, lat: 30.659462 },
    { name: '山东', lng: 117.000923, lat: 36.675807 },
    { name: '河南', lng: 113.665412, lat: 34.757975 },
    { name: '湖北', lng: 114.298572, lat: 30.584355 },
    { name: '福建', lng: 119.306239, lat: 26.075302 },
  ]
  
  heatmapData.value = provinces.map(p => ({
    ...p,
    value: Math.floor(Math.random() * 1500) + 500
  }))
  
  init2DMap()
  init3DGlobe()
}

// 加载最新数据
const refreshLatestData = async () => {
  try {
    const res = await getLatestData(20)
    if (res.code === 200) {
      latestNews.value = res.data
    }
  } catch (error) {
    console.error('加载最新数据失败:', error)
    // 使用模拟数据
    generateMockLatestData()
  }
}

// 生成模拟最新数据
const generateMockLatestData = () => {
  const titles = [
    '准备开抢！成都电影、餐饮、汽车消费券来了',
    '网络不给力，请稍后重试',
    '深耕域沃土 铸就金融标杆：银行业高质量发展纪实',
    '时尚WEEKLY | 迪桑特"精工极致"系列全新上市',
    '成都至阿拉木图航线开航 执飞机型为空客A320',
    '2024年度十大科技突破盘点',
    '人工智能赋能传统产业转型升级',
    '新能源汽车销量再创新高',
    '数字经济发展报告发布',
    '智慧城市建设加速推进',
  ]
  
  const now = new Date()
  latestNews.value = titles.map((title, index) => ({
    id: index + 1,
    title,
    time: new Date(now - index * 60000 * Math.random() * 10).toISOString(),
    url: '#'
  }))
}

// 加载排行数据
const loadRankingData = async () => {
  try {
    const res = await getRankingData({ ranking_type: 'region', limit: 10 })
    if (res.code === 200) {
      regionRanking.value = res.data
    }
  } catch (error) {
    console.error('加载排行数据失败:', error)
    // 使用模拟数据
    regionRanking.value = [
      { name: '广东', value: 1856 },
      { name: '北京', value: 1723 },
      { name: '上海', value: 1654 },
      { name: '浙江', value: 1432 },
      { name: '江苏', value: 1321 },
    ]
  }
}

// AI分析
const handleAIAnalysis = async () => {
  if (!aiQuery.value.trim()) return
  
  aiLoading.value = true
  try {
    const res = await aiDataAnalysis({ query: aiQuery.value })
    if (res.code === 200) {
      aiResult.value = res.data.analysis
    }
  } catch (error) {
    console.error('AI分析失败:', error)
    aiResult.value = '分析请求失败，请稍后重试'
  } finally {
    aiLoading.value = false
  }
}

// 初始化2D地图
const init2DMap = async () => {
  if (!map2dRef.value) return
  
  // 动态加载中国地图数据
  try {
    const chinaJson = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    const chinaData = await chinaJson.json()
    echarts.registerMap('china', chinaData)
  } catch (error) {
    console.error('加载地图数据失败:', error)
  }
  
  map2dChart = echarts.init(map2dRef.value)
  
  const mapData = heatmapData.value.map(item => ({
    name: item.name,
    value: item.value
  }))
  
  const scatterData = heatmapData.value.map(item => ({
    name: item.name,
    value: [item.lng, item.lat, item.value]
  }))
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.seriesType === 'scatter') {
          return `${params.name}<br/>热度: ${params.value[2]}`
        }
        return `${params.name}<br/>热度: ${params.value || 0}`
      }
    },
    visualMap: {
      min: 0,
      max: 2000,
      left: 20,
      bottom: 20,
      text: ['高', '低'],
      textStyle: { color: '#fff' },
      inRange: {
        color: ['#0d3c55', '#1a5a7a', '#2d8a9e', '#4fc3c7', '#80deea']
      },
      show: true
    },
    geo: {
      map: 'china',
      roam: true,
      zoom: 1.2,
      center: [104.114129, 37.550339],
      label: {
        show: true,
        color: 'rgba(255,255,255,0.6)',
        fontSize: 10
      },
      itemStyle: {
        areaColor: '#0d3c55',
        borderColor: '#1a8a9e',
        borderWidth: 1
      },
      emphasis: {
        label: { color: '#fff' },
        itemStyle: {
          areaColor: '#2d8a9e'
        }
      }
    },
    series: [
      {
        name: '热度',
        type: 'map',
        map: 'china',
        geoIndex: 0,
        data: mapData
      },
      {
        name: '热点',
        type: 'scatter',
        coordinateSystem: 'geo',
        data: scatterData,
        symbolSize: (val) => Math.max(val[2] / 100, 8),
        itemStyle: {
          color: '#00d2ff',
          shadowBlur: 10,
          shadowColor: '#00d2ff'
        },
        label: {
          show: false
        }
      },
      {
        name: '涟漪',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: scatterData.slice(0, 5),
        symbolSize: (val) => Math.max(val[2] / 80, 10),
        rippleEffect: {
          brushType: 'stroke',
          scale: 4,
          period: 4
        },
        itemStyle: {
          color: '#00d2ff',
          shadowBlur: 10,
          shadowColor: '#00d2ff'
        }
      }
    ]
  }
  
  map2dChart.setOption(option)
}

// 初始化3D地球
const init3DGlobe = () => {
  if (!globe3dRef.value) return
  
  globe3dChart = echarts.init(globe3dRef.value)
  
  const scatterData = heatmapData.value.map(item => ({
    name: item.name,
    value: [item.lng, item.lat, item.value]
  }))
  
  const option = {
    backgroundColor: 'transparent',
    globe: {
      baseTexture: 'https://cdn.jsdelivr.net/gh/apache/echarts-website@asf-site/examples/data-gl/asset/world.topo.bathy.200401.jpg',
      heightTexture: 'https://cdn.jsdelivr.net/gh/apache/echarts-website@asf-site/examples/data-gl/asset/bathymetry_bw_composite_4k.jpg',
      displacementScale: 0.04,
      shading: 'realistic',
      environment: 'https://cdn.jsdelivr.net/gh/apache/echarts-website@asf-site/examples/data-gl/asset/starfield.jpg',
      realisticMaterial: {
        roughness: 0.9
      },
      postEffect: {
        enable: true,
        bloom: {
          enable: true,
          strength: 0.1
        }
      },
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 3,
        distance: 200,
        alpha: 30,
        beta: 160
      },
      light: {
        main: {
          intensity: 2,
          shadow: true
        },
        ambient: {
          intensity: 0.5
        }
      }
    },
    series: [
      {
        type: 'scatter3D',
        coordinateSystem: 'globe',
        blendMode: 'lighter',
        symbolSize: (val) => Math.max(val[2] / 50, 5),
        itemStyle: {
          color: '#00d2ff',
          opacity: 0.8
        },
        data: scatterData
      },
      {
        type: 'lines3D',
        coordinateSystem: 'globe',
        blendMode: 'lighter',
        lineStyle: {
          width: 2,
          color: '#00d2ff',
          opacity: 0.6
        },
        effect: {
          show: true,
          period: 4,
          trailWidth: 4,
          trailLength: 0.2,
          trailOpacity: 0.5,
          trailColor: '#00d2ff'
        },
        data: scatterData.slice(0, 5).map((item, index) => {
          const next = scatterData[(index + 1) % 5]
          return {
            coords: [
              [item.value[0], item.value[1]],
              [next.value[0], next.value[1]]
            ]
          }
        })
      }
    ]
  }
  
  globe3dChart.setOption(option)
}

// 初始化饼图
const initPieChart = async () => {
  if (!pieChartRef.value) return
  
  pieChart = echarts.init(pieChartRef.value)
  
  let data = []
  try {
    const res = await getIndustryDistribution()
    data = res.data || []
  } catch (error) {
    data = [
      { name: '科技', value: 1548 },
      { name: '金融', value: 1235 },
      { name: '医疗', value: 980 },
      { name: '教育', value: 784 },
      { name: '其他', value: 500 }
    ]
  }
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#aaa', fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#1a1a2e',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: '#fff'
        }
      },
      data: data.map((item, index) => ({
        ...item,
        itemStyle: {
          color: ['#00d2ff', '#3a7bd5', '#00d4aa', '#f5a623', '#ee6666'][index % 5]
        }
      }))
    }]
  }
  
  pieChart.setOption(option)
}

// 初始化柱状图
const initBarChart = async () => {
  if (!barChartRef.value) return
  
  barChart = echarts.init(barChartRef.value)
  
  let data = []
  try {
    const res = await getTrendData({ days: 7 })
    data = res.data || []
  } catch (error) {
    data = [
      { date: '12-01', value: 820 },
      { date: '12-02', value: 932 },
      { date: '12-03', value: 901 },
      { date: '12-04', value: 1034 },
      { date: '12-05', value: 1290 },
      { date: '12-06', value: 1330 },
      { date: '12-07', value: 1520 }
    ]
  }
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date),
      axisLine: { lineStyle: { color: '#1a8a9e' } },
      axisLabel: { color: '#aaa' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#1a8a9e' } },
      axisLabel: { color: '#aaa' },
      splitLine: { lineStyle: { color: 'rgba(26, 138, 158, 0.2)' } }
    },
    series: [{
      type: 'bar',
      data: data.map(item => item.value),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#00d2ff' },
          { offset: 1, color: '#0d3c55' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }
  
  barChart.setOption(option)
}

// 处理窗口大小变化
const handleResize = () => {
  map2dChart?.resize()
  globe3dChart?.resize()
  pieChart?.resize()
  barChart?.resize()
}

// 新闻列表自动滚动
const startNewsScroll = () => {
  scrollInterval = setInterval(() => {
    if (newsListRef.value && latestNews.value.length > 5) {
      const container = newsListRef.value
      if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
        container.scrollTop = 0
      } else {
        container.scrollTop += 1
      }
    }
  }, 50)
}

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  // 加载数据
  await Promise.all([
    loadHeatmapData(),
    refreshLatestData(),
    loadRankingData()
  ])
  
  // 初始化图表
  await nextTick()
  initPieChart()
  initBarChart()
  
  // 启动新闻滚动
  startNewsScroll()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(timeInterval)
  clearInterval(scrollInterval)
  window.removeEventListener('resize', handleResize)
  
  map2dChart?.dispose()
  globe3dChart?.dispose()
  pieChart?.dispose()
  barChart?.dispose()
})
</script>

<style lang="scss" scoped>
.bigscreen-container {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0a0e17 0%, #0d1a26 50%, #0a1628 100%);
  color: #fff;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// 顶部标题栏
.header {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  background: linear-gradient(180deg, rgba(0, 210, 255, 0.1) 0%, transparent 100%);
  border-bottom: 1px solid rgba(0, 210, 255, 0.3);
  
  .header-left {
    .logo {
      font-size: 28px;
    }
  }
  
  .header-center {
    h1 {
      font-size: 28px;
      font-weight: bold;
      background: linear-gradient(90deg, #00d2ff, #00d4aa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 30px rgba(0, 210, 255, 0.5);
      letter-spacing: 4px;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .time {
      font-size: 16px;
      color: #00d2ff;
    }
    
    .switch-btn {
      color: #00d4aa;
    }
  }
}

// 主内容区
.main-content {
  flex: 1;
  display: flex;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

// 左侧面板
.left-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  .map-card {
    flex: 2;
  }
  
  .bottom-charts {
    flex: 1;
    display: flex;
    gap: 20px;
    
    .panel-card {
      flex: 1;
    }
  }
}

// 右侧面板
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 400px;
  
  .news-card {
    flex: 2;
  }
  
  .ai-card {
    flex: 1;
  }
  
  .ranking-card {
    flex: 1;
  }
}

// 面板卡片
.panel-card {
  background: rgba(13, 60, 85, 0.3);
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  .panel-header {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(0, 210, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .panel-title {
      font-size: 14px;
      font-weight: bold;
      color: #00d2ff;
      padding-left: 10px;
      border-left: 3px solid #00d2ff;
    }
  }
  
  .panel-body {
    flex: 1;
    padding: 12px;
    overflow: hidden;
  }
}

// 图表容器
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

// 新闻列表
.news-list {
  height: 100%;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 210, 255, 0.3);
    border-radius: 2px;
  }
  
  .news-item {
    padding: 12px;
    border-bottom: 1px solid rgba(0, 210, 255, 0.1);
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      background: rgba(0, 210, 255, 0.1);
    }
    
    .news-title {
      font-size: 13px;
      color: #ddd;
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .news-meta {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 6px;
      font-size: 12px;
      color: #00d2ff;
    }
  }
}

// AI分析
.ai-input {
  margin-bottom: 12px;
  
  :deep(.el-input__wrapper) {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 210, 255, 0.3);
  }
  
  :deep(.el-input__inner) {
    color: #fff;
  }
}

.ai-result {
  background: rgba(0, 210, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  max-height: 150px;
  overflow-y: auto;
  
  .ai-result-content {
    font-size: 13px;
    color: #ccc;
    line-height: 1.6;
  }
}

// 排行榜
.ranking-list {
  .ranking-item {
    display: flex;
    align-items: center;
    padding: 8px 0;
    gap: 10px;
    
    .ranking-index {
      width: 22px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      font-size: 12px;
      font-weight: bold;
      background: rgba(255, 255, 255, 0.1);
      
      &.top-1 { background: linear-gradient(135deg, #f5a623, #f7931e); }
      &.top-2 { background: linear-gradient(135deg, #c0c0c0, #a8a8a8); }
      &.top-3 { background: linear-gradient(135deg, #cd7f32, #b87333); }
    }
    
    .ranking-name {
      width: 50px;
      font-size: 13px;
      color: #ccc;
    }
    
    .ranking-bar {
      flex: 1;
      height: 8px;
      background: rgba(0, 210, 255, 0.1);
      border-radius: 4px;
      overflow: hidden;
      
      .ranking-bar-inner {
        height: 100%;
        background: linear-gradient(90deg, #00d2ff, #00d4aa);
        border-radius: 4px;
        transition: width 0.5s ease;
      }
    }
    
    .ranking-value {
      width: 50px;
      text-align: right;
      font-size: 13px;
      color: #00d2ff;
    }
  }
}
</style>
