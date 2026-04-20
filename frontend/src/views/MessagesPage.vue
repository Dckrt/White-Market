<template>
  <div class="wm-msg-page">
    <div class="wm-msg-layout" :class="{ 'wm-msg-layout--chat-open': activeThread }">

      <!-- Sidebar -->
      <aside class="wm-msg-sidebar" :class="{ 'wm-msg-sidebar--hidden': activeThread }">
        <div class="wm-msg-sidebar__head">
          <h1 class="wm-msg-sidebar__title">Messages</h1>
          <div v-if="totalUnread > 0" class="wm-msg-sidebar__count">{{ totalUnread }} unread</div>
        </div>
        <div class="wm-msg-sidebar__search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input v-model="search" placeholder="Search conversations…" class="wm-msg-search-input" />
        </div>

        <div v-if="loadingThreads" class="wm-msg-thread-list">
          <div class="wm-thread-skel" v-for="n in 5" :key="n"></div>
        </div>

        <div class="wm-msg-thread-list" v-else>
          <p v-if="!filteredThreads.length" class="wm-msg-empty-threads">
            {{ search ? 'No results.' : 'No conversations yet.' }}
          </p>
          <div
            v-for="t in filteredThreads"
            :key="t.seller_id"
            class="wm-thread-item"
            :class="{ 'wm-thread-item--active': activeThread?.seller_id === t.seller_id, 'wm-thread-item--unread': t.unread }"
            @click="openThread(t)"
          >
            <div class="wm-thread-avatar">{{ initials(t.seller_name) }}</div>
            <div class="wm-thread-body">
              <div class="wm-thread-row">
                <span class="wm-thread-name">{{ t.seller_name }}</span>
                <span class="wm-thread-time">{{ relTime(t.last_time) }}</span>
              </div>
              <p class="wm-thread-preview">{{ t.last_message || 'Start a conversation' }}</p>
            </div>
            <div v-if="t.unread" class="wm-thread-pip"></div>
          </div>
        </div>
      </aside>

      <!-- Chat panel -->
      <main v-if="activeThread" class="wm-msg-chat">
        <div class="wm-msg-chat__head">
          <button class="wm-msg-back" @click="activeThread = null">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div class="wm-thread-avatar wm-thread-avatar--gold">{{ initials(activeThread.seller_name) }}</div>
          <div>
            <p class="wm-msg-chat__partner-name">{{ activeThread.seller_name }}</p>
            <p class="wm-msg-chat__status">
              <span class="wm-msg-chat__status-dot"></span>ADNU Verified Student
            </p>
          </div>
        </div>

        <div v-if="isSelfChat" class="wm-self-warn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          This is your own account — you cannot message yourself.
        </div>

        <div class="wm-msg-list" ref="msgListRef">
          <div v-if="loadingMsgs" style="padding:16px">
            <div class="wm-bubble-skel wm-bubble-skel--right"></div>
            <div class="wm-bubble-skel wm-bubble-skel--left"></div>
            <div class="wm-bubble-skel wm-bubble-skel--right"></div>
          </div>
          <template v-else>
            <div v-if="!messages.length" class="wm-msg-empty-chat">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <p>No messages yet — say hello!</p>
            </div>

            <!-- date group + messages -->
            <template v-for="(msg, i) in messages" :key="i">
              <div v-if="showDateSep(i)" class="wm-date-sep">
                <span>{{ dateLabel(msg.sent_at) }}</span>
              </div>
              <div class="wm-msg-row" :class="isMine(msg) ? 'wm-msg-row--mine' : 'wm-msg-row--theirs'">
                <div v-if="!isMine(msg)" class="wm-msg-mini-av">{{ initials(activeThread.seller_name) }}</div>
                <div class="wm-bubble" :class="isMine(msg) ? 'wm-bubble--mine' : 'wm-bubble--theirs'">
                  {{ msg.message_text }}
                  <span class="wm-bubble__time">{{ msgTime(msg.sent_at) }}</span>
                </div>
              </div>
            </template>
          </template>
        </div>

        <div class="wm-msg-compose">
          <input
            v-model="newMsg"
            class="wm-msg-input"
            placeholder="Type a message…"
            :disabled="isSelfChat || sending"
            @keyup.enter="send"
          />
          <button class="wm-send-btn" :disabled="!newMsg.trim() || sending || isSelfChat" @click="send">
            <svg v-if="!sending" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" style="animation:spin .8s linear infinite;transform-origin:center"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur=".8s" repeatCount="indefinite"/></path></svg>
          </button>
        </div>
      </main>

      <!-- Empty state -->
      <div v-else class="wm-msg-empty">
        <div class="wm-msg-empty__icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.4"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <p class="wm-msg-empty__title">Your conversations</p>
        <p class="wm-msg-empty__sub">Select a thread to start messaging</p>
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
const newMsg = ref('')
const search = ref('')
const sending = ref(false)
const loadingThreads = ref(true)
const loadingMsgs = ref(false)
const msgListRef = ref(null)
let poll = null

const totalUnread = computed(() => threads.value.filter(t => t.unread).length)
const isSelfChat = computed(() => activeThread.value && Number(activeThread.value.seller_id) === Number(user?.user_id))
const filteredThreads = computed(() => {
  if (!search.value) return threads.value
  return threads.value.filter(t => t.seller_name?.toLowerCase().includes(search.value.toLowerCase()))
})
const isMine = msg => Number(msg.sender_id) === Number(user?.user_id)
const initials = name => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const fetchThreads = async (silent = false) => {
  if (!user) return
  if (!silent) loadingThreads.value = true
  try {
    const r = await api.getThreads(user.user_id)
    const fresh = r.data || []
    if (activeThread.value) {
      const at = fresh.find(t => Number(t.seller_id) === Number(activeThread.value.seller_id))
      if (at) at.unread = false
    }
    threads.value = fresh
  } catch {}
  finally { loadingThreads.value = false }
}

const openThread = async (t) => {
  activeThread.value = { ...t, seller_id: Number(t.seller_id) }
  const local = threads.value.find(x => Number(x.seller_id) === Number(t.seller_id))
  if (local) local.unread = false
  loadingMsgs.value = true
  try {
    const r = await api.getMessages(Number(user.user_id), Number(t.seller_id))
    messages.value = r.data || []
    await scrollBottom()
    await api.markMessagesRead({ reader_id: Number(user.user_id), sender_id: Number(t.seller_id) }).catch(() => {})
  } catch { messages.value = [] }
  finally { loadingMsgs.value = false }
}

const send = async () => {
  if (!newMsg.value.trim() || sending.value || isSelfChat.value) return
  const text = newMsg.value.trim()
  newMsg.value = ''
  sending.value = true
  try {
    await api.sendMessage({ sender_id: Number(user.user_id), receiver_id: Number(activeThread.value.seller_id), message_text: text })
    messages.value.push({ sender_id: Number(user.user_id), receiver_id: Number(activeThread.value.seller_id), message_text: text, sent_at: new Date().toISOString() })
    const t = threads.value.find(x => Number(x.seller_id) === Number(activeThread.value.seller_id))
    if (t) { t.last_message = text; t.last_time = new Date().toISOString() }
    await scrollBottom()
  } catch (e) {
    newMsg.value = text
    alert((e.response?.data?.message || 'Failed to send') + ' ❌')
  } finally { sending.value = false }
}

const pollMsgs = async () => {
  if (!activeThread.value || isSelfChat.value) return
  try {
    const r = await api.getMessages(Number(user.user_id), Number(activeThread.value.seller_id))
    const fresh = r.data || []
    if (fresh.length > messages.value.length) { messages.value = fresh; await scrollBottom() }
  } catch {}
}

const scrollBottom = async () => {
  await nextTick()
  if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight
}

const showDateSep = (i) => {
  if (i === 0) return true
  const a = new Date(messages.value[i-1].sent_at).toDateString()
  const b = new Date(messages.value[i].sent_at).toDateString()
  return a !== b
}

const dateLabel = (d) => {
  if (!d) return ''
  const date = new Date(d)
  const today = new Date()
  const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1)
  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return date.toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' })
}

const relTime = (d) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000) return 'now'
  if (diff < 3600000) return `${Math.floor(diff/60000)}m`
  if (diff < 86400000) return new Date(d).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})
  return new Date(d).toLocaleDateString('en-PH', {month:'short', day:'numeric'})
}

const msgTime = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})
}

onMounted(async () => {
  await fetchThreads()
  const sid = route.query.seller_id
  if (sid) {
    const sidN = Number(sid)
    let t = threads.value.find(x => Number(x.seller_id) === sidN)
    if (!t) { t = { seller_id: sidN, seller_name: route.query.seller_name || 'Seller', last_message: '', last_time: '', unread: false }; threads.value.unshift(t) }
    openThread(t)
  }
  poll = setInterval(() => { pollMsgs(); if (!activeThread.value) fetchThreads(true) }, 4000)
})

onUnmounted(() => { if (poll) clearInterval(poll) })
</script>

<style scoped>
.wm-msg-page { background:#f4f7fb; min-height:calc(100vh - 60px); padding:20px; }

.wm-msg-layout {
  max-width:1020px;
  margin:0 auto;
  display:grid;
  grid-template-columns:300px 1fr;
  height:calc(100vh - 100px);
  min-height:500px;
  background:#fff;
  border-radius:16px;
  border:1px solid #e2eaf4;
  overflow:hidden;
  box-shadow:0 4px 24px rgba(0,51,102,0.08);
}

/* Sidebar */
.wm-msg-sidebar { border-right:1px solid #e8edf4; display:flex; flex-direction:column; background:#fafcff; }

.wm-msg-sidebar__head { padding:18px 16px 12px; border-bottom:1px solid #eef2f8; display:flex; align-items:center; justify-content:space-between; }
.wm-msg-sidebar__title { font-size:1.1rem; font-weight:800; color:#003366; margin:0; }
.wm-msg-sidebar__count { background:#003366; color:#FFD700; font-size:11px; font-weight:800; padding:2px 8px; border-radius:12px; }

.wm-msg-sidebar__search { padding:10px 12px; border-bottom:1px solid #eef2f8; display:flex; align-items:center; gap:8px; }
.wm-msg-sidebar__search svg { color:#aaa; flex-shrink:0; }
.wm-msg-search-input { flex:1; border:none; outline:none; font-size:0.875rem; color:#333; background:transparent; font-family:inherit; }
.wm-msg-search-input::placeholder { color:#bbb; }

.wm-msg-thread-list { flex:1; overflow-y:auto; }
.wm-msg-empty-threads { padding:24px 16px; text-align:center; color:#bbb; font-size:0.85rem; margin:0; }

.wm-thread-skel { height:66px; margin:6px 10px; border-radius:10px; background:linear-gradient(110deg,#f0f0f0 8%,#f8f8f8 18%,#f0f0f0 33%); background-size:200% 100%; animation:sk 1.5s linear infinite; }
@keyframes sk { to { background-position-x:-200%; } }

.wm-thread-item { display:flex; align-items:center; gap:10px; padding:12px 14px; cursor:pointer; border-bottom:1px solid #f0f4f8; transition:background 0.12s; position:relative; }
.wm-thread-item:hover { background:#f0f5ff; }
.wm-thread-item--active { background:#e8f0fe; border-right:3px solid #003366; }
.wm-thread-item--unread { background:#f5f8ff; }

.wm-thread-avatar { width:40px; height:40px; border-radius:50%; background:#003366; color:#FFD700; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:13px; flex-shrink:0; }
.wm-thread-avatar--gold { background:#FFD700; color:#003366; }

.wm-thread-body { flex:1; min-width:0; }
.wm-thread-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; }
.wm-thread-name { font-size:0.875rem; font-weight:700; color:#1a1a2e; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:120px; }
.wm-thread-item--unread .wm-thread-name { color:#003366; }
.wm-thread-time { font-size:0.68rem; color:#aaa; white-space:nowrap; }
.wm-thread-preview { font-size:0.78rem; color:#888; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin:0; }
.wm-thread-item--unread .wm-thread-preview { color:#555; font-weight:500; }

.wm-thread-pip { width:8px; height:8px; background:#003366; border-radius:50%; flex-shrink:0; }

/* Chat */
.wm-msg-chat { display:flex; flex-direction:column; background:#fff; }

.wm-msg-chat__head { display:flex; align-items:center; gap:10px; padding:14px 16px; border-bottom:1px solid #eef2f8; background:#fff; }

.wm-msg-back { display:none; background:none; border:none; color:#003366; cursor:pointer; padding:4px; border-radius:7px; }
.wm-msg-back:hover { background:#f0f5ff; }

.wm-msg-chat__partner-name { font-size:0.9rem; font-weight:800; color:#003366; margin:0 0 2px; }
.wm-msg-chat__status { font-size:0.72rem; color:#16a34a; margin:0; display:flex; align-items:center; gap:5px; }
.wm-msg-chat__status-dot { display:block; width:6px; height:6px; border-radius:50%; background:#16a34a; }

.wm-self-warn { display:flex; align-items:center; gap:8px; background:#fffbeb; color:#92400e; font-size:0.82rem; font-weight:600; padding:10px 16px; border-bottom:1px solid #fde68a; }
.wm-self-warn svg { flex-shrink:0; }

.wm-msg-list { flex:1; overflow-y:auto; padding:16px; display:flex; flex-direction:column; gap:2px; background:#f8fafc; }

.wm-bubble-skel { height:40px; border-radius:18px; width:55%; background:linear-gradient(110deg,#ece8f5 8%,#f5f3fa 18%,#ece8f5 33%); background-size:200% 100%; animation:sk 1.5s linear infinite; margin-bottom:10px; }
.wm-bubble-skel--right { align-self:flex-end; }
.wm-bubble-skel--left { align-self:flex-start; }

.wm-msg-empty-chat { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; color:#ccc; font-size:0.875rem; margin:auto; padding:2rem; }
.wm-msg-empty-chat p { margin:0; }

.wm-date-sep { display:flex; align-items:center; justify-content:center; margin:12px 0 8px; }
.wm-date-sep span { font-size:0.72rem; font-weight:600; color:#aaa; background:#eef2f8; padding:3px 12px; border-radius:20px; }

.wm-msg-row { display:flex; align-items:flex-end; gap:6px; margin-bottom:4px; }
.wm-msg-row--mine { justify-content:flex-end; }
.wm-msg-row--theirs { justify-content:flex-start; }

.wm-msg-mini-av { width:24px; height:24px; border-radius:50%; background:#003366; color:#FFD700; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:800; flex-shrink:0; }

.wm-bubble { max-width:65%; padding:10px 14px 8px; border-radius:18px; font-size:0.875rem; line-height:1.5; word-break:break-word; position:relative; }
.wm-bubble--mine { background:#003366; color:#fff; border-bottom-right-radius:4px; }
.wm-bubble--theirs { background:#fff; color:#1a1a2e; border:1px solid #e4eaf2; border-bottom-left-radius:4px; }
.wm-bubble__time { display:block; font-size:0.62rem; opacity:0.55; text-align:right; margin-top:4px; }
.wm-bubble--mine .wm-bubble__time { opacity:0.65; }

.wm-msg-compose { display:flex; align-items:center; gap:10px; padding:12px 16px; border-top:1px solid #eef2f8; background:#fff; }

.wm-msg-input { flex:1; padding:10px 16px; border:1.5px solid #e0e8f4; border-radius:24px; font-size:0.9rem; outline:none; font-family:inherit; transition:border-color 0.15s; color:#1a1a2e; }
.wm-msg-input:focus { border-color:#003366; }
.wm-msg-input:disabled { background:#f8fafc; color:#aaa; }

.wm-send-btn { width:42px; height:42px; border-radius:50%; background:#003366; color:#FFD700; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:0.15s; flex-shrink:0; }
.wm-send-btn:hover:not(:disabled) { background:#002244; transform:scale(1.06); }
.wm-send-btn:disabled { opacity:0.4; cursor:not-allowed; transform:none; }

/* Empty panel */
.wm-msg-empty { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; background:#fafcff; }
.wm-msg-empty__icon { width:72px; height:72px; background:#e8f0fe; border-radius:50%; display:flex; align-items:center; justify-content:center; }
.wm-msg-empty__title { font-size:1rem; font-weight:700; color:#003366; margin:0; }
.wm-msg-empty__sub { font-size:0.875rem; color:#aaa; margin:0; }

@media(max-width:680px) {
  .wm-msg-page { padding:0; }
  .wm-msg-layout { grid-template-columns:1fr; border-radius:0; border:none; height:calc(100vh - 60px); }
  .wm-msg-sidebar--hidden { display:none; }
  .wm-msg-back { display:flex; }
  .wm-msg-empty { display:none; }
}
</style>