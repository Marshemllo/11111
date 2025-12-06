<template>
  <div class="crawler-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Search /></el-icon>
        数据采集管理
      </h1>
      <p class="page-desc">输入关键词进行数据采集，支持深度采集和数据存储</p>
    </div>

    <!-- 采集输入区 -->
    <div class="crawl-input-section">
      <el-input
        v-model="keyword"
        placeholder="请输入采集关键词或需求..."
        size="large"
        class="keyword-input"
        @keyup.enter="startCrawl"
      >
        <template #append>
          <el-button type="primary" :loading="crawling" @click="startCrawl">
            <el-icon><Search /></el-icon>
            开始采集
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 进度提示 -->
    <div v-if="currentTask" class="progress-section">
      <el-alert
        :title="progressTitle"
        :type="progressType"
        :closable="false"
        show-icon
      >
        <template #default>
          <div class="progress-info">
            <span>{{ currentTask.progress_message }}</span>
            <el-progress
              v-if="currentTask.status === 'running'"
              :percentage="progressPercent"
              :stroke-width="8"
              style="width: 200px; margin-left: 20px;"
            />
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 操作栏 -->
    <div v-if="items.length > 0" class="action-bar">
      <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
      <el-button type="primary" :disabled="selectedIds.length === 0" @click="saveSelected">
        <el-icon><Download /></el-icon>
        保存选中 ({{ selectedIds.length }})
      </el-button>
      <el-button @click="viewSaved">
        <el-icon><FolderOpened /></el-icon>
        查看已保存
      </el-button>
    </div>

    <!-- 数据列表 -->
    <div v-loading="loading" class="items-grid">
      <div
        v-for="item in items"
        :key="item.id"
        class="item-card"
        :class="{ 'is-selected': selectedIds.includes(item.id), 'is-saved': item.is_saved }"
      >
        <div class="card-checkbox">
          <el-checkbox
            :model-value="selectedIds.includes(item.id)"
            @change="toggleSelect(item.id)"
            :disabled="item.is_saved"
          />
        </div>
        
        <div class="card-cover" @click="openUrl(item.source_url)">
          <img v-if="item.cover_url" :src="item.cover_url" alt="cover" />
          <div v-else class="no-cover">
            <el-icon><Picture /></el-icon>
          </div>
        </div>
        
        <div class="card-content">
          <h3 class="card-title" @click="openUrl(item.source_url)">{{ item.title }}</h3>
          <p class="card-summary">{{ item.summary || '暂无摘要' }}</p>
          <div class="card-meta">
            <span class="source">{{ item.source_name }}</span>
            <div class="card-actions">
              <el-tag v-if="item.is_saved" type="success" size="small">已保存</el-tag>
              <el-tag v-if="item.deep_crawled" type="info" size="small">已深度采集</el-tag>
              <el-button
                v-if="!item.deep_crawled"
                type="primary"
                size="small"
                :loading="item.deepCrawling"
                @click="handleDeepCrawl(item)"
              >
                深度采集
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <el-empty v-if="!loading && items.length === 0" description="暂无数据，请输入关键词开始采集" />
    </div>

    <!-- 已保存数据弹窗 -->
    <el-dialog v-model="savedDialogVisible" title="已保存的数据" width="80%">
      <el-table :data="savedData" style="width: 100%">
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column prop="source_name" label="来源" width="100" />
        <el-table-column prop="created_at" label="保存时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="openUrl(row.source_url)">查看</el-button>
            <el-button size="small" type="danger" @click="handleDeleteSaved(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download, FolderOpened, Picture } from '@element-plus/icons-vue'
import {
  startCrawl as startCrawlApi,
  getCrawlTask,
  getCrawlItems,
  deepCrawlItem,
  saveItems,
  getSavedData,
  deleteSavedData
} from '@/api/crawler'

const keyword = ref('')
const crawling = ref(false)
const loading = ref(false)
const currentTask = ref(null)
const items = ref([])
const selectedIds = ref([])
const selectAll = ref(false)
const savedDialogVisible = ref(false)
const savedData = ref([])

const progressPercent = computed(() => {
  if (!currentTask.value || currentTask.value.total_count === 0) return 0
  return Math.round((currentTask.value.current_count / currentTask.value.total_count) * 100)
})

const progressTitle = computed(() => {
  if (!currentTask.value) return ''
  const statusMap = {
    pending: '等待中',
    running: '采集中',
    completed: '采集完成',
    failed: '采集失败'
  }
  return statusMap[currentTask.value.status] || currentTask.value.status
})

const progressType = computed(() => {
  if (!currentTask.value) return 'info'
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'error'
  }
  return typeMap[currentTask.value.status] || 'info'
})

const startCrawl = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入采集关键词')
    return
  }
  
  crawling.value = true
  items.value = []
  selectedIds.value = []
  
  try {
    const task = await startCrawlApi(keyword.value)
    currentTask.value = task
    pollTaskStatus(task.id)
  } catch (error) {
    ElMessage.error('启动采集失败')
    crawling.value = false
  }
}

const pollTaskStatus = async (taskId) => {
  const poll = async () => {
    try {
      const task = await getCrawlTask(taskId)
      currentTask.value = task
      
      if (task.status === 'completed' || task.status === 'failed') {
        crawling.value = false
        if (task.status === 'completed') {
          await loadItems(taskId)
        }
        return
      }
      
      setTimeout(poll, 1000)
    } catch (error) {
      crawling.value = false
    }
  }
  poll()
}

const loadItems = async (taskId) => {
  loading.value = true
  try {
    items.value = await getCrawlItems(taskId)
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleDeepCrawl = async (item) => {
  item.deepCrawling = true
  try {
    const result = await deepCrawlItem(item.id)
    if (result.success) {
      item.deep_crawled = true
      item.content = result.item?.content
      item.cover_url = result.item?.cover_url || item.cover_url
      ElMessage.success('深度采集成功')
    } else {
      ElMessage.error(result.message || '深度采集失败')
    }
  } catch (error) {
    ElMessage.error('深度采集失败')
  } finally {
    item.deepCrawling = false
  }
}

const toggleSelect = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
  selectAll.value = selectedIds.value.length === items.value.filter(i => !i.is_saved).length
}

const handleSelectAll = (val) => {
  if (val) {
    selectedIds.value = items.value.filter(i => !i.is_saved).map(i => i.id)
  } else {
    selectedIds.value = []
  }
}

const saveSelected = async () => {
  if (selectedIds.value.length === 0) return
  
  try {
    const result = await saveItems(selectedIds.value)
    ElMessage.success(`成功保存 ${result.saved_count} 条数据`)
    selectedIds.value.forEach(id => {
      const item = items.value.find(i => i.id === id)
      if (item) item.is_saved = true
    })
    selectedIds.value = []
    selectAll.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const viewSaved = async () => {
  savedDialogVisible.value = true
  try {
    savedData.value = await getSavedData({ limit: 50 })
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handleDeleteSaved = async (id) => {
  try {
    await deleteSavedData(id)
    savedData.value = savedData.value.filter(d => d.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const openUrl = (url) => {
  window.open(url, '_blank')
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.crawler-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-desc {
  color: #909399;
  margin: 0;
}

.crawl-input-section {
  margin-bottom: 20px;
}

.keyword-input {
  max-width: 600px;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-info {
  display: flex;
  align-items: center;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.item-card {
  position: relative;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s;
}

.item-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.item-card.is-selected {
  border: 2px solid #409eff;
}

.item-card.is-saved {
  opacity: 0.7;
}

.card-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 4px;
}

.card-cover {
  height: 160px;
  background: #f5f7fa;
  cursor: pointer;
  overflow: hidden;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 48px;
  color: #c0c4cc;
}

.card-content {
  padding: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  cursor: pointer;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-title:hover {
  color: #409eff;
}

.card-summary {
  font-size: 13px;
  color: #909399;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source {
  font-size: 12px;
  color: #c0c4cc;
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
