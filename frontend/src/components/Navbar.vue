<template>
  <nav class="wm-nav">
    <div class="wm-nav__inner">

      <router-link to="/" class="wm-brand">
        <span class="brand-icon">🛍️</span>
        <span class="wm-brand__text">Adnu<span class="wm-brand__gold">Market</span></span>
      </router-link>

      <div class="wm-nav__links">
        <router-link to="/products" class="wm-nav__link">Marketplace</router-link>
        <router-link to="/dashboard" class="wm-nav__link" v-if="auth.user">My Shop</router-link>
      </div>

      <div class="wm-nav__actions" v-if="auth.user">

        <router-link to="/messages" class="wm-icon-btn" title="Messages">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span v-if="unreadMsgCount > 0" class="wm-badge">{{ unreadMsgCount > 9 ? '9+' : unreadMsgCount }}</span>
        </router-link>

        <div class="wm-icon-btn wm-notif-wrap" @click.stop="toggleNotif" v-click-outside="closeNotif">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span v-if="unreadNotifCount > 0" class="wm-badge">{{ unreadNotifCount > 9 ? '9+' : unreadNotifCount }}</span>
          <Transition name="wm-drop">
            <div v-if="showNotif" class="wm-dropdown wm-dropdown--wide" @click.stop>
              <div class="wm-dd-head">
                <span>Notifications</span>
                <button v-if="unreadNotifCount > 0" @click.stop="markAllRead" class="wm-dd-link">Mark all read</button>
              </div>
              <div v-if="loadingNotifs" style="padding:12px"><div class="wm-skel" style="height:44px;margin-bottom:8px;border-radius:8px" v-for="n in 3" :key="n"></div></div>
              <p v-else-if="!notifications.length" class="wm-dd-empty">No notifications yet</p>
              <div v-for="(n,i) in notifications" :key="n.id||i" class="wm-notif-item" :class="{'wm-notif-item--unread':!n.is_read}">
                <span class="wm-notif-dot" :class="{'wm-notif-dot--on':!n.is_read}"></span>
                <div>
                  <p class="wm-notif-msg">{{ n.message }}</p>
                  <span class="wm-notif-time">{{ relTime(n.created_at) }}</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <router-link to="/cart" class="wm-icon-btn" title="Cart">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
          <span v-if="cartCount > 0" class="wm-badge">{{ cartCount > 9 ? '9+' : cartCount }}</span>
        </router-link>

        <div class="wm-user-btn" @click.stop="toggleMenu" v-click-outside="closeMenu">
          <div class="wm-avatar">{{ initials }}</div>
          <span class="wm-uname">{{ firstName }}</span>
          <svg :class="['wm-chevron', showMenu && 'wm-chevron--open']" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>

          <Transition name="wm-drop">
            <div v-if="showMenu" class="wm-dropdown" @click.stop>
              <div class="wm-dd-profile">
                <div class="wm-dd-avatar">{{ initials }}</div>
                <div>
                  <p class="wm-dd-name">{{ auth.user.name }}</p>
                  <p class="wm-dd-email">{{ auth.user.email }}</p>
                </div>
              </div>
              <div class="wm-dd-sep"></div>
              <router-link class="wm-dd-item" to="/profile" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> Profile
              </router-link>
              <router-link class="wm-dd-item" to="/dashboard" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg> My Shop
              </router-link>
              <router-link class="wm-dd-item" to="/messages" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> Messages
                <span v-if="unreadMsgCount > 0" class="wm-dd-count">{{ unreadMsgCount }}</span>
              </router-link>
              <router-link class="wm-dd-item" to="/add-product" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Sell an Item
              </router-link>
              <router-link class="wm-dd-item" to="/admin" @click="showMenu=false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Admin Panel
              </router-link>
              <div class="wm-dd-sep"></div>
              <button class="wm-dd-item wm-dd-item--danger" @click="logout">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                Log out
              </button>
            </div>
          </Transition>
        </div>
      </div>

      <router-link v-else to="/auth" class="wm-signin-btn" style="margin-left:auto">Sign in</router-link>
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
const cartCount = ref(0), unreadMsgCount = ref(0), notifications = ref([])
const showMenu = ref(false), showNotif = ref(false), loadingNotifs = ref(false)
let pA = null, pB = null

const unreadNotifCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const initials = computed(() => !auth.user?.name ? '?' : auth.user.name.split(' ').map(n => n[0]).slice(0,2).join('').toUpperCase())
const firstName = computed(() => auth.user?.name?.split(' ')[0] || 'User')

const fetchCart = async () => { if (!auth.user) return; try { const r = await api.getCart(auth.user.user_id); cartCount.value = Array.isArray(r.data) ? r.data.length : 0 } catch {} }
const fetchUnread = async () => { if (!auth.user) return; try { const r = await api.getUnreadCount(auth.user.user_id); unreadMsgCount.value = r.data?.count || 0 } catch {} }
const fetchNotifs = async (loader = false) => { if (!auth.user) return; if (loader) loadingNotifs.value = true; try { const r = await api.getNotifications(auth.user.user_id); notifications.value = Array.isArray(r.data) ? r.data : [] } catch {} finally { loadingNotifs.value = false } }
const markAllRead = async () => { try { await api.markNotificationsRead(auth.user.user_id); notifications.value = notifications.value.map(n => ({...n, is_read:1})) } catch {} }

const toggleMenu = () => { showMenu.value = !showMenu.value; if (showMenu.value) showNotif.value = false }
const closeMenu = () => { showMenu.value = false }
const toggleNotif = () => { showNotif.value = !showNotif.value; if (showNotif.value) { showMenu.value = false; fetchNotifs(!notifications.value.length) } }
const closeNotif = () => { showNotif.value = false }

const logout = () => {
  clearInterval(pA); clearInterval(pB)
  localStorage.removeItem('user'); auth.user = null
  cartCount.value = 0; unreadMsgCount.value = 0; notifications.value = []
  showMenu.value = false; showNotif.value = false
  router.push('/auth')
}

const relTime = (d) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d)
  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`
  if (diff < 86400000) return new Date(d).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})
  return new Date(d).toLocaleDateString('en-PH', {month:'short',day:'numeric'})
}

const vClickOutside = {
  mounted(el, b) { el._co = e => { if (!el.contains(e.target)) b.value(e) }; document.addEventListener('click', el._co) },
  unmounted(el) { document.removeEventListener('click', el._co) }
}

onMounted(async () => {
  const s = localStorage.getItem('user'); if (s) try { auth.user = JSON.parse(s) } catch {}
  if (auth.user) {
    await Promise.all([fetchCart(), fetchUnread(), fetchNotifs()])
    pA = setInterval(() => { fetchCart(); fetchUnread() }, 8000)
    pB = setInterval(() => fetchNotifs(), 15000)
  }
})
onUnmounted(() => { clearInterval(pA); clearInterval(pB) })
</script>

<style scoped>
.wm-nav { background:#fff; border-bottom:1px solid #e8edf2; height:60px; position:sticky; top:0; z-index:999; }
.wm-nav__inner { max-width:1200px; margin:0 auto; height:100%; padding:0 24px; display:flex; align-items:center; gap:28px; }

.wm-brand { display:flex; align-items:center; gap:10px; text-decoration:none; flex-shrink:0; }
.wm-brand__mark { width:34px; height:34px; background:#003366; border-radius:9px; display:flex; align-items:center; justify-content:center; color:#FFD700; font-size:17px; font-weight:900; font-family:Georgia,serif; letter-spacing:-1px; flex-shrink:0; }
.wm-brand__text { font-size:1.05rem; font-weight:800; color:#003366; letter-spacing:-0.5px; }
.wm-brand__gold { color:#B8960C; }

.wm-nav__links { display:flex; gap:2px; flex:1; }
.wm-nav__link { font-size:0.875rem; font-weight:500; color:#666; text-decoration:none; padding:6px 12px; border-radius:7px; transition:0.15s; }
.wm-nav__link:hover { color:#003366; background:#f0f5ff; }
.wm-nav__link.router-link-active { color:#003366; font-weight:700; background:#eef3ff; }

.wm-nav__actions { display:flex; align-items:center; gap:2px; margin-left:auto; }

.wm-icon-btn { position:relative; width:38px; height:38px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#666; cursor:pointer; transition:0.15s; text-decoration:none; border:none; background:none; }
.wm-icon-btn:hover { color:#003366; background:#f0f5ff; }
.wm-icon-btn.router-link-active { color:#003366; background:#eef3ff; }

.wm-badge { position:absolute; top:2px; right:2px; background:#003366; color:#FFD700; font-size:9px; font-weight:800; min-width:15px; height:15px; border-radius:8px; display:flex; align-items:center; justify-content:center; padding:0 3px; pointer-events:none; border:1.5px solid white; }

.wm-notif-wrap { position:relative; }

.wm-user-btn { display:flex; align-items:center; gap:7px; cursor:pointer; padding:5px 10px 5px 5px; border-radius:9px; transition:0.15s; position:relative; border:1px solid transparent; margin-left:6px; }
.wm-user-btn:hover { background:#f0f5ff; border-color:#dde8f8; }
.wm-avatar { width:28px; height:28px; background:#003366; color:#FFD700; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:900; flex-shrink:0; }
.wm-uname { font-size:0.875rem; font-weight:600; color:#1a1a2e; }
.wm-chevron { color:#aaa; transition:transform 0.2s; flex-shrink:0; }
.wm-chevron--open { transform:rotate(180deg); }

.wm-dropdown { position:absolute; top:calc(100% + 10px); right:0; background:#fff; border:1px solid #e4eaf2; border-radius:14px; box-shadow:0 12px 40px rgba(0,51,102,0.12); z-index:1000; overflow:hidden; min-width:220px; }
.wm-dropdown--wide { min-width:320px; max-height:420px; overflow-y:auto; }
.wm-drop-enter-active,.wm-drop-leave-active { transition:all 0.15s ease; }
.wm-drop-enter-from,.wm-drop-leave-to { opacity:0; transform:translateY(-6px) scale(0.98); }

.wm-dd-head { display:flex; justify-content:space-between; align-items:center; padding:12px 16px 10px; border-bottom:1px solid #f0f0f0; font-size:0.875rem; font-weight:700; color:#003366; position:sticky; top:0; background:#fff; }
.wm-dd-link { background:none; border:none; color:#003366; font-size:0.72rem; font-weight:600; cursor:pointer; padding:0; text-decoration:underline; text-underline-offset:2px; font-family:inherit; }
.wm-dd-empty { padding:24px; text-align:center; color:#bbb; font-size:0.85rem; margin:0; }
.wm-dd-sep { height:1px; background:#f0f0f0; }

.wm-dd-profile { display:flex; align-items:center; gap:12px; padding:14px 16px; background:#f8faff; border-bottom:1px solid #f0f0f0; }
.wm-dd-avatar { width:38px; height:38px; border-radius:50%; background:#003366; color:#FFD700; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:900; flex-shrink:0; }
.wm-dd-name { font-size:0.875rem; font-weight:700; color:#003366; margin:0 0 2px; }
.wm-dd-email { font-size:0.72rem; color:#888; margin:0; }

.wm-dd-item { display:flex; align-items:center; gap:10px; padding:10px 16px; font-size:0.875rem; color:#444; text-decoration:none; background:none; border:none; width:100%; text-align:left; cursor:pointer; transition:0.12s; font-family:inherit; }
.wm-dd-item:hover { background:#f0f5ff; color:#003366; }
.wm-dd-item svg { flex-shrink:0; color:#aaa; }
.wm-dd-item:hover svg { color:#003366; }
.wm-dd-item--danger { color:#c0392b; }
.wm-dd-item--danger svg { color:#c0392b; }
.wm-dd-item--danger:hover { background:#fff5f5; color:#c0392b; }
.wm-dd-count { margin-left:auto; background:#003366; color:#FFD700; font-size:10px; font-weight:800; min-width:18px; height:18px; border-radius:9px; display:flex; align-items:center; justify-content:center; padding:0 4px; }

.wm-notif-item { display:flex; align-items:flex-start; gap:10px; padding:10px 16px; border-bottom:1px solid #f5f5f5; transition:background 0.12s; cursor:default; }
.wm-notif-item:last-child { border-bottom:none; }
.wm-notif-item:hover { background:#f8faff; }
.wm-notif-item--unread { background:#f0f5ff; }
.wm-notif-dot { display:block; width:7px; height:7px; border-radius:50%; background:#ddd; flex-shrink:0; margin-top:6px; }
.wm-notif-dot--on { background:#003366; }
.wm-notif-msg { font-size:0.82rem; color:#333; margin:0 0 3px; line-height:1.4; }
.wm-notif-time { font-size:0.7rem; color:#aaa; }

.wm-signin-btn { background:#003366; color:#fff; padding:8px 20px; border-radius:8px; font-weight:700; font-size:0.875rem; text-decoration:none; transition:0.15s; letter-spacing:0.1px; }
.wm-signin-btn:hover { background:#002244; }

.wm-skel { background:linear-gradient(110deg,#f0f0f0 8%,#f8f8f8 18%,#f0f0f0 33%); background-size:200% 100%; animation:sk 1.5s linear infinite; }
@keyframes sk { to { background-position-x:-200%; } }

@media(max-width:640px) { .wm-uname,.wm-nav__links { display:none; } .wm-nav__inner { gap:10px; } }
</style>