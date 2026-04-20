<template>
  <div class="admin-wrapper">

    <!-- LOGIN SCREEN -->
    <div v-if="!authed" class="admin-login-screen">
      <div class="login-card">
        <div class="login-logo">🛍️</div>
        <h2>White Market</h2>
        <p>Admin Dashboard — Staff Only</p>
        <div class="input-wrap">
          <i class="fa-solid fa-lock"></i>
          <input
            v-model="password"
            type="password"
            placeholder="Enter admin password"
            @keyup.enter="doLogin"
          />
        </div>
        <button @click="doLogin" :disabled="loggingIn" class="login-btn">
          <i class="fa-solid fa-circle-notch fa-spin" v-if="loggingIn"></i>
          <span v-else>Access Dashboard</span>
        </button>
        <p class="login-error" v-if="loginError">{{ loginError }}</p>
      </div>
    </div>

    <!-- DASHBOARD -->
    <div v-else class="admin-dashboard">

      <!-- HEADER -->
      <header class="admin-header">
        <div class="header-brand">
          <span>🛍️</span>
          <span>White Market <strong>Admin</strong></span>
        </div>
        <nav class="admin-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="nav-tab"
            :class="{ active: activeTab === tab.key }"
            @click="switchTab(tab.key)"
          >
            <i :class="tab.icon"></i> {{ tab.label }}
          </button>
        </nav>
        <button class="logout-btn" @click="doLogout">
          <i class="fa-solid fa-right-from-bracket"></i> Logout
        </button>
      </header>

      <!-- OVERVIEW TAB -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <h2 class="tab-title">Overview</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon"><i class="fa-solid fa-users"></i></div>
            <div class="stat-body">
              <span class="stat-num">{{ stats.users ?? '—' }}</span>
              <span class="stat-label">Registered Users</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green"><i class="fa-solid fa-box"></i></div>
            <div class="stat-body">
              <span class="stat-num">{{ stats.products ?? '—' }}</span>
              <span class="stat-label">Total Listings</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon gold"><i class="fa-solid fa-message"></i></div>
            <div class="stat-body">
              <span class="stat-num">{{ stats.messages ?? '—' }}</span>
              <span class="stat-label">Messages Sent</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon red"><i class="fa-solid fa-cart-shopping"></i></div>
            <div class="stat-body">
              <span class="stat-num">{{ stats.cart_items ?? '—' }}</span>
              <span class="stat-label">Cart Items</span>
            </div>
          </div>
        </div>

        <h3 class="section-label">Recent Listings</h3>
        <div class="recent-list">
          <p v-if="!recentProducts.length" class="empty-msg">No listings yet.</p>
          <div
            v-for="p in recentProducts.slice(0, 8)"
            :key="p.id"
            class="recent-item"
          >
            <img
              :src="p.image_url || ''"
              class="recent-thumb"
              alt=""
              @error="e => e.target.style.opacity = '.15'"
            />
            <div class="recent-info">
              <div class="recent-title">{{ p.title }}</div>
              <div class="recent-meta">{{ p.category }} · {{ p.seller_name || '—' }} · {{ formatDate(p.created_at) }}</div>
            </div>
            <span class="recent-price">₱{{ fmtPrice(p.price) }}</span>
          </div>
        </div>
      </div>

      <!-- PRODUCTS TAB -->
      <div v-if="activeTab === 'products'" class="tab-content">
        <div class="tab-header">
          <div class="tab-header-left">
            <h2 class="tab-title">All Listings</h2>
            <span class="count-badge">{{ filteredProducts.length }} items</span>
          </div>
          <input
            v-model="productSearch"
            class="search-input"
            placeholder="Search title, seller, category..."
          />
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Image</th><th>Title</th><th>Category</th>
                <th>Price</th><th>Status</th><th>Seller</th><th>Posted</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loadingProducts"><td colspan="9" class="center-cell">Loading...</td></tr>
              <tr v-else-if="!filteredProducts.length"><td colspan="9" class="center-cell">No products found</td></tr>
              <tr v-for="p in filteredProducts" :key="p.id">
                <td class="muted">{{ p.id }}</td>
                <td>
                  <img v-if="p.image_url" :src="p.image_url" class="thumb-img" alt="" @error="e => e.target.style.opacity='.15'" />
                  <div v-else class="thumb-img placeholder"></div>
                </td>
                <td class="td-title">{{ p.title }}</td>
                <td><span class="cat-tag">{{ p.category }}</span></td>
                <td class="nowrap">₱{{ fmtPrice(p.price) }}</td>
                <td>
                  <span :class="['status-tag', 'status-' + (p.status||'').toLowerCase()]">{{ p.status }}</span>
                </td>
                <td class="muted">{{ p.seller_name || '—' }}</td>
                <td class="muted nowrap">{{ formatDate(p.created_at) }}</td>
                <td>
                  <button class="del-btn" @click="adminDeleteProduct(p)">
                    <i class="fa-solid fa-trash"></i> Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- USERS TAB -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="tab-header">
          <div class="tab-header-left">
            <h2 class="tab-title">All Users</h2>
            <span class="count-badge">{{ filteredUsers.length }} users</span>
          </div>
          <input
            v-model="userSearch"
            class="search-input"
            placeholder="Search name, email, student ID..."
          />
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Name</th><th>Email</th>
                <th>Student ID</th><th>Course</th><th>Year</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loadingUsers"><td colspan="7" class="center-cell">Loading...</td></tr>
              <tr v-else-if="!filteredUsers.length"><td colspan="7" class="center-cell">No users found</td></tr>
              <tr v-for="u in filteredUsers" :key="u.id">
                <td class="muted">{{ u.id }}</td>
                <td class="td-title">{{ u.name }}</td>
                <td class="td-email">{{ u.email }}</td>
                <td class="mono">{{ u.student_id || '—' }}</td>
                <td class="muted ellipsis" style="max-width:160px">{{ u.course || '—' }}</td>
                <td class="muted">{{ u.year_level ? 'Year ' + u.year_level : '—' }}</td>
                <td>
                  <button class="del-btn" @click="adminDeleteUser(u)">
                    <i class="fa-solid fa-trash"></i> Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- MESSAGES TAB -->
      <div v-if="activeTab === 'messages'" class="tab-content">
        <div class="tab-header">
          <div class="tab-header-left">
            <h2 class="tab-title">All Messages</h2>
            <span class="count-badge">{{ filteredMessages.length }} messages</span>
          </div>
          <input
            v-model="msgSearch"
            class="search-input"
            placeholder="Search sender, receiver, message..."
          />
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>From</th><th>To</th>
                <th>Message</th><th>Sent</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loadingMessages"><td colspan="6" class="center-cell">Loading...</td></tr>
              <tr v-else-if="!filteredMessages.length"><td colspan="6" class="center-cell">No messages found</td></tr>
              <tr v-for="m in filteredMessages" :key="m.id">
                <td class="muted">{{ m.id }}</td>
                <td class="bold">{{ m.sender_name || m.sender_id }}</td>
                <td class="muted">{{ m.receiver_name || m.receiver_id }}</td>
                <td class="td-msg" :title="m.message">{{ m.message }}</td>
                <td class="muted nowrap small">{{ formatDate(m.sent_at) }}</td>
                <td>
                  <span :class="['read-tag', m.is_read ? 'read-yes' : 'read-no']">
                    {{ m.is_read ? 'Read' : 'Unread' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- TOAST -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['toast-msg', toast.type]">{{ toast.text }}</div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

// ── Auth ──────────────────────────────────────────────────
const ADMIN_PW = 'adnu_admin_2024'
const authed = ref(false)
const password = ref('')
const loginError = ref('')
const loggingIn = ref(false)

const doLogin = async () => {
  if (!password.value.trim()) { loginError.value = 'Please enter the admin password.'; return }
  loggingIn.value = true
  loginError.value = ''
  try {
    const res = await api.adminLogin(password.value.trim())
    if (res.data?.success) {
      sessionStorage.setItem('admin_auth', '1')
      authed.value = true
      loadAll()
    } else {
      loginError.value = 'Wrong password.'
    }
  } catch {
    // fallback offline
    if (password.value.trim() === ADMIN_PW) {
      sessionStorage.setItem('admin_auth', '1')
      authed.value = true
      loadAll()
      showToast('Offline mode', 'success')
    } else {
      loginError.value = 'Cannot reach backend. Is Flask running?'
    }
  } finally {
    loggingIn.value = false
  }
}

const doLogout = () => {
  sessionStorage.removeItem('admin_auth')
  authed.value = false
  password.value = ''
}

onMounted(() => {
  if (sessionStorage.getItem('admin_auth')) {
    authed.value = true
    loadAll()
  }
})

// ── Tabs ──────────────────────────────────────────────────
const tabs = [
  { key: 'overview',  label: 'Overview',  icon: 'fa-solid fa-chart-pie' },
  { key: 'products',  label: 'Products',  icon: 'fa-solid fa-box' },
  { key: 'users',     label: 'Users',     icon: 'fa-solid fa-users' },
  { key: 'messages',  label: 'Messages',  icon: 'fa-solid fa-message' },
]
const activeTab = ref('overview')

const switchTab = (key) => {
  activeTab.value = key
  if (key === 'products' && !allProducts.value.length) loadProducts()
  if (key === 'users' && !allUsers.value.length) loadUsers()
  if (key === 'messages' && !allMessages.value.length) loadMessages()
}

// ── Data ──────────────────────────────────────────────────
const stats = ref({})
const recentProducts = ref([])
const allProducts = ref([])
const allUsers = ref([])
const allMessages = ref([])
const loadingProducts = ref(false)
const loadingUsers = ref(false)
const loadingMessages = ref(false)
const productSearch = ref('')
const userSearch = ref('')
const msgSearch = ref('')

const filteredProducts = computed(() => {
  const q = productSearch.value.toLowerCase()
  if (!q) return allProducts.value
  return allProducts.value.filter(p =>
    (p.title||'').toLowerCase().includes(q) ||
    (p.seller_name||'').toLowerCase().includes(q) ||
    (p.category||'').toLowerCase().includes(q)
  )
})

const filteredUsers = computed(() => {
  const q = userSearch.value.toLowerCase()
  if (!q) return allUsers.value
  return allUsers.value.filter(u =>
    (u.name||'').toLowerCase().includes(q) ||
    (u.email||'').toLowerCase().includes(q) ||
    (u.student_id||'').toLowerCase().includes(q)
  )
})

const filteredMessages = computed(() => {
  const q = msgSearch.value.toLowerCase()
  if (!q) return allMessages.value
  return allMessages.value.filter(m =>
    (m.message||'').toLowerCase().includes(q) ||
    (m.sender_name||'').toLowerCase().includes(q) ||
    (m.receiver_name||'').toLowerCase().includes(q)
  )
})

const loadAll = async () => {
  try {
    const r = await api.adminStats()
    stats.value = r.data
  } catch {}
  try {
    const r = await api.adminProducts()
    recentProducts.value = r.data
  } catch {}
}

const loadProducts = async () => {
  loadingProducts.value = true
  try {
    const r = await api.adminProducts()
    allProducts.value = r.data
  } catch { showToast('Failed to load products', 'error') }
  finally { loadingProducts.value = false }
}

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const r = await api.adminUsers()
    allUsers.value = r.data
  } catch { showToast('Failed to load users', 'error') }
  finally { loadingUsers.value = false }
}

const loadMessages = async () => {
  loadingMessages.value = true
  try {
    const r = await api.adminMessages()
    allMessages.value = r.data
  } catch { showToast('Failed to load messages', 'error') }
  finally { loadingMessages.value = false }
}

const adminDeleteProduct = async (p) => {
  if (!confirm(`Delete "${p.title}"?\n\nThis cannot be undone.`)) return
  try {
    await api.adminDeleteProduct(p.id)
    allProducts.value = allProducts.value.filter(x => x.id !== p.id)
    recentProducts.value = recentProducts.value.filter(x => x.id !== p.id)
    showToast('Product deleted', 'success')
  } catch { showToast('Failed to delete', 'error') }
}

const adminDeleteUser = async (u) => {
  if (!confirm(`Delete user "${u.name}"?\n\nThis removes their products, cart, and messages. Cannot be undone.`)) return
  try {
    await api.adminDeleteUser(u.id)
    allUsers.value = allUsers.value.filter(x => x.id !== u.id)
    showToast('User deleted', 'success')
  } catch { showToast('Failed to delete', 'error') }
}

// ── Toast ──────────────────────────────────────────────────
const toast = ref({ show: false, text: '', type: '' })
let toastTimer = null
const showToast = (text, type = '') => {
  clearTimeout(toastTimer)
  toast.value = { show: true, text, type }
  toastTimer = setTimeout(() => { toast.value.show = false }, 3000)
}

// ── Helpers ────────────────────────────────────────────────
const formatDate = (d) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' }) }
  catch { return d }
}
const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })
</script>

<style scoped>
.admin-wrapper {
  font-family: 'Space Grotesk', 'Inter', sans-serif;
  background: #0d0f14;
  color: #e8eaf0;
  min-height: 100vh;
  font-size: 14px;
  line-height: 1.6;
}

/* ── LOGIN ── */
.admin-login-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d0f14;
  background-image:
    radial-gradient(ellipse 60% 50% at 20% 20%, rgba(108,99,255,0.14) 0%, transparent 70%),
    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(78,204,163,0.09) 0%, transparent 70%);
}

.login-card {
  background: #13161d;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 18px;
  padding: 2.5rem 2.25rem;
  width: 100%;
  max-width: 380px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.login-logo {
  font-size: 2.5rem;
  margin-bottom: 0.25rem;
}

.login-card h2 {
  font-size: 20px;
  font-weight: 600;
  color: #e8eaf0;
  margin: 0;
}

.login-card > p {
  color: #7a7f96;
  font-size: 13px;
  margin: 0 0 0.5rem;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #1a1e28;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  padding: 10px 14px;
  transition: border-color 0.2s;
}

.input-wrap:focus-within { border-color: #6c63ff; }
.input-wrap i { color: #555a72; font-size: 13px; flex-shrink: 0; }

.input-wrap input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e8eaf0;
  font-size: 14px;
  letter-spacing: 2px;
  font-family: 'JetBrains Mono', monospace;
}

.login-btn {
  background: #6c63ff;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 11px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-btn:hover:not(:disabled) { opacity: 0.9; }
.login-btn:active { transform: scale(0.98); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.login-error {
  color: #ff5e6c;
  font-size: 12.5px;
  margin: 0;
}

/* ── HEADER ── */
.admin-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  height: 56px;
  background: rgba(13,15,20,0.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-wrap: nowrap;
  overflow-x: auto;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  white-space: nowrap;
  margin-right: 6px;
  flex-shrink: 0;
}

.header-brand strong { color: #6c63ff; font-weight: 600; }

.admin-nav {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: #7a7f96;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  font-family: inherit;
}

.nav-tab:hover { color: #e8eaf0; background: #1a1e28; }
.nav-tab.active { color: #6c63ff; background: rgba(108,99,255,0.12); border-color: rgba(108,99,255,0.25); }
.nav-tab i { font-size: 12px; }

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(255,94,108,0.1);
  border: 1px solid rgba(255,94,108,0.2);
  border-radius: 8px;
  color: #ff5e6c;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  font-family: inherit;
  flex-shrink: 0;
}

.logout-btn:hover { background: rgba(255,94,108,0.18); border-color: rgba(255,94,108,0.35); }

/* ── CONTENT ── */
.tab-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

.tab-title {
  font-size: 20px;
  font-weight: 600;
  color: #e8eaf0;
  margin: 0 0 20px;
}

/* ── STATS ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}

.stat-card {
  background: #13161d;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color 0.2s;
}

.stat-card:hover { border-color: rgba(255,255,255,0.12); }

.stat-icon {
  width: 36px;
  height: 36px;
  background: rgba(108,99,255,0.12);
  color: #6c63ff;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}

.stat-icon.green { background: rgba(78,204,163,0.12); color: #4ecca3; }
.stat-icon.gold  { background: rgba(255,181,71,0.1); color: #ffb547; }
.stat-icon.red   { background: rgba(255,94,108,0.1); color: #ff5e6c; }

.stat-body { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 26px; font-weight: 600; color: #e8eaf0; line-height: 1; }
.stat-label { font-size: 12px; color: #7a7f96; }

/* ── RECENT LIST ── */
.section-label {
  font-size: 12.5px;
  font-weight: 500;
  color: #7a7f96;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 12px;
}

.recent-list {
  background: #13161d;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  overflow: hidden;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  transition: background 0.15s;
}

.recent-item:last-child { border-bottom: none; }
.recent-item:hover { background: #1a1e28; }

.recent-thumb {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  background: #222636;
  flex-shrink: 0;
}

.recent-info { flex: 1; min-width: 0; }
.recent-title { font-size: 13px; font-weight: 500; color: #e8eaf0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.recent-meta { font-size: 12px; color: #7a7f96; margin-top: 2px; }
.recent-price { font-size: 13px; font-weight: 600; color: #4ecca3; white-space: nowrap; }

.empty-msg { padding: 1.5rem; color: #7a7f96; text-align: center; font-size: 13px; }

/* ── TAB HEADER ── */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tab-header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.tab-header-left .tab-title { margin-bottom: 0; }

.count-badge {
  font-size: 12px;
  color: #7a7f96;
  background: #1a1e28;
  border: 1px solid rgba(255,255,255,0.07);
  padding: 2px 10px;
  border-radius: 20px;
}

.search-input {
  background: #13161d;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  padding: 8px 14px;
  color: #e8eaf0;
  font-size: 13px;
  outline: none;
  width: 280px;
  transition: border-color 0.2s;
  font-family: inherit;
}

.search-input::placeholder { color: #555a72; }
.search-input:focus { border-color: #6c63ff; }

/* ── TABLE ── */
.table-wrap {
  background: #13161d;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  overflow: hidden;
  overflow-x: auto;
}

table { width: 100%; border-collapse: collapse; }

thead tr { background: #1a1e28; border-bottom: 1px solid rgba(255,255,255,0.12); }

th {
  padding: 11px 14px;
  text-align: left;
  font-size: 11.5px;
  font-weight: 500;
  color: #7a7f96;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

td {
  padding: 11px 14px;
  font-size: 13px;
  color: #e8eaf0;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  vertical-align: middle;
}

tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #1a1e28; }

.muted { color: #7a7f96; }
.bold { font-weight: 500; }
.nowrap { white-space: nowrap; }
.small { font-size: 12.5px; }
.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.td-title { font-weight: 500; max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.td-email { color: #7a7f96; font-size: 12.5px; }
.td-msg { max-width: 240px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #7a7f96; font-size: 12.5px; }

.center-cell { text-align: center; padding: 36px; color: #7a7f96; }

.thumb-img {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  object-fit: cover;
  background: #222636;
  display: block;
}
.thumb-img.placeholder { opacity: 0.3; }

.cat-tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(108,99,255,0.1);
  color: #a89fff;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 500;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 500;
}
.status-available { background: rgba(78,204,163,0.12); color: #4ecca3; }
.status-sold { background: rgba(255,94,108,0.1); color: #ff8a94; }

.read-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 500;
}
.read-yes { background: rgba(78,204,163,0.1); color: #4ecca3; }
.read-no { background: rgba(255,181,71,0.1); color: #ffb547; }

.del-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: transparent;
  border: 1px solid rgba(255,94,108,0.2);
  border-radius: 6px;
  color: #ff5e6c;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  font-family: inherit;
}
.del-btn:hover { background: rgba(255,94,108,0.1); border-color: rgba(255,94,108,0.4); }

/* ── TOAST ── */
.toast-msg {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 11px 18px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  background: #1a1e28;
  border: 1px solid rgba(255,255,255,0.12);
  color: #e8eaf0;
  z-index: 9999;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.toast-msg.success { border-color: rgba(78,204,163,0.4); color: #4ecca3; }
.toast-msg.error { border-color: rgba(255,94,108,0.4); color: #ff5e6c; }

.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(10px); }

@media (max-width: 640px) {
  .search-input { width: 100%; }
  .tab-header { flex-direction: column; align-items: flex-start; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
}
</style>