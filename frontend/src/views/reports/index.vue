<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="行业">
          <el-select v-model="searchForm.industry" placeholder="选择行业" clearable>
            <el-option v-for="item in industries" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker v-model="searchForm.dateRange" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="报告标题" clearable />
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
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="industry" label="行业" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="查看" width="80" />
      <el-table-column prop="download_count" label="下载" width="80" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleView(row)">查看</el-button>
          <el-button type="success" link @click="handleDownload(row)">下载PDF</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="mt-20 flex-center">
      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :total="pagination.total" layout="total, prev, pager, next" @current-change="loadData" />
    </div>
    
    <el-dialog v-model="showAIDialog" title="AI生成报告" width="500px">
      <el-form :model="aiForm" label-width="80px">
        <el-form-item label="主题">
          <el-input v-model="aiForm.topic" placeholder="输入报告主题" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="aiForm.industry" placeholder="选择行业">
            <el-option v-for="item in industries" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAIDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAIGenerate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { getReportList, deleteReport, downloadReportPdf, aiGenerateReport } from '@/api/report'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const reportList = ref([])
const industries = ref(['科技', '金融', '医疗', '教育', '制造'])
const showAIDialog = ref(false)
const searchForm = reactive({ industry: '', dateRange: null, keyword: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const aiForm = reactive({ topic: '', industry: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getReportList({ skip: (pagination.page - 1) * pagination.pageSize, limit: pagination.pageSize, ...searchForm })
    reportList.value = res.items || res
    pagination.total = res.total || 0
  } catch (e) { console.error(e) }
  loading.value = false
}

const handleSearch = () => { pagination.page = 1; loadData() }
const handleReset = () => { Object.assign(searchForm, { industry: '', dateRange: null, keyword: '' }); handleSearch() }
const handleView = (row) => ElMessage.info(`查看报告: ${row.title}`)
const handleDownload = async (row) => {
  try {
    const blob = await downloadReportPdf(row.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${row.title}.pdf`; a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) { ElMessage.error('下载失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除?', '提示')
  await deleteReport(row.id)
  ElMessage.success('删除成功'); loadData()
}
const handleAIGenerate = () => { showAIDialog.value = true }
const submitAIGenerate = async () => {
  try { await aiGenerateReport(aiForm); ElMessage.success('生成中'); showAIDialog.value = false; loadData() } catch (e) { ElMessage.error('生成失败') }
}

loadData()
</script>
