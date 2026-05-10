<template>
  <div class="msg-page">
    <div class="msg-layout" :class="{ 'msg-layout--open': activeThread }">

      <!-- SIDEBAR -->
      <aside class="msg-sidebar" :class="{ 'msg-sidebar--hidden': activeThread }">
        <div class="msg-sidebar__head">
          <h1 class="msg-sidebar__title">Messages</h1>
          <span v-if="totalUnread > 0" class="msg-unread-badge">{{ totalUnread }}</span>
        </div>
        <div class="msg-sidebar__search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input v-model="search" placeholder="Search conversations…" class="msg-search-input" />
        </div>

        <div v-if="loadingThreads" class="msg-thread-list">
          <div class="thread-skel" v-for="n in 4" :key="n"></div>
        </div>

        <div v-else class="msg-thread-list">
          <p v-if="!filteredThreads.length" class="msg-empty-threads">
            {{ search ? 'No results.' : 'No conversations yet.' }}
          </p>
          <div
            v-for="t in filteredThreads"
            :key="t.seller_id"
            class="thread-item"
            :class="{
              'thread-item--active': activeThread?.seller_id === t.seller_id,
              'thread-item--unread': t.unread
            }"
            @click="openThread(t)"
          >
            <div class="thread-av">{{ initials(t.seller_name) }}</div>
            <div class="thread-body">
              <div class="thread-row">
                <span class="thread-name">{{ t.seller_name }}</span>
                <span class="thread-time">{{ relTime(t.last_time) }}</span>
              </div>
              <p class="thread-preview">{{ t.last_message || 'Tap to open conversation' }}</p>
            </div>
            <div v-if="t.unread" class="thread-pip"></div>
          </div>
        </div>
      </aside>

      <!-- CHAT PANEL -->
      <main v-if="activeThread" class="msg-chat">
        <div class="msg-chat__head">
          <button class="msg-back" @click="backToList">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div class="thread-av thread-av--gold">{{ initials(activeThread.seller_name) }}</div>
          <div>
            <p class="msg-chat__name">{{ activeThread.seller_name }}</p>
            <p class="msg-chat__status">
              <span class="msg-chat__dot"></span>ADNU Verified Student
            </p>
          </div>
          <span class="msg-chat__hint" style="margin-left:auto">Enter to send</span>
        </div>

        <div v-if="isSelfChat" class="self-warn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          You cannot message yourself.
        </div>

        <div class="msg-list" ref="msgListRef">
          <div v-if="loadingMsgs" style="padding:16px;display:flex;flex-direction:column;gap:10px">
            <div class="bubble-skel bubble-skel--r"></div>
            <div class="bubble-skel bubble-skel--l"></div>
            <div class="bubble-skel bubble-skel--r"></div>
          </div>
          <template v-else>
            <div v-if="!messages.length" class="msg-empty-chat">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              <p>No messages yet. Say hello!</p>
            </div>
            <template v-for="(msg, i) in messages" :key="i">
              <div v-if="showDateSep(i)" class="date-sep">
                <span>{{ dateLabel(msg.sent_at) }}</span>
              </div>
              <div class="msg-row" :class="isMine(msg) ? 'msg-row--mine' : 'msg-row--theirs'">
                <div v-if="!isMine(msg)" class="msg-mini-av">{{ initials(activeThread.seller_name) }}</div>
                <div class="bubble" :class="isMine(msg) ? 'bubble--mine' : 'bubble--theirs'">
                  {{ msg.message_text }}
                  <span class="bubble__time">{{ msgTime(msg.sent_at) }}</span>
                </div>
              </div>
            </template>
          </template>
        </div>

        <div class="msg-compose">
          <input
            v-model="newMsg"
            class="msg-input"
            placeholder="Type a message…"
            :disabled="isSelfChat || sending"
            @keyup.enter="send"
            ref="msgInputRef"
          />
          <button class="send-btn" :disabled="!newMsg.trim() || sending || isSelfChat" @click="send">
            <svg v-if="!sending" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          </button>
        </div>
      </main>

      <!-- Empty panel -->
      <div v-else class="msg-empty-panel">
        <div class="msg-empty-panel__icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.4"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        </div>
        <p class="msg-empty-panel__title">Your conversations</p>
        <p class="msg-empty-panel__sub">Select a thread to start messaging</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const user  = JSON.parse(localStorage.getItem('user') || 'null')

const threads        = ref([])
const activeThread   = ref(null)
const messages       = ref([])
const newMsg         = ref('')
const search         = ref('')
const sending        = ref(false)
const loadingThreads = ref(true)
const loadingMsgs    = ref(false)
const msgListRef     = ref(null)
const msgInputRef    = ref(null)
let   pollTimer      = null

// ── Computed ──────────────────────────────────────────────────────────────────
const totalUnread = computed(() => threads.value.filter(t => t.unread).length)
const isSelfChat  = computed(() =>
  activeThread.value && Number(activeThread.value.seller_id) === Number(user?.user_id)
)
const filteredThreads = computed(() => {
  if (!search.value.trim()) return threads.value
  const q = search.value.toLowerCase()
  return threads.value.filter(t => t.seller_name?.toLowerCase().includes(q))
})
const isMine   = (msg) => Number(msg.sender_id) === Number(user?.user_id)
const initials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

// ── Fetch all conversation threads ────────────────────────────────────────────
const fetchThreads = async (silent = false) => {
  if (!user) return
  if (!silent) loadingThreads.value = true
  try {
    const r = await api.getThreads(user.user_id)
    const fresh = Array.isArray(r.data) ? r.data : []

    // If we have an active thread, preserve its unread=false status
    if (activeThread.value) {
      const found = fresh.find(t => Number(t.seller_id) === Number(activeThread.value.seller_id))
      if (found) found.unread = false
    }

    // Merge: keep any temp threads (added before server confirms) 
    const serverIds = new Set(fresh.map(t => Number(t.seller_id)))
    const localOnly = threads.value.filter(t => t._temp && !serverIds.has(Number(t.seller_id)))
    threads.value = [...fresh, ...localOnly]

  } catch (e) {
    console.error('fetchThreads error:', e)
  } finally {
    loadingThreads.value = false
  }
}

// ── Open a conversation thread ────────────────────────────────────────────────
const openThread = async (t) => {
  const partnerId = Number(t.seller_id)
  activeThread.value = { ...t, seller_id: partnerId }

  // Mark as read locally
  const local = threads.value.find(x => Number(x.seller_id) === partnerId)
  if (local) local.unread = false

  loadingMsgs.value = true
  messages.value = []

  try {
    const r = await api.getMessages(Number(user.user_id), partnerId)
    messages.value = Array.isArray(r.data) ? r.data : []
    await scrollBottom()
    // Mark server-side as read
    api.markMessagesRead({
      reader_id: Number(user.user_id),
      sender_id: partnerId
    }).catch(() => {})
  } catch (e) {
    console.error('openThread error:', e)
    messages.value = []
  } finally {
    loadingMsgs.value = false
  }

  await nextTick()
  msgInputRef.value?.focus()
}

// ── Back to thread list (mobile) ──────────────────────────────────────────────
const backToList = () => {
  activeThread.value = null
  fetchThreads(true) // refresh threads when going back
}

// ── Send a message ────────────────────────────────────────────────────────────
const send = async () => {
  const text = newMsg.value.trim()
  if (!text || sending.value || isSelfChat.value) return

  newMsg.value = ''
  sending.value = true

  const partnerId = Number(activeThread.value.seller_id)
  const now       = new Date().toISOString()

  // Optimistic: add to messages immediately
  const optimistic = {
    sender_id:    Number(user.user_id),
    receiver_id:  partnerId,
    message_text: text,
    sent_at:      now,
    _optimistic:  true
  }
  messages.value.push(optimistic)
  await scrollBottom()

  // Optimistic: update thread preview
  let thread = threads.value.find(x => Number(x.seller_id) === partnerId)
  if (thread) {
    thread.last_message = text
    thread.last_time    = now
    thread.unread       = false
    thread._temp        = false
  } else {
    // Thread not in list yet — add it temporarily
    threads.value.unshift({
      seller_id:    partnerId,
      seller_name:  activeThread.value.seller_name,
      last_message: text,
      last_time:    now,
      unread:       false,
      _temp:        true
    })
  }

  try {
    await api.sendMessage({
      sender_id:    Number(user.user_id),
      receiver_id:  partnerId,
      message_text: text
    })
    // Remove optimistic flag after success
    optimistic._optimistic = false
  } catch (e) {
    // Revert on failure
    messages.value = messages.value.filter(m => m !== optimistic)
    newMsg.value   = text
    alert('Failed to send. Please try again.')
  } finally {
    sending.value = false
  }
}

// ── Poll for new messages every 3 seconds ────────────────────────────────────
const pollMessages = async () => {
  if (!activeThread.value || isSelfChat.value) return
  const partnerId = Number(activeThread.value.seller_id)
  try {
    const r     = await api.getMessages(Number(user.user_id), partnerId)
    const fresh = Array.isArray(r.data) ? r.data : []
    // Only update if there are genuinely new messages from server
    const serverCount = fresh.length
    const localCount  = messages.value.filter(m => !m._optimistic).length
    if (serverCount > localCount) {
      // Keep optimistic messages, replace rest
      const optimistics = messages.value.filter(m => m._optimistic)
      messages.value = [...fresh, ...optimistics]
      messages.value.sort((a, b) => new Date(a.sent_at) - new Date(b.sent_at))
      await scrollBottom()
      api.markMessagesRead({ reader_id: Number(user.user_id), sender_id: partnerId }).catch(() => {})
    }
  } catch {}
}

// ── Scroll to bottom of chat ──────────────────────────────────────────────────
const scrollBottom = async () => {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
}

// ── Date/time helpers ─────────────────────────────────────────────────────────
const showDateSep = (i) => {
  if (i === 0) return true
  const a = new Date(messages.value[i - 1].sent_at).toDateString()
  const b = new Date(messages.value[i].sent_at).toDateString()
  return a !== b
}
const dateLabel = (d) => {
  if (!d) return ''
  const date  = new Date(d)
  const today = new Date()
  const yest  = new Date(today)
  yest.setDate(today.getDate() - 1)
  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yest.toDateString())  return 'Yesterday'
  return date.toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' })
}
const relTime = (d) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000)    return 'now'
  if (diff < 3600000)  return `${Math.floor(diff / 60000)}m`
  if (diff < 86400000) return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
}
const msgTime = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  if (!user) return

  await fetchThreads()

  // Auto-open thread from query params (e.g. from "Chat Seller" button)
  const sid = route.query.seller_id
  if (sid) {
    const sidN = Number(sid)
    let t = threads.value.find(x => Number(x.seller_id) === sidN)
    if (!t) {
      // Thread not loaded yet — create a temporary one
      t = {
        seller_id:    sidN,
        seller_name:  route.query.seller_name || 'Seller',
        last_message: '',
        last_time:    '',
        unread:       false,
        _temp:        true
      }
      threads.value.unshift(t)
    }
    await openThread(t)
  }

  // Poll every 3 seconds
  pollTimer = setInterval(async () => {
    await pollMessages()
    await fetchThreads(true)
  }, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; transform-origin: center; }

.msg-page { background: #f4f7fb; min-height: calc(100vh - 62px); padding: 20px; }
.msg-layout {
  max-width: 1020px; margin: 0 auto;
  display: grid; grid-template-columns: 300px 1fr;
  height: calc(100vh - 102px); min-height: 500px;
  background: #fff; border-radius: 16px; border: 1px solid #e2eaf4;
  overflow: hidden; box-shadow: 0 4px 24px rgba(0,51,102,0.08);
}

/* Sidebar */
.msg-sidebar { border-right: 1px solid #e8edf4; display: flex; flex-direction: column; background: #fafcff; overflow: hidden; }
.msg-sidebar__head { padding: 18px 16px 12px; border-bottom: 1px solid #eef2f8; display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.msg-sidebar__title { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0; }
.msg-unread-badge { background: #003366; color: #FFD700; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px; }
.msg-sidebar__search { padding: 10px 12px; border-bottom: 1px solid #eef2f8; display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.msg-search-input { flex: 1; border: none; outline: none; font-size: 0.875rem; color: #333; background: transparent; font-family: inherit; }
.msg-search-input::placeholder { color: #bbb; }
.msg-thread-list { flex: 1; overflow-y: auto; }
.msg-empty-threads { padding: 24px 16px; text-align: center; color: #bbb; font-size: 0.85rem; margin: 0; }
.thread-skel { height: 66px; margin: 6px 10px; border-radius: 10px; background: linear-gradient(110deg,#f0f0f0 8%,#f8f8f8 18%,#f0f0f0 33%); background-size: 200% 100%; animation: sk 1.5s linear infinite; }
@keyframes sk { to { background-position-x: -200%; } }
.thread-item { display: flex; align-items: center; gap: 10px; padding: 12px 14px; cursor: pointer; border-bottom: 1px solid #f0f4f8; transition: background 0.12s; position: relative; }
.thread-item:hover { background: #f0f5ff; }
.thread-item--active { background: #e8f0fe; border-right: 3px solid #003366; }
.thread-item--unread { background: #f5f8ff; }
.thread-av { width: 40px; height: 40px; border-radius: 50%; background: #003366; color: #FFD700; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; flex-shrink: 0; }
.thread-av--gold { background: #FFD700; color: #003366; }
.thread-body { flex: 1; min-width: 0; }
.thread-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; }
.thread-name { font-size: 0.875rem; font-weight: 700; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px; }
.thread-item--unread .thread-name { color: #003366; }
.thread-time { font-size: 0.68rem; color: #aaa; white-space: nowrap; }
.thread-preview { font-size: 0.78rem; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0; }
.thread-item--unread .thread-preview { color: #555; font-weight: 500; }
.thread-pip { width: 8px; height: 8px; background: #003366; border-radius: 50%; flex-shrink: 0; }

/* Chat */
.msg-chat { display: flex; flex-direction: column; background: #fff; overflow: hidden; }
.msg-chat__head { display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-bottom: 1px solid #eef2f8; flex-shrink: 0; }
.msg-back { display: none; background: none; border: none; color: #003366; cursor: pointer; padding: 4px 8px; border-radius: 7px; }
.msg-back:hover { background: #f0f5ff; }
.msg-chat__name { font-size: 0.9rem; font-weight: 800; color: #003366; margin: 0 0 2px; }
.msg-chat__status { font-size: 0.72rem; color: #16a34a; margin: 0; display: flex; align-items: center; gap: 5px; }
.msg-chat__dot { display: block; width: 6px; height: 6px; border-radius: 50%; background: #16a34a; }
.msg-chat__hint { font-size: 0.72rem; color: #bbb; }
.self-warn { display: flex; align-items: center; gap: 8px; background: #fffbeb; color: #92400e; font-size: 0.82rem; font-weight: 600; padding: 10px 16px; border-bottom: 1px solid #fde68a; flex-shrink: 0; }
.msg-list { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 2px; background: #f8fafc; }
.bubble-skel { height: 40px; border-radius: 18px; width: 55%; background: linear-gradient(110deg,#ece8f5 8%,#f5f3fa 18%,#ece8f5 33%); background-size: 200% 100%; animation: sk 1.5s linear infinite; margin-bottom: 10px; }
.bubble-skel--r { align-self: flex-end; }
.bubble-skel--l { align-self: flex-start; }
.msg-empty-chat { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; color: #ccc; font-size: 0.875rem; margin: auto; padding: 2rem; }
.msg-empty-chat p { margin: 0; }
.date-sep { display: flex; align-items: center; justify-content: center; margin: 12px 0 8px; }
.date-sep span { font-size: 0.72rem; font-weight: 600; color: #aaa; background: #eef2f8; padding: 3px 12px; border-radius: 20px; }
.msg-row { display: flex; align-items: flex-end; gap: 6px; margin-bottom: 4px; }
.msg-row--mine   { justify-content: flex-end; }
.msg-row--theirs { justify-content: flex-start; }
.msg-mini-av { width: 24px; height: 24px; border-radius: 50%; background: #003366; color: #FFD700; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 800; flex-shrink: 0; }
.bubble { max-width: 65%; padding: 10px 14px 8px; border-radius: 18px; font-size: 0.875rem; line-height: 1.5; word-break: break-word; }
.bubble--mine   { background: #003366; color: #fff; border-bottom-right-radius: 4px; }
.bubble--theirs { background: #fff; color: #1a1a2e; border: 1px solid #e4eaf2; border-bottom-left-radius: 4px; }
.bubble__time { display: block; font-size: 0.62rem; opacity: 0.55; text-align: right; margin-top: 4px; }

/* Compose */
.msg-compose { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-top: 1px solid #eef2f8; background: #fff; flex-shrink: 0; }
.msg-input { flex: 1; padding: 10px 16px; border: 1.5px solid #e0e8f4; border-radius: 24px; font-size: 0.9rem; outline: none; font-family: inherit; transition: border-color 0.15s; color: #1a1a2e; }
.msg-input:focus { border-color: #003366; }
.msg-input:disabled { background: #f8fafc; color: #aaa; }
.send-btn { width: 42px; height: 42px; border-radius: 50%; background: #003366; color: #FFD700; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.15s; flex-shrink: 0; }
.send-btn:hover:not(:disabled) { background: #002244; transform: scale(1.06); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Empty panel */
.msg-empty-panel { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: #fafcff; }
.msg-empty-panel__icon { width: 72px; height: 72px; background: #e8f0fe; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.msg-empty-panel__title { font-size: 1rem; font-weight: 700; color: #003366; margin: 0; }
.msg-empty-panel__sub   { font-size: 0.875rem; color: #aaa; margin: 0; }

@media (max-width: 680px) {
  .msg-page   { padding: 0; }
  .msg-layout { grid-template-columns: 1fr; border-radius: 0; border: none; height: calc(100vh - 62px); }
  .msg-sidebar--hidden { display: none; }
  .msg-back   { display: flex; }
  .msg-empty-panel { display: none; }
}
</style>