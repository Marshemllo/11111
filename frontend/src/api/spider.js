import request from './request'

// ==================== 数据源API ====================

/**
 * 获取数据源列表
 */
export function getDataSourceList(params) {
  return request.get('/spiders/sources', { params })
}

/**
 * 获取数据源详情
 */
export function getDataSourceDetail(id) {
  return request.get(`/spiders/sources/${id}`)
}

/**
 * 创建数据源
 */
export function createDataSource(data) {
  return request.post('/spiders/sources', data)
}

/**
 * 更新数据源
 */
export function updateDataSource(id, data) {
  return request.put(`/spiders/sources/${id}`, data)
}

/**
 * 删除数据源
 */
export function deleteDataSource(id) {
  return request.delete(`/spiders/sources/${id}`)
}

// ==================== 爬虫规则API ====================

/**
 * 获取爬虫规则列表
 */
export function getSpiderRuleList(params) {
  return request.get('/spiders/rules', { params })
}

/**
 * 获取爬虫规则详情
 */
export function getSpiderRuleDetail(id) {
  return request.get(`/spiders/rules/${id}`)
}

/**
 * 创建爬虫规则
 */
export function createSpiderRule(data) {
  return request.post('/spiders/rules', data)
}

/**
 * 更新爬虫规则
 */
export function updateSpiderRule(id, data) {
  return request.put(`/spiders/rules/${id}`, data)
}

/**
 * 删除爬虫规则
 */
export function deleteSpiderRule(id) {
  return request.delete(`/spiders/rules/${id}`)
}

/**
 * 启动爬虫
 */
export function startSpider(id) {
  return request.post(`/spiders/rules/${id}/start`)
}

/**
 * 停止爬虫
 */
export function stopSpider(id) {
  return request.post(`/spiders/rules/${id}/stop`)
}

/**
 * 测试爬虫
 */
export function testSpider(data) {
  return request.post('/spiders/test', data)
}

/**
 * 获取行业标签列表
 */
export function getIndustryTags() {
  return request.get('/spiders/industry-tags')
}
