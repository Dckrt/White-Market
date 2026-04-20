<template>
  <nav class="navbar">
    <div class="nav-container">

      <!-- Logo -->
      <router-link to="/" class="brand">
        <span class="logo">🛍️</span>
        White <span class="highlight">Market</span>
      </router-link>

      <!-- Links -->
      <div class="links">

        <router-link to="/products" class="nav-item">Market</router-link>
        <router-link to="/dashboard" class="nav-item" v-if="auth.user">My Shop</router-link>

        <!-- Messages -->
        <router-link to="/messages" class="icon-btn" v-if="auth.user">
          <i class="fa-solid fa-message"></i>
          <span v-if="unreadMsgCount > 0" class="badge">{{ unreadMsgCount > 9 ? '9+' : unreadMsgCount }}</span>
        </router-link>

        <!-- Notifications -->
        <div class="icon-btn notif-wrap" @click.stop="toggleNotif" v-if="auth.user" v-click-outside="closeNotif">
          <i class="fa-solid fa-bell"></i>
          <span v-if="unreadNotifCount > 0" class="badge">{{ unreadNotifCount > 9 ? '9+' : unreadNotifCount }}</span>

          <Transition name="dropdown">
            <div v-if="showNotif" class="dropdown notif-dropdown" @click.stop>
              <div class="dropdown-title-row">
                <p class="dropdown-title">Notifications</p>
                <button
                  v-if="unreadNotifCount > 0"
                  class="mark-read-btn"
                  @click.stop="markAllRead"
                >
                  Mark all read
                </button>
              </div>

              <div v-if="loadingNotifs" class="notif-loading">
                <div class="notif-skeleton" v-for="n in 3" :key="n"></div>
              </div>

              <p v-else-if="notifications.length === 0" class="empty-notif">
                No notifications yet
              </p>

              <div
                v-for="(n, i) in notifications"
                :key="n.id || i"
                class="notif-item"
                :class="{ unread: !n.is_read }"
              >
                <div class="notif-dot-wrap">
                  <span :class="['notif-dot', n.is_read ? 'read' : 'unread']"></span>
                </div>
                <div class="notif-text">
                  <p>{{ n.message }}</p>
                  <span>{{ formatTime(n.created_at) }}</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Cart -->
        <router-link to="/cart" class="icon-btn cart-btn" v-if="auth.user">
          <i class="fa-solid fa-cart-shopping"></i>
          <span v-if="cartCount > 0" class="badge">{{ cartCount > 9 ? '9+' : cartCount }}</span>
        </router-link>

        <!-- User Menu -->
        <div v-if="auth.user" class="user-wrapper" v-click-outside="closeMenu">
          <div class="user-btn" @click.stop="toggleMenu">
            <div class="avatar">{{ initials }}</div>
            <span class="user-name">{{ firstName }}</span>
            <i class="fa-solid fa-chevron-down chevron" :class="{ rotated: showMenu }"></i>
          </div>

          <Transition name="dropdown">
            <div v-if="showMenu" class="dropdown user-dropdown" @click.stop>
              <div class="dropdown-header">
                <p class="dropdown-name">{{ auth.user.name }}</p>
                <p class="dropdown-email">{{ auth.user.email }}</p>
              </div>
              <div class="dropdown-divider"></div>
              <router-link to="/profile" @click="showMenu = false">
                <i class="fa-solid fa-user"></i> Profile
              </router-link>
              <router-link to="/dashboard" @click="showMenu = false">
                <i class="fa-solid fa-store"></i> My Shop
              </router-link>
              <router-link to="/messages" @click="showMenu = false">
                <i class="fa-solid fa-message"></i> Messages
                <span v-if="unreadMsgCount > 0" class="menu-badge">{{ unreadMsgCount }}</span>
              </router-link>
              <router-link to="/add-product" @click="showMenu = false">
                <i class="fa-solid fa-plus"></i> Sell Item
              </router-link>

              <!-- Admin link if admin -->
              <router-link to="/admin" @click="showMenu = false" v-if="isAdmin">
                <i class="fa-solid fa-shield-halved"></i> Admin Panel
              </router-link>

              <div class="dropdown-divider"></div>
              <button @click="logout" class="logout-btn">
                <i class="fa-solid fa-right-from-bracket"></i> Logout
              </button>
            </div>
          </Transition>
        </div>

        <!-- Login -->
        <router-link v-if="!auth.user" to="/auth" class="login-btn">Login</router-link>

      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const auth = useAuthStore()
const router = useRouter()

const cartCount = ref(0)
const unreadMsgCount = ref(0)
const notifications = ref([])
const showMenu = ref(false)
const showNotif = ref(false)
const loadingNotifs = ref(false)

let msgPollInterval = null
let notifPollInterval = null

// ── Computed ──────────────────────────────────────────────

const unreadNotifCount = computed(() =>
  notifications.value.filter(n => !n.is_read).length
)

const initials = computed(() => {
  if (!auth.user?.name) return '?'
  return auth.user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
})

const firstName = computed(() => {
  if (!auth.user?.name) return 'User'
  return auth.user.name.split(' ')[0]
})

// Admin: user whose email is stored in localStorage with admin flag, or check email
const isAdmin = computed(() => {
  if (!auth.user) return false
  // You can customize this — e.g. specific emails or a role field
  return auth.user?.email?.endsWith('@adnu.edu.ph') || false
})

// ── Fetchers ──────────────────────────────────────────────

const loadUser = () => {
  const saved = localStorage.getItem('user')
  if (saved) {
    try { auth.user = JSON.parse(saved) } catch {}
  }
}

const fetchCart = async () => {
  if (!auth.user) return
  try {
    const res = await api.getCart(auth.user.user_id)
    cartCount.value = Array.isArray(res.data) ? res.data.length : 0
  } catch { /* silent */ }
}

const fetchUnreadMessages = async () => {
  if (!auth.user) return
  try {
    const res = await api.getUnreadCount(auth.user.user_id)
    unreadMsgCount.value = res.data?.count || 0
  } catch { /* silent */ }
}

const fetchNotifications = async (showLoader = false) => {
  if (!auth.user) return
  if (showLoader) loadingNotifs.value = true
  try {
    const res = await api.getNotifications(auth.user.user_id)
    notifications.value = Array.isArray(res.data) ? res.data : []
  } catch { /* silent */ }
  finally { loadingNotifs.value = false }
}

const markAllRead = async () => {
  if (!auth.user) return
  try {
    await api.markNotificationsRead(auth.user.user_id)
    notifications.value = notifications.value.map(n => ({ ...n, is_read: 1 }))
  } catch { /* silent */ }
}

// ── UI Handlers ────────────────────────────────────────────

const toggleMenu = () => {
  showMenu.value = !showMenu.value
  if (showMenu.value) showNotif.value = false
}
const closeMenu = () => { showMenu.value = false }

const toggleNotif = () => {
  showNotif.value = !showNotif.value
  if (showNotif.value) {
    showMenu.value = false
    fetchNotifications(notifications.value.length === 0)
  }
}
const closeNotif = () => { showNotif.value = false }

const logout = () => {
  if (msgPollInterval) clearInterval(msgPollInterval)
  if (notifPollInterval) clearInterval(notifPollInterval)
  localStorage.removeItem('user')
  auth.user = null
  cartCount.value = 0
  unreadMsgCount.value = 0
  notifications.value = []
  showMenu.value = false
  showNotif.value = false
  router.push('/auth')
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

// ── Click Outside Directive ────────────────────────────────

const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => { if (!el.contains(e.target)) binding.value(e) }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  }
}

// ── Lifecycle ──────────────────────────────────────────────

onMounted(async () => {
  loadUser()
  if (auth.user) {
    await Promise.all([fetchCart(), fetchUnreadMessages(), fetchNotifications()])

    // Poll messages every 8s
    msgPollInterval = setInterval(() => {
      fetchUnreadMessages()
      fetchCart()
    }, 8000)

    // Poll notifications every 15s
    notifPollInterval = setInterval(() => {
      fetchNotifications()
    }, 15000)
  }
})

onUnmounted(() => {
  if (msgPollInterval) clearInterval(msgPollInterval)
  if (notifPollInterval) clearInterval(notifPollInterval)
})
</script>

<style scoped>
.navbar {
  background: #003366;
  color: white;
  padding: 0 24px;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 2px 16px rgba(0,0,0,0.18);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  font-weight: 800;
  font-size: 1.15rem;
  color: white;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.highlight { color: #FFD700; }

.links { display: flex; align-items: center; gap: 6px; }

.nav-item {
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  font-size: 0.9rem;
  padding: 6px 12px;
  border-radius: 7px;
  transition: 0.2s;
  font-weight: 500;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: white;
  background: rgba(255,255,255,0.12);
}

.icon-btn {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: rgba(255,255,255,0.85);
  cursor: pointer;
  transition: 0.2s;
  text-decoration: none;
}

.icon-btn:hover { background: rgba(255,255,255,0.12); color: white; }
.icon-btn.router-link-active { color: #FFD700; background: rgba(255,255,255,0.1); }

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #FFD700;
  color: #003366;
  font-size: 9px;
  font-weight: 900;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
  pointer-events: none;
}

/* Notification wrap */
.notif-wrap { position: relative; }

/* User */
.user-wrapper { position: relative; }

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 8px;
  transition: 0.2s;
  user-select: none;
}

.user-btn:hover { background: rgba(255,255,255,0.12); }

.avatar {
  width: 30px;
  height: 30px;
  background: #FFD700;
  color: #003366;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 900;
  flex-shrink: 0;
}

.user-name { font-size: 0.875rem; font-weight: 600; color: white; }
.chevron { font-size: 10px; color: rgba(255,255,255,0.7); transition: transform 0.2s; }
.chevron.rotated { transform: rotate(180deg); }

/* Dropdown */
.dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  background: white;
  color: #333;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.16);
  min-width: 210px;
  overflow: hidden;
  z-index: 1000;
  border: 0.5px solid #e5e7eb;
}

.dropdown-enter-active,
.dropdown-leave-active { transition: all 0.18s ease; }
.dropdown-enter-from,
.dropdown-leave-to { opacity: 0; transform: translateY(-6px); }

.dropdown-header { padding: 12px 16px; background: #f8fafc; }
.dropdown-name { font-weight: 800; font-size: 0.875rem; color: #003366; margin: 0 0 2px; }
.dropdown-email { font-size: 0.72rem; color: #888; margin: 0; }
.dropdown-divider { height: 1px; background: #eee; }

.dropdown a,
.dropdown button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  font-size: 0.875rem;
  color: #333;
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: 0.15s;
  font-family: inherit;
}

.dropdown a:hover, .dropdown button:hover { background: #f0f4ff; color: #003366; }
.dropdown i { width: 14px; color: #888; }

.menu-badge {
  margin-left: auto;
  background: #003366;
  color: white;
  font-size: 10px;
  font-weight: 800;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.logout-btn { color: #e74c3c !important; }
.logout-btn i { color: #e74c3c !important; }
.logout-btn:hover { background: #fff5f5 !important; }

/* Notif Dropdown */
.notif-dropdown {
  min-width: 320px;
  max-height: 420px;
  overflow-y: auto;
}

.dropdown-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 10px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.dropdown-title { font-weight: 800; font-size: 0.875rem; color: #003366; margin: 0; }

.mark-read-btn {
  background: none !important;
  border: none !important;
  color: #003366 !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  padding: 0 !important;
  width: auto !important;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.mark-read-btn:hover { opacity: 0.7; background: none !important; }

.notif-loading { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.notif-skeleton {
  height: 52px;
  border-radius: 8px;
  background: linear-gradient(110deg, #ececec 8%, #f5f5f5 18%, #ececec 33%);
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}

@keyframes shimmer { to { background-position-x: -200%; } }

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.15s;
  cursor: default;
}

.notif-item:last-child { border-bottom: none; }
.notif-item.unread { background: #f0f4ff; }
.notif-item:hover { background: #e8f0fe; }

.notif-dot-wrap { padding-top: 5px; flex-shrink: 0; }
.notif-dot {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.notif-dot.unread { background: #003366; }
.notif-dot.read { background: #ddd; }

.notif-text p { font-size: 0.82rem; color: #333; margin: 0 0 3px; line-height: 1.4; }
.notif-text span { font-size: 0.7rem; color: #aaa; }

.empty-notif { padding: 24px 16px; text-align: center; color: #bbb; font-size: 0.85rem; margin: 0; }

/* Login */
.login-btn {
  background: #FFD700;
  color: #003366;
  padding: 7px 18px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 0.875rem;
  text-decoration: none;
  transition: 0.2s;
}

.login-btn:hover { background: #e6c200; }

@media (max-width: 640px) {
  .user-name { display: none; }
  .nav-item { padding: 6px 8px; font-size: 0.82rem; }
}
</style>