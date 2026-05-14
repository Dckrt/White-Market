<template>
  <div class="notif-page">
    <div class="notif-inner">

      <!-- Header -->
      <div class="notif-header">
        <div class="notif-header__left">
          <div class="notif-header__icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD700" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 01-3.46 0"/>
            </svg>
          </div>
          <div>
            <h1 class="notif-header__title">Notifications</h1>
            <p class="notif-header__sub">{{ unreadCount }} unread</p>
          </div>
        </div>
        <button
          v-if="unreadCount > 0"
          class="notif-mark-btn"
          @click="markAllRead"
          :disabled="markingAll"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          {{ markingAll ? 'Marking…' : 'Mark all read' }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="notif-list">
        <div v-for="n in 6" :key="n" class="notif-skel">
          <div class="skel skel--circle"></div>
          <div style="flex:1;display:flex;flex-direction:column;gap:6px">
            <div class="skel skel--line"></div>
            <div class="skel skel--line" style="width:50%"></div>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="!notifications.length" class="notif-empty">
        <div class="notif-empty__icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#c8d8ea" stroke-width="1.4">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 01-3.46 0"/>
          </svg>
        </div>
        <p class="notif-empty__title">No notifications yet</p>
        <p class="notif-empty__sub">You'll be notified when someone messages you, adds your product to cart, or places an order.</p>
      </div>

      <!-- List -->
      <div v-else class="notif-list">
        <TransitionGroup name="notif-item">
          <div
            v-for="n in notifications"
            :key="n.id"
            class="notif-card"
            :class="{ 'notif-card--unread': !n.is_read }"
            @click="markOne(n)"
          >
            <div class="notif-card__dot-wrap">
              <div class="notif-card__dot" :class="{ 'notif-card__dot--on': !n.is_read }"></div>
            </div>
            <div class="notif-card__icon" :style="{ background: iconBg(n.message) }">
              <svg v-if="isMessage(n.message)" width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="iconColor(n.message)" stroke-width="1.8" stroke-linecap="round">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
              </svg>
              <svg v-else-if="isOrder(n.message)" width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="iconColor(n.message)" stroke-width="1.8" stroke-linecap="round">
                <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="iconColor(n.message)" stroke-width="1.8" stroke-linecap="round">
                <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/>
              </svg>
            </div>
            <div class="notif-card__body">
              <p class="notif-card__msg">{{ n.message }}</p>
              <span class="notif-card__time">{{ relTime(n.created_at) }}</span>
            </div>
          </div>
        </TransitionGroup>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const user          = JSON.parse(localStorage.getItem('user') || 'null')
const notifications = ref([])
const loading       = ref(true)
const markingAll    = ref(false)

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

// ── Icon helpers ───────────────────────────────────────────────────────────
const isMessage = (msg) => msg && msg.toLowerCase().includes('message')
const isOrder   = (msg) => msg && msg.toLowerCase().includes('order')
const isCart    = (msg) => msg && (msg.toLowerCase().includes('cart') || msg.toLowerCase().includes('add'))

const iconBg = (msg) => {
  if (isMessage(msg)) return '#e8f0fe'
  if (isOrder(msg))   return '#fce8ff'
  return '#e8f8f0'
}
const iconColor = (msg) => {
  if (isMessage(msg)) return '#003366'
  if (isOrder(msg))   return '#7c3aed'
  return '#15803d'
}

// ── Fetch ──────────────────────────────────────────────────────────────────
const fetchNotifs = async () => {
  if (!user) return
  loading.value = true
  try {
    const r = await api.getNotifications(user.user_id)
    notifications.value = Array.isArray(r.data) ? r.data : []
  } catch {
    notifications.value = []
  } finally {
    loading.value = false
  }
}

// ── Mark all read ──────────────────────────────────────────────────────────
const markAllRead = async () => {
  markingAll.value = true
  try {
    await api.markNotificationsRead(user.user_id)
    notifications.value = notifications.value.map(n => ({ ...n, is_read: 1 }))
  } catch {
    alert('Failed to mark notifications as read')
  } finally {
    markingAll.value = false
  }
}

// ── Mark one on click ──────────────────────────────────────────────────────
const markOne = async (n) => {
  if (n.is_read) return
  try {
    // Mark all (simplest) — server marks all for this user
    await api.markNotificationsRead(user.user_id)
    notifications.value = notifications.value.map(x => ({ ...x, is_read: 1 }))
  } catch {}
}

// ── Relative time ──────────────────────────────────────────────────────────
const relTime = (d) => {
  if (!d) return ''
  try {
    const diff = Date.now() - new Date(d)
    if (diff < 60000)    return 'just now'
    if (diff < 3600000)  return `${Math.floor(diff / 60000)} min ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hr ago`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)} day${Math.floor(diff/86400000)>1?'s':''} ago`
    return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch { return '' }
}

onMounted(fetchNotifs)
</script>

<style scoped>
@keyframes sk { to { background-position-x: -200%; } }

.notif-page  { background: #f4f7fb; min-height: calc(100vh - 62px); padding: 2rem 1.5rem; }
.notif-inner { max-width: 680px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem; }

/* Header */
.notif-header {
  display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 12px;
}
.notif-header__left { display: flex; align-items: center; gap: 14px; }
.notif-header__icon {
  width: 48px; height: 48px; background: #003366;
  border-radius: 13px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.notif-header__title { font-size: 1.5rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.notif-header__sub   { font-size: 0.82rem; color: #888; margin: 0; }

.notif-mark-btn {
  display: flex; align-items: center; gap: 7px;
  background: #003366; color: #FFD700;
  border: none; padding: 9px 18px; border-radius: 8px;
  font-weight: 700; font-size: 0.82rem; cursor: pointer;
  transition: 0.15s; font-family: inherit;
}
.notif-mark-btn:hover:not(:disabled) { background: #002244; }
.notif-mark-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* Skeleton */
.notif-skel {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border-radius: 12px; padding: 16px;
  border: 1px solid #e8edf4;
}
.skel {
  background: linear-gradient(110deg,#f0f0f0 8%,#f8f8f8 18%,#f0f0f0 33%);
  background-size: 200% 100%; animation: sk 1.5s linear infinite; border-radius: 6px;
}
.skel--circle { width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; }
.skel--line   { height: 14px; }

/* Empty */
.notif-empty {
  text-align: center; padding: 5rem 2rem;
  background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.notif-empty__icon {
  width: 72px; height: 72px; background: #f0f4f8;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
}
.notif-empty__title { font-size: 1.1rem; font-weight: 700; color: #003366; margin: 0; }
.notif-empty__sub   { font-size: 0.875rem; color: #aaa; margin: 0; max-width: 340px; line-height: 1.5; }

/* List */
.notif-list { display: flex; flex-direction: column; gap: 10px; }

.notif-card {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border-radius: 14px; padding: 14px 16px;
  border: 1px solid #e8edf4; cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.notif-card:hover { box-shadow: 0 4px 16px rgba(0,51,102,0.08); border-color: #c8d8ea; }
.notif-card--unread { background: #f5f8ff; border-color: #c8d8ea; }

.notif-card__dot-wrap { width: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.notif-card__dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #d1d5db; flex-shrink: 0;
}
.notif-card__dot--on { background: #003366; }

.notif-card__icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

.notif-card__body { flex: 1; min-width: 0; }
.notif-card__msg  {
  font-size: 0.875rem; color: #1a1a2e; margin: 0 0 4px;
  line-height: 1.4;
}
.notif-card--unread .notif-card__msg { font-weight: 600; color: #003366; }
.notif-card__time { font-size: 0.75rem; color: #aaa; }

/* Transition */
.notif-item-enter-active, .notif-item-leave-active { transition: all 0.25s ease; }
.notif-item-enter-from { opacity: 0; transform: translateY(-8px); }
.notif-item-leave-to   { opacity: 0; transform: translateX(20px); }

@media (max-width: 600px) {
  .notif-page  { padding: 1rem; }
  .notif-inner { gap: 1rem; }
}
</style>