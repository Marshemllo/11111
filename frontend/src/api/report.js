import request from './request'

/**
 * 获取报告列表
 */
export function getReportList(params) {
  return request.get('/reports', { params })
}

/**
 * 获取报告详情
 */
export function getReportDetail(id) {
  return request.get(`/reports/${id}`)
}

/**
 * 创建报告
 */
export function createReport(data) {
  return request.post('/reports', data)
}

/**
 * 更新报告
 */
export function updateReport(id, data) {
  return request.put(`/reports/${id}`, data)
}

/**
 * 删除报告
 */
export function deleteReport(id) {
  return request.delete(`/reports/${id}`)
}

/**
 * 下载报告PDF
 */
export function downloadReportPdf(id) {
  return request.get(`/reports/${id}/download`, {
    responseType: 'blob'
  })
}

/**
 * 生成报告PDF
 */
export function generateReportPdf(id) {
  return request.post(`/reports/${id}/generate-pdf`)
}

/**
 * AI生成报告
 */
export function aiGenerateReport(data) {
  return request.post('/reports/ai-generate', data)
}

/**
 * 获取行业列表
 */
export function getIndustries() {
  return request.get('/reports/industries')
}
