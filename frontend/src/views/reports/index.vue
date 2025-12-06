<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="行业">
          <el-select v-model="searchForm.industry" placeholder="选择行业" clearable style="width: 150px">
            <el-option v-for="item in industries" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker 
            v-model="searchForm.dateRange" 
            type="daterange" 
            start-placeholder="开始日期" 
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="报告标题" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="table-actions mb-20">
      <el-button type="primary" @click="handleAIGenerate">AI生成报告</el-button>
    </div>
    
    <el-table :data="reportList" v-loading="loading" border>
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="industry" label="行业" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.industry" type="info">{{ row.industry }}</el-tag>
          <span v-else class="text-gray">未分类</span>
        </template>
      </el-table-column>
      <el-table-column prop="report_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.report_type === 'AI生成'" type="success">AI生成</el-tag>
          <el-tag v-else-if="row.report_type" type="warning">{{ row.report_type }}</el-tag>
          <span v-else class="text-gray">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="查看" width="70" align="center" />
      <el-table-column prop="download_count" label="下载" width="70" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleView(row)">查看</el-button>
          <el-button type="success" link @click="handleDownload(row)">下载PDF</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="mt-20 flex-center">
      <el-pagination 
        v-model:current-page="pagination.page" 
        v-model:page-size="pagination.pageSize" 
        :total="pagination.total" 
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="loadData"
        @size-change="handleSizeChange"
      />
    </div>
    
    <!-- AI生成报告弹窗 -->
    <el-dialog v-model="showAIDialog" title="AI生成报告" width="500px">
      <el-form :model="aiForm" label-width="80px">
        <el-form-item label="主题" required>
          <el-input v-model="aiForm.topic" placeholder="输入报告主题，如：2024年电商行业发展趋势" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="aiForm.industry" placeholder="选择行业" style="width: 100%">
            <el-option v-for="item in allIndustries" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAIDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAIGenerate" :loading="aiGenerating">
          {{ aiGenerating ? '生成中...' : '生成报告' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 报告详情弹窗 -->
    <el-dialog v-model="showDetailDialog" :title="currentReport?.title || '报告详情'" width="800px" top="5vh">
      <div v-if="currentReport" class="report-detail">
        <el-descriptions :column="2" border class="mb-20">
          <el-descriptions-item label="行业分类">{{ currentReport.industry || '未分类' }}</el-descriptions-item>
          <el-descriptions-item label="报告类型">{{ currentReport.report_type || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="数据来源">{{ currentReport.data_source || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentReport.status)">{{ getStatusText(currentReport.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="查看次数">{{ currentReport.view_count }}</el-descriptions-item>
          <el-descriptions-item label="下载次数">{{ currentReport.download_count }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ formatDate(currentReport.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">报告摘要</el-divider>
        <div class="report-summary">{{ currentReport.summary || '暂无摘要' }}</div>
        
        <el-divider content-position="left">报告内容</el-divider>
        <div class="report-content" v-html="renderMarkdown(currentReport.content)"></div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="success" @click="handleDownload(currentReport)">下载PDF</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getReportList, getReportDetail, deleteReport, downloadReportPdf, aiGenerateReport, getIndustries } from '@/api/report'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'

const loading = ref(false)
const reportList = ref([])
const industries = ref([])
const allIndustries = ref(['科技', '金融', '医疗', '教育', '制造', '零售', '能源', '交通', '农业', '其他'])
const showAIDialog = ref(false)
const showDetailDialog = ref(false)
const currentReport = ref(null)
const aiGenerating = ref(false)
const searchForm = reactive({ industry: '', dateRange: null, keyword: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const aiForm = reactive({ topic: '', industry: '' })

// 加载行业列表
const loadIndustries = async () => {
  try {
    const res = await getIndustries()
    if (res && res.length > 0) {
      industries.value = res
      // 合并已有行业和预设行业
      const allSet = new Set([...allIndustries.value, ...res])
      allIndustries.value = Array.from(allSet)
    }
  } catch (e) {
    console.error('加载行业列表失败', e)
  }
}

// 加载报告列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      industry: searchForm.industry || undefined,
      keyword: searchForm.keyword || undefined
    }
    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    const res = await getReportList(params)
    reportList.value = res.items || res
    pagination.total = res.total || 0
  } catch (e) {
    console.error('加载报告列表失败', e)
    ElMessage.error('加载报告列表失败')
  }
  loading.value = false
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, { industry: '', dateRange: null, keyword: '' })
  handleSearch()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  loadData()
}

// 查看报告详情
const handleView = async (row) => {
  try {
    const res = await getReportDetail(row.id)
    currentReport.value = res
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('获取报告详情失败')
  }
}

// 下载PDF
const handleDownload = async (row) => {
  if (!row) return
  try {
    ElMessage.info('正在生成PDF，请稍候...')
    const blob = await downloadReportPdf(row.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.title}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (e) {
    console.error('下载失败', e)
    ElMessage.error('下载失败，请稍后重试')
  }
}

// 删除报告
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该报告吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteReport(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 打开AI生成弹窗
const handleAIGenerate = () => {
  aiForm.topic = ''
  aiForm.industry = ''
  showAIDialog.value = true
}

// 提交AI生成
const submitAIGenerate = async () => {
  if (!aiForm.topic.trim()) {
    ElMessage.warning('请输入报告主题')
    return
  }
  aiGenerating.value = true
  try {
    await aiGenerateReport(aiForm)
    ElMessage.success('报告生成成功')
    showAIDialog.value = false
    loadData()
  } catch (e) {
    console.error('生成失败', e)
    ElMessage.error('报告生成失败，请稍后重试')
  }
  aiGenerating.value = false
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 状态类型
const getStatusType = (status) => {
  const types = {
    'draft': 'info',
    'published': 'success',
    'archived': 'warning'
  }
  return types[status] || 'info'
}

// 状态文本
const getStatusText = (status) => {
  const texts = {
    'draft': '草稿',
    'published': '已发布',
    'archived': '已归档'
  }
  return texts[status] || status
}

// 渲染Markdown
const renderMarkdown = (content) => {
  if (!content) return '<p class="text-gray">暂无内容</p>'
  try {
    return marked(content)
  } catch (e) {
    return content.replace(/\n/g, '<br>')
  }
}

onMounted(() => {
  loadIndustries()
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.search-form {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.table-actions {
  margin-bottom: 15px;
}

.mb-20 {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.flex-center {
  display: flex;
  justify-content: center;
}

.text-gray {
  color: #909399;
}

.report-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.report-summary {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #606266;
  line-height: 1.8;
}

.report-content {
  padding: 15px;
  background: #fafafa;
  border-radius: 4px;
  line-height: 1.8;
}

.report-content :deep(h1),
.report-content :deep(h2),
.report-content :deep(h3) {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #303133;
}

.report-content :deep(p) {
  margin-bottom: 10px;
  color: #606266;
}

.report-content :deep(ul),
.report-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 10px;
}

.report-content :deep(li) {
  margin-bottom: 5px;
}

.report-content :deep(code) {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.report-content :deep(pre) {
  background: #f0f0f0;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
