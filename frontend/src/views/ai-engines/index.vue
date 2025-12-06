<template>
  <div class="ai-engines-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <i class="fas fa-robot"></i>
          AI引擎管理
        </h1>
        <p class="page-desc">管理和配置多个AI大模型服务，支持OpenAI API兼容格式</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openCreateDialog" class="add-btn">
          <i class="fas fa-plus"></i>
          新增引擎
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="fas fa-server"></i>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ engines.length }}</span>
          <span class="stat-label">引擎总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ activeCount }}</span>
          <span class="stat-label">已启用</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon default">
          <i class="fas fa-star"></i>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ defaultEngine?.name || '未设置' }}</span>
          <span class="stat-label">默认引擎</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon requests">
          <i class="fas fa-chart-line"></i>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ totalRequests.toLocaleString() }}</span>
          <span class="stat-label">总请求数</span>
        </div>
      </div>
    </div>

    <!-- 引擎橱窗列表 -->
    <div class="engines-grid" v-loading="loading">
      <div 
        v-for="engine in engines" 
        :key="engine.id" 
        class="engine-card"
        :class="{ 
          'is-default': engine.is_default, 
          'is-inactive': !engine.is_active 
        }"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="provider-icon" :style="{ background: getProviderColor(engine.provider) }">
            {{ getProviderIcon(engine.provider) }}
          </div>
          <div class="engine-info">
            <h3 class="engine-name">{{ engine.name }}</h3>
            <span class="provider-label">{{ getProviderLabel(engine.provider) }}</span>
          </div>
          <div class="card-badges">
            <span v-if="engine.is_default" class="badge default">
              <i class="fas fa-star"></i> 默认
            </span>
            <span v-if="!engine.is_active" class="badge inactive">
              <i class="fas fa-pause"></i> 已禁用
            </span>
          </div>
        </div>

        <!-- 卡片内容 -->
        <div class="card-body">
          <div class="model-info">
            <i class="fas fa-microchip"></i>
            <span class="model-name">{{ engine.model_name }}</span>
          </div>
          <p class="engine-desc">{{ engine.description || '暂无描述' }}</p>
          
          <div class="config-items">
            <div class="config-item">
              <span class="config-label">API地址</span>
              <span class="config-value" :title="engine.api_base_url">
                {{ truncateUrl(engine.api_base_url) }}
              </span>
            </div>
            <div class="config-item">
              <span class="config-label">API密钥</span>
              <span class="config-value api-key">{{ engine.api_key || '未配置' }}</span>
            </div>
            <div class="config-row">
              <div class="config-item small">
                <span class="config-label">最大Token</span>
                <span class="config-value">{{ engine.max_tokens }}</span>
              </div>
              <div class="config-item small">
                <span class="config-label">温度</span>
                <span class="config-value">{{ engine.temperature }}</span>
              </div>
              <div class="config-item small">
                <span class="config-label">超时</span>
                <span class="config-value">{{ engine.timeout }}s</span>
              </div>
            </div>
          </div>

          <!-- 使用统计 -->
          <div class="usage-stats">
            <div class="usage-item">
              <i class="fas fa-paper-plane"></i>
              <span>{{ engine.total_requests.toLocaleString() }} 次请求</span>
            </div>
            <div class="usage-item">
              <i class="fas fa-coins"></i>
              <span>{{ engine.total_tokens.toLocaleString() }} Tokens</span>
            </div>
          </div>
        </div>

        <!-- 卡片操作 -->
        <div class="card-footer">
          <el-button 
            type="primary" 
            text 
            @click="testEngine(engine)"
            :loading="testingId === engine.id"
          >
            <i class="fas fa-vial"></i> 测试
          </el-button>
          <el-button type="success" text @click="openEditDialog(engine)">
            <i class="fas fa-edit"></i> 编辑
          </el-button>
          <el-button 
            v-if="!engine.is_default" 
            type="warning" 
            text 
            @click="setDefault(engine)"
          >
            <i class="fas fa-star"></i> 设为默认
          </el-button>
          <el-button 
            :type="engine.is_active ? 'info' : 'success'" 
            text 
            @click="toggleStatus(engine)"
          >
            <i :class="engine.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
            {{ engine.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button type="danger" text @click="confirmDelete(engine)">
            <i class="fas fa-trash"></i> 删除
          </el-button>
        </div>

        <!-- 装饰光效 -->
        <div class="card-glow"></div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && engines.length === 0" class="empty-state">
        <i class="fas fa-robot"></i>
        <p>暂无AI引擎配置</p>
        <el-button type="primary" @click="openCreateDialog">
          <i class="fas fa-plus"></i> 添加第一个引擎
        </el-button>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑AI引擎' : '新增AI引擎'"
      width="600px"
      class="engine-dialog"
      destroy-on-close
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        label-width="100px"
        class="engine-form"
      >
        <el-form-item label="引擎名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：GPT-4 生产环境" />
        </el-form-item>

        <el-form-item label="服务商" prop="provider">
          <el-select v-model="formData.provider" placeholder="选择服务商" @change="onProviderChange">
            <el-option 
              v-for="p in providers" 
              :key="p.name" 
              :label="p.label" 
              :value="p.name"
            >
              <span>{{ p.icon }} {{ p.label }}</span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="API地址" prop="api_base_url">
          <el-input v-model="formData.api_base_url" placeholder="https://api.openai.com/v1" />
        </el-form-item>

        <el-form-item label="API密钥" prop="api_key">
          <el-input 
            v-model="formData.api_key" 
            type="password" 
            show-password
            placeholder="sk-xxxxxxxx"
          />
        </el-form-item>

        <el-form-item label="模型名称" prop="model_name">
          <el-select 
            v-model="formData.model_name" 
            placeholder="选择或输入模型名称"
            filterable
            allow-create
          >
            <el-option 
              v-for="m in currentModels" 
              :key="m" 
              :label="m" 
              :value="m" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="2"
            placeholder="引擎用途描述（可选）"
          />
        </el-form-item>

        <el-divider>高级配置</el-divider>

        <div class="form-row">
          <el-form-item label="最大Token" prop="max_tokens">
            <el-input-number v-model="formData.max_tokens" :min="100" :max="128000" />
          </el-form-item>
          <el-form-item label="温度" prop="temperature">
            <el-slider v-model="formData.temperature" :min="0" :max="2" :step="0.1" show-input />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="超时(秒)" prop="timeout">
            <el-input-number v-model="formData.timeout" :min="5" :max="300" />
          </el-form-item>
          <el-form-item label="状态">
            <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
          </el-form-item>
        </div>

        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" />
          <span class="form-tip">默认引擎将用于系统AI功能调用</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEdit ? '保存修改' : '创建引擎' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试结果对话框 -->
    <el-dialog 
      v-model="testDialogVisible" 
      title="引擎测试结果"
      width="500px"
      class="test-dialog"
    >
      <div class="test-result" :class="testResult.success ? 'success' : 'error'">
        <div class="result-icon">
          <i :class="testResult.success ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
        </div>
        <h3>{{ testResult.success ? '测试成功' : '测试失败' }}</h3>
        <p class="result-message">{{ testResult.message }}</p>
        <div v-if="testResult.latency_ms" class="result-latency">
          <i class="fas fa-clock"></i> 响应时间: {{ testResult.latency_ms }}ms
        </div>
        <div v-if="testResult.response" class="result-response">
          <h4>AI回复:</h4>
          <p>{{ testResult.response }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getAIEngines, 
  createAIEngine, 
  updateAIEngine, 
  deleteAIEngine,
  setDefaultEngine,
  toggleEngineStatus,
  testAIEngine,
  getProviders
} from '@/api/aiEngine'

// 数据
const loading = ref(false)
const engines = ref([])
const providers = ref([])
const dialogVisible = ref(false)
const testDialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const testingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const testResult = reactive({
  success: false,
  message: '',
  response: '',
  latency_ms: null
})

const formData = reactive({
  name: '',
  provider: 'openai',
  api_key: '',
  api_base_url: 'https://api.openai.com/v1',
  model_name: 'gpt-3.5-turbo',
  description: '',
  max_tokens: 2048,
  temperature: 0.7,
  timeout: 30,
  is_active: true,
  is_default: false
})

const formRules = {
  name: [{ required: true, message: '请输入引擎名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择服务商', trigger: 'change' }],
  api_base_url: [{ required: true, message: '请输入API地址', trigger: 'blur' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }]
}

// 计算属性
const activeCount = computed(() => engines.value.filter(e => e.is_active).length)
const defaultEngine = computed(() => engines.value.find(e => e.is_default))
const totalRequests = computed(() => engines.value.reduce((sum, e) => sum + e.total_requests, 0))

const currentModels = computed(() => {
  const provider = providers.value.find(p => p.name === formData.provider)
  return provider?.models || []
})

// 方法
const fetchEngines = async () => {
  loading.value = true
  try {
    engines.value = await getAIEngines()
  } catch (error) {
    ElMessage.error('获取引擎列表失败')
  } finally {
    loading.value = false
  }
}

const fetchProviders = async () => {
  try {
    providers.value = await getProviders()
  } catch (error) {
    console.error('获取服务商列表失败', error)
  }
}

const getProviderIcon = (provider) => {
  const icons = {
    openai: '🤖',
    siliconflow: '🌊',
    deepseek: '🔍',
    moonshot: '🌙',
    qwen: '🧠',
    zhipu: '📚',
    azure: '☁️',
    custom: '⚙️'
  }
  return icons[provider] || '🤖'
}

const getProviderLabel = (provider) => {
  const p = providers.value.find(item => item.name === provider)
  return p?.label || provider
}

const getProviderColor = (provider) => {
  const colors = {
    openai: 'linear-gradient(135deg, #10a37f 0%, #1a7f64 100%)',
    siliconflow: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    deepseek: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    moonshot: 'linear-gradient(135deg, #0c0c0c 0%, #434343 100%)',
    qwen: 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)',
    zhipu: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    azure: 'linear-gradient(135deg, #0078d4 0%, #106ebe 100%)',
    custom: 'linear-gradient(135deg, #6c757d 0%, #495057 100%)'
  }
  return colors[provider] || colors.custom
}

const truncateUrl = (url) => {
  if (!url) return '未配置'
  if (url.length > 35) return url.substring(0, 35) + '...'
  return url
}

const onProviderChange = (provider) => {
  const p = providers.value.find(item => item.name === provider)
  if (p) {
    formData.api_base_url = p.api_base_url
    if (p.models.length > 0) {
      formData.model_name = p.models[0]
    }
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(formData, {
    name: '',
    provider: 'openai',
    api_key: '',
    api_base_url: 'https://api.openai.com/v1',
    model_name: 'gpt-3.5-turbo',
    description: '',
    max_tokens: 2048,
    temperature: 0.7,
    timeout: 30,
    is_active: true,
    is_default: false
  })
  dialogVisible.value = true
}

const openEditDialog = (engine) => {
  isEdit.value = true
  editingId.value = engine.id
  Object.assign(formData, {
    name: engine.name,
    provider: engine.provider,
    api_key: '', // 编辑时不显示原密钥
    api_base_url: engine.api_base_url,
    model_name: engine.model_name,
    description: engine.description || '',
    max_tokens: engine.max_tokens,
    temperature: engine.temperature,
    timeout: engine.timeout,
    is_active: engine.is_active,
    is_default: engine.is_default
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateAIEngine(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await createAIEngine(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchEngines()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (engine) => {
  ElMessageBox.confirm(
    `确定要删除引擎 "${engine.name}" 吗？此操作不可恢复。`,
    '删除确认',
    { type: 'warning' }
  ).then(async () => {
    try {
      await deleteAIEngine(engine.id)
      ElMessage.success('删除成功')
      fetchEngines()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const setDefault = async (engine) => {
  try {
    await setDefaultEngine(engine.id)
    ElMessage.success(`已将 "${engine.name}" 设为默认引擎`)
    fetchEngines()
  } catch (error) {
    ElMessage.error('设置失败')
  }
}

const toggleStatus = async (engine) => {
  try {
    await toggleEngineStatus(engine.id)
    ElMessage.success(engine.is_active ? '已禁用' : '已启用')
    fetchEngines()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const testEngine = async (engine) => {
  testingId.value = engine.id
  try {
    const result = await testAIEngine(engine.id)
    Object.assign(testResult, result)
    testDialogVisible.value = true
  } catch (error) {
    Object.assign(testResult, {
      success: false,
      message: error.response?.data?.detail || '测试请求失败',
      response: '',
      latency_ms: null
    })
    testDialogVisible.value = true
  } finally {
    testingId.value = null
  }
}

onMounted(() => {
  fetchEngines()
  fetchProviders()
})
</script>

<style lang="scss" scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.ai-engines-page {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  .page-title {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 12px;

    i {
      color: #667eea;
    }
  }

  .page-desc {
    color: rgba(255, 255, 255, 0.6);
    margin: 0;
  }
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 12px 24px;
  font-size: 15px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }
}

// 统计卡片
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    border-color: rgba(102, 126, 234, 0.3);
  }
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;

  &.total { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
  &.active { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
  &.default { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
  &.requests { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

// 引擎网格
.engines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

// 引擎卡片
.engine-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  transition: all 0.4s ease;

  &:hover {
    transform: translateY(-8px);
    border-color: rgba(102, 126, 234, 0.5);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

    .card-glow {
      opacity: 1;
    }
  }

  &.is-default {
    border-color: rgba(240, 147, 251, 0.5);

    .card-glow {
      background: radial-gradient(circle at 50% 0%, rgba(240, 147, 251, 0.2), transparent 70%);
    }
  }

  &.is-inactive {
    opacity: 0.6;
  }
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 150px;
  background: radial-gradient(circle at 50% 0%, rgba(102, 126, 234, 0.15), transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.card-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.provider-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.engine-info {
  flex: 1;
  min-width: 0;
}

.engine-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.provider-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.card-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;

  &.default {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: #fff;
  }

  &.inactive {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
  }
}

.card-body {
  padding: 0 20px 20px;
  position: relative;
  z-index: 1;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 10px;
  margin-bottom: 12px;

  i {
    color: #667eea;
  }

  .model-name {
    color: #fff;
    font-family: 'Monaco', monospace;
    font-size: 13px;
  }
}

.engine-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.config-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  &.small {
    flex: 1;
  }
}

.config-row {
  display: flex;
  gap: 16px;
}

.config-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.config-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Monaco', monospace;

  &.api-key {
    color: #667eea;
  }
}

.usage-stats {
  display: flex;
  gap: 20px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.usage-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);

  i {
    color: #667eea;
  }
}

.card-footer {
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;

  .el-button {
    color: rgba(255, 255, 255, 0.7);

    &:hover {
      color: #fff;
    }
  }
}

// 空状态
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);

  i {
    font-size: 64px;
    margin-bottom: 20px;
    opacity: 0.3;
  }

  p {
    font-size: 18px;
    margin-bottom: 24px;
  }
}

// 对话框样式
.engine-dialog {
  :deep(.el-dialog) {
    background: #1a1a2e;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
  }

  :deep(.el-dialog__header) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  :deep(.el-dialog__title) {
    color: #fff;
  }

  :deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.8);
  }

  :deep(.el-input__wrapper),
  :deep(.el-select__wrapper),
  :deep(.el-textarea__inner) {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    color: #fff;
  }

  :deep(.el-input__inner) {
    color: #fff;
  }
}

.form-row {
  display: flex;
  gap: 20px;

  .el-form-item {
    flex: 1;
  }
}

.form-tip {
  margin-left: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

// 测试结果对话框
.test-dialog {
  :deep(.el-dialog) {
    background: #1a1a2e;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
  }

  :deep(.el-dialog__title) {
    color: #fff;
  }
}

.test-result {
  text-align: center;
  padding: 20px;

  .result-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }

  &.success .result-icon {
    color: #38ef7d;
  }

  &.error .result-icon {
    color: #f5576c;
  }

  h3 {
    color: #fff;
    margin: 0 0 12px 0;
  }

  .result-message {
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 16px;
  }

  .result-latency {
    color: rgba(255, 255, 255, 0.5);
    font-size: 14px;
    margin-bottom: 16px;

    i {
      margin-right: 8px;
    }
  }

  .result-response {
    text-align: left;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 16px;

    h4 {
      color: #667eea;
      margin: 0 0 8px 0;
      font-size: 14px;
    }

    p {
      color: rgba(255, 255, 255, 0.8);
      margin: 0;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .engines-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
