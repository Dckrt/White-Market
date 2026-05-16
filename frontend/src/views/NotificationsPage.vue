<template>
  <div class="notif-page">
    <div class="notif-container">

      <!-- Header -->
      <div class="notif-header">
        <div class="notif-header__left">
          <div class="notif-header__icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>
            </svg>
          </div>
          <div>
            <h1 class="notif-header__title">Notifications</h1>
            <p class="notif-header__sub">
              <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }} unread</span>
              <span v-else class="all-read">All caught up ✓</span>
            </p>
          </div>
        </div>
        <button v-if="hasUnread" class="mark-all-btn" @click="markAllRead">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
          Mark all read
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="notif-loading">
        <div class="notif-spinner"></div>
        <p>Loading notifications…</p>
      </div>

      <!-- Empty -->
      <div v-else-if="notifications.length === 0" class="notif-empty">
        <div class="notif-empty__icon">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#c0cdd8" stroke-width="1.4">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>
          </svg>
        </div>
        <h3>No notifications yet</h3>
        <p>You'll be notified about orders, messages, and more.</p>
      </div>

      <!-- List -->
      <div v-else class="notif-list">
        <TransitionGroup name="notif-item">
          <div
            v-for="notif in notifications"
            :key="notif.id"
            :class="['notif-card', !notif.is_read && 'notif-card--unread']"
          >
            <div class="notif-dot-wrap">
              <span :class="['notif-dot', !notif.is_read && 'notif-dot--active']"></span>
            </div>

            <div class="notif-icon-wrap">
              <span v-if="notif.message.includes('order') || notif.message.includes('Order')" class="notif-icon notif-icon--order">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/></svg>
              </span>
              <span v-else-if="notif.message.includes('message') || notif.message.includes('💬')" class="notif-icon notif-icon--msg">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              </span>
              <span v-else-if="notif.message.includes('cart') || notif.message.includes('Cart')" class="notif-icon notif-icon--cart">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
              </span>
              <span v-else class="notif-icon notif-icon--default">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
              </span>
            </div>

            <div class="notif-content">
              <p class="notif-message">{{ notif.message }}</p>
              <span class="notif-time">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {{ formatDate(notif.created_at) }}
              </span>
            </div>

            <span v-if="!notif.is_read" class="new-chip">New</span>
          </div>
        </TransitionGroup>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'

const notifications = ref([])
const loading       = ref(true)
const user          = JSON.parse(localStorage.getItem('user'))

let refreshInterval = null

// ── Computed ────────────────────────────────────────────────────────────────
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const hasUnread   = computed(() => unreadCount.value > 0)

// ── Fetch ────────────────────────────────────────────────────────────────────
const fetchNotifications = async (showLoader = false) => {
  if (showLoader) loading.value = true
  try {
    const res = await api.getNotifications(user.user_id)
    notifications.value = res.data || []
  } catch (err) {
    console.error('Notifications error:', err)
    notifications.value = []
  } finally {
    loading.value = false
  }
}

// ── Mark all read ─────────────────────────────────────────────────────────────
// Updates locally immediately (no flicker), then calls the API,
// and also clears whatever global unread count your navbar is tracking.
const markAllRead = async () => {
  // 1. Optimistically update local list so the UI clears right away
  notifications.value = notifications.value.map(n => ({ ...n, is_read: 1 }))

  // 2. Clear the global navbar badge.
  //    This handles the three most common patterns — use whichever your app uses:

  // Option A — Pinia store (e.g. useNotifStore)
  // import { useNotifStore } from '@/stores/notif'
  // useNotifStore().unreadCount = 0

  // Option B — Vuex store
  // import { useStore } from 'vuex'
  // useStore().commit('SET_NOTIF_COUNT', 0)

  // Option C — localStorage + custom event (works without any store)
  localStorage.setItem('notif_unread', '0')
  window.dispatchEvent(new CustomEvent('notif-cleared'))

  // 3. Persist to backend
  try {
    await api.markNotificationsRead(user.user_id)
  } catch (err) {
    console.error('Mark read error:', err)
  }
}

// ── Format date ───────────────────────────────────────────────────────────────
const formatDate = (date) => {
  if (!date) return ''
  const d    = new Date(date)
  const diff = Math.floor((Date.now() - d) / 1000)
  if (diff < 60)     return 'Just now'
  if (diff < 3600)   return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400)  return `${Math.floor(diff / 3600)}h ago`
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`
  return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  if (!user) return
  await fetchNotifications(true)

  // Auto-mark all read as soon as the page is opened — this is the fix
  // for the badge not clearing when the user clicks Notifications.
  if (hasUnread.value) {
    await markAllRead()
  }

  refreshInterval = setInterval(() => fetchNotifications(), 30000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
@keyframes spin  { to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.notif-page { background: #f0f4f8; min-height: 100vh; padding: 2rem 1.5rem; }
.notif-container { max-width: 700px; margin: 0 auto; }

/* Header */
.notif-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 12px; }
.notif-header__left { display: flex; align-items: center; gap: 14px; }
.notif-header__icon { width: 50px; height: 50px; background: #fff; border: 1.5px solid #e0e8f4; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.notif-header__title { font-size: 1.4rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.notif-header__sub { font-size: 0.82rem; color: #888; margin: 0; }
.unread-badge { background: #003366; color: #FFD700; font-size: 0.75rem; font-weight: 800; padding: 2px 10px; border-radius: 20px; }
.all-read { color: #15803d; font-weight: 600; }

.mark-all-btn { display: flex; align-items: center; gap: 6px; background: #fff; border: 1.5px solid #d0dbe8; color: #003366; font-size: 0.82rem; font-weight: 700; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-family: inherit; }
.mark-all-btn:hover { background: #003366; color: #FFD700; border-color: #003366; }

/* Loading */
.notif-loading { text-align: center; padding: 4rem; color: #888; }
.notif-spinner { width: 34px; height: 34px; border: 3px solid #e0e0e0; border-top-color: #003366; border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto 1rem; }

/* Empty */
.notif-empty { text-align: center; padding: 4rem 2rem; background: #fff; border-radius: 16px; border: 1px solid #e8edf4; }
.notif-empty__icon { width: 76px; height: 76px; background: #f0f4f8; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; }
.notif-empty h3 { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0 0 6px; }
.notif-empty p  { color: #aaa; font-size: 0.875rem; margin: 0; }

/* List */
.notif-list { display: flex; flex-direction: column; gap: 10px; }

.notif-card { display: flex; align-items: flex-start; gap: 12px; background: #fff; border: 1px solid #e8edf4; border-radius: 14px; padding: 14px 16px; position: relative; transition: box-shadow 0.2s; }
.notif-card:hover { box-shadow: 0 4px 16px rgba(0,51,102,0.08); }
.notif-card--unread { background: #f8faff; border-color: #c5d5ef; }

/* Dot */
.notif-dot-wrap { padding-top: 4px; flex-shrink: 0; }
.notif-dot { display: block; width: 8px; height: 8px; border-radius: 50%; background: #e0e8f4; }
.notif-dot--active { background: #003366; animation: pulse 2s ease-in-out infinite; }

/* Icon */
.notif-icon-wrap { flex-shrink: 0; }
.notif-icon { width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; }
.notif-icon--order   { background: #fff8e0; color: #b45309; }
.notif-icon--msg     { background: #e8f0fe; color: #185FA5; }
.notif-icon--cart    { background: #f0fdf4; color: #15803d; }
.notif-icon--default { background: #f0f4f8; color: #003366; }

/* Content */
.notif-content { flex: 1; min-width: 0; }
.notif-message { font-size: 0.9rem; font-weight: 600; color: #1a1a1a; margin: 0 0 6px; line-height: 1.4; }
.notif-time { display: flex; align-items: center; gap: 4px; font-size: 0.75rem; color: #aaa; }

/* New chip */
.new-chip { position: absolute; top: 12px; right: 12px; background: #FFD700; color: #003366; font-size: 0.65rem; font-weight: 800; padding: 2px 8px; border-radius: 20px; letter-spacing: 0.3px; }

/* Transitions */
.notif-item-enter-active, .notif-item-leave-active { transition: all 0.3s ease; }
.notif-item-enter-from { opacity: 0; transform: translateY(-8px); }
.notif-item-leave-to   { opacity: 0; transform: translateX(20px); }
</style>