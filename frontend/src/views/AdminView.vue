<template>
  <div class="adm">
    <div class="adm-dash">

      <!-- SIDEBAR -->
      <aside class="adm-aside">
        <div class="adm-aside__brand">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
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
          <button
            v-for="tab in tabs" :key="tab.key"
            class="adm-nav__item"
            :class="{ 'adm-nav__item--on': activeTab === tab.key }"
            @click="switchTab(tab.key)"
          >
            <component :is="tab.icon"/>
            {{ tab.label }}
            <span v-if="navBadge(tab)" class="adm-nav__pill">{{ navBadge(tab) }}</span>
          </button>
        </nav>

        <div class="adm-aside__foot">
          <router-link to="/" class="adm-back-link">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
            Back to site
          </router-link>
        </div>
      </aside>

      <!-- MAIN -->
      <main class="adm-main">

        <!-- OVERVIEW -->
        <section v-if="activeTab === 'overview'" class="adm-section">
          <div class="adm-section__head">
            <h1 class="adm-section__title">Overview</h1>
            <p class="adm-section__sub">AdnuMarket platform at a glance</p>
          </div>
          <div class="adm-stat-grid">
            <div class="adm-stat" v-for="s in statCards" :key="s.label">
              <div class="adm-stat__icon" :style="`background:${s.bg}`">
                <component :is="s.icon" :style="`color:${s.color}`"/>
              </div>
              <div>
                <span class="adm-stat__num">{{ stats[s.key] ?? '—' }}</span>
                <span class="adm-stat__lbl">{{ s.label }}</span>
              </div>
            </div>
          </div>

          <h2 class="adm-subtitle" style="margin-top:28px;margin-bottom:12px">Recent Listings</h2>
          <div class="adm-list">
            <p v-if="!recentProds.length" class="adm-empty">No listings yet.</p>
            <div v-for="p in recentProds.slice(0, 8)" :key="p.id" class="adm-list-item">
              <img v-if="p.image_url" :src="p.image_url" class="adm-list-item__img" alt=""
                   @error="e => e.target.style.display='none'"/>
              <div v-else class="adm-list-item__img adm-list-item__img--empty"></div>
              <div class="adm-list-item__info">
                <p class="adm-list-item__title">{{ p.title }}</p>
                <p class="adm-list-item__meta">{{ p.category }} · {{ p.seller_name || '—' }} · {{ fmtDate(p.created_at) }}</p>
              </div>
              <span class="adm-list-item__price">₱{{ fmtPrice(p.price) }}</span>
            </div>
          </div>
        </section>

        <!-- PRODUCTS -->
        <section v-if="activeTab === 'products'" class="adm-section">
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
              <button class="adm-icon-btn" @click="loadProds" title="Refresh">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
              </button>
              <button class="adm-add-btn" @click="openAddProduct">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Add Product
              </button>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>IMG</th><th>TITLE</th><th>CATEGORY</th><th>PRICE</th><th>STATUS</th><th>SELLER</th><th>POSTED</th><th></th></tr></thead>
              <tbody>
                <tr v-if="loadingProds"><td colspan="9" class="adm-table__empty">
                  <span class="adm-spinner"></span> Loading…
                </td></tr>
                <tr v-else-if="!filteredProds.length"><td colspan="9" class="adm-table__empty">No products found</td></tr>
                <tr v-for="p in filteredProds" :key="p.id" class="adm-table__row">
                  <td class="adm-table__id">{{ p.id }}</td>
                  <td>
                    <img v-if="p.image_url" :src="p.image_url" class="adm-thumb" alt=""
                         @error="e => e.target.style.display='none'"/>
                    <div v-else class="adm-thumb adm-thumb--empty"></div>
                  </td>
                  <td class="adm-table__bold">{{ p.title }}</td>
                  <td><span class="adm-cat-tag">{{ p.category }}</span></td>
                  <td class="adm-table__price">₱{{ fmtPrice(p.price) }}</td>
                  <td><span :class="['adm-status', p.status === 'Available' ? 'adm-status--avail' : 'adm-status--sold']">{{ p.status }}</span></td>
                  <td class="adm-table__muted">{{ p.seller_name || '—' }}</td>
                  <td class="adm-table__muted">{{ fmtDate(p.created_at) }}</td>
                  <td>
                    <div style="display:flex;gap:6px">
                      <button class="adm-edit-btn" @click="openEditProduct(p)">Edit</button>
                      <button class="adm-del-btn"  @click="confirmDelete('product', p)">Delete</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- USERS -->
        <section v-if="activeTab === 'users'" class="adm-section">
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
              <button class="adm-icon-btn" @click="loadUsers" title="Refresh">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
              </button>
              <button class="adm-add-btn" @click="openAddUser">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Add User
              </button>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>NAME</th><th>EMAIL</th><th>STUDENT ID</th><th>COURSE</th><th>YEAR</th><th>ROLE</th><th>STATUS</th><th></th></tr></thead>
              <tbody>
                <tr v-if="loadingUsers"><td colspan="9" class="adm-table__empty">
                  <span class="adm-spinner"></span> Loading…
                </td></tr>
                <tr v-else-if="!filteredUsers.length"><td colspan="9" class="adm-table__empty">No users found</td></tr>
                <tr v-for="u in filteredUsers" :key="u.id" class="adm-table__row">
                  <td class="adm-table__id">{{ u.id }}</td>
                  <td>
                    <div style="display:flex;align-items:center;gap:8px">
                      <div class="adm-av">{{ u.name?.charAt(0) || '?' }}</div>
                      <span class="adm-table__bold">{{ u.name }}</span>
                    </div>
                  </td>
                  <td class="adm-table__muted">{{ u.email }}</td>
                  <td style="font-family:monospace;font-size:0.8rem">{{ u.student_id || '—' }}</td>
                  <td class="adm-table__muted">{{ u.course || '—' }}</td>
                  <td class="adm-table__muted">{{ u.year_level ? 'Year ' + u.year_level : '—' }}</td>
                  <td><span :class="['adm-role', u.is_admin ? 'adm-role--admin' : 'adm-role--user']">{{ u.is_admin ? 'Admin' : 'Student' }}</span></td>
                  <td>
                    <span v-if="u.is_blocked" class="adm-status adm-status--sold">Blocked</span>
                    <span v-else class="adm-status adm-status--avail">Active</span>
                  </td>
                  <td>
                    <div style="display:flex;gap:6px;flex-wrap:wrap">
                      <button class="adm-edit-btn"  @click="openEditUser(u)">Edit</button>
                      <button class="adm-block-btn" @click="u.is_blocked ? unblockUser(u) : openBlockModal(u)">
                        {{ u.is_blocked ? 'Unblock' : 'Block' }}
                      </button>
                      <button class="adm-admin-btn" @click="toggleAdmin(u)">
                        {{ u.is_admin ? 'Remove Admin' : 'Make Admin' }}
                      </button>
                      <button class="adm-del-btn" @click="confirmDelete('user', u)">Delete</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ORDERS -->
        <section v-if="activeTab === 'orders'" class="adm-section">
          <div class="adm-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="adm-section__title">Orders</h1>
              <span class="adm-badge">{{ filteredOrders.length }}</span>
            </div>
            <div style="display:flex;gap:10px">
              <div class="adm-search-wrap">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input v-model="orderSearch" class="adm-search" placeholder="Search…"/>
              </div>
              <button class="adm-icon-btn" @click="loadOrdersTab" title="Refresh">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
              </button>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>PRODUCT</th><th>BUYER</th><th>SELLER</th><th>PRICE</th><th>PAYMENT</th><th>STATUS</th><th>DATE</th></tr></thead>
              <tbody>
                <tr v-if="loadingOrders"><td colspan="8" class="adm-table__empty">
                  <span class="adm-spinner"></span> Loading…
                </td></tr>
                <tr v-else-if="!filteredOrders.length"><td colspan="8" class="adm-table__empty">No orders yet</td></tr>
                <tr v-for="o in filteredOrders" :key="o.id" class="adm-table__row">
                  <td class="adm-table__id">{{ o.id }}</td>
                  <td class="adm-table__bold">{{ o.product_title }}</td>
                  <td class="adm-table__muted">{{ o.buyer_name }}</td>
                  <td class="adm-table__muted">{{ o.seller_name }}</td>
                  <td class="adm-table__price">₱{{ fmtPrice(o.product_price) }}</td>
                  <td class="adm-table__muted">{{ o.payment_method }}</td>
                  <td><span :class="['adm-status', orderStatusClass(o.status)]">{{ o.status }}</span></td>
                  <td class="adm-table__muted">{{ fmtDate(o.ordered_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- MESSAGES -->
        <section v-if="activeTab === 'messages'" class="adm-section">
          <div class="adm-table-head">
            <div style="display:flex;align-items:center;gap:10px">
              <h1 class="adm-section__title">Messages</h1>
              <span class="adm-badge">{{ filteredMsgs.length }}</span>
            </div>
            <div style="display:flex;gap:10px">
              <div class="adm-search-wrap">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input v-model="msgSearch" class="adm-search" placeholder="Search…"/>
              </div>
              <button class="adm-icon-btn" @click="loadMsgsTab" title="Refresh">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
              </button>
            </div>
          </div>
          <div class="adm-table-wrap">
            <table class="adm-table">
              <thead><tr><th>ID</th><th>FROM</th><th>TO</th><th>MESSAGE</th><th>SENT</th><th>STATUS</th></tr></thead>
              <tbody>
                <tr v-if="loadingMsgs"><td colspan="6" class="adm-table__empty">
                  <span class="adm-spinner"></span> Loading…
                </td></tr>
                <tr v-else-if="!filteredMsgs.length"><td colspan="6" class="adm-table__empty">No messages</td></tr>
                <tr v-for="m in filteredMsgs" :key="m.id" class="adm-table__row">
                  <td class="adm-table__id">{{ m.id }}</td>
                  <td class="adm-table__bold">{{ m.sender_name }}</td>
                  <td class="adm-table__muted">{{ m.receiver_name }}</td>
                  <td class="adm-msg-preview">{{ m.message }}</td>
                  <td class="adm-table__muted">{{ fmtDate(m.sent_at) }}</td>
                  <td><span :class="['adm-read', m.is_read ? 'adm-read--read' : 'adm-read--unread']">{{ m.is_read ? 'Read' : 'Unread' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>

    <!-- ══ PRODUCT MODAL ══════════════════════════════════════════════════ -->
    <Transition name="modal">
      <div v-if="showProdModal" class="modal-backdrop" @click.self="closeProdModal">
        <div class="modal-box">
          <button class="modal-close" @click="closeProdModal">×</button>
          <h2 class="modal-title">{{ editingProd ? 'Edit Product' : 'Add Product' }}</h2>

          <div class="modal-fields">
            <div class="mf">
              <label>Product Images <span class="mf-hint">up to 5</span></label>
              <div class="img-upload-area" @click="triggerProdFile" @dragover.prevent @drop.prevent="handleProdDrop">
                <div v-if="!prodPreviews.length" class="img-upload-placeholder">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.5"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/></svg>
                  <p>Click or drag images here</p>
                  <span>JPG, PNG, WEBP — max 5MB each</span>
                </div>
                <div v-else class="img-preview-grid">
                  <div v-for="(prev, i) in prodPreviews" :key="i" class="img-preview-item">
                    <img :src="prev" class="img-preview-thumb"/>
                    <button class="img-preview-remove" @click.stop="removeProdImage(i)">×</button>
                    <span v-if="i === 0" class="img-preview-main">Main</span>
                  </div>
                  <div v-if="prodPreviews.length < 5" class="img-add-more" @click.stop="triggerProdFile">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    <span>Add</span>
                  </div>
                </div>
              </div>
              <input ref="prodFileRef" type="file" accept="image/*" multiple style="display:none" @change="handleProdFileChange"/>
            </div>

            <div class="mf"><label>Title *</label><input v-model="prodForm.title" class="mf-input" placeholder="Product title"/></div>
            <div class="mf"><label>Price (₱) *</label><input v-model="prodForm.price" type="number" class="mf-input" placeholder="e.g. 350" min="0"/></div>
            <div class="mf">
              <label>Category *</label>
              <select v-model="prodForm.category" class="mf-select">
                <option value="" disabled>Select category</option>
                <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="mf" v-if="!editingProd">
              <label>Seller User ID *</label>
              <input v-model="prodForm.seller_id" type="number" class="mf-input" placeholder="Check Users tab for ID"/>
              <p class="mf-hint-text">The user ID of the seller (from Users tab)</p>
            </div>
            <div class="mf"><label>Description</label><textarea v-model="prodForm.description" rows="3" class="mf-textarea" placeholder="Product condition, details…"></textarea></div>
            <div class="mf">
              <label>Tags <span class="mf-hint">(comma-separated)</span></label>
              <input v-model="prodForm.tags" class="mf-input" placeholder="e.g. casio,calculator,math"/>
            </div>
          </div>

          <button class="modal-submit" @click="saveProd" :disabled="savingProd">
            <svg v-if="!savingProd" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            <span class="adm-spinner adm-spinner--sm" v-else></span>
            {{ savingProd ? 'Saving…' : (editingProd ? 'Save Changes' : 'Post Product') }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- ══ USER MODAL ══════════════════════════════════════════════════════ -->
    <Transition name="modal">
      <div v-if="showUserModal" class="modal-backdrop" @click.self="showUserModal = false">
        <div class="modal-box">
          <button class="modal-close" @click="showUserModal = false">×</button>
          <h2 class="modal-title">{{ editingUser ? 'Edit User' : 'Add User' }}</h2>
          <div class="modal-fields">
            <div class="mf"><label>Full Name *</label><input v-model="userForm.name" class="mf-input" placeholder="e.g. Juan Dela Cruz"/></div>
            <div class="mf"><label>ADNU Email *</label><input v-model="userForm.email" class="mf-input" placeholder="@gbox.adnu.edu.ph" :disabled="!!editingUser"/></div>
            <div class="mf" v-if="!editingUser"><label>Password *</label><input v-model="userForm.password" type="password" class="mf-input" placeholder="Min 6 characters"/></div>
            <div class="mf"><label>Student ID</label><input v-model="userForm.student_id" class="mf-input" placeholder="e.g. 2024-00001"/></div>
            <div class="mf"><label>Course</label><input v-model="userForm.course" class="mf-input" placeholder="e.g. BS Information Technology"/></div>
            <div class="mf">
              <label>Year Level</label>
              <select v-model="userForm.year_level" class="mf-select">
                <option value="">— Select —</option>
                <option v-for="y in ['1st Year','2nd Year','3rd Year','4th Year','Graduate']" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <div class="mf"><label>Department</label><input v-model="userForm.department" class="mf-input" placeholder="e.g. College of Computer Studies"/></div>
          </div>
          <button class="modal-submit" @click="saveUser" :disabled="savingUser">
            {{ savingUser ? 'Saving…' : (editingUser ? 'Save Changes' : 'Create User') }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- ══ BLOCK USER MODAL ════════════════════════════════════════════════ -->
    <!-- FIX: replaced browser prompt() with a proper modal -->
    <Transition name="modal">
      <div v-if="showBlockModal" class="modal-backdrop" @click.self="showBlockModal = false">
        <div class="modal-box" style="max-width:380px">
          <button class="modal-close" @click="showBlockModal = false">×</button>
          <h2 class="modal-title">Block User</h2>
          <p class="block-modal__name">{{ blockTarget?.name }}</p>

          <div class="modal-fields">
            <div class="mf">
              <label>Block Duration</label>
              <div class="block-options">
                <label v-for="opt in blockOptions" :key="opt.value" class="block-option"
                  :class="{ 'block-option--on': blockForm.preset === opt.value }"
                  @click="selectBlockPreset(opt)">
                  <span class="block-option__label">{{ opt.label }}</span>
                  <span class="block-option__desc">{{ opt.desc }}</span>
                </label>
              </div>
            </div>

            <div class="mf" v-if="blockForm.preset === 'custom'">
              <label>Custom Duration (hours)</label>
              <input v-model.number="blockForm.customHours" type="number" min="1" max="8760" class="mf-input" placeholder="e.g. 48"/>
            </div>
          </div>

          <div class="block-modal__reason" style="margin-bottom:12px">
            <label class="mf" style="gap:5px">
              <span style="font-size:0.75rem;font-weight:700;color:#003366;text-transform:uppercase;letter-spacing:0.4px">Reason <span style="color:#aaa;font-weight:400;text-transform:none">(optional)</span></span>
              <textarea v-model="blockForm.reason" rows="2" class="mf-textarea" placeholder="Why is this user being blocked?"></textarea>
            </label>
          </div>

          <button class="modal-submit modal-submit--danger" @click="executeBlock" :disabled="blockingUser">
            {{ blockingUser ? 'Blocking…' : 'Block User' }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- ══ CONFIRM DELETE MODAL ════════════════════════════════════════════ -->
    <Transition name="modal">
      <div v-if="showConfirmModal" class="modal-backdrop" @click.self="showConfirmModal = false">
        <div class="modal-box" style="max-width:380px">
          <button class="modal-close" @click="showConfirmModal = false">×</button>
          <div class="confirm-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="1.8"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
          </div>
          <h2 class="modal-title" style="text-align:center;margin-top:8px">Delete {{ confirmTarget?.type === 'product' ? 'Product' : 'User' }}?</h2>
          <p class="confirm-body">
            <strong>{{ confirmTarget?.item?.title || confirmTarget?.item?.name }}</strong> will be permanently removed.
            <span v-if="confirmTarget?.type === 'user'"> All their listings, orders, and messages will also be deleted.</span>
          </p>
          <div style="display:flex;gap:10px;margin-top:16px">
            <button class="modal-cancel" @click="showConfirmModal = false">Cancel</button>
            <button class="modal-submit modal-submit--danger" @click="executeDelete" :disabled="deletingItem" style="flex:1">
              {{ deletingItem ? 'Deleting…' : 'Yes, Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['adm-toast', `adm-toast--${toast.type}`]">
        <svg v-if="toast.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ toast.text }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import api from '@/services/api'

// ── Icons ──────────────────────────────────────────────────────────────────
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
  { key:'messages', label:'Messages',  icon:IconMsg,   badge:'messages' },
]

const statCards = [
  { key:'users',    label:'Users',    icon:IconUsers, bg:'#e8f0fe', color:'#003366' },
  { key:'products', label:'Listings', icon:IconBox,   bg:'#e8f8f0', color:'#15803d' },
  { key:'orders',   label:'Orders',   icon:IconOrder, bg:'#fff8e0', color:'#854d0e' },
  { key:'messages', label:'Messages', icon:IconMsg,   bg:'#fce8ff', color:'#7c3aed' },
]

const categories = ['Textbooks','Electronics','Dorm Items','Uniforms','School Supplies','Food','Services','Others']

const blockOptions = [
  { value:'1h',      label:'1 Hour',    desc:'Expires in 1 hour',   type:'hours', duration:1 },
  { value:'24h',     label:'1 Day',     desc:'Expires in 24 hours', type:'hours', duration:24 },
  { value:'168h',    label:'1 Week',    desc:'Expires in 7 days',   type:'hours', duration:168 },
  { value:'custom',  label:'Custom',    desc:'Set your own hours',  type:'hours', duration:null },
  { value:'perm',    label:'Permanent', desc:'Until manually lifted', type:'permanent', duration:null },
]

// ── State ──────────────────────────────────────────────────────────────────
const activeTab    = ref('overview')
const stats        = ref({})
const recentProds  = ref([])
const allProds     = ref([])
const allUsers     = ref([])
const allMsgs      = ref([])
const allOrders    = ref([])
const loadingProds  = ref(false)
const loadingUsers  = ref(false)
const loadingMsgs   = ref(false)
const loadingOrders = ref(false)
const prodSearch    = ref('')
const userSearch    = ref('')
const msgSearch     = ref('')
const orderSearch   = ref('')
const toast         = ref({ show:false, text:'', type:'' })
let   toastTimer    = null

// Product modal
const showProdModal = ref(false)
const editingProd   = ref(null)
const savingProd    = ref(false)
const prodForm      = ref({ title:'', price:'', category:'', seller_id:'', description:'', tags:'' })
// FIX: track which previews are existing URLs vs new blob URLs separately
const existingImages = ref([])  // URLs already on server
const prodFiles      = ref([])  // new File objects (parallel to blob previews)
const prodPreviews   = ref([])  // all preview URLs shown in UI
const prodFileRef    = ref(null)

// User modal
const showUserModal = ref(false)
const editingUser   = ref(null)
const savingUser    = ref(false)
const userForm      = ref({ name:'', email:'', password:'', student_id:'', course:'', year_level:'', department:'' })

// Block modal
const showBlockModal = ref(false)
const blockTarget    = ref(null)
const blockingUser   = ref(false)
const blockForm      = ref({ preset:'24h', customHours:48, reason:'' })

// Confirm delete modal
const showConfirmModal = ref(false)
const confirmTarget    = ref(null)   // { type: 'product'|'user', item }
const deletingItem     = ref(false)

// ── Computed ───────────────────────────────────────────────────────────────
const filteredProds  = computed(() => {
  const q = prodSearch.value.toLowerCase()
  return q ? allProds.value.filter(p => `${p.title} ${p.seller_name} ${p.category}`.toLowerCase().includes(q)) : allProds.value
})
const filteredUsers  = computed(() => {
  const q = userSearch.value.toLowerCase()
  return q ? allUsers.value.filter(u => `${u.name} ${u.email} ${u.student_id}`.toLowerCase().includes(q)) : allUsers.value
})
const filteredMsgs   = computed(() => {
  const q = msgSearch.value.toLowerCase()
  return q ? allMsgs.value.filter(m => `${m.message} ${m.sender_name} ${m.receiver_name}`.toLowerCase().includes(q)) : allMsgs.value
})
const filteredOrders = computed(() => {
  const q = orderSearch.value.toLowerCase()
  return q ? allOrders.value.filter(o => `${o.product_title} ${o.buyer_name} ${o.seller_name}`.toLowerCase().includes(q)) : allOrders.value
})

// FIX: sidebar badges now use unread message count, not total
const unreadMsgCount = computed(() => allMsgs.value.filter(m => !m.is_read).length)
const navBadge = (tab) => {
  if (tab.key === 'messages') return unreadMsgCount.value || ''
  return stats.value[tab.badge] || ''
}

// ── Data loading ───────────────────────────────────────────────────────────
const loadAll = async () => {
  try { stats.value = (await api.adminStats()).data } catch {}
  try { recentProds.value = (await api.adminProducts()).data } catch {}
}

// FIX: always reload data when switching tabs (not just when empty)
const switchTab = (k) => {
  activeTab.value = k
  if (k === 'products') loadProds()
  if (k === 'users')    loadUsers()
  if (k === 'messages') loadMsgsTab()
  if (k === 'orders')   loadOrdersTab()
}

const loadProds    = async () => { loadingProds.value=true;  try { allProds.value  = (await api.adminProducts()).data  } catch { showToast('Failed to load products','error') } finally { loadingProds.value=false } }
const loadUsers    = async () => { loadingUsers.value=true;  try { allUsers.value  = (await api.adminUsers()).data     } catch { showToast('Failed to load users','error')    } finally { loadingUsers.value=false } }
const loadMsgsTab  = async () => { loadingMsgs.value=true;   try { allMsgs.value   = (await api.adminMessages()).data  } catch { showToast('Failed to load messages','error') } finally { loadingMsgs.value=false } }
const loadOrdersTab= async () => { loadingOrders.value=true; try { allOrders.value = (await api.adminOrders()).data   } catch { showToast('Failed to load orders','error')   } finally { loadingOrders.value=false } }

// ── Confirm Delete (modal replaces browser confirm()) ─────────────────────
const confirmDelete = (type, item) => {
  confirmTarget.value = { type, item }
  showConfirmModal.value = true
}

const executeDelete = async () => {
  const { type, item } = confirmTarget.value
  deletingItem.value = true
  try {
    if (type === 'product') {
      await api.adminDeleteProduct(item.id)
      allProds.value    = allProds.value.filter(x => x.id !== item.id)
      recentProds.value = recentProds.value.filter(x => x.id !== item.id)
    } else {
      await api.adminDeleteUser(item.id)
      allUsers.value = allUsers.value.filter(x => x.id !== item.id)
    }
    showToast('Deleted successfully', 'success')
    showConfirmModal.value = false
  } catch {
    showToast('Delete failed', 'error')
  } finally {
    deletingItem.value = false
  }
}

// ── Block / Unblock ────────────────────────────────────────────────────────
const openBlockModal = (u) => {
  blockTarget.value = u
  blockForm.value   = { preset:'24h', customHours:48, reason:'' }
  showBlockModal.value = true
}

const selectBlockPreset = (opt) => {
  blockForm.value.preset = opt.value
}

// FIX: unblock is a separate clean function — no mutation before API call
const unblockUser = async (u) => {
  try {
    await api.adminBlockUser(u.id, { action: 'unblock' })
    // Only update local state after success
    const idx = allUsers.value.findIndex(x => x.id === u.id)
    if (idx >= 0) {
      allUsers.value[idx] = { ...allUsers.value[idx], is_blocked: 0, block_until: null }
    }
    showToast('User unblocked', 'success')
  } catch {
    showToast('Failed to unblock', 'error')
  }
}

const executeBlock = async () => {
  const u = blockTarget.value
  if (!u) return

  const preset = blockOptions.find(o => o.value === blockForm.value.preset)
  if (!preset) return

  // FIX: validate custom hours before sending
  if (preset.value === 'custom') {
    const h = Number(blockForm.value.customHours)
    if (!h || h < 1 || h > 8760) {
      showToast('Enter a valid hour count (1–8760)', 'error')
      return
    }
  }

  blockingUser.value = true
  try {
    const payload = preset.value === 'perm'
      ? { action:'block', block_type:'permanent' }
      : preset.value === 'custom'
        ? { action:'block', block_type:'hours', duration: Number(blockForm.value.customHours) }
        : { action:'block', block_type:'hours', duration: preset.duration }

    await api.adminBlockUser(u.id, payload)

    // Only mutate after successful API call
    const idx = allUsers.value.findIndex(x => x.id === u.id)
    if (idx >= 0) {
      allUsers.value[idx] = { ...allUsers.value[idx], is_blocked: 1 }
    }
    showToast(`${u.name} blocked`, 'success')
    showBlockModal.value = false
  } catch {
    showToast('Failed to block user', 'error')
  } finally {
    blockingUser.value = false
  }
}

// FIX: toggleAdmin — capture current value BEFORE flip so toast is correct
const toggleAdmin = async (u) => {
  const wasAdmin = !!u.is_admin
  const newVal   = wasAdmin ? 0 : 1
  try {
    await api.adminUpdateUser(u.id, { is_admin: newVal })
    const idx = allUsers.value.findIndex(x => x.id === u.id)
    if (idx >= 0) allUsers.value[idx] = { ...allUsers.value[idx], is_admin: newVal }
    showToast(newVal ? `${u.name} is now admin` : `Admin removed from ${u.name}`, 'success')
  } catch {
    showToast('Failed to update role', 'error')
  }
}

// ── Product modal ──────────────────────────────────────────────────────────
const openAddProduct = () => {
  editingProd.value  = null
  prodForm.value     = { title:'', price:'', category:'', seller_id:'', description:'', tags:'' }
  prodFiles.value    = []
  existingImages.value = []
  prodPreviews.value = []
  showProdModal.value = true
}

const openEditProduct = (p) => {
  editingProd.value = p
  prodForm.value = {
    title:       p.title || '',
    price:       p.price || '',
    category:    p.category || '',
    seller_id:   p.seller_id || '',
    description: p.description || '',
    tags:        Array.isArray(p.tags) ? p.tags.filter(Boolean).join(',') : (p.tags || ''),
  }
  prodFiles.value = []
  // FIX: track existing server images separately so removeProdImage is unambiguous
  if (p.images && p.images.length) {
    existingImages.value = [...p.images]
  } else if (p.image_url) {
    existingImages.value = [p.image_url]
  } else {
    existingImages.value = []
  }
  prodPreviews.value = [...existingImages.value]
  showProdModal.value = true
}

const closeProdModal = () => {
  showProdModal.value  = false
  prodFiles.value      = []
  existingImages.value = []
  prodPreviews.value   = []
}

const triggerProdFile = () => prodFileRef.value?.click()
const handleProdFileChange = (e) => processProdFiles(e.target.files)
const handleProdDrop       = (e) => processProdFiles(e.dataTransfer.files)

const processProdFiles = (files) => {
  const slots = 5 - prodPreviews.value.length
  if (slots <= 0) return
  Array.from(files).slice(0, slots).forEach(file => {
    if (!file.type.startsWith('image/')) return
    if (file.size > 5 * 1024 * 1024) { showToast(`${file.name} is too large (max 5MB)`, 'error'); return }
    prodFiles.value.push(file)
    prodPreviews.value.push(URL.createObjectURL(file))
  })
}

// FIX: use separate existingImages/prodFiles arrays — no ambiguous index math
const removeProdImage = (i) => {
  const preview = prodPreviews.value[i]
  if (preview.startsWith('blob:')) {
    // It's a new file — find its position among blob-only previews
    const blobPreviews = prodPreviews.value.filter(p => p.startsWith('blob:'))
    const blobIdx = blobPreviews.indexOf(preview)
    if (blobIdx >= 0) prodFiles.value.splice(blobIdx, 1)
    URL.revokeObjectURL(preview)
  } else {
    // It's an existing server image
    existingImages.value = existingImages.value.filter(u => u !== preview)
  }
  prodPreviews.value.splice(i, 1)
}

const saveProd = async () => {
  if (!prodForm.value.title || !prodForm.value.price || !prodForm.value.category) {
    showToast('Title, price and category are required', 'error'); return
  }
  if (!editingProd.value && !prodForm.value.seller_id) {
    showToast('Seller ID is required', 'error'); return
  }
  savingProd.value = true
  try {
    const fd = new FormData()
    fd.append('title',       prodForm.value.title.trim())
    fd.append('description', prodForm.value.description || '')
    fd.append('price',       Number(prodForm.value.price))
    fd.append('category',    prodForm.value.category)
    fd.append('tags',        prodForm.value.tags || '')

    if (editingProd.value) {
      fd.append('user_id', editingProd.value.seller_id)
      prodFiles.value.forEach(f => fd.append('images', f))
      await api.updateProductWithImage(editingProd.value.id, fd)
      showToast('Product updated', 'success')
    } else {
      fd.append('user_id', prodForm.value.seller_id)
      prodFiles.value.forEach(f => fd.append('images', f))
      await api.createProduct(fd)
      showToast('Product added', 'success')
    }
    await loadProds()
    // FIX: also refresh overview recent listings
    try { recentProds.value = (await api.adminProducts()).data } catch {}
    closeProdModal()
  } catch (e) {
    showToast(e.response?.data?.message || 'Failed to save product', 'error')
  } finally {
    savingProd.value = false
  }
}

// ── User modal ─────────────────────────────────────────────────────────────
const openAddUser = () => {
  editingUser.value   = null
  userForm.value      = { name:'', email:'', password:'', student_id:'', course:'', year_level:'', department:'' }
  showUserModal.value = true
}
const openEditUser = (u) => {
  editingUser.value   = u
  userForm.value      = { name:u.name||'', email:u.email||'', password:'', student_id:u.student_id||'', course:u.course||'', year_level:u.year_level||'', department:u.department||'' }
  showUserModal.value = true
}
const saveUser = async () => {
  if (!userForm.value.name || !userForm.value.email) { showToast('Name and email are required','error'); return }
  if (!editingUser.value && !userForm.value.password) { showToast('Password is required','error'); return }
  if (!editingUser.value && userForm.value.password.length < 6) { showToast('Password must be at least 6 characters','error'); return }
  savingUser.value = true
  try {
    if (editingUser.value) {
      await api.adminUpdateUser(editingUser.value.id, userForm.value)
      const idx = allUsers.value.findIndex(x => x.id === editingUser.value.id)
      if (idx >= 0) allUsers.value[idx] = { ...allUsers.value[idx], ...userForm.value }
      showToast('User updated', 'success')
    } else {
      await api.adminCreateUser(userForm.value)
      await loadUsers()
      showToast('User created', 'success')
    }
    showUserModal.value = false
  } catch (e) {
    showToast(e.response?.data?.message || 'Failed to save user', 'error')
  } finally {
    savingUser.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const showToast = (text, type = '') => {
  clearTimeout(toastTimer)
  toast.value = { show:true, text, type }
  toastTimer  = setTimeout(() => toast.value.show = false, 3200)
}

const fmtDate = (d) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('en-PH', { month:'short', day:'numeric', year:'numeric' }) }
  catch { return d }
}

const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits:2 })

const orderStatusClass = (status) => ({
  'Pending':   'adm-status--pending',
  'Completed': 'adm-status--avail',
  'Cancelled': 'adm-status--sold',
}[status] || 'adm-status--pending')

onMounted(() => {
  loadAll()
  loadProds()
  loadUsers()
  loadMsgsTab()
  loadOrdersTab()
})
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes spinner-ring {
  0%   { stroke-dashoffset: 88; }
  100% { stroke-dashoffset: 0; }
}

/* Spinner */
.adm-spinner {
  display: inline-block;
  width: 16px; height: 16px;
  border: 2px solid #e0e8f4;
  border-top-color: #003366;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  vertical-align: middle;
}
.adm-spinner--sm { width: 13px; height: 13px; border-width: 2px; }

.adm { min-height: 100vh; font-family: 'Plus Jakarta Sans','Inter',sans-serif; }
.adm-dash { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }

/* Sidebar */
.adm-aside { background: #003366; display: flex; flex-direction: column; position: sticky; top: 0; height: 100vh; }
.adm-aside__brand { display: flex; align-items: center; gap: 12px; padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.adm-aside__name  { font-size: 0.95rem; font-weight: 800; color: #fff; margin: 0 0 2px; }
.adm-aside__role  { font-size: 0.7rem; color: rgba(255,255,255,0.5); margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
.adm-nav { padding: 12px 10px; display: flex; flex-direction: column; gap: 2px; flex: 1; overflow-y: auto; }
.adm-nav__item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: none; background: none; color: rgba(255,255,255,0.65); font-size: 0.875rem; font-weight: 500; cursor: pointer; border-radius: 9px; transition: 0.15s; text-align: left; font-family: inherit; width: 100%; }
.adm-nav__item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.adm-nav__item--on { background: #FFD700; color: #003366; font-weight: 700; }
.adm-nav__pill { margin-left: auto; background: rgba(255,255,255,0.2); color: #fff; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px; }
.adm-nav__item--on .adm-nav__pill { background: rgba(0,51,102,0.2); color: #003366; }
.adm-aside__foot { padding: 16px; border-top: 1px solid rgba(255,255,255,0.08); }
.adm-back-link { font-size: 0.78rem; color: rgba(255,255,255,0.45); text-decoration: none; display: flex; align-items: center; gap: 5px; justify-content: center; }
.adm-back-link:hover { color: rgba(255,255,255,0.8); }

/* Main */
.adm-main { background: #f4f7fb; overflow-y: auto; }
.adm-section { padding: 28px 32px 48px; }
.adm-section__head { margin-bottom: 20px; }
.adm-section__title { font-size: 1.5rem; font-weight: 800; color: #003366; margin: 0 0 4px; }
.adm-section__sub  { font-size: 0.875rem; color: #888; margin: 0; }
.adm-subtitle { font-size: 1rem; font-weight: 700; color: #003366; margin: 0; }
.adm-stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 14px; }
.adm-stat { background: #fff; border: 1px solid #e2eaf4; border-radius: 14px; padding: 18px 20px; display: flex; align-items: center; gap: 14px; }
.adm-stat__icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.adm-stat__num { font-size: 1.6rem; font-weight: 800; color: #003366; line-height: 1; display: block; }
.adm-stat__lbl { font-size: 0.78rem; color: #888; display: block; }
.adm-list { background: #fff; border: 1px solid #e2eaf4; border-radius: 14px; overflow: hidden; }
.adm-empty { padding: 1.5rem; text-align: center; color: #bbb; font-size: 0.875rem; margin: 0; }
.adm-list-item { display: flex; align-items: center; gap: 14px; padding: 12px 16px; border-bottom: 1px solid #f0f4f8; }
.adm-list-item:last-child { border-bottom: none; }
.adm-list-item__img { width: 42px; height: 42px; border-radius: 8px; object-fit: cover; background: #f0f4f8; flex-shrink: 0; }
.adm-list-item__img--empty { background: #f0f4f8; }
.adm-list-item__info { flex: 1; min-width: 0; }
.adm-list-item__title { font-size: 0.875rem; font-weight: 600; color: #003366; margin: 0 0 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.adm-list-item__meta  { font-size: 0.75rem; color: #888; margin: 0; }
.adm-list-item__price { font-size: 0.9rem; font-weight: 700; color: #003366; white-space: nowrap; }

/* Table */
.adm-table-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.adm-badge { background: #e8f0fe; color: #003366; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 12px; }
.adm-search-wrap { display: flex; align-items: center; gap: 8px; background: #fff; border: 1.5px solid #e0e8f4; border-radius: 9px; padding: 8px 14px; }
.adm-search-wrap:focus-within { border-color: #003366; }
.adm-search { border: none; outline: none; font-size: 0.875rem; color: #333; background: transparent; width: 200px; font-family: inherit; }
.adm-add-btn { display: flex; align-items: center; gap: 6px; background: #003366; color: #FFD700; border: none; padding: 9px 16px; border-radius: 8px; font-size: 0.82rem; font-weight: 700; cursor: pointer; font-family: inherit; transition: 0.15s; white-space: nowrap; }
.adm-add-btn:hover { background: #002244; }
.adm-icon-btn { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: #fff; border: 1.5px solid #e0e8f4; border-radius: 8px; cursor: pointer; color: #666; transition: 0.15s; flex-shrink: 0; }
.adm-icon-btn:hover { border-color: #003366; color: #003366; }
.adm-table-wrap { background: #fff; border: 1px solid #e2eaf4; border-radius: 14px; overflow: hidden; overflow-x: auto; }
.adm-table { width: 100%; border-collapse: collapse; }
.adm-table thead tr { background: #f8faff; border-bottom: 1px solid #e8edf4; }
.adm-table th { padding: 11px 14px; text-align: left; font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
.adm-table td { padding: 11px 14px; font-size: 0.875rem; color: #1a1a2e; border-bottom: 1px solid #f0f4f8; vertical-align: middle; }
.adm-table tr:last-child td { border-bottom: none; }
.adm-table__row:hover td { background: #f8faff; }
.adm-table__empty { text-align: center; padding: 36px; color: #bbb; font-size: 0.875rem; }
.adm-table__id    { color: #aaa; font-size: 0.75rem; font-family: monospace; }
.adm-table__bold  { font-weight: 600; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.adm-table__muted { color: #888; font-size: 0.82rem; }
.adm-table__price { font-weight: 700; color: #003366; white-space: nowrap; }
.adm-msg-preview  { max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #555; font-size: 0.82rem; }
.adm-thumb        { width: 36px; height: 36px; border-radius: 7px; object-fit: cover; display: block; background: #f0f4f8; }
.adm-thumb--empty { width: 36px; height: 36px; border-radius: 7px; background: #f0f4f8; display: block; }
.adm-cat-tag { display: inline-block; padding: 3px 9px; background: #eef3ff; color: #003366; border-radius: 6px; font-size: 11px; font-weight: 700; user-select: none; }
.adm-status { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: 11px; font-weight: 700; user-select: none; }
.adm-status--avail   { background: #e8f8f0; color: #15803d; }
.adm-status--sold    { background: #fee8e8; color: #b91c1c; }
.adm-status--pending { background: #fff8e0; color: #854d0e; }
.adm-read { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: 11px; font-weight: 700; user-select: none; }
.adm-read--read   { background: #e8f8f0; color: #15803d; }
.adm-read--unread { background: #fef9e0; color: #854d0e; }
.adm-role { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: 11px; font-weight: 700; user-select: none; }
.adm-role--admin { background: #fce8ff; color: #7c3aed; }
.adm-role--user  { background: #e8f0fe; color: #003366; }
.adm-av { width: 28px; height: 28px; border-radius: 50%; background: #003366; color: #FFD700; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; flex-shrink: 0; }
.adm-edit-btn  { background: none; border: 1px solid #d0dbe8; color: #003366; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.12s; font-family: inherit; white-space: nowrap; }
.adm-edit-btn:hover  { background: #eef3ff; }
.adm-del-btn   { background: none; border: 1px solid #fcc; color: #c0392b; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.12s; font-family: inherit; white-space: nowrap; }
.adm-del-btn:hover   { background: #fff5f5; }
.adm-block-btn { background: none; border: 1px solid #f59e0b; color: #b45309; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.12s; font-family: inherit; white-space: nowrap; }
.adm-block-btn:hover { background: #fff7ed; }
.adm-admin-btn { background: none; border: 1px solid #7c3aed; color: #7c3aed; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.12s; font-family: inherit; white-space: nowrap; }
.adm-admin-btn:hover { background: #f3e8ff; }

/* Modals */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-box { background: #fff; border-radius: 18px; width: 100%; max-width: 500px; padding: 1.75rem; position: relative; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.2); display: flex; flex-direction: column; }
.modal-close { position: absolute; top: 14px; right: 14px; width: 32px; height: 32px; background: #f0f4f8; border: none; border-radius: 8px; color: #666; cursor: pointer; font-size: 20px; display: flex; align-items: center; justify-content: center; transition: 0.15s; line-height: 1; }
.modal-close:hover { background: #e74c3c; color: #fff; }
.modal-title { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0 0 1.25rem; }
.modal-fields { display: flex; flex-direction: column; gap: 12px; margin-bottom: 1.25rem; }
.modal-cancel { flex: 1; background: #f0f4f8; color: #666; border: none; padding: 13px; border-radius: 10px; font-weight: 700; font-size: 0.95rem; cursor: pointer; font-family: inherit; transition: 0.15s; }
.modal-cancel:hover { background: #e0e8f4; }
.mf { display: flex; flex-direction: column; gap: 5px; }
.mf label { font-size: 0.75rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.4px; }
.mf-hint { font-size: 0.72rem; color: #aaa; font-weight: 400; text-transform: none; letter-spacing: 0; margin-left: 4px; }
.mf-hint-text { font-size: 0.72rem; color: #bbb; margin: 3px 0 0; }
.mf-input,.mf-select,.mf-textarea { padding: 9px 12px; border: 1.5px solid #e0e8f4; border-radius: 8px; font-size: 0.875rem; color: #1a1a2e; outline: none; font-family: inherit; background: #fafcff; transition: 0.15s; width: 100%; box-sizing: border-box; }
.mf-input:focus,.mf-select:focus,.mf-textarea:focus { border-color: #003366; }
.mf-input:disabled { background: #f0f0f0; color: #aaa; cursor: not-allowed; }
.mf-textarea { resize: vertical; }

/* Block modal */
.block-modal__name { font-size: 0.95rem; font-weight: 700; color: #003366; margin: -0.75rem 0 1rem; }
.block-options { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.block-option { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; border: 1.5px solid #e0e8f4; border-radius: 9px; cursor: pointer; transition: 0.15s; background: #fafcff; }
.block-option:hover { border-color: #f59e0b; background: #fffbf0; }
.block-option--on { border-color: #f59e0b; background: #fff7ed; }
.block-option__label { font-size: 0.82rem; font-weight: 700; color: #003366; }
.block-option__desc  { font-size: 0.72rem; color: #888; }

/* Confirm delete modal */
.confirm-icon { width: 56px; height: 56px; border-radius: 50%; background: #fff5f5; border: 2px solid #fcc; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px; }
.confirm-body { font-size: 0.875rem; color: #555; text-align: center; line-height: 1.6; margin: 0; }

/* Image upload */
.img-upload-area { border: 2px dashed #c8d8ea; border-radius: 12px; cursor: pointer; min-height: 110px; transition: border-color 0.2s; overflow: hidden; }
.img-upload-area:hover { border-color: #003366; }
.img-upload-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 7px; padding: 1.5rem; color: #aaa; text-align: center; min-height: 110px; }
.img-upload-placeholder p { font-size: 0.875rem; font-weight: 600; color: #555; margin: 0; }
.img-upload-placeholder span { font-size: 0.75rem; }
.img-preview-grid { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px; }
.img-preview-item { position: relative; width: 80px; height: 80px; border-radius: 8px; overflow: hidden; border: 1.5px solid #e0e8f4; }
.img-preview-thumb { width: 100%; height: 100%; object-fit: cover; }
.img-preview-remove { position: absolute; top: 3px; right: 3px; width: 20px; height: 20px; background: rgba(0,0,0,0.65); color: #fff; border: none; border-radius: 50%; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; line-height: 1; }
.img-preview-main { position: absolute; bottom: 3px; left: 3px; background: #003366; color: #FFD700; font-size: 8px; font-weight: 700; padding: 2px 5px; border-radius: 4px; }
.img-add-more { width: 80px; height: 80px; border-radius: 8px; border: 2px dashed #c8d8ea; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; cursor: pointer; color: #003366; font-size: 0.65rem; font-weight: 600; transition: 0.15s; }
.img-add-more:hover { border-color: #003366; background: #f0f5ff; }

.modal-submit { width: 100%; background: #003366; color: #FFD700; border: none; padding: 13px; border-radius: 10px; font-weight: 800; font-size: 0.95rem; cursor: pointer; font-family: inherit; transition: 0.15s; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 4px; }
.modal-submit:hover:not(:disabled) { background: #002244; }
.modal-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.modal-submit--danger { background: #c0392b; color: #fff; }
.modal-submit--danger:hover:not(:disabled) { background: #a93226; }

/* Toast */
.adm-toast { position: fixed; bottom: 24px; right: 24px; padding: 12px 16px; border-radius: 10px; font-size: 0.875rem; font-weight: 600; z-index: 9999; box-shadow: 0 8px 24px rgba(0,0,0,0.12); display: flex; align-items: center; gap: 8px; }
.adm-toast--success { background: #fff; border: 1.5px solid #16a34a; color: #15803d; }
.adm-toast--error   { background: #fff; border: 1.5px solid #c0392b; color: #c0392b; }

/* Transitions */
.toast-enter-active,.toast-leave-active { transition: all 0.2s; }
.toast-enter-from,.toast-leave-to { opacity: 0; transform: translateY(8px); }
.modal-enter-active,.modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from,.modal-leave-to { opacity: 0; transform: scale(0.95); }

@media (max-width: 768px) {
  .adm-dash { grid-template-columns: 1fr; }
  .adm-aside { display: none; }
  .adm-section { padding: 20px 16px; }
  .block-options { grid-template-columns: 1fr; }
}
</style>