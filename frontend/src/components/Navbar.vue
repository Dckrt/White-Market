<template>
  <nav class="nav">
    <div class="nav__inner">

      <!-- ── LOGO ── -->
      <router-link to="/" class="nav__logo">
        <div class="nav__logo-icon">
          <!-- Shopping bag SVG mark -->
          <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav__logo-svg">
            <rect width="36" height="36" rx="9" fill="#003366"/>
            <path d="M10 14h16l-2 12H12L10 14z" fill="#FFD700" opacity="0.15"/>
            <path d="M10 14h16l-2 12H12L10 14z" stroke="#FFD700" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M14 14v-2a4 4 0 018 0v2" stroke="#FFD700" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="15" cy="20" r="1" fill="#FFD700"/>
            <circle cx="21" cy="20" r="1" fill="#FFD700"/>
          </svg>
        </div>
        <div class="nav__logo-text">
          <span class="nav__logo-name">Adnu<span class="nav__logo-accent">Market</span></span>
        </div>
      </router-link>

      <!-- ── LINKS ── -->
      <div class="nav__links">
        <router-link to="/products" class="nav__link">Marketplace</router-link>
        <router-link to="/dashboard" class="nav__link" v-if="auth.user">My Shop</router-link>
      </div>

      <!-- ── ACTIONS ── -->
      <div class="nav__actions" v-if="auth.user">

        <!-- Messages -->
        <router-link to="/messages" class="nav__icon-btn" title="Messages">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
          <span v-if="unreadMsgCount > 0" class="nav__badge">{{ unreadMsgCount > 9 ? '9+' : unreadMsgCount }}</span>
        </router-link>

        <!-- Notifications -->
        <div class="nav__icon-btn nav__notif-wrap" @click.stop="toggleNotif" v-click-outside="closeNotif" title="Notifications">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
          <span v-if="unreadNotifCount > 0" class="nav__badge">{{ unreadNotifCount > 9 ? '9+' : unreadNotifCount }}</span>
          <Transition name="dropdown">
            <div v-if="showNotif" class="nav__dropdown nav__dropdown--notif" @click.stop>
              <div class="nav__dd-head">
                <span class="nav__dd-title">Notifications</span>
                <button v-if="unreadNotifCount > 0" @click.stop="markAllRead" class="nav__dd-mark">Mark all read</button>
              </div>
              <div v-if="loadingNotifs" class="nav__dd-loading">
                <div class="nav__skel" v-for="n in 3" :key="n"></div>
              </div>
              <p v-else-if="!notifications.length" class="nav__dd-empty">No notifications yet</p>
              <div v-for="(n,i) in notifications" :key="n.id||i" class="nav__notif-item" :class="{'nav__notif-item--unread':!n.is_read}">
                <span class="nav__notif-dot" :class="{'nav__notif-dot--on':!n.is_read}"></span>
                <div class="nav__notif-body">
                  <p>{{ n.message }}</p>
                  <span>{{ relTime(n.created_at) }}</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Cart -->
        <router-link to="/cart" class="nav__icon-btn" title="Cart">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
          <span v-if="cartCount > 0" class="nav__badge">{{ cartCount > 9 ? '9+' : cartCount }}</span>
        </router-link>

        <!-- User menu -->
        <div class="nav__user-btn" @click.stop="toggleMenu" v-click-outside="closeMenu">
          <!-- Shows profile pic if available, else initials -->
          <div class="nav__avatar">
            <img v-if="profilePic" :src="profilePic" class="nav__avatar-img" alt="Profile" @error="profilePic = null" />
            <span v-else class="nav__avatar-initials">{{ initials }}</span>
          </div>
          <span class="nav__username">{{ firstName }}</span>
          <svg :class="['nav__chevron', showMenu && 'nav__chevron--open']" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>

          <Transition name="dropdown">
            <div v-if="showMenu" class="nav__dropdown nav__dropdown--user" @click.stop>
              <div class="nav__dd-profile">
                <div class="nav__dd-av">
                  <img v-if="profilePic" :src="profilePic" class="nav__dd-av-img" alt="" @error="profilePic = null" />
                  <span v-else>{{ initials }}</span>
                </div>
                <div class="nav__dd-info">
                  <p class="nav__dd-name">{{ auth.user.name }}</p>
                  <p class="nav__dd-email">{{ auth.user.email }}</p>
                </div>
              </div>
              <div class="nav__dd-sep"></div>
              <router-link class="nav__dd-item" to="/profile" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                Profile
              </router-link>
              <router-link class="nav__dd-item" to="/dashboard" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                My Shop
              </router-link>
              <router-link class="nav__dd-item" to="/messages" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                Messages
                <span v-if="unreadMsgCount > 0" class="nav__dd-badge">{{ unreadMsgCount }}</span>
              </router-link>
              <router-link class="nav__dd-item" to="/add-product" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Sell an Item
              </router-link>
              <router-link class="nav__dd-item" to="/admin" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                Admin Panel
              </router-link>
              <div class="nav__dd-sep"></div>
              <button class="nav__dd-item nav__dd-item--danger" @click="logout">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                Log out
              </button>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Not logged in -->
      <div v-else class="nav__auth-btns">
        <router-link to="/auth" class="nav__signin-btn">Sign in</router-link>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const auth   = useAuthStore()
const router = useRouter()

const cartCount    = ref(0)
const unreadMsgCount  = ref(0)
const notifications   = ref([])
const showMenu     = ref(false)
const showNotif    = ref(false)
const loadingNotifs = ref(false)
const profilePic   = ref(null)
let pA = null, pB = null

// ── Computed ──────────────────────────────────────────────────────────────

const unreadNotifCount = computed(() => notifications.value.filter(n => !n.is_read).length)

const initials = computed(() => {
  if (!auth.user?.name) return '?'
  return auth.user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
})

const firstName = computed(() => auth.user?.name?.split(' ')[0] || 'User')

// ── Watch profile pic changes (e.g. after upload on Profile page) ─────────

watch(() => auth.user?.profile_pic, (val) => {
  profilePic.value = val || null
}, { immediate: true })

// Also watch localStorage changes (cross-component)
const syncProfilePic = () => {
  try {
    const u = JSON.parse(localStorage.getItem('user'))
    if (u?.profile_pic) profilePic.value = u.profile_pic
  } catch {}
}

// ── Fetchers ──────────────────────────────────────────────────────────────

const fetchCart   = async () => {
  if (!auth.user) return
  try { const r = await api.getCart(auth.user.user_id); cartCount.value = Array.isArray(r.data) ? r.data.length : 0 } catch {}
}

const fetchUnread = async () => {
  if (!auth.user) return
  try { const r = await api.getUnreadCount(auth.user.user_id); unreadMsgCount.value = r.data?.count || 0 } catch {}
}

const fetchNotifs = async (loader = false) => {
  if (!auth.user) return
  if (loader) loadingNotifs.value = true
  try { const r = await api.getNotifications(auth.user.user_id); notifications.value = Array.isArray(r.data) ? r.data : [] }
  catch {} finally { loadingNotifs.value = false }
}

const markAllRead = async () => {
  try { await api.markNotificationsRead(auth.user.user_id); notifications.value = notifications.value.map(n => ({...n, is_read: 1})) } catch {}
}

// ── UI ────────────────────────────────────────────────────────────────────

const toggleMenu  = () => { showMenu.value = !showMenu.value; if (showMenu.value) showNotif.value = false }
const closeMenu   = () => { showMenu.value = false }
const toggleNotif = () => { showNotif.value = !showNotif.value; if (showNotif.value) { showMenu.value = false; fetchNotifs(!notifications.value.length) } }
const closeNotif  = () => { showNotif.value = false }

const logout = () => {
  clearInterval(pA); clearInterval(pB)
  auth.logout()
  cartCount.value = 0; unreadMsgCount.value = 0
  notifications.value = []; profilePic.value = null
  showMenu.value = false; showNotif.value = false
  router.push('/auth')
}

const relTime = (d) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
}

// ── Click outside directive ───────────────────────────────────────────────

const vClickOutside = {
  mounted(el, b)  { el._co = e => { if (!el.contains(e.target)) b.value(e) }; document.addEventListener('click', el._co) },
  unmounted(el)   { document.removeEventListener('click', el._co) }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────

onMounted(async () => {
  auth.loadFromStorage()
  syncProfilePic()

  // Listen for profile pic changes from Profile.vue
  window.addEventListener('profile-pic-updated', syncProfilePic)

  if (auth.user) {
    await Promise.all([fetchCart(), fetchUnread(), fetchNotifs()])
    pA = setInterval(() => { fetchCart(); fetchUnread() }, 8000)
    pB = setInterval(() => fetchNotifs(), 15000)
  }
})

onUnmounted(() => {
  clearInterval(pA); clearInterval(pB)
  window.removeEventListener('profile-pic-updated', syncProfilePic)
})
</script>

<style scoped>
/* ── BASE ── */
.nav {
  background: #fff;
  border-bottom: 1px solid #e5eaf2;
  height: 62px;
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 1px 6px rgba(0, 51, 102, 0.06);
}

.nav__inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

/* ── LOGO ── */
.nav__logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.nav__logo-icon { display: flex; align-items: center; }
.nav__logo-svg  { width: 36px; height: 36px; }

.nav__logo-text { display: flex; flex-direction: column; line-height: 1; }
.nav__logo-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #003366;
  letter-spacing: -0.5px;
}
.nav__logo-accent { color: #c09b00; }

/* ── LINKS ── */
.nav__links { display: flex; gap: 2px; flex: 1; }

.nav__link {
  font-size: 0.875rem;
  font-weight: 500;
  color: #555;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 7px;
  transition: 0.15s;
}
.nav__link:hover, .nav__link.router-link-active {
  color: #003366;
  background: #eef3ff;
  font-weight: 600;
}

/* ── ACTIONS ── */
.nav__actions { display: flex; align-items: center; gap: 2px; margin-left: auto; }

.nav__icon-btn {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #555;
  cursor: pointer;
  transition: 0.15s;
  text-decoration: none;
  border: none;
  background: none;
}
.nav__icon-btn:hover, .nav__icon-btn.router-link-active {
  color: #003366;
  background: #eef3ff;
}

.nav__badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #003366;
  color: #FFD700;
  font-size: 9px;
  font-weight: 800;
  min-width: 15px;
  height: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
  border: 1.5px solid #fff;
  pointer-events: none;
}

.nav__notif-wrap { position: relative; }

/* ── USER BUTTON ── */
.nav__user-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  padding: 4px 10px 4px 4px;
  border-radius: 9px;
  transition: 0.15s;
  position: relative;
  border: 1px solid transparent;
  margin-left: 4px;
}
.nav__user-btn:hover { background: #eef3ff; border-color: #dde8f5; }

.nav__avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #003366;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid #FFD700;
}
.nav__avatar-img      { width: 100%; height: 100%; object-fit: cover; }
.nav__avatar-initials { color: #FFD700; font-size: 10px; font-weight: 900; }

.nav__username { font-size: 0.875rem; font-weight: 600; color: #1a1a2e; }
.nav__chevron  { color: #aaa; transition: transform 0.2s; flex-shrink: 0; }
.nav__chevron--open { transform: rotate(180deg); }

/* ── DROPDOWN ── */
.nav__dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: #fff;
  border: 1px solid #e4eaf2;
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0, 51, 102, 0.12);
  z-index: 1000;
  overflow: hidden;
  min-width: 220px;
}

.nav__dropdown--notif { min-width: 320px; max-height: 420px; overflow-y: auto; }

.dropdown-enter-active, .dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px) scale(0.98); }

.nav__dd-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 10px;
  border-bottom: 1px solid #f0f0f0;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 1;
}
.nav__dd-title { font-size: 0.875rem; font-weight: 700; color: #003366; }
.nav__dd-mark  { background: none; border: none; color: #003366; font-size: 0.72rem; font-weight: 600; cursor: pointer; padding: 0; text-decoration: underline; text-underline-offset: 2px; font-family: inherit; }

.nav__dd-loading { padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; }
.nav__skel { height: 48px; border-radius: 8px; background: linear-gradient(110deg,#f0f0f0 8%,#f8f8f8 18%,#f0f0f0 33%); background-size: 200% 100%; animation: sk 1.5s linear infinite; }
@keyframes sk { to { background-position-x: -200%; } }

.nav__dd-empty { padding: 24px; text-align: center; color: #bbb; font-size: 0.85rem; margin: 0; }

.nav__dd-profile { display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: #f8faff; border-bottom: 1px solid #f0f0f0; }
.nav__dd-av {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #003366;
  color: #FFD700;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 900;
  flex-shrink: 0;
  border: 2px solid #FFD700;
}
.nav__dd-av-img { width: 100%; height: 100%; object-fit: cover; }
.nav__dd-name  { font-size: 0.875rem; font-weight: 700; color: #003366; margin: 0 0 2px; }
.nav__dd-email { font-size: 0.72rem; color: #888; margin: 0; }
.nav__dd-sep   { height: 1px; background: #f0f0f0; }

.nav__dd-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  font-size: 0.875rem;
  color: #444;
  text-decoration: none;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: 0.12s;
  font-family: inherit;
}
.nav__dd-item:hover { background: #eef3ff; color: #003366; }
.nav__dd-item svg { flex-shrink: 0; color: #aaa; }
.nav__dd-item:hover svg { color: #003366; }
.nav__dd-item--danger { color: #c0392b !important; }
.nav__dd-item--danger svg { color: #c0392b !important; }
.nav__dd-item--danger:hover { background: #fff5f5 !important; }
.nav__dd-badge { margin-left: auto; background: #003366; color: #FFD700; font-size: 10px; font-weight: 800; min-width: 18px; height: 18px; border-radius: 9px; display: flex; align-items: center; justify-content: center; padding: 0 4px; }

/* Notifications */
.nav__notif-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 16px; border-bottom: 1px solid #f5f5f5; transition: background 0.12s; }
.nav__notif-item:last-child { border-bottom: none; }
.nav__notif-item:hover { background: #f8faff; }
.nav__notif-item--unread { background: #f0f5ff; }
.nav__notif-dot { display: block; width: 7px; height: 7px; border-radius: 50%; background: #ddd; flex-shrink: 0; margin-top: 6px; }
.nav__notif-dot--on { background: #003366; }
.nav__notif-body p    { font-size: 0.82rem; color: #333; margin: 0 0 3px; line-height: 1.4; }
.nav__notif-body span { font-size: 0.7rem; color: #aaa; }

/* Auth buttons */
.nav__auth-btns { margin-left: auto; display: flex; gap: 8px; align-items: center; }
.nav__signin-btn {
  background: #003366;
  color: #fff;
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.875rem;
  text-decoration: none;
  transition: 0.15s;
}
.nav__signin-btn:hover { background: #002244; }

@media (max-width: 640px) {
  .nav__username, .nav__links { display: none; }
  .nav__inner { gap: 8px; }
  .nav__logo-name { font-size: 0.9rem; }
}
</style>