<template>
  <div class="dashboard-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ summary.total_reports || 0 }}</div>
            <div class="stat-label">报告总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div class="stat-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ summary.total_spiders || 0 }}</div>
            <div class="stat-label">爬虫数量</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <div class="stat-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ summary.total_data_sources || 0 }}</div>
            <div class="stat-label">数据源</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ summary.total_users || 0 }}</div>
            <div class="stat-label">用户数量</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <div class="chart-card">
          <div class="chart-header">
            <h3>数据趋势</h3>
            <div class="header-actions">
              <el-button type="success" @click="goBigScreen">
                <el-icon><Monitor /></el-icon>
                舆情大屏
              </el-button>
              <el-button type="primary" link @click="goFullscreen">
                <el-icon><FullScreen /></el-icon>
                全屏大屏
              </el-button>
            </div>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="chart-card">
          <div class="chart-header">
            <h3>行业分布</h3>
          </div>
          <div ref="pieChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 底部区域 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>最新报告</h3>
          </div>
          <el-table :data="recentReports" style="width: 100%">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="industry" label="行业" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="160" />
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>AI分析助手</h3>
          </div>
          <div class="ai-assistant">
            <el-input
              v-model="aiQuery"
              placeholder="输入问题，如：显示销售数据饼图"
              @keyup.enter="handleAIQuery"
            >
              <template #append>
                <el-button @click="handleAIQuery">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <div v-if="aiResponse" class="ai-response">
              {{ aiResponse }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getDashboardSummary, getTrendData, getIndustryDistribution, aiDataAnalysis } from '@/api/dashboard'

const router = useRouter()

const summary = ref({})
const recentReports = ref([])
const aiQuery = ref('')
const aiResponse = ref('')

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['报告数', '爬取数据']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '报告数',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230, 210],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        }
      },
      {
        name: '爬取数据',
        type: 'line',
        smooth: true,
        data: [220, 182, 191, 234, 290, 330, 310],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
          ])
        }
      }
    ]
  }
  trendChart.setOption(option)
}

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return
  
  pieChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '行业分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 1048, name: '科技' },
          { value: 735, name: '金融' },
          { value: 580, name: '医疗' },
          { value: 484, name: '教育' },
          { value: 300, name: '其他' }
        ]
      }
    ]
  }
  pieChart.setOption(option)
}

// 处理窗口大小变化
const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

// 跳转全屏大屏
const goFullscreen = () => {
  router.push('/fullscreen-dashboard')
}

// 跳转舆情大屏
const goBigScreen = () => {
  router.push('/bigscreen')
}

// AI查询
const handleAIQuery = async () => {
  if (!aiQuery.value.trim()) return
  
  try {
    const res = await aiDataAnalysis({ query: aiQuery.value })
    aiResponse.value = res.analysis
  } catch (error) {
    aiResponse.value = '查询失败，请稍后重试'
  }
}

// 加载数据
const loadData = async () => {
  try {
    const res = await getDashboardSummary()
    summary.value = res
    recentReports.value = res.recent_activities?.slice(0, 5) || []
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  }
}

onMounted(() => {
  loadData()
  initTrendChart()
  initPieChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  .stat-cards {
    margin-bottom: 20px;
  }
  
  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    border-radius: 12px;
    color: #fff;
    
    .stat-icon {
      width: 60px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      margin-right: 16px;
      
      .el-icon {
        font-size: 28px;
      }
    }
    
    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: bold;
      }
      
      .stat-label {
        font-size: 14px;
        opacity: 0.8;
      }
    }
  }
  
  .chart-row, .bottom-row {
    margin-bottom: 20px;
  }
  
  .chart-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        color: #333;
      }
    }
    
    .chart-container {
      height: 300px;
    }
  }
  
  .ai-assistant {
    .ai-response {
      margin-top: 16px;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;
      color: #666;
    }
  }
}
</style>
