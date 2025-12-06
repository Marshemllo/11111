import request from './request'

/**
 * 开始采集任务
 */
export function startCrawl(keyword) {
  return request.post('/crawler/start', { keyword })
}

/**
 * 获取采集任务列表
 */
export function getCrawlTasks() {
  return request.get('/crawler/tasks')
}

/**
 * 获取任务详情和进度
 */
export function getCrawlTask(taskId) {
  return request.get(`/crawler/tasks/${taskId}`)
}

/**
 * 获取任务的采集数据
 */
export function getCrawlItems(taskId) {
  return request.get(`/crawler/tasks/${taskId}/items`)
}

/**
 * 深度采集单个数据项
 */
export function deepCrawlItem(itemId) {
  return request.post(`/crawler/items/${itemId}/deep-crawl`)
}

/**
 * 保存选中的数据到数据库
 */
export function saveItems(itemIds) {
  return request.post('/crawler/items/save', { item_ids: itemIds })
}

/**
 * 获取已保存的数据列表
 */
export function getSavedData(params) {
  return request.get('/crawler/saved', { params })
}

/**
 * 删除已保存的数据
 */
export function deleteSavedData(dataId) {
  return request.delete(`/crawler/saved/${dataId}`)
}
