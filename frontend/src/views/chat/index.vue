<template>
  <div class="chat-container">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" size="small" @click="handleCreateRoom">新建群聊</el-button>
      </div>
      <div class="room-list">
        <div v-for="room in roomList" :key="room.id" class="room-item" :class="{ active: currentRoom?.id === room.id }" @click="selectRoom(room)">
          <el-avatar :size="40">{{ room.name?.charAt(0) }}</el-avatar>
          <div class="room-info">
            <div class="room-name">{{ room.name }}</div>
            <div class="room-desc">{{ room.description || '暂无描述' }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-main">
      <div v-if="currentRoom" class="chat-header">
        <span>{{ currentRoom.name }}</span>
        <span class="member-count">{{ currentRoom.member_count || 0 }}人</span>
      </div>
      
      <div class="message-list" ref="messageListRef">
        <div v-for="msg in messages" :key="msg.id" class="message-item" :class="{ 'is-self': msg.sender_id === currentUserId, 'is-ai': msg.message_type === 'ai_response' }">
          <el-avatar :size="36">{{ msg.sender_name?.charAt(0) || 'AI' }}</el-avatar>
          <div class="message-content">
            <div class="message-header">
              <span class="sender-name">{{ msg.sender_name || 'AI助手' }}</span>
              <span class="message-time">{{ msg.created_at }}</span>
            </div>
            <div class="message-text">{{ msg.content }}</div>
            <div v-if="msg.ai_response" class="ai-response-box">
              <div class="ai-label">AI回复:</div>
              <div>{{ msg.ai_response }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <el-input v-model="inputMessage" placeholder="输入消息，@AI 可调用AI助手" @keyup.enter="sendMessage">
          <template #append>
            <el-button @click="sendMessage">发送</el-button>
          </template>
        </el-input>
        <div class="input-tips">提示: 输入 @AI 播放音乐/查询天气/显示图表 等命令</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { getChatRoomList, getChatMessages, sendMessage as sendMessageApi } from '@/api/chat'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUserId = ref(1)
const roomList = ref([])
const currentRoom = ref(null)
const messages = ref([])
const inputMessage = ref('')
const messageListRef = ref(null)
let ws = null

const loadRooms = async () => {
  try { roomList.value = await getChatRoomList() } catch (e) { console.error(e) }
}

const selectRoom = async (room) => {
  currentRoom.value = room
  try { messages.value = await getChatMessages(room.id) } catch (e) { console.error(e) }
  scrollToBottom()
  if (ws) ws.send(JSON.stringify({ type: 'join_room', room_id: room.id }))
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !currentRoom.value) return
  const content = inputMessage.value
  inputMessage.value = ''
  messages.value.push({ id: Date.now(), sender_id: currentUserId.value, sender_name: '我', content, created_at: new Date().toLocaleTimeString() })
  scrollToBottom()
  if (ws) ws.send(JSON.stringify({ type: 'chat_message', room_id: currentRoom.value.id, content }))
}

const scrollToBottom = () => { nextTick(() => { if (messageListRef.value) messageListRef.value.scrollTop = messageListRef.value.scrollHeight }) }
const handleCreateRoom = () => { /* TODO */ }

const connectWebSocket = () => {
  ws = new WebSocket(`ws://${window.location.host}/ws/chat/${currentUserId.value}`)
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'chat_message' || data.type === 'ai_response') {
      messages.value.push({ id: Date.now(), ...data })
      scrollToBottom()
    }
  }
}

onMounted(() => { loadRooms(); connectWebSocket() })
onUnmounted(() => { if (ws) ws.close() })
</script>

<style lang="scss" scoped>
.chat-container { display: flex; height: calc(100vh - 100px); background: #fff; border-radius: 8px; overflow: hidden; }
.chat-sidebar { width: 280px; border-right: 1px solid #e4e7ed; display: flex; flex-direction: column; }
.sidebar-header { padding: 15px; border-bottom: 1px solid #e4e7ed; }
.room-list { flex: 1; overflow-y: auto; }
.room-item { display: flex; align-items: center; padding: 12px 15px; cursor: pointer; &:hover, &.active { background: #f5f7fa; } }
.room-info { margin-left: 10px; flex: 1; overflow: hidden; }
.room-name { font-weight: 500; }
.room-desc { font-size: 12px; color: #909399; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-main { flex: 1; display: flex; flex-direction: column; }
.chat-header { padding: 15px 20px; border-bottom: 1px solid #e4e7ed; font-weight: 500; .member-count { margin-left: 10px; color: #909399; font-size: 12px; } }
.message-list { flex: 1; overflow-y: auto; padding: 20px; }
.message-item { display: flex; margin-bottom: 20px; &.is-self { flex-direction: row-reverse; .message-content { align-items: flex-end; } } &.is-ai .message-text { background: #e6f7ff; } }
.message-content { margin: 0 10px; max-width: 70%; }
.message-header { font-size: 12px; color: #909399; margin-bottom: 5px; }
.message-text { background: #f5f7fa; padding: 10px 15px; border-radius: 8px; }
.ai-response-box { margin-top: 10px; padding: 10px; background: #f0f9eb; border-radius: 8px; .ai-label { font-weight: 500; color: #67c23a; margin-bottom: 5px; } }
.chat-input { padding: 15px 20px; border-top: 1px solid #e4e7ed; .input-tips { font-size: 12px; color: #909399; margin-top: 8px; } }
</style>
