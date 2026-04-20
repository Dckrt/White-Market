<template>
  <div class="messages-page">
    <div class="messages-layout">

      <!-- Sidebar -->
      <div class="thread-sidebar">
        <div class="sidebar-header">
          <h2>Messages</h2>
        </div>
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input v-model="search" placeholder="Search conversations..." />
        </div>
        <div class="thread-list">
          <p v-if="filteredThreads.length === 0" class="empty-threads">No conversations yet.</p>
          <div
            v-for="thread in filteredThreads"
            :key="thread.seller_id"
            class="thread-item"
            :class="{ active: activeThread?.seller_id === thread.seller_id }"
            @click="openThread(thread)"
          >
            <div class="avatar">{{ thread.seller_name?.charAt(0)?.toUpperCase() || '?' }}</div>
            <div class="thread-info">
              <div class="thread-top">
                <span class="thread-name">{{ thread.seller_name }}</span>
                <span class="thread-time">{{ formatTime(thread.last_time) }}</span>
              </div>
              <p class="thread-preview">{{ thread.last_message || 'Start a conversation' }}</p>
            </div>
            <span v-if="thread.unread" class="unread-dot"></span>
          </div>
        </div>
      </div>

      <!-- Chat Window -->
      <div class="chat-window" v-if="activeThread">
        <div class="chat-header">
          <div class="avatar gold">{{ activeThread.seller_name?.charAt(0)?.toUpperCase() }}</div>
          <div>
            <p class="chat-partner-name">{{ activeThread.seller_name }}</p>
            <span class="chat-status">ADNU Student</span>
          </div>
        </div>

        <div v-if="isSelfChat" class="self-chat-warning">
          <i class="fa-solid fa-circle-info"></i>
          This is your own account. Use a different account to send messages.
        </div>

        <div class="message-list" ref="messageListRef">
          <div v-if="messages.length === 0" class="no-messages">
            No messages yet. Say hello! 👋
          </div>
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="message-row"
            :class="Number(msg.sender_id) === Number(user?.user_id) ? 'mine' : 'theirs'"
          >
            <div class="bubble">
              {{ msg.message_text }}
              <span class="msg-time">{{ formatTime(msg.sent_at) }}</span>
            </div>
          </div>
        </div>

        <div class="chat-input-row">
          <input
            v-model="newMessage"
            placeholder="Type a message..."
            @keyup.enter="sendMessage"
            :disabled="isSelfChat"
          />
          <button class="send-btn" @click="sendMessage"
            :disabled="!newMessage.trim() || sending || isSelfChat">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-chat" v-else>
        <i class="fa-regular fa-comments empty-icon"></i>
        <p>Select a conversation to start messaging</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const user = JSON.parse(localStorage.getItem('user'))

const threads = ref([])
const activeThread = ref(null)
const messages = ref([])
const newMessage = ref('')
const search = ref('')
const sending = ref(false)
const messageListRef = ref(null)
let pollInterval = null

const isSelfChat = computed(() =>
  activeThread.value &&
  Number(activeThread.value.seller_id) === Number(user?.user_id)
)

const filteredThreads = computed(() => {
  if (!search.value) return threads.value
  return threads.value.filter(t =>
    t.seller_name?.toLowerCase().includes(search.value.toLowerCase())
  )
})

const fetchThreads = async () => {
  if (!user) return
  try {
    const res = await api.getThreads(user.user_id)
    threads.value = res.data || []
    const sellerId = route.query.seller_id
    if (sellerId) {
      const sellerIdNum = Number(sellerId)
      let thread = threads.value.find(t => Number(t.seller_id) === sellerIdNum)
      if (!thread) {
        thread = {
          seller_id: sellerIdNum,
          seller_name: route.query.seller_name || 'Seller',
          last_message: '', last_time: '', unread: false
        }
        threads.value.unshift(thread)
      }
      openThread(thread)
    }
  } catch (err) {
    console.error('Fetch threads error:', err)
  }
}

const openThread = async (thread) => {
  activeThread.value = { ...thread, seller_id: Number(thread.seller_id) }
  thread.unread = false
  try {
    const res = await api.getMessages(Number(user.user_id), Number(thread.seller_id))
    messages.value = res.data || []
    await scrollToBottom()
  } catch (err) {
    console.error('Open thread error:', err)
    messages.value = []
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || sending.value || isSelfChat.value) return
  const text = newMessage.value.trim()
  try {
    sending.value = true
    await api.sendMessage({
      sender_id: Number(user.user_id),
      receiver_id: Number(activeThread.value.seller_id),
      message_text: text
    })
    messages.value.push({
      sender_id: Number(user.user_id),
      receiver_id: Number(activeThread.value.seller_id),
      message_text: text,
      sent_at: new Date().toISOString()
    })
    const thread = threads.value.find(t => Number(t.seller_id) === Number(activeThread.value.seller_id))
    if (thread) thread.last_message = text
    newMessage.value = ''
    await scrollToBottom()
  } catch (err) {
    console.error('Send error:', err)
    alert((err.response?.data?.message || 'Failed to send message') + ' ❌')
  } finally {
    sending.value = false
  }
}

const pollMessages = async () => {
  if (!activeThread.value || isSelfChat.value) return
  try {
    const res = await api.getMessages(Number(user.user_id), Number(activeThread.value.seller_id))
    const fresh = res.data || []
    if (fresh.length !== messages.value.length) {
      messages.value = fresh
      await scrollToBottom()
    }
  } catch {}
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) messageListRef.value.scrollTop = messageListRef.value.scrollHeight
}

const formatTime = (d) => {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = now - date
  if (diff < 3600000) return `${Math.max(1, Math.floor(diff / 60000))}m ago`
  if (diff < 86400000) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return date.toLocaleDateString()
}

onMounted(async () => {
  await fetchThreads()
  pollInterval = setInterval(pollMessages, 5000)
})

onUnmounted(() => { if (pollInterval) clearInterval(pollInterval) })
</script>

<style scoped>
.messages-page { background: #f8fafc; min-height: 100vh; padding: 24px; }
.messages-layout {
  max-width: 1000px; margin: 0 auto;
  display: grid; grid-template-columns: 280px 1fr;
  height: calc(100vh - 108px); background: white;
  border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.thread-sidebar { border-right: 1px solid #e5e7eb; display: flex; flex-direction: column; }
.sidebar-header { padding: 16px; border-bottom: 1px solid #e5e7eb; }
.sidebar-header h2 { font-size: 1rem; font-weight: 700; color: #003366; margin: 0; }
.search-box { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center; gap: 8px; color: #aaa; }
.search-box input { flex: 1; border: none; outline: none; font-size: 0.85rem; background: transparent; color: #333; }
.thread-list { overflow-y: auto; flex: 1; }
.empty-threads { padding: 20px; text-align: center; color: #999; font-size: 0.85rem; }
.thread-item { display: flex; gap: 10px; padding: 12px 14px; cursor: pointer; border-bottom: 1px solid #f5f5f5; align-items: flex-start; transition: background 0.15s; position: relative; }
.thread-item:hover { background: #f0f4ff; }
.thread-item.active { background: #e8f0fe; }
.avatar { width: 38px; height: 38px; border-radius: 50%; background: #003366; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; flex-shrink: 0; }
.avatar.gold { background: #FFD700; color: #003366; }
.thread-info { flex: 1; min-width: 0; }
.thread-top { display: flex; justify-content: space-between; margin-bottom: 2px; }
.thread-name { font-size: 0.85rem; font-weight: 700; color: #1a1a1a; }
.thread-time { font-size: 0.7rem; color: #999; }
.thread-preview { font-size: 0.78rem; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0; }
.unread-dot { width: 8px; height: 8px; background: #003366; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.chat-window { display: flex; flex-direction: column; }
.chat-header { padding: 12px 16px; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center; gap: 10px; }
.chat-partner-name { font-size: 0.9rem; font-weight: 700; color: #003366; margin: 0 0 2px; }
.chat-status { font-size: 0.75rem; color: #16a34a; }
.self-chat-warning { display: flex; align-items: center; gap: 8px; background: #fffbeb; color: #92400e; font-size: 0.82rem; font-weight: 600; padding: 10px 16px; border-bottom: 1px solid #fde68a; }
.message-list { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; background: #f8fafc; }
.no-messages { text-align: center; color: #aaa; font-size: 0.85rem; margin-top: 2rem; }
.message-row { display: flex; }
.message-row.mine { justify-content: flex-end; }
.message-row.theirs { justify-content: flex-start; }
.bubble { max-width: 65%; padding: 10px 14px; border-radius: 16px; font-size: 0.875rem; line-height: 1.5; }
.mine .bubble { background: #003366; color: white; border-bottom-right-radius: 4px; }
.theirs .bubble { background: white; color: #333; border: 1px solid #e5e7eb; border-bottom-left-radius: 4px; }
.msg-time { display: block; font-size: 0.65rem; margin-top: 4px; opacity: 0.6; text-align: right; }
.chat-input-row { padding: 12px 16px; border-top: 1px solid #e5e7eb; display: flex; gap: 10px; align-items: center; background: white; }
.chat-input-row input { flex: 1; padding: 10px 16px; border: 1px solid #e2e8f0; border-radius: 24px; font-size: 0.9rem; outline: none; }
.chat-input-row input:focus { border-color: #003366; }
.chat-input-row input:disabled { background: #f8fafc; color: #aaa; }
.send-btn { width: 40px; height: 40px; border-radius: 50%; background: #003366; color: #FFD700; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; transition: 0.2s; flex-shrink: 0; }
.send-btn:hover:not(:disabled) { background: #002244; transform: scale(1.05); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.empty-chat { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #ccc; font-size: 0.9rem; gap: 12px; background: #f8fafc; }
.empty-icon { font-size: 3rem; }
@media (max-width: 640px) {
  .messages-layout { grid-template-columns: 1fr; }
  .thread-sidebar { display: none; }
}
</style>