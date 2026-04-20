<template>
  <div class="messages-page">
    <div class="messages-layout">

      <!-- Sidebar -->
      <div class="thread-sidebar" :class="{ 'mobile-hidden': activeThread }">
        <div class="sidebar-header">
          <h2>Messages</h2>
          <span v-if="totalUnread > 0" class="total-unread-badge">{{ totalUnread }}</span>
        </div>
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input v-model="search" placeholder="Search conversations..." />
        </div>

        <div v-if="loadingThreads" class="thread-loading">
          <div class="thread-skeleton" v-for="n in 4" :key="n"></div>
        </div>

        <div class="thread-list" v-else>
          <p v-if="filteredThreads.length === 0" class="empty-threads">
            {{ search ? 'No results found.' : 'No conversations yet.' }}
          </p>
          <div
            v-for="thread in filteredThreads"
            :key="thread.seller_id"
            class="thread-item"
            :class="{ active: activeThread?.seller_id === thread.seller_id, unread: thread.unread }"
            @click="openThread(thread)"
          >
            <div class="avatar">{{ initials(thread.seller_name) }}</div>
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
      <div v-if="activeThread" class="chat-window">
        <div class="chat-header">
          <button class="back-btn" @click="activeThread = null">
            <i class="fa-solid fa-arrow-left"></i>
          </button>
          <div class="avatar gold">{{ initials(activeThread.seller_name) }}</div>
          <div class="chat-partner-info">
            <p class="chat-partner-name">{{ activeThread.seller_name }}</p>
            <span class="chat-status">
              <i class="fa-solid fa-circle"></i> ADNU Student
            </span>
          </div>
        </div>

        <div v-if="isSelfChat" class="self-chat-warning">
          <i class="fa-solid fa-circle-info"></i>
          This is your own account. You cannot message yourself.
        </div>

        <div class="message-list" ref="messageListRef">
          <div v-if="loadingMessages" class="messages-loading">
            <div class="msg-skeleton right"></div>
            <div class="msg-skeleton left"></div>
            <div class="msg-skeleton right"></div>
          </div>
          <template v-else>
            <div v-if="messages.length === 0" class="no-messages">
              <i class="fa-regular fa-comments" style="font-size:2rem;color:#ccc;display:block;margin-bottom:8px"></i>
              No messages yet. Say hello! 👋
            </div>
            <div
              v-for="(msg, i) in messages"
              :key="i"
              class="message-row"
              :class="isMine(msg) ? 'mine' : 'theirs'"
            >
              <div v-if="!isMine(msg)" class="msg-avatar">{{ initials(activeThread.seller_name) }}</div>
              <div class="bubble">
                {{ msg.message_text }}
                <span class="msg-time">{{ formatTime(msg.sent_at) }}</span>
              </div>
            </div>
          </template>
        </div>

        <div class="chat-input-row">
          <input
            v-model="newMessage"
            placeholder="Type a message..."
            @keyup.enter="sendMessage"
            :disabled="isSelfChat || sending"
            class="chat-input"
          />
          <button
            class="send-btn"
            @click="sendMessage"
            :disabled="!newMessage.trim() || sending || isSelfChat"
          >
            <i class="fa-solid fa-paper-plane" v-if="!sending"></i>
            <i class="fa-solid fa-circle-notch fa-spin" v-else></i>
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
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
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
const loadingThreads = ref(true)
const loadingMessages = ref(false)
const messageListRef = ref(null)
let pollInterval = null

// ── Computed ──────────────────────────────────────────────

const totalUnread = computed(() => threads.value.filter(t => t.unread).length)

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

const isMine = (msg) => Number(msg.sender_id) === Number(user?.user_id)
const initials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

// ── Fetchers ──────────────────────────────────────────────

const fetchThreads = async (silent = false) => {
  if (!user) return
  if (!silent) loadingThreads.value = true
  try {
    const res = await api.getThreads(user.user_id)
    const fresh = res.data || []

    // Preserve unread state for active thread
    if (activeThread.value) {
      const active = fresh.find(t => Number(t.seller_id) === Number(activeThread.value.seller_id))
      if (active) active.unread = false
    }

    threads.value = fresh
  } catch (err) {
    console.error('Fetch threads error:', err)
  } finally {
    loadingThreads.value = false
  }
}

const openThread = async (thread) => {
  activeThread.value = { ...thread, seller_id: Number(thread.seller_id) }
  // Mark as read locally immediately
  const t = threads.value.find(t => Number(t.seller_id) === Number(thread.seller_id))
  if (t) t.unread = false

  loadingMessages.value = true
  try {
    const res = await api.getMessages(Number(user.user_id), Number(thread.seller_id))
    messages.value = res.data || []
    await scrollToBottom()

    // Mark messages as read on the server
    await api.markMessagesRead({
      reader_id: Number(user.user_id),
      sender_id: Number(thread.seller_id)
    }).catch(() => {})
  } catch (err) {
    console.error('Open thread error:', err)
    messages.value = []
  } finally {
    loadingMessages.value = false
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || sending.value || isSelfChat.value) return
  const text = newMessage.value.trim()
  newMessage.value = ''
  try {
    sending.value = true
    await api.sendMessage({
      sender_id: Number(user.user_id),
      receiver_id: Number(activeThread.value.seller_id),
      message_text: text
    })
    // Optimistically add message
    messages.value.push({
      sender_id: Number(user.user_id),
      receiver_id: Number(activeThread.value.seller_id),
      message_text: text,
      sent_at: new Date().toISOString()
    })
    // Update thread preview
    const t = threads.value.find(t => Number(t.seller_id) === Number(activeThread.value.seller_id))
    if (t) { t.last_message = text; t.last_time = new Date().toISOString() }
    await scrollToBottom()
  } catch (err) {
    console.error('Send error:', err)
    newMessage.value = text // restore on failure
    alert((err.response?.data?.message || 'Failed to send message') + ' ❌')
  } finally {
    sending.value = false
  }
}

// ── Polling ───────────────────────────────────────────────

const pollMessages = async () => {
  if (!activeThread.value || isSelfChat.value) return
  try {
    const res = await api.getMessages(Number(user.user_id), Number(activeThread.value.seller_id))
    const fresh = res.data || []
    if (fresh.length > messages.value.length) {
      messages.value = fresh
      await scrollToBottom()
    }
  } catch {}
}

const pollThreads = async () => {
  await fetchThreads(true)
}

// ── Helpers ───────────────────────────────────────────────

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const formatTime = (d) => {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
}

// ── Lifecycle ─────────────────────────────────────────────

onMounted(async () => {
  await fetchThreads()

  // Handle query param from product page / cart
  const sellerId = route.query.seller_id
  if (sellerId) {
    const sellerIdNum = Number(sellerId)
    let thread = threads.value.find(t => Number(t.seller_id) === sellerIdNum)
    if (!thread) {
      thread = {
        seller_id: sellerIdNum,
        seller_name: route.query.seller_name || 'Seller',
        last_message: '',
        last_time: '',
        unread: false
      }
      threads.value.unshift(thread)
    }
    openThread(thread)
  }

  // Poll messages every 4s, threads every 10s
  pollInterval = setInterval(() => {
    pollMessages()
  }, 4000)

  setInterval(() => {
    pollThreads()
  }, 10000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.messages-page {
  background: #f8fafc;
  min-height: calc(100vh - 60px);
  padding: 20px;
}

.messages-layout {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 300px 1fr;
  height: calc(100vh - 100px);
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

/* Sidebar */
.thread-sidebar {
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
}

.sidebar-header h2 {
  font-size: 1rem;
  font-weight: 800;
  color: #003366;
  margin: 0;
  flex: 1;
}

.total-unread-badge {
  background: #003366;
  color: white;
  font-size: 11px;
  font-weight: 800;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}

.search-box {
  padding: 10px 14px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #aaa;
  background: white;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.85rem;
  background: transparent;
  color: #333;
  font-family: inherit;
}

.thread-list { overflow-y: auto; flex: 1; }

.thread-loading { padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.thread-skeleton {
  height: 64px;
  border-radius: 10px;
  background: linear-gradient(110deg, #ececec 8%, #f5f5f5 18%, #ececec 33%);
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}
@keyframes shimmer { to { background-position-x: -200%; } }

.empty-threads {
  padding: 24px 16px;
  text-align: center;
  color: #999;
  font-size: 0.85rem;
}

.thread-item {
  display: flex;
  gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  align-items: flex-start;
  transition: background 0.15s;
  position: relative;
}

.thread-item:hover { background: #f0f4ff; }
.thread-item.active { background: #e8f0fe; }
.thread-item.unread { background: #f5f8ff; }

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #003366;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
  flex-shrink: 0;
  letter-spacing: 0;
}

.avatar.gold { background: #FFD700; color: #003366; }

.thread-info { flex: 1; min-width: 0; }

.thread-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3px;
}

.thread-name {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
}

.thread-time { font-size: 0.68rem; color: #999; white-space: nowrap; }
.thread-preview {
  font-size: 0.78rem;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}

.thread-item.unread .thread-name { color: #003366; }
.thread-item.unread .thread-preview { color: #555; font-weight: 500; }

.unread-dot {
  width: 9px;
  height: 9px;
  background: #003366;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}

/* Chat Window */
.chat-window {
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
}

.back-btn {
  display: none;
  background: none;
  border: none;
  color: #003366;
  cursor: pointer;
  font-size: 1rem;
  padding: 4px 8px;
  border-radius: 6px;
}

.back-btn:hover { background: #f0f4ff; }

.chat-partner-info { flex: 1; }
.chat-partner-name { font-size: 0.9rem; font-weight: 800; color: #003366; margin: 0 0 2px; }
.chat-status { font-size: 0.72rem; color: #16a34a; display: flex; align-items: center; gap: 4px; }
.chat-status i { font-size: 7px; }

.self-chat-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fffbeb;
  color: #92400e;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 10px 16px;
  border-bottom: 1px solid #fde68a;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f8fafc;
}

.messages-loading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.msg-skeleton {
  height: 44px;
  width: 60%;
  border-radius: 14px;
  background: linear-gradient(110deg, #ececec 8%, #f5f5f5 18%, #ececec 33%);
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}

.msg-skeleton.right { align-self: flex-end; }
.msg-skeleton.left { align-self: flex-start; }

.no-messages {
  text-align: center;
  color: #bbb;
  font-size: 0.875rem;
  margin: auto;
  padding: 2rem;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 7px;
}

.message-row.mine { justify-content: flex-end; }
.message-row.theirs { justify-content: flex-start; }

.msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #003366;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.65rem;
  flex-shrink: 0;
}

.bubble {
  max-width: 62%;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 0.875rem;
  line-height: 1.5;
  word-break: break-word;
}

.mine .bubble {
  background: #003366;
  color: white;
  border-bottom-right-radius: 4px;
}

.theirs .bubble {
  background: white;
  color: #222;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}

.msg-time {
  display: block;
  font-size: 0.62rem;
  margin-top: 4px;
  opacity: 0.6;
  text-align: right;
}

.chat-input-row {
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 10px;
  align-items: center;
  background: white;
}

.chat-input {
  flex: 1;
  padding: 10px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 24px;
  font-size: 0.9rem;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.chat-input:focus { border-color: #003366; }
.chat-input:disabled { background: #f8fafc; color: #aaa; }

.send-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #003366;
  color: #FFD700;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  transition: 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) { background: #002244; transform: scale(1.05); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

/* Empty chat state */
.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ccc;
  font-size: 0.9rem;
  gap: 12px;
  background: #fafafa;
}

.empty-icon { font-size: 3.5rem; }

/* Mobile */
@media (max-width: 640px) {
  .messages-page { padding: 0; }

  .messages-layout {
    grid-template-columns: 1fr;
    height: calc(100vh - 60px);
    border-radius: 0;
    border: none;
  }

  .thread-sidebar { border-right: none; }
  .thread-sidebar.mobile-hidden { display: none; }
  .back-btn { display: flex; }
  .empty-chat { display: none; }
}
</style>