import request from './request'

/**
 * 用户登录
 */
export function login(data) {
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  return request.post('/users/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return request.get('/users/me')
}

/**
 * 更新当前用户信息
 */
export function updateUserInfo(data) {
  return request.put('/users/me', data)
}

/**
 * 用户登出
 */
export function logout() {
  return request.post('/users/logout')
}

/**
 * 获取用户列表
 */
export function getUserList(params) {
  return request.get('/users', { params })
}

/**
 * 获取用户详情
 */
export function getUserDetail(id) {
  return request.get(`/users/${id}`)
}

/**
 * 创建用户（超级管理员）
 */
export function createUser(data) {
  return request.post('/users/create', data)
}

/**
 * 更新用户
 */
export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

/**
 * 删除用户
 */
export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

/**
 * 切换用户状态
 */
export function toggleUserStatus(id) {
  return request.post(`/users/${id}/toggle-status`)
}
