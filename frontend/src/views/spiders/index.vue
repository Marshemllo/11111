<template>
  <div class="page-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="数据源管理" name="sources">
        <div class="table-actions mb-20">
          <el-button type="primary" @click="handleAddSource">新增数据源</el-button>
        </div>
        <el-table :data="sourceList" v-loading="loading" border>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="url" label="URL" />
          <el-table-column prop="industry_tag" label="行业标签" />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEditSource(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDeleteSource(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="爬虫规则" name="rules">
        <div class="table-actions mb-20">
          <el-button type="primary" @click="handleAddRule">新增爬虫</el-button>
          <el-button @click="showTestDialog = true">测试爬虫</el-button>
        </div>
        <el-table :data="ruleList" v-loading="loading" border>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="spider_type" label="类型" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_items" label="数据量" width="100" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="success" link @click="handleStartSpider(row)">启动</el-button>
              <el-button type="warning" link @click="handleStopSpider(row)">停止</el-button>
              <el-button type="primary" link @click="handleEditRule(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 测试对话框 -->
    <el-dialog v-model="showTestDialog" title="爬虫测试" width="600px">
      <el-form :model="testForm" label-width="80px">
        <el-form-item label="测试URL">
          <el-input v-model="testForm.url" placeholder="输入要测试的URL" />
        </el-form-item>
        <el-form-item label="标题规则">
          <el-input v-model="testForm.titleSelector" placeholder="XPath或CSS选择器" />
        </el-form-item>
      </el-form>
      <div v-if="testResult" class="test-result">
        <h4>测试结果:</h4>
        <pre>{{ JSON.stringify(testResult, null, 2) }}</pre>
      </div>
      <template #footer>
        <el-button @click="showTestDialog = false">关闭</el-button>
        <el-button type="primary" @click="handleTest">测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { getDataSourceList, getSpiderRuleList, testSpider, startSpider, stopSpider } from '@/api/spider'
import { ElMessage } from 'element-plus'

const activeTab = ref('sources')
const loading = ref(false)
const sourceList = ref([])
const ruleList = ref([])
const showTestDialog = ref(false)
const testForm = reactive({ url: '', titleSelector: '' })
const testResult = ref(null)

const getStatusType = (status) => {
  const map = { idle: 'info', running: 'success', error: 'danger', completed: 'warning' }
  return map[status] || 'info'
}

const loadSources = async () => {
  loading.value = true
  try { sourceList.value = await getDataSourceList() } catch (e) { console.error(e) }
  loading.value = false
}

const loadRules = async () => {
  loading.value = true
  try { ruleList.value = await getSpiderRuleList() } catch (e) { console.error(e) }
  loading.value = false
}

const handleAddSource = () => ElMessage.info('新增数据源功能待实现')
const handleEditSource = () => ElMessage.info('编辑数据源功能待实现')
const handleDeleteSource = () => ElMessage.info('删除数据源功能待实现')
const handleAddRule = () => ElMessage.info('新增爬虫功能待实现')
const handleEditRule = () => ElMessage.info('编辑爬虫功能待实现')

const handleStartSpider = async (row) => {
  try { await startSpider(row.id); ElMessage.success('启动成功'); loadRules() } catch (e) { ElMessage.error('启动失败') }
}

const handleStopSpider = async (row) => {
  try { await stopSpider(row.id); ElMessage.success('停止成功'); loadRules() } catch (e) { ElMessage.error('停止失败') }
}

const handleTest = async () => {
  try {
    testResult.value = await testSpider({ url: testForm.url, rules: { title: { type: 'xpath', selector: testForm.titleSelector } } })
  } catch (e) { testResult.value = { error: '测试失败' } }
}

loadSources()
loadRules()
</script>

<style scoped>
.test-result { margin-top: 20px; background: #f5f7fa; padding: 15px; border-radius: 8px; }
.test-result pre { white-space: pre-wrap; word-break: break-all; }
</style>
