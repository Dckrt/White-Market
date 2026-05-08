<template>
  <div class="wm-admin">
    <div class="wm-admin-dash">

      <!-- Sidebar -->
      <aside class="wm-admin-aside">
        <div class="wm-admin-aside__brand">
          <div class="wm-admin-aside__mark">
            <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" width="22" height="22">
              <path d="M10 14h16l-2 12H12L10 14z" fill="#FFD700" opacity="0.2"/>
              <path d="M10 14h16l-2 12H12L10 14z" stroke="#FFD700" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M14 14v-2a4 4 0 018 0v2" stroke="#FFD700" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div>
            <p class="wm-admin-aside__name">AdnuMarket</p>
            <p class="wm-admin-aside__role">Admin Panel</p>
          </div>
        </div>

        <nav class="wm-admin-nav">
          <button v-for="tab in tabs" :key="tab.key"
            class="wm-admin-nav__item"
            :class="{ 'wm-admin-nav__item--active': activeTab === tab.key }"
            @click="switchTab(tab.key)">
            <component :is="tab.icon" />
            {{ tab.label }}
            <span v-if="tab.key==='users' && stats.users" class="wm-admin-nav__pill">{{ stats.users }}</span>
            <span v-if="tab.key==='products' && stats.products" class="wm-admin-nav__pill">{{ stats.products }}</span>
            <span v-if="tab.key==='orders' && stats.orders" class="wm-admin-nav__pill">{{ stats.orders }}</span>
          </button>
        </nav>

        <div class="wm-admin-aside__footer">
          <router-link to="/" class="wm-admin-site-link">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            Back to site
          </router-link>
        </div>
      </aside>

      <!-- Main -->
      <main class="wm-admin-main">

        <!-- OVERVIEW -->
        <div v-if="activeTab==='overview'" class="wm-admin-section">
          <div class="wm-admin-section__head">
            <h1 class="wm-admin-section__title">Overview</h1>
            <p class="wm-admin-section__sub">AdnuMarket platform summary</p>
          </div>
          <div class="wm-admin-stat-grid">
            <div class="wm-stat-card" v-for="s in statCards" :key="s.label">
              <div class="wm-stat-card__icon" :style="`background:${s.bg}`">
                <component :is="s.icon" :style="`color:${s.color}`" />
              </div>
              <div class="wm-stat-card__body">
                <span class="wm-stat-card__num">{{ stats[s.key] ?? '—' }}</span>
                <span class="wm-stat-card__label">{{ s.label }}</span>
              </div>
            </div>
          </div>
          <div style="margin-top:28px">
            <h2 class="wm-admin-section__subtitle">Recent Listings</h2>
          </div>
          <div class="wm-recent-list" style="margin-top:12px">
            <p v-if="!recentProds.length" class="wm-admin-empty">No listings yet.</p>
            <div v-for="p in recentProds.slice(0,8)" :key="p.id" class="wm-recent-item">
              <img :src="p.image_url||''" class="wm-recent-item__img" alt="" @error="e=>e.target.style.opacity='.1'" />
              <div class="wm-recent-item__info">
                <p class="wm-recent-item__title">{{ p.title }}</p>
                <p class="wm-recent-item__meta">{{ p.category }} · {{ p.seller_name||'—' }} · {{ fmtDate(p.created_at) }}</p>
              </div>
              <span class="wm-recent-item__price">₱{{ fmtPrice(p.price) }}</span>
            </div>
          </div>
        </div>

        <!-- PRODUCTS -->
        <div v-if="activeTab==='products'" class="wm-admin-section">
          <div class="wm-admin-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="wm-admin-section__title">All Listings</h1>
              <span class="wm-admin-count-badge">{{ filteredProds.length }}</span>
            </div>
            <div class="wm-admin-search-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="prodSearch" class="wm-admin-search" placeholder="Search…" />
            </div>
          </div>
          <div class="wm-table-wrap">
            <table class="wm-table">
              <thead><tr><th>ID</th><th>Image</th><th>Title</th><th>Category</th><th>Price</th><th>Status</th><th>Seller</th><th>Posted</th><th></th></tr></thead>
              <tbody>
                <tr v-if="loadingProds"><td colspan="9" class="wm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredProds.length"><td colspan="9" class="wm-table__empty">No products found</td></tr>
                <tr v-for="p in filteredProds" :key="p.id" class="wm-table__row">
                  <td class="wm-table__id">{{ p.id }}</td>
                  <td><img v-if="p.image_url" :src="p.image_url" class="wm-table__thumb" alt="" /></td>
                  <td class="wm-table__title">{{ p.title }}</td>
                  <td><span class="wm-cat-tag">{{ p.category }}</span></td>
                  <td class="wm-table__price">₱{{ fmtPrice(p.price) }}</td>
                  <td><span :class="['wm-status-tag', p.status==='Available'?'wm-status-tag--avail':'wm-status-tag--sold']">{{ p.status }}</span></td>
                  <td class="wm-table__muted">{{ p.seller_name||'—' }}</td>
                  <td class="wm-table__muted">{{ fmtDate(p.created_at) }}</td>
                  <td><button class="wm-del-btn" @click="delProd(p)">Delete</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- USERS -->
        <div v-if="activeTab==='users'" class="wm-admin-section">
          <div class="wm-admin-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="wm-admin-section__title">All Users</h1>
              <span class="wm-admin-count-badge">{{ filteredUsers.length }}</span>
            </div>
            <div class="wm-admin-search-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="userSearch" class="wm-admin-search" placeholder="Search…" />
            </div>
          </div>
          <div class="wm-table-wrap">
            <table class="wm-table">
              <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Student ID</th><th>Course</th><th>Year</th><th></th></tr></thead>
              <tbody>
                <tr v-if="loadingUsers"><td colspan="7" class="wm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredUsers.length"><td colspan="7" class="wm-table__empty">No users found</td></tr>
                <tr v-for="u in filteredUsers" :key="u.id" class="wm-table__row">
                  <td class="wm-table__id">{{ u.id }}</td>
                  <td>
                    <div style="display:flex;align-items:center;gap:8px">
                      <div class="wm-user-av">{{ u.name?.charAt(0)||'?' }}</div>
                      <span class="wm-table__title">{{ u.name }}</span>
                    </div>
                  </td>
                  <td class="wm-table__muted">{{ u.email }}</td>
                  <td style="font-family:monospace;font-size:0.8rem">{{ u.student_id||'—' }}</td>
                  <td class="wm-table__muted">{{ u.course||'—' }}</td>
                  <td class="wm-table__muted">{{ u.year_level ? 'Year '+u.year_level : '—' }}</td>
                  <td><button class="wm-del-btn" @click="delUser(u)">Delete</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ORDERS -->
        <div v-if="activeTab==='orders'" class="wm-admin-section">
          <div class="wm-admin-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="wm-admin-section__title">All Orders</h1>
              <span class="wm-admin-count-badge">{{ filteredOrders.length }}</span>
            </div>
            <div class="wm-admin-search-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="orderSearch" class="wm-admin-search" placeholder="Search…" />
            </div>
          </div>
          <div class="wm-table-wrap">
            <table class="wm-table">
              <thead><tr><th>ID</th><th>Product</th><th>Buyer</th><th>Seller</th><th>Price</th><th>Payment</th><th>Status</th><th>Date</th></tr></thead>
              <tbody>
                <tr v-if="loadingOrders"><td colspan="8" class="wm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredOrders.length"><td colspan="8" class="wm-table__empty">No orders yet</td></tr>
                <tr v-for="o in filteredOrders" :key="o.id" class="wm-table__row">
                  <td class="wm-table__id">{{ o.id }}</td>
                  <td class="wm-table__title">{{ o.product_title }}</td>
                  <td class="wm-table__muted">{{ o.buyer_name||o.buyer_id }}</td>
                  <td class="wm-table__muted">{{ o.seller_name||o.seller_id }}</td>
                  <td class="wm-table__price">₱{{ fmtPrice(o.product_price) }}</td>
                  <td class="wm-table__muted">{{ o.payment_method }}</td>
                  <td><span class="wm-status-tag wm-status-tag--avail">{{ o.status }}</span></td>
                  <td class="wm-table__muted">{{ fmtDate(o.ordered_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- MESSAGES -->
        <div v-if="activeTab==='messages'" class="wm-admin-section">
          <div class="wm-admin-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="wm-admin-section__title">All Messages</h1>
              <span class="wm-admin-count-badge">{{ filteredMsgs.length }}</span>
            </div>
            <div class="wm-admin-search-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="msgSearch" class="wm-admin-search" placeholder="Search…" />
            </div>
          </div>
          <div class="wm-table-wrap">
            <table class="wm-table">
              <thead><tr><th>ID</th><th>From</th><th>To</th><th>Message</th><th>Sent</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-if="loadingMsgs"><td colspan="6" class="wm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredMsgs.length"><td colspan="6" class="wm-table__empty">No messages</td></tr>
                <tr v-for="m in filteredMsgs" :key="m.id" class="wm-table__row">
                  <td class="wm-table__id">{{ m.id }}</td>
                  <td style="font-weight:600">{{ m.sender_name }}</td>
                  <td class="wm-table__muted">{{ m.receiver_name }}</td>
                  <td style="max-width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#666">{{ m.message }}</td>
                  <td class="wm-table__muted">{{ fmtDate(m.sent_at) }}</td>
                  <td><span :class="['wm-read-tag', m.is_read?'wm-read-tag--read':'wm-read-tag--unread']">{{ m.is_read?'Read':'Unread' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>

    <!-- Toast -->
    <Transition name="wm-toast">
      <div v-if="toast.show" :class="['wm-admin-toast',`wm-admin-toast--${toast.type}`]">
        {{ toast.text }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import api from '@/services/api'

// ── Icon components ──────────────────────────────────────────────────────────
const IconGrid  = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8'},[h('rect',{x:3,y:3,width:7,height:7}),h('rect',{x:14,y:3,width:7,height:7}),h('rect',{x:14,y:14,width:7,height:7}),h('rect',{x:3,y:14,width:7,height:7})]) }
const IconBox   = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z'}),h('polyline',{points:'3.27 6.96 12 12.01 20.73 6.96'}),h('line',{x1:12,y1:'22.08',x2:12,y2:12})]) }
const IconUsers = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2'}),h('circle',{cx:9,cy:7,r:4}),h('path',{d:'M23 21v-2a4 4 0 00-3-3.87'}),h('path',{d:'M16 3.13a4 4 0 010 7.75'})]) }
const IconMsg   = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z'})]) }
const IconCart  = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('circle',{cx:9,cy:21,r:1}),h('circle',{cx:20,cy:21,r:1}),h('path',{d:'M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6'})]) }
const IconOrder = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2'}),h('rect',{x:9,y:3,width:6,height:4,rx:2}),h('path',{d:'M9 12h6M9 16h4'})]) }

const tabs = [
  { key:'overview', label:'Overview',  icon: IconGrid  },
  { key:'products', label:'Products',  icon: IconBox   },
  { key:'users',    label:'Users',     icon: IconUsers },
  { key:'orders',   label:'Orders',    icon: IconOrder },
  { key:'messages', label:'Messages',  icon: IconMsg   },
]
const statCards = [
  { key:'users',    label:'Registered Users', icon: IconUsers, bg:'#e8f0fe', color:'#003366' },
  { key:'products', label:'Total Listings',   icon: IconBox,   bg:'#e8f8f0', color:'#15803d' },
  { key:'orders',   label:'Total Orders',     icon: IconOrder, bg:'#fff8e0', color:'#854d0e' },
  { key:'messages', label:'Messages Sent',    icon: IconMsg,   bg:'#fce8ff', color:'#7c3aed' },
]

// ── State ────────────────────────────────────────────────────────────────────
const activeTab   = ref('overview')
const stats       = ref({})
const recentProds = ref([])
const allProds    = ref([]), allUsers = ref([]), allMsgs = ref([]), allOrders = ref([])
const loadingProds = ref(false), loadingUsers = ref(false), loadingMsgs = ref(false), loadingOrders = ref(false)
const prodSearch  = ref(''), userSearch = ref(''), msgSearch = ref(''), orderSearch = ref('')
const toast       = ref({ show: false, text: '', type: '' })
let toastTimer    = null

// ── Computed ─────────────────────────────────────────────────────────────────
const filteredProds  = computed(() => { const q = prodSearch.value.toLowerCase();  return q ? allProds.value.filter(p  => `${p.title} ${p.seller_name} ${p.category}`.toLowerCase().includes(q))  : allProds.value  })
const filteredUsers  = computed(() => { const q = userSearch.value.toLowerCase();  return q ? allUsers.value.filter(u  => `${u.name} ${u.email} ${u.student_id}`.toLowerCase().includes(q))         : allUsers.value  })
const filteredMsgs   = computed(() => { const q = msgSearch.value.toLowerCase();   return q ? allMsgs.value.filter(m   => `${m.message} ${m.sender_name} ${m.receiver_name}`.toLowerCase().includes(q)): allMsgs.value  })
const filteredOrders = computed(() => { const q = orderSearch.value.toLowerCase(); return q ? allOrders.value.filter(o => `${o.product_title} ${o.buyer_name} ${o.seller_name}`.toLowerCase().includes(q)): allOrders.value })

// ── Load ─────────────────────────────────────────────────────────────────────
const loadAll = async () => {
  try { const r = await api.adminStats();    stats.value      = r.data } catch {}
  try { const r = await api.adminProducts(); recentProds.value = r.data } catch {}
}

const switchTab = (k) => {
  activeTab.value = k
  if (k==='products' && !allProds.value.length)   loadProds()
  if (k==='users'    && !allUsers.value.length)    loadUsers()
  if (k==='messages' && !allMsgs.value.length)     loadMsgsTab()
  if (k==='orders'   && !allOrders.value.length)   loadOrders()
}

const loadProds  = async () => { loadingProds.value  = true; try { allProds.value  = (await api.adminProducts()).data } catch { showToast('Failed','error') } finally { loadingProds.value  = false } }
const loadUsers  = async () => { loadingUsers.value  = true; try { allUsers.value  = (await api.adminUsers()).data    } catch { showToast('Failed','error') } finally { loadingUsers.value  = false } }
const loadMsgsTab= async () => { loadingMsgs.value   = true; try { allMsgs.value   = (await api.adminMessages()).data } catch { showToast('Failed','error') } finally { loadingMsgs.value   = false } }
const loadOrders = async () => { loadingOrders.value = true; try { allOrders.value = (await api.adminOrders()).data   } catch { showToast('Failed','error') } finally { loadingOrders.value = false } }

// ── Delete ────────────────────────────────────────────────────────────────────
const delProd = async (p) => {
  if (!confirm(`Delete "${p.title}"?`)) return
  try { await api.adminDeleteProduct(p.id); allProds.value = allProds.value.filter(x=>x.id!==p.id); recentProds.value = recentProds.value.filter(x=>x.id!==p.id); showToast('Deleted','success') } catch { showToast('Failed','error') }
}
const delUser = async (u) => {
  if (!confirm(`Delete "${u.name}"? This removes all their data.`)) return
  try { await api.adminDeleteUser(u.id); allUsers.value = allUsers.value.filter(x=>x.id!==u.id); showToast('Deleted','success') } catch { showToast('Failed','error') }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const showToast = (text, type='') => { clearTimeout(toastTimer); toast.value = { show:true, text, type }; toastTimer = setTimeout(() => toast.value.show = false, 3000) }
const fmtDate   = (d) => { if (!d) return '—'; try { return new Date(d).toLocaleDateString('en-PH',{month:'short',day:'numeric',year:'numeric'}) } catch { return d } }
const fmtPrice  = (v) => Number(v).toLocaleString('en-PH',{minimumFractionDigits:2})

onMounted(loadAll)
</script>

<style scoped>
.wm-admin { min-height:100vh; font-family:'Plus Jakarta Sans','Inter',sans-serif; }
.wm-admin-dash { display:grid; grid-template-columns:240px 1fr; min-height:100vh; }

/* ASIDE */
.wm-admin-aside { background:#003366; display:flex; flex-direction:column; }
.wm-admin-aside__brand { display:flex; align-items:center; gap:12px; padding:20px; border-bottom:1px solid rgba(255,255,255,0.08); }
.wm-admin-aside__mark { width:38px; height:38px; background:#FFD700; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.wm-admin-aside__name { font-size:0.95rem; font-weight:800; color:#fff; margin:0 0 2px; }
.wm-admin-aside__role { font-size:0.7rem; color:rgba(255,255,255,0.5); margin:0; text-transform:uppercase; letter-spacing:0.5px; }

.wm-admin-nav { padding:12px 10px; display:flex; flex-direction:column; gap:2px; flex:1; }
.wm-admin-nav__item { display:flex; align-items:center; gap:10px; padding:10px 12px; border:none; background:none; color:rgba(255,255,255,0.65); font-size:0.875rem; font-weight:500; cursor:pointer; border-radius:9px; transition:0.15s; text-align:left; font-family:inherit; width:100%; }
.wm-admin-nav__item:hover { background:rgba(255,255,255,0.1); color:#fff; }
.wm-admin-nav__item--active { background:#FFD700; color:#003366; font-weight:700; }
.wm-admin-nav__item--active:hover { background:#e6c200; }
.wm-admin-nav__pill { margin-left:auto; background:rgba(255,255,255,0.2); color:#fff; font-size:10px; font-weight:700; padding:2px 7px; border-radius:10px; }
.wm-admin-nav__item--active .wm-admin-nav__pill { background:rgba(0,51,102,0.2); color:#003366; }

.wm-admin-aside__footer { padding:16px; border-top:1px solid rgba(255,255,255,0.08); }
.wm-admin-site-link { font-size:0.78rem; color:rgba(255,255,255,0.45); text-decoration:none; display:flex; align-items:center; gap:5px; justify-content:center; }
.wm-admin-site-link:hover { color:rgba(255,255,255,0.8); }

/* MAIN */
.wm-admin-main { background:#f4f7fb; overflow-y:auto; }
.wm-admin-section { padding:28px 32px 48px; }
.wm-admin-section__head { margin-bottom:20px; }
.wm-admin-section__title { font-size:1.5rem; font-weight:800; color:#003366; margin:0 0 4px; }
.wm-admin-section__sub { font-size:0.875rem; color:#888; margin:0; }
.wm-admin-section__subtitle { font-size:1rem; font-weight:700; color:#003366; margin:0; }

.wm-admin-stat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }
.wm-stat-card { background:#fff; border:1px solid #e2eaf4; border-radius:14px; padding:18px 20px; display:flex; align-items:center; gap:14px; }
.wm-stat-card__icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.wm-stat-card__num { font-size:1.6rem; font-weight:800; color:#003366; line-height:1; display:block; }
.wm-stat-card__label { font-size:0.78rem; color:#888; display:block; }

.wm-recent-list { background:#fff; border:1px solid #e2eaf4; border-radius:14px; overflow:hidden; }
.wm-admin-empty { padding:1.5rem; text-align:center; color:#bbb; font-size:0.875rem; margin:0; }
.wm-recent-item { display:flex; align-items:center; gap:14px; padding:12px 16px; border-bottom:1px solid #f0f4f8; }
.wm-recent-item:last-child { border-bottom:none; }
.wm-recent-item__img { width:42px; height:42px; border-radius:8px; object-fit:cover; background:#f0f4f8; flex-shrink:0; }
.wm-recent-item__info { flex:1; min-width:0; }
.wm-recent-item__title { font-size:0.875rem; font-weight:600; color:#003366; margin:0 0 2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.wm-recent-item__meta { font-size:0.75rem; color:#888; margin:0; }
.wm-recent-item__price { font-size:0.9rem; font-weight:700; color:#003366; white-space:nowrap; }

.wm-admin-table-head { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:16px; flex-wrap:wrap; }
.wm-admin-count-badge { background:#e8f0fe; color:#003366; font-size:12px; font-weight:700; padding:3px 10px; border-radius:12px; }
.wm-admin-search-wrap { display:flex; align-items:center; gap:8px; background:#fff; border:1.5px solid #e0e8f4; border-radius:9px; padding:8px 14px; }
.wm-admin-search-wrap:focus-within { border-color:#003366; }
.wm-admin-search { border:none; outline:none; font-size:0.875rem; color:#333; background:transparent; width:220px; font-family:inherit; }

.wm-table-wrap { background:#fff; border:1px solid #e2eaf4; border-radius:14px; overflow:hidden; overflow-x:auto; }
.wm-table { width:100%; border-collapse:collapse; }
.wm-table thead tr { background:#f8faff; border-bottom:1px solid #e8edf4; }
.wm-table th { padding:11px 14px; text-align:left; font-size:11px; font-weight:700; color:#888; text-transform:uppercase; letter-spacing:0.06em; white-space:nowrap; }
.wm-table td { padding:11px 14px; font-size:0.875rem; color:#1a1a2e; border-bottom:1px solid #f0f4f8; vertical-align:middle; }
.wm-table tr:last-child td { border-bottom:none; }
.wm-table__row:hover td { background:#f8faff; }
.wm-table__empty { text-align:center; padding:36px; color:#bbb; font-size:0.875rem; }
.wm-table__id { color:#aaa; font-size:0.75rem; font-family:monospace; }
.wm-table__title { font-weight:600; max-width:200px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.wm-table__muted { color:#888; font-size:0.82rem; }
.wm-table__price { font-weight:700; color:#003366; white-space:nowrap; }
.wm-table__thumb { width:36px; height:36px; border-radius:7px; object-fit:cover; display:block; background:#f0f4f8; }

.wm-cat-tag { display:inline-block; padding:3px 9px; background:#e8f0fe; color:#003366; border-radius:6px; font-size:11px; font-weight:700; }
.wm-status-tag { display:inline-block; padding:3px 9px; border-radius:6px; font-size:11px; font-weight:700; }
.wm-status-tag--avail { background:#e8f8f0; color:#15803d; }
.wm-status-tag--sold  { background:#fee8e8; color:#b91c1c; }
.wm-read-tag { display:inline-block; padding:3px 9px; border-radius:6px; font-size:11px; font-weight:700; }
.wm-read-tag--read   { background:#e8f8f0; color:#15803d; }
.wm-read-tag--unread { background:#fef9e0; color:#854d0e; }
.wm-user-av { width:28px; height:28px; border-radius:50%; background:#003366; color:#FFD700; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:800; flex-shrink:0; }

.wm-del-btn { background:none; border:1px solid #fcc; color:#c0392b; padding:5px 10px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; transition:0.12s; font-family:inherit; }
.wm-del-btn:hover { background:#fff5f5; }

.wm-admin-toast { position:fixed; bottom:24px; right:24px; padding:12px 20px; border-radius:10px; font-size:0.875rem; font-weight:600; z-index:9999; box-shadow:0 8px 24px rgba(0,0,0,0.12); }
.wm-admin-toast--success { background:#fff; border:1.5px solid #16a34a; color:#15803d; }
.wm-admin-toast--error   { background:#fff; border:1.5px solid #c0392b; color:#c0392b; }
.wm-toast-enter-active,.wm-toast-leave-active { transition:all 0.2s; }
.wm-toast-enter-from,.wm-toast-leave-to { opacity:0; transform:translateY(8px); }

@media(max-width:768px) {
  .wm-admin-dash { grid-template-columns:1fr; }
  .wm-admin-aside { display:none; }
  .wm-admin-section { padding:20px 16px; }
}
</style>