import request from './request'

/**
 * 获取AI引擎列表
 */
export function getAIEngines(params) {
  return request.get('/ai-engines', { params })
}

/**
 * 获取默认AI引擎
 */
export function getDefaultEngine() {
  return request.get('/ai-engines/default')
}

/**
 * 获取AI引擎详情
 */
export function getAIEngine(id) {
  return request.get(`/ai-engines/${id}`)
}

/**
 * 创建AI引擎
 */
export function createAIEngine(data) {
  return request.post('/ai-engines', data)
}

/**
 * 更新AI引擎
 */
export function updateAIEngine(id, data) {
  return request.put(`/ai-engines/${id}`, data)
}

/**
 * 删除AI引擎
 */
export function deleteAIEngine(id) {
  return request.delete(`/ai-engines/${id}`)
}

/**
 * 设置默认引擎
 */
export function setDefaultEngine(id) {
  return request.post(`/ai-engines/${id}/set-default`)
}

/**
 * 切换引擎状态
 */
export function toggleEngineStatus(id) {
  return request.post(`/ai-engines/${id}/toggle-status`)
}

/**
 * 测试AI引擎
 */
export function testAIEngine(id, data = { prompt: '你好，请简单介绍一下你自己' }) {
  return request.post(`/ai-engines/${id}/test`, data)
}

/**
 * 获取支持的服务商列表
 */
export function getProviders() {
  return request.get('/ai-engines/providers/list')
}
