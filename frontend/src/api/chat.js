import request from './request'

// ==================== 聊天室API ====================

/**
 * 获取聊天室列表
 */
export function getChatRoomList() {
  return request.get('/chat/rooms')
}

/**
 * 获取聊天室详情
 */
export function getChatRoomDetail(id) {
  return request.get(`/chat/rooms/${id}`)
}

/**
 * 创建聊天室
 */
export function createChatRoom(data) {
  return request.post('/chat/rooms', data)
}

/**
 * 更新聊天室
 */
export function updateChatRoom(id, data) {
  return request.put(`/chat/rooms/${id}`, data)
}

/**
 * 删除聊天室
 */
export function deleteChatRoom(id) {
  return request.delete(`/chat/rooms/${id}`)
}

/**
 * 加入聊天室
 */
export function joinChatRoom(id) {
  return request.post(`/chat/rooms/${id}/join`)
}

/**
 * 离开聊天室
 */
export function leaveChatRoom(id) {
  return request.post(`/chat/rooms/${id}/leave`)
}

/**
 * 获取聊天室成员
 */
export function getChatRoomMembers(id) {
  return request.get(`/chat/rooms/${id}/members`)
}

// ==================== 消息API ====================

/**
 * 获取聊天记录
 */
export function getChatMessages(roomId, params) {
  return request.get(`/chat/rooms/${roomId}/messages`, { params })
}

/**
 * 发送消息
 */
export function sendMessage(data) {
  return request.post('/chat/messages', data)
}

/**
 * 删除消息
 */
export function deleteMessage(id) {
  return request.delete(`/chat/messages/${id}`)
}

// ==================== 私聊API ====================

/**
 * 发起私聊
 */
export function startPrivateChat(userId) {
  return request.post(`/chat/private/${userId}`)
}

// ==================== AI命令API ====================

/**
 * 处理AI命令
 */
export function processAICommand(content) {
  return request.post('/chat/ai-command', null, { params: { content } })
}
