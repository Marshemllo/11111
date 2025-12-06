import request from './request'

/**
 * 获取仪表盘概览
 */
export function getDashboardSummary() {
  return request.get('/dashboard/summary')
}

/**
 * 获取图表数据
 */
export function getChartData(data) {
  return request.post('/dashboard/chart', data)
}

/**
 * 获取2D地图数据
 */
export function get2DMapData(params) {
  return request.get('/dashboard/map/2d', { params })
}

/**
 * 获取3D地球数据
 */
export function get3DGlobeData(params) {
  return request.get('/dashboard/map/3d', { params })
}

/**
 * 获取实时数据
 */
export function getRealtimeData() {
  return request.get('/dashboard/realtime')
}

/**
 * 获取行业分布
 */
export function getIndustryDistribution() {
  return request.get('/dashboard/industry-distribution')
}

/**
 * 获取趋势数据
 */
export function getTrendData(params) {
  return request.get('/dashboard/trend', { params })
}

/**
 * AI数据分析
 */
export function aiDataAnalysis(data) {
  return request.post('/dashboard/ai-analysis', data)
}

/**
 * 获取排行榜数据
 */
export function getRankingData(params) {
  return request.get('/dashboard/ranking', { params })
}

/**
 * 获取全国地区热力数据
 */
export function getHeatmapData() {
  return request.get('/dashboard/heatmap')
}

/**
 * 获取最新采集的20条数据
 */
export function getLatestData(limit = 20) {
  return request.get('/dashboard/latest', { params: { limit } })
}
