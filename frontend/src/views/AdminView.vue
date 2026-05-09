<template>
  <div class="adm">
    <div class="adm-dash">

      <!-- SIDEBAR -->
      <aside class="adm-aside">
        <div class="adm-aside__brand">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="36" height="36" rx="9" fill="#FFD700"/>
            <path d="M10 15h16l-2 11H12L10 15z" fill="#003366" fill-opacity="0.2"/>
            <path d="M10 15h16l-2 11H12L10 15z" stroke="#003366" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M14 15v-2a4 4 0 018 0v2" stroke="#003366" stroke-width="1.6" stroke-linecap="round"/>
            <circle cx="15.5" cy="21" r="1" fill="#003366"/>
            <circle cx="20.5" cy="21" r="1" fill="#003366"/>
          </svg>
          <div>
            <p class="adm-aside__name">AdnuMarket</p>
            <p class="adm-aside__role">Admin Panel</p>
          </div>
        </div>
        <nav class="adm-nav">
          <button v-for="tab in tabs" :key="tab.key" class="adm-nav__item" :class="{'adm-nav__item--on': activeTab===tab.key}" @click="switchTab(tab.key)">
            <component :is="tab.icon" />
            {{ tab.label }}
            <span v-if="stats[tab.badge]" class="adm-nav__pill">{{ stats[tab.badge] }}</span>
          </button>
        </nav>
        <div class="adm-aside__foot">
          <router-link to="/" class="adm-back-link">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            Back to site
          </router-link>
        </div>
      </aside>

      <!-- MAIN -->
      <main class="adm-main">

        <!-- OVERVIEW -->
        <section v-if="activeTab==='overview'" class="adm-section">
          <div class="adm-section__head">
            <h1 class="adm-section__title">Overview</h1>
            <p class="adm-section__sub">AdnuMarket platform at a glance</p>
          </div>
          <div class="adm-stat-grid">
            <div class="adm-stat" v-for="s in statCards" :key="s.label">
              <div class="adm-stat__icon" :style="`background:${s.bg}`"><component :is="s.icon" :style="`color:${s.color}`" /></div>
              <div><span class="adm-stat__num">{{ stats[s.key]??'—' }}</span><span class="adm-stat__lbl">{{ s.label }}</span></div>
            </div>
          </div>
          <h2 class="adm-subtitle" style="margin-top:24px">Recent Listings</h2>
          <div class="adm-list">
            <p v-if="!recentProds.length" class="adm-empty">No listings yet.</p>
            <div v-for="p in recentProds.slice(0,8)" :key="p.id" class="adm-list-item">
              <img :src="p.image_url||''" class="adm-list-item__img" alt="" @error="e=>e.target.style.opacity='.1'"/>
              <div class="adm-list-item__info">
                <p class="adm-list-item__title">{{ p.title }}</p>
                <p class="adm-list-item__meta">{{ p.category }} · {{ p.seller_name||'—' }} · {{ fmtDate(p.created_at) }}</p>
              </div>
              <span class="adm-list-item__price">₱{{ fmtPrice(p.price) }}</span>
            </div>
          </div>
        </section>

        <!-- PRODUCTS -->
        <section v-if="activeTab==='products'" class="adm-section">
          <div class="adm-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="adm-section__title">Products</h1>
              <span class="adm-badge">{{ filteredProds.length }}</span>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <div class="adm-search-wrap">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input v-model="prodSearch" class="adm-search" placeholder="Search…"/>
              </div>
              <button class="adm-add-btn" @click="openAddProduct">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Add Product
              </button>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>Img</th><th>Title</th><th>Category</th><th>Price</th><th>Status</th><th>Seller</th><th>Posted</th><th></th></tr></thead>
              <tbody>
                <tr v-if="loadingProds"><td colspan="9" class="adm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredProds.length"><td colspan="9" class="adm-table__empty">No products</td></tr>
                <tr v-for="p in filteredProds" :key="p.id" class="adm-table__row">
                  <td class="adm-table__id">{{ p.id }}</td>
                  <td><img v-if="p.image_url" :src="p.image_url" class="adm-thumb" alt=""/></td>
                  <td class="adm-table__bold">{{ p.title }}</td>
                  <td><span class="adm-cat">{{ p.category }}</span></td>
                  <td class="adm-table__price">₱{{ fmtPrice(p.price) }}</td>
                  <td><span :class="['adm-status', p.status==='Available'?'adm-status--avail':'adm-status--sold']">{{ p.status }}</span></td>
                  <td class="adm-table__muted">{{ p.seller_name||'—' }}</td>
                  <td class="adm-table__muted">{{ fmtDate(p.created_at) }}</td>
                  <td><button class="adm-del" @click="delProd(p)">Delete</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- USERS -->
        <section v-if="activeTab==='users'" class="adm-section">
          <div class="adm-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="adm-section__title">Users</h1>
              <span class="adm-badge">{{ filteredUsers.length }}</span>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <div class="adm-search-wrap">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input v-model="userSearch" class="adm-search" placeholder="Search…"/>
              </div>
              <button class="adm-add-btn" @click="openAddUser">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Add User
              </button>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Student ID</th><th>Course</th><th>Year</th><th>Role</th><th></th></tr></thead>
              <tbody>
                <tr v-if="loadingUsers"><td colspan="8" class="adm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredUsers.length"><td colspan="8" class="adm-table__empty">No users</td></tr>
                <tr v-for="u in filteredUsers" :key="u.id" class="adm-table__row">
                  <td class="adm-table__id">{{ u.id }}</td>
                  <td>
                    <div style="display:flex;align-items:center;gap:8px">
                      <div class="adm-av">{{ u.name?.charAt(0)||'?' }}</div>
                      <span class="adm-table__bold">{{ u.name }}</span>
                    </div>
                  </td>
                  <td class="adm-table__muted">{{ u.email }}</td>
                  <td style="font-family:monospace;font-size:0.8rem">{{ u.student_id||'—' }}</td>
                  <td class="adm-table__muted">{{ u.course||'—' }}</td>
                  <td class="adm-table__muted">{{ u.year_level?'Year '+u.year_level:'—' }}</td>
                  <td>
                    <span :class="['adm-role', u.is_admin?'adm-role--admin':'adm-role--user']">
                      {{ u.is_admin ? 'Admin' : 'Student' }}
                    </span>
                  </td>
                  <td>
                    <div style="display:flex;gap:6px">
                      <button class="adm-edit-btn" @click="openEditUser(u)">Edit</button>
                      <button class="adm-del" @click="delUser(u)">Delete</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ORDERS -->
        <section v-if="activeTab==='orders'" class="adm-section">
          <div class="adm-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="adm-section__title">Orders</h1>
              <span class="adm-badge">{{ filteredOrders.length }}</span>
            </div>
            <div class="adm-search-wrap">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="orderSearch" class="adm-search" placeholder="Search…"/>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>Product</th><th>Buyer</th><th>Seller</th><th>Price</th><th>Payment</th><th>Status</th><th>Date</th></tr></thead>
              <tbody>
                <tr v-if="loadingOrders"><td colspan="8" class="adm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredOrders.length"><td colspan="8" class="adm-table__empty">No orders yet</td></tr>
                <tr v-for="o in filteredOrders" :key="o.id" class="adm-table__row">
                  <td class="adm-table__id">{{ o.id }}</td>
                  <td class="adm-table__bold">{{ o.product_title }}</td>
                  <td class="adm-table__muted">{{ o.buyer_name }}</td>
                  <td class="adm-table__muted">{{ o.seller_name }}</td>
                  <td class="adm-table__price">₱{{ fmtPrice(o.product_price) }}</td>
                  <td class="adm-table__muted">{{ o.payment_method }}</td>
                  <td><span class="adm-status adm-status--avail">{{ o.status }}</span></td>
                  <td class="adm-table__muted">{{ fmtDate(o.ordered_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- MESSAGES -->
        <section v-if="activeTab==='messages'" class="adm-section">
          <div class="adm-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="adm-section__title">Messages</h1>
              <span class="adm-badge">{{ filteredMsgs.length }}</span>
            </div>
            <div class="adm-search-wrap">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="msgSearch" class="adm-search" placeholder="Search…"/>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>From</th><th>To</th><th>Message</th><th>Sent</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-if="loadingMsgs"><td colspan="6" class="adm-table__empty">Loading…</td></tr>
                <tr v-else-if="!filteredMsgs.length"><td colspan="6" class="adm-table__empty">No messages</td></tr>
                <tr v-for="m in filteredMsgs" :key="m.id" class="adm-table__row">
                  <td class="adm-table__id">{{ m.id }}</td>
                  <td class="adm-table__bold">{{ m.sender_name }}</td>
                  <td class="adm-table__muted">{{ m.receiver_name }}</td>
                  <td style="max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#666">{{ m.message }}</td>
                  <td class="adm-table__muted">{{ fmtDate(m.sent_at) }}</td>
                  <td><span :class="['adm-read', m.is_read?'adm-read--read':'adm-read--unread']">{{ m.is_read?'Read':'Unread' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>

    <!-- ── ADD / EDIT USER MODAL ── -->
    <Transition name="modal">
      <div v-if="showUserModal" class="modal-backdrop" @click.self="showUserModal=false">
        <div class="modal-box">
          <button class="modal-close" @click="showUserModal=false">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          <h2 class="modal-title">{{ editingUser ? 'Edit User' : 'Add User' }}</h2>
          <div class="modal-fields">
            <div class="mf">
              <label>Full Name *</label>
              <input v-model="userForm.name" placeholder="e.g. Juan Dela Cruz" class="mf-input"/>
            </div>
            <div class="mf">
              <label>ADNU Email *</label>
              <input v-model="userForm.email" placeholder="e.g. jdelacruz@gbox.adnu.edu.ph" class="mf-input" :disabled="!!editingUser"/>
            </div>
            <div class="mf" v-if="!editingUser">
              <label>Password *</label>
              <input v-model="userForm.password" type="password" placeholder="Min 6 characters" class="mf-input"/>
            </div>
            <div class="mf">
              <label>Student ID *</label>
              <input v-model="userForm.student_id" placeholder="e.g. 2024-00001" class="mf-input"/>
            </div>
            <div class="mf">
              <label>Course</label>
              <input v-model="userForm.course" placeholder="e.g. BS Information Technology" class="mf-input"/>
            </div>
            <div class="mf">
              <label>Year Level</label>
              <select v-model="userForm.year_level" class="mf-select">
                <option value="">— Select —</option>
                <option v-for="y in ['1st Year','2nd Year','3rd Year','4th Year','Graduate']" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <div class="mf">
              <label>Department</label>
              <input v-model="userForm.department" placeholder="e.g. College of Computer Studies" class="mf-input"/>
            </div>
            <div class="mf">
              <label>Role</label>
              <div class="mf-toggle">
                <button type="button" :class="['mf-toggle-btn', !userForm.is_admin && 'mf-toggle-btn--on']" @click="userForm.is_admin=false">Student</button>
                <button type="button" :class="['mf-toggle-btn', userForm.is_admin && 'mf-toggle-btn--on']" @click="userForm.is_admin=true">Admin</button>
              </div>
            </div>
          </div>
          <button class="modal-submit" @click="saveUser" :disabled="savingUser">
            {{ savingUser ? 'Saving…' : (editingUser ? 'Save Changes' : 'Create User') }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- ── ADD PRODUCT MODAL ── -->
    <Transition name="modal">
      <div v-if="showProdModal" class="modal-backdrop" @click.self="showProdModal=false">
        <div class="modal-box">
          <button class="modal-close" @click="showProdModal=false">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          <h2 class="modal-title">Add Product</h2>
          <div class="modal-fields">
            <div class="mf">
              <label>Title *</label>
              <input v-model="prodForm.title" placeholder="Product title" class="mf-input"/>
            </div>
            <div class="mf">
              <label>Price (₱) *</label>
              <input v-model="prodForm.price" type="number" placeholder="e.g. 350" class="mf-input"/>
            </div>
            <div class="mf">
              <label>Category *</label>
              <select v-model="prodForm.category" class="mf-select">
                <option value="" disabled>Select category</option>
                <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="mf">
              <label>Seller User ID *</label>
              <input v-model="prodForm.seller_id" type="number" placeholder="User ID of seller" class="mf-input"/>
              <p style="font-size:0.72rem;color:#aaa;margin:4px 0 0">Check Users tab for IDs</p>
            </div>
            <div class="mf">
              <label>Description</label>
              <textarea v-model="prodForm.description" placeholder="Product description…" rows="3" class="mf-textarea"></textarea>
            </div>
            <div class="mf">
              <label>Tags <span style="font-weight:400;color:#aaa">(comma-separated)</span></label>
              <input v-model="prodForm.tags" placeholder="e.g. casio,calculator,math" class="mf-input"/>
            </div>
          </div>
          <button class="modal-submit" @click="saveProduct" :disabled="savingProd">
            {{ savingProd ? 'Posting…' : 'Post Product' }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['adm-toast', `adm-toast--${toast.type}`]">{{ toast.text }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import api from '@/services/api'

// ── Icons ─────────────────────────────────────────────────────────────────────
const IconGrid  = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8'},[h('rect',{x:3,y:3,width:7,height:7}),h('rect',{x:14,y:3,width:7,height:7}),h('rect',{x:14,y:14,width:7,height:7}),h('rect',{x:3,y:14,width:7,height:7})]) }
const IconBox   = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z'}),h('polyline',{points:'3.27 6.96 12 12.01 20.73 6.96'}),h('line',{x1:12,y1:'22.08',x2:12,y2:12})]) }
const IconUsers = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2'}),h('circle',{cx:9,cy:7,r:4}),h('path',{d:'M23 21v-2a4 4 0 00-3-3.87'}),h('path',{d:'M16 3.13a4 4 0 010 7.75'})]) }
const IconMsg   = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z'})]) }
const IconOrder = { render: () => h('svg',{width:16,height:16,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'},[h('path',{d:'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2'}),h('rect',{x:9,y:3,width:6,height:4,rx:2}),h('path',{d:'M9 12h6M9 16h4'})]) }

const tabs = [
  { key:'overview', label:'Overview',  icon:IconGrid,  badge:'' },
  { key:'products', label:'Products',  icon:IconBox,   badge:'products' },
  { key:'users',    label:'Users',     icon:IconUsers, badge:'users' },
  { key:'orders',   label:'Orders',    icon:IconOrder, badge:'orders' },
  { key:'messages', label:'Messages',  icon:IconMsg,   badge:'' },
]
const statCards = [
  { key:'users',    label:'Users',    icon:IconUsers, bg:'#e8f0fe', color:'#003366' },
  { key:'products', label:'Listings', icon:IconBox,   bg:'#e8f8f0', color:'#15803d' },
  { key:'orders',   label:'Orders',   icon:IconOrder, bg:'#fff8e0', color:'#854d0e' },
  { key:'messages', label:'Messages', icon:IconMsg,   bg:'#fce8ff', color:'#7c3aed' },
]

const categories = ['Textbooks','Electronics','Dorm Items','Uniforms','School Supplies','Food','Services','Others']

// ── State ─────────────────────────────────────────────────────────────────────
const activeTab = ref('overview')
const stats     = ref({})
const recentProds = ref([])
const allProds  = ref([]), allUsers  = ref([]), allMsgs  = ref([]), allOrders = ref([])
const loadingProds = ref(false), loadingUsers = ref(false), loadingMsgs = ref(false), loadingOrders = ref(false)
const prodSearch = ref(''), userSearch = ref(''), msgSearch = ref(''), orderSearch = ref('')
const toast = ref({ show:false, text:'', type:'' }); let toastTimer = null

// User modal
const showUserModal = ref(false)
const editingUser   = ref(null)
const savingUser    = ref(false)
const userForm      = ref({ name:'', email:'', password:'', student_id:'', course:'', year_level:'', department:'', is_admin:false })

// Product modal
const showProdModal = ref(false)
const savingProd    = ref(false)
const prodForm      = ref({ title:'', price:'', category:'', seller_id:'', description:'', tags:'' })

// ── Computed ──────────────────────────────────────────────────────────────────
const filteredProds  = computed(() => { const q=prodSearch.value.toLowerCase();  return q?allProds.value.filter(p=>`${p.title} ${p.seller_name} ${p.category}`.toLowerCase().includes(q)):allProds.value })
const filteredUsers  = computed(() => { const q=userSearch.value.toLowerCase();  return q?allUsers.value.filter(u=>`${u.name} ${u.email} ${u.student_id}`.toLowerCase().includes(q)):allUsers.value })
const filteredMsgs   = computed(() => { const q=msgSearch.value.toLowerCase();   return q?allMsgs.value.filter(m=>`${m.message} ${m.sender_name} ${m.receiver_name}`.toLowerCase().includes(q)):allMsgs.value })
const filteredOrders = computed(() => { const q=orderSearch.value.toLowerCase(); return q?allOrders.value.filter(o=>`${o.product_title} ${o.buyer_name} ${o.seller_name}`.toLowerCase().includes(q)):allOrders.value })

// ── Load ──────────────────────────────────────────────────────────────────────
const loadAll = async () => {
  try { stats.value = (await api.adminStats()).data } catch {}
  try { recentProds.value = (await api.adminProducts()).data } catch {}
}
const switchTab = (k) => {
  activeTab.value = k
  if (k==='products' && !allProds.value.length)  loadProds()
  if (k==='users'    && !allUsers.value.length)   loadUsers()
  if (k==='messages' && !allMsgs.value.length)    loadMsgsTab()
  if (k==='orders'   && !allOrders.value.length)  loadOrders()
}
const loadProds   = async () => { loadingProds.value=true;  try { allProds.value  = (await api.adminProducts()).data } catch { showToast('Failed','error') } finally { loadingProds.value=false } }
const loadUsers   = async () => { loadingUsers.value=true;  try { allUsers.value  = (await api.adminUsers()).data    } catch { showToast('Failed','error') } finally { loadingUsers.value=false } }
const loadMsgsTab = async () => { loadingMsgs.value=true;   try { allMsgs.value   = (await api.adminMessages()).data } catch { showToast('Failed','error') } finally { loadingMsgs.value=false } }
const loadOrders  = async () => { loadingOrders.value=true; try { allOrders.value = (await api.adminOrders()).data   } catch { showToast('Failed','error') } finally { loadingOrders.value=false } }

// ── Delete ────────────────────────────────────────────────────────────────────
const delProd = async (p) => { if (!confirm(`Delete "${p.title}"?`)) return; try { await api.adminDeleteProduct(p.id); allProds.value=allProds.value.filter(x=>x.id!==p.id); recentProds.value=recentProds.value.filter(x=>x.id!==p.id); showToast('Product deleted','success') } catch { showToast('Failed','error') } }
const delUser = async (u) => { if (!confirm(`Delete "${u.name}"? All their data will be removed.`)) return; try { await api.adminDeleteUser(u.id); allUsers.value=allUsers.value.filter(x=>x.id!==u.id); showToast('User deleted','success') } catch { showToast('Failed','error') } }

// ── Add / Edit User ───────────────────────────────────────────────────────────
const openAddUser  = () => { editingUser.value=null; userForm.value={name:'',email:'',password:'',student_id:'',course:'',year_level:'',department:'',is_admin:false}; showUserModal.value=true }
const openEditUser = (u) => { editingUser.value=u; userForm.value={name:u.name,email:u.email,password:'',student_id:u.student_id||'',course:u.course||'',year_level:u.year_level||'',department:u.department||'',is_admin:!!u.is_admin}; showUserModal.value=true }

const saveUser = async () => {
  if (!userForm.value.name || !userForm.value.email) { showToast('Name and email required','error'); return }
  if (!editingUser.value && !userForm.value.password) { showToast('Password required','error'); return }
  savingUser.value = true
  try {
    if (editingUser.value) {
      await api.adminUpdateUser(editingUser.value.id, userForm.value)
      // Update locally
      const i = allUsers.value.findIndex(x=>x.id===editingUser.value.id)
      if (i>=0) allUsers.value[i] = { ...allUsers.value[i], ...userForm.value }
      showToast('User updated','success')
    } else {
      await api.adminCreateUser(userForm.value)
      await loadUsers()
      showToast('User created','success')
    }
    showUserModal.value = false
  } catch (e) {
    showToast(e.response?.data?.message || 'Failed to save','error')
  } finally { savingUser.value = false }
}

// ── Add Product ───────────────────────────────────────────────────────────────
const openAddProduct = () => { prodForm.value={title:'',price:'',category:'',seller_id:'',description:'',tags:''}; showProdModal.value=true }

const saveProduct = async () => {
  if (!prodForm.value.title || !prodForm.value.price || !prodForm.value.category || !prodForm.value.seller_id) {
    showToast('Title, price, category and seller ID required','error'); return
  }
  savingProd.value = true
  try {
    await api.adminCreateProduct(prodForm.value)
    await loadProds()
    showToast('Product added','success')
    showProdModal.value = false
  } catch (e) {
    showToast(e.response?.data?.message || 'Failed to add product','error')
  } finally { savingProd.value = false }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const showToast = (text, type='') => { clearTimeout(toastTimer); toast.value={show:true,text,type}; toastTimer=setTimeout(()=>toast.value.show=false,3000) }
const fmtDate   = (d) => { if(!d) return '—'; try { return new Date(d).toLocaleDateString('en-PH',{month:'short',day:'numeric',year:'numeric'}) } catch { return d } }
const fmtPrice  = (v) => Number(v).toLocaleString('en-PH',{minimumFractionDigits:2})

onMounted(loadAll)
</script>

<style scoped>
.adm { min-height:100vh; font-family:'Plus Jakarta Sans','Inter',sans-serif; }
.adm-dash { display:grid; grid-template-columns:240px 1fr; min-height:100vh; }

/* ASIDE */
.adm-aside { background:#003366; display:flex; flex-direction:column; }
.adm-aside__brand { display:flex; align-items:center; gap:12px; padding:20px; border-bottom:1px solid rgba(255,255,255,0.08); }
.adm-aside__name { font-size:0.95rem; font-weight:800; color:#fff; margin:0 0 2px; }
.adm-aside__role { font-size:0.7rem; color:rgba(255,255,255,0.5); margin:0; text-transform:uppercase; letter-spacing:0.5px; }

.adm-nav { padding:12px 10px; display:flex; flex-direction:column; gap:2px; flex:1; }
.adm-nav__item { display:flex; align-items:center; gap:10px; padding:10px 12px; border:none; background:none; color:rgba(255,255,255,0.65); font-size:0.875rem; font-weight:500; cursor:pointer; border-radius:9px; transition:0.15s; text-align:left; font-family:inherit; width:100%; }
.adm-nav__item:hover { background:rgba(255,255,255,0.1); color:#fff; }
.adm-nav__item--on { background:#FFD700; color:#003366; font-weight:700; }
.adm-nav__item--on:hover { background:#e6c200; }
.adm-nav__pill { margin-left:auto; background:rgba(255,255,255,0.2); color:#fff; font-size:10px; font-weight:700; padding:2px 7px; border-radius:10px; }
.adm-nav__item--on .adm-nav__pill { background:rgba(0,51,102,0.2); color:#003366; }

.adm-aside__foot { padding:16px; border-top:1px solid rgba(255,255,255,0.08); }
.adm-back-link { font-size:0.78rem; color:rgba(255,255,255,0.45); text-decoration:none; display:flex; align-items:center; gap:5px; justify-content:center; }
.adm-back-link:hover { color:rgba(255,255,255,0.8); }

/* MAIN */
.adm-main { background:#f4f7fb; overflow-y:auto; }
.adm-section { padding:28px 32px 48px; }
.adm-section__head { margin-bottom:20px; }
.adm-section__title { font-size:1.5rem; font-weight:800; color:#003366; margin:0 0 4px; }
.adm-section__sub   { font-size:0.875rem; color:#888; margin:0; }
.adm-subtitle { font-size:1rem; font-weight:700; color:#003366; margin:0; }

.adm-stat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }
.adm-stat { background:#fff; border:1px solid #e2eaf4; border-radius:14px; padding:18px 20px; display:flex; align-items:center; gap:14px; }
.adm-stat__icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.adm-stat__num { font-size:1.6rem; font-weight:800; color:#003366; line-height:1; display:block; }
.adm-stat__lbl { font-size:0.78rem; color:#888; display:block; }

.adm-list { background:#fff; border:1px solid #e2eaf4; border-radius:14px; overflow:hidden; margin-top:12px; }
.adm-empty { padding:1.5rem; text-align:center; color:#bbb; font-size:0.875rem; margin:0; }
.adm-list-item { display:flex; align-items:center; gap:14px; padding:12px 16px; border-bottom:1px solid #f0f4f8; }
.adm-list-item:last-child { border-bottom:none; }
.adm-list-item__img { width:42px; height:42px; border-radius:8px; object-fit:cover; background:#f0f4f8; flex-shrink:0; }
.adm-list-item__info { flex:1; min-width:0; }
.adm-list-item__title { font-size:0.875rem; font-weight:600; color:#003366; margin:0 0 2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.adm-list-item__meta  { font-size:0.75rem; color:#888; margin:0; }
.adm-list-item__price { font-size:0.9rem; font-weight:700; color:#003366; white-space:nowrap; }

.adm-table-head { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:16px; flex-wrap:wrap; }
.adm-badge { background:#e8f0fe; color:#003366; font-size:12px; font-weight:700; padding:3px 10px; border-radius:12px; }
.adm-search-wrap { display:flex; align-items:center; gap:8px; background:#fff; border:1.5px solid #e0e8f4; border-radius:9px; padding:8px 14px; }
.adm-search-wrap:focus-within { border-color:#003366; }
.adm-search { border:none; outline:none; font-size:0.875rem; color:#333; background:transparent; width:200px; font-family:inherit; }
.adm-add-btn { display:flex; align-items:center; gap:6px; background:#003366; color:#FFD700; border:none; padding:9px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; cursor:pointer; font-family:inherit; transition:0.15s; white-space:nowrap; }
.adm-add-btn:hover { background:#002244; }

.adm-table-wrap { background:#fff; border:1px solid #e2eaf4; border-radius:14px; overflow:hidden; overflow-x:auto; }
.adm-table { width:100%; border-collapse:collapse; }
.adm-table thead tr { background:#f8faff; border-bottom:1px solid #e8edf4; }
.adm-table th { padding:11px 14px; text-align:left; font-size:11px; font-weight:700; color:#888; text-transform:uppercase; letter-spacing:0.06em; white-space:nowrap; }
.adm-table td { padding:11px 14px; font-size:0.875rem; color:#1a1a2e; border-bottom:1px solid #f0f4f8; vertical-align:middle; }
.adm-table tr:last-child td { border-bottom:none; }
.adm-table__row:hover td { background:#f8faff; }
.adm-table__empty { text-align:center; padding:36px; color:#bbb; font-size:0.875rem; }
.adm-table__id    { color:#aaa; font-size:0.75rem; font-family:monospace; }
.adm-table__bold  { font-weight:600; max-width:200px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.adm-table__muted { color:#888; font-size:0.82rem; }
.adm-table__price { font-weight:700; color:#003366; white-space:nowrap; }
.adm-thumb { width:36px; height:36px; border-radius:7px; object-fit:cover; display:block; background:#f0f4f8; }

.adm-cat   { display:inline-block; padding:3px 9px; background:#e8f0fe; color:#003366; border-radius:6px; font-size:11px; font-weight:700; }
.adm-status { display:inline-block; padding:3px 9px; border-radius:6px; font-size:11px; font-weight:700; }
.adm-status--avail { background:#e8f8f0; color:#15803d; }
.adm-status--sold  { background:#fee8e8; color:#b91c1c; }
.adm-read { display:inline-block; padding:3px 9px; border-radius:6px; font-size:11px; font-weight:700; }
.adm-read--read   { background:#e8f8f0; color:#15803d; }
.adm-read--unread { background:#fef9e0; color:#854d0e; }

.adm-role { display:inline-block; padding:3px 9px; border-radius:6px; font-size:11px; font-weight:700; }
.adm-role--admin { background:#fce8ff; color:#7c3aed; }
.adm-role--user  { background:#e8f0fe; color:#003366; }

.adm-av { width:28px; height:28px; border-radius:50%; background:#003366; color:#FFD700; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:800; flex-shrink:0; }

.adm-del      { background:none; border:1px solid #fcc; color:#c0392b; padding:5px 10px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; transition:0.12s; font-family:inherit; white-space:nowrap; }
.adm-del:hover{ background:#fff5f5; }
.adm-edit-btn { background:none; border:1px solid #d0dbe8; color:#003366; padding:5px 10px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; transition:0.12s; font-family:inherit; white-space:nowrap; }
.adm-edit-btn:hover { background:#eef3ff; }

/* MODALS */
.modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.5); backdrop-filter:blur(3px); z-index:1000; display:flex; align-items:center; justify-content:center; padding:1rem; }
.modal-box { background:#fff; border-radius:18px; width:100%; max-width:480px; padding:1.75rem; position:relative; max-height:90vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.2); }
.modal-close { position:absolute; top:16px; right:16px; width:32px; height:32px; background:#f0f4f8; border:none; border-radius:8px; color:#666; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:0.15s; }
.modal-close:hover { background:#e74c3c; color:#fff; }
.modal-title { font-size:1.15rem; font-weight:800; color:#003366; margin:0 0 1.25rem; }

.modal-fields { display:flex; flex-direction:column; gap:12px; margin-bottom:1.25rem; }
.mf { display:flex; flex-direction:column; gap:5px; }
.mf label { font-size:0.75rem; font-weight:700; color:#003366; text-transform:uppercase; letter-spacing:0.4px; }
.mf-input,.mf-select,.mf-textarea { padding:9px 12px; border:1.5px solid #e0e8f4; border-radius:8px; font-size:0.875rem; color:#1a1a2e; outline:none; font-family:inherit; background:#fafcff; transition:0.15s; }
.mf-input:focus,.mf-select:focus,.mf-textarea:focus { border-color:#003366; }
.mf-input:disabled { background:#f0f0f0; color:#aaa; cursor:not-allowed; }
.mf-textarea { resize:vertical; }

.mf-toggle { display:flex; gap:8px; }
.mf-toggle-btn { flex:1; padding:9px; border:1.5px solid #e5e7eb; border-radius:8px; background:#f8fafc; font-size:0.82rem; font-weight:700; color:#666; cursor:pointer; font-family:inherit; transition:0.15s; }
.mf-toggle-btn:hover { border-color:#003366; color:#003366; }
.mf-toggle-btn--on { background:#003366; color:#FFD700; border-color:#003366; }

.modal-submit { width:100%; background:#003366; color:#FFD700; border:none; padding:13px; border-radius:10px; font-weight:800; font-size:0.95rem; cursor:pointer; font-family:inherit; transition:0.15s; }
.modal-submit:hover:not(:disabled) { background:#002244; }
.modal-submit:disabled { opacity:0.6; cursor:not-allowed; }

/* TOAST */
.adm-toast { position:fixed; bottom:24px; right:24px; padding:12px 20px; border-radius:10px; font-size:0.875rem; font-weight:600; z-index:9999; box-shadow:0 8px 24px rgba(0,0,0,0.12); }
.adm-toast--success { background:#fff; border:1.5px solid #16a34a; color:#15803d; }
.adm-toast--error   { background:#fff; border:1.5px solid #c0392b; color:#c0392b; }
.toast-enter-active,.toast-leave-active { transition:all 0.2s; }
.toast-enter-from,.toast-leave-to { opacity:0; transform:translateY(8px); }
.modal-enter-active,.modal-leave-active { transition:all 0.25s ease; }
.modal-enter-from,.modal-leave-to { opacity:0; transform:scale(0.95); }

@media(max-width:768px) {
  .adm-dash { grid-template-columns:1fr; }
  .adm-aside { display:none; }
  .adm-section { padding:20px 16px; }
}
</style>