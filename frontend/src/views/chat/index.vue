<template>
  <div class="chat-container">
    <!-- 侧边栏 - 在线用户列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <h3>💬 聊天室</h3>
      </div>
      <div class="user-list">
        <div class="user-list-title">在线用户 ({{ onlineUsers.length }})</div>
        <div v-for="user in onlineUsers" :key="user.id" class="user-item">
          <el-avatar :size="32" :style="{ backgroundColor: getAvatarColor(user.username) }">
            {{ user.username?.charAt(0) }}
          </el-avatar>
          <span class="user-name">{{ user.username }}</span>
          <span class="online-dot"></span>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="current-user">
          <el-avatar :size="36" :style="{ backgroundColor: getAvatarColor(currentUsername) }">
            {{ currentUsername?.charAt(0) }}
          </el-avatar>
          <span>{{ currentUsername }}</span>
        </div>
      </div>
    </div>
    
    <!-- 主聊天区域 -->
    <div class="chat-main">
      <div class="chat-header">
        <span class="room-name">🏠 公共聊天室</span>
        <span class="room-info">General Room</span>
      </div>
      
      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div class="system-message">欢迎来到聊天室！</div>
        <template v-for="msg in messages" :key="msg.id">
          <!-- 系统消息 -->
          <div v-if="msg.type === 'system'" class="system-message">
            {{ msg.content }}
          </div>
          <!-- 普通消息 -->
          <div v-else class="message-item" :class="{ 
            'is-self': msg.username === currentUsername, 
            'is-ai': msg.is_ai 
          }">
            <el-avatar :size="36" :style="{ backgroundColor: getAvatarColor(msg.username) }">
              {{ msg.username?.charAt(0) || '?' }}
            </el-avatar>
            <div class="message-content">
              <div class="message-header">
                <span class="sender-name" :class="{ 'ai-name': msg.is_ai }">{{ msg.username }}</span>
                <span class="message-time">{{ msg.time }}</span>
              </div>
              <div class="message-text" :class="{ 'ai-message': msg.is_ai }" v-html="formatMessage(msg.content)"></div>
            </div>
          </div>
        </template>
      </div>
      
      <!-- 工具栏和输入区域 -->
      <div class="chat-input-area">
        <div class="toolbar">
          <el-tooltip content="@成小理 AI助手" placement="top">
            <el-button class="tool-btn" @click="insertText('@成小理 ')">🤖 @成小理</el-button>
          </el-tooltip>
          <el-tooltip content="音乐推荐" placement="top">
            <el-button class="tool-btn" @click="insertText('@音乐 ')">🎵 音乐</el-button>
          </el-tooltip>
          <el-tooltip content="电影推荐" placement="top">
            <el-button class="tool-btn" @click="insertText('@电影 ')">🎬 电影</el-button>
          </el-tooltip>
          <el-tooltip content="天气查询" placement="top">
            <el-button class="tool-btn" @click="insertText('@天气 ')">☀️ 天气</el-button>
          </el-tooltip>
          <el-divider direction="vertical" />
          <el-popover placement="top" :width="280" trigger="click">
            <template #reference>
              <el-button class="tool-btn">😀 表情</el-button>
            </template>
            <div class="emoji-picker">
              <span v-for="emoji in emojis" :key="emoji" class="emoji-item" @click="insertEmoji(emoji)">{{ emoji }}</span>
            </div>
          </el-popover>
          <el-tooltip content="查看历史记录" placement="top">
            <el-button class="tool-btn" @click="showHistory">📜 历史</el-button>
          </el-tooltip>
        </div>
        <div class="input-group">
          <el-input 
            v-model="inputMessage" 
            ref="inputRef"
            placeholder="输入消息... (Enter发送)" 
            @keyup.enter="sendMessage"
            size="large"
          />
          <el-button type="primary" size="large" @click="sendMessage" :disabled="!inputMessage.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>

    <!-- 历史记录对话框 -->
    <el-dialog v-model="historyDialogVisible" title="📜 聊天历史记录" width="600px">
      <div class="history-list">
        <div v-if="historyMessages.length === 0" class="no-history">暂无历史记录</div>
        <div v-for="msg in historyMessages" :key="msg.id" class="history-item">
          <span class="history-user">{{ msg.username }}:</span>
          <span class="history-content">{{ msg.content }}</span>
          <span class="history-time">{{ msg.time }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 用户信息
const currentUsername = ref(localStorage.getItem('chat_username') || '用户' + Math.floor(Math.random() * 1000))
const currentUserId = ref(Date.now())

// 消息和用户列表
const messages = ref([])
const onlineUsers = ref([])
const inputMessage = ref('')
const messageListRef = ref(null)
const inputRef = ref(null)

// 历史记录
const historyDialogVisible = ref(false)
const historyMessages = computed(() => messages.value.filter(m => m.type !== 'system').slice(-50))

// 表情列表
const emojis = ['😀', '😂', '🤣', '😊', '😍', '🥰', '😘', '😎', '🤔', '😴', '😭', '😱', '🥳', '👍', '👎', '👏', '🙏', '💪', '❤️', '💔', '🔥', '⭐', '🎉', '🎊']

// WebSocket
let ws = null
const wsUrl = computed(() => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.hostname}:8000/ws/chat/${currentUserId.value}`
})

// 连接WebSocket
const connectWebSocket = () => {
  try {
    ws = new WebSocket(wsUrl.value)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      // 加入房间
      ws.send(JSON.stringify({ 
        type: 'join_room', 
        room_id: 1,
        username: currentUsername.value 
      }))
      // 添加自己到在线用户
      if (!onlineUsers.value.find(u => u.id === currentUserId.value)) {
        onlineUsers.value.push({ id: currentUserId.value, username: currentUsername.value })
      }
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected, reconnecting...')
      setTimeout(connectWebSocket, 3000)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  } catch (e) {
    console.error('WebSocket connection failed:', e)
  }
}

// 处理WebSocket消息
const handleWebSocketMessage = (data) => {
  const now = new Date().toLocaleTimeString()
  
  switch (data.type) {
    case 'chat_message':
      // 避免重复添加自己发的消息
      if (data.user_id !== currentUserId.value || data.is_ai) {
        messages.value.push({
          id: Date.now() + Math.random(),
          username: data.username,
          content: data.content,
          time: now,
          is_ai: data.is_ai || false
        })
        scrollToBottom()
      }
      break
      
    case 'ai_response':
      messages.value.push({
        id: Date.now() + Math.random(),
        username: 'AI助手',
        content: data.content,
        time: now,
        is_ai: true
      })
      scrollToBottom()
      break
      
    case 'user_joined':
      messages.value.push({
        id: Date.now(),
        type: 'system',
        content: `${data.username || '用户'} 加入了聊天室`
      })
      // 更新在线用户
      if (data.user_id && !onlineUsers.value.find(u => u.id === data.user_id)) {
        onlineUsers.value.push({ id: data.user_id, username: data.username || `用户${data.user_id}` })
      }
      scrollToBottom()
      break
      
    case 'user_left':
      messages.value.push({
        id: Date.now(),
        type: 'system',
        content: `${data.username || '用户'} 离开了聊天室`
      })
      onlineUsers.value = onlineUsers.value.filter(u => u.id !== data.user_id)
      scrollToBottom()
      break
      
    case 'online_users':
      onlineUsers.value = data.users || []
      break
  }
}

// 发送消息
const sendMessage = () => {
  if (!inputMessage.value.trim()) return
  
  const content = inputMessage.value.trim()
  const now = new Date().toLocaleTimeString()
  
  // 添加到本地消息列表
  messages.value.push({
    id: Date.now(),
    username: currentUsername.value,
    content: content,
    time: now,
    is_ai: false
  })
  
  // 通过WebSocket发送
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'chat_message',
      room_id: 1,
      content: content,
      username: currentUsername.value
    }))
  }
  
  inputMessage.value = ''
  scrollToBottom()
}

// 插入文本到输入框
const insertText = (text) => {
  inputMessage.value += text
  inputRef.value?.focus()
}

// 插入表情
const insertEmoji = (emoji) => {
  inputMessage.value += emoji
  inputRef.value?.focus()
}

// 显示历史记录
const showHistory = () => {
  historyDialogVisible.value = true
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 格式化消息（支持链接）
const formatMessage = (content) => {
  if (!content) return ''
  // 将URL转换为可点击链接
  const urlRegex = /(https?:\/\/[^\s]+)/g
  return content.replace(urlRegex, '<a href="$1" target="_blank" class="message-link">$1</a>')
    .replace(/\n/g, '<br>')
}

// 根据用户名生成头像颜色
const getAvatarColor = (username) => {
  if (!username) return '#409EFF'
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#9B59B6', '#3498DB', '#1ABC9C']
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

// 保存用户名
const saveUsername = () => {
  localStorage.setItem('chat_username', currentUsername.value)
}

onMounted(() => {
  saveUsername()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style lang="scss" scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 100px);
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

// 侧边栏
.chat-sidebar {
  width: 250px;
  background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
  color: white;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  text-align: center;
  
  h3 {
    margin: 0;
    font-size: 18px;
  }
}

.user-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.user-list-title {
  font-size: 12px;
  color: #bbb;
  margin-bottom: 15px;
  text-transform: uppercase;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 8px;
  margin-bottom: 5px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.user-name {
  margin-left: 10px;
  flex: 1;
  font-size: 14px;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #67C23A;
  border-radius: 50%;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.current-user {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

// 主聊天区域
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f6fa;
}

.chat-header {
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.room-name {
  font-weight: 600;
  font-size: 16px;
}

.room-info {
  color: #909399;
  font-size: 12px;
}

// 消息列表
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.system-message {
  text-align: center;
  padding: 8px 16px;
  background: #e1e1e1;
  border-radius: 20px;
  font-size: 12px;
  color: #666;
  margin: 10px auto;
  display: inline-block;
  width: fit-content;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  
  &.is-self {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-text {
      background: #dcf8c6;
      border-top-right-radius: 0;
      border-top-left-radius: 12px;
    }
  }
  
  &.is-ai {
    .message-text {
      background: linear-gradient(135deg, #e6f7ff 0%, #f0f9eb 100%);
      border: 1px solid #b7eb8f;
    }
    
    .sender-name {
      color: #52c41a;
    }
  }
}

.message-content {
  margin: 0 10px;
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-header {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
  display: flex;
  gap: 10px;
}

.sender-name {
  font-weight: 500;
  color: #606266;
  
  &.ai-name {
    color: #52c41a;
  }
}

.message-text {
  background: #fff;
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
  line-height: 1.5;
  
  :deep(.message-link) {
    color: #409EFF;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

// 输入区域
.chat-input-area {
  padding: 15px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.tool-btn {
  font-size: 13px;
  padding: 6px 12px;
}

.input-group {
  display: flex;
  gap: 10px;
}

// 表情选择器
.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.emoji-item {
  font-size: 24px;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background 0.2s;
  
  &:hover {
    background: #f5f7fa;
  }
}

// 历史记录
.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.no-history {
  text-align: center;
  color: #909399;
  padding: 40px;
}

.history-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    border-bottom: none;
  }
}

.history-user {
  font-weight: 500;
  color: #409EFF;
  margin-right: 8px;
}

.history-content {
  color: #606266;
}

.history-time {
  float: right;
  font-size: 12px;
  color: #909399;
}

// 响应式
@media (max-width: 768px) {
  .chat-sidebar {
    display: none;
  }
  
  .chat-container {
    border-radius: 0;
  }
}
</style>
