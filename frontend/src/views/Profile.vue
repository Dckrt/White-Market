<template>
  <div class="profile-page">
    <div class="profile-layout">

      <!-- ── LEFT SIDEBAR ── -->
      <aside class="profile-sidebar">
        <div class="profile-sidebar__avatar-wrap">
          <!-- Avatar with upload -->
          <div class="profile-avatar-ring">
            <div class="profile-avatar" @click="triggerPicUpload">
              <img v-if="localProfilePic" :src="localProfilePic" class="profile-avatar__img" alt="Profile" @error="localProfilePic = null" />
              <span v-else class="profile-avatar__initials">{{ initials }}</span>
              <div class="profile-avatar__overlay">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
              </div>
            </div>
          </div>
          <input ref="picInput" type="file" accept="image/*" style="display:none" @change="handlePicUpload" />

          <p v-if="uploadingPic" class="profile-sidebar__uploading">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
            Uploading…
          </p>
          <p v-else class="profile-sidebar__change-pic" @click="triggerPicUpload">Change photo</p>

          <h2 class="profile-sidebar__name">{{ auth.user?.name || 'Student' }}</h2>
          <div class="profile-sidebar__badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            Student Account
          </div>
        </div>

        <nav class="profile-sidebar__nav">
          <router-link to="/dashboard" class="profile-sidebar__link">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            My Shop
          </router-link>
          <router-link to="/cart" class="profile-sidebar__link">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
            My Cart
          </router-link>
          <router-link to="/add-product" class="profile-sidebar__link">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Sell an Item
          </router-link>
          <router-link to="/messages" class="profile-sidebar__link">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            Messages
          </router-link>
        </nav>

        <button @click="handleLogout" class="profile-sidebar__logout">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Log Out
        </button>
      </aside>

      <!-- ── MAIN ── -->
      <main class="profile-main">

        <!-- Account Info -->
        <div class="profile-section">
          <div class="profile-section__head">
            <h3 class="profile-section__title">Account Information</h3>
            <span class="profile-section__verified">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Verified Student
            </span>
          </div>
          <div class="profile-details-grid">
            <div class="profile-detail-card">
              <div class="profile-detail-card__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
              <div>
                <label>FULL NAME</label>
                <span>{{ auth.user?.name || 'N/A' }}</span>
              </div>
            </div>

            <div class="profile-detail-card">
              <div class="profile-detail-card__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              </div>
              <div>
                <label>SCHOOL EMAIL</label>
                <span>{{ auth.user?.email || 'N/A' }}</span>
              </div>
            </div>

            <div class="profile-detail-card">
              <div class="profile-detail-card__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
              </div>
              <div>
                <label>STUDENT ID</label>
                <span>{{ auth.user?.student_id_number || 'N/A' }}</span>
              </div>
            </div>

            <div class="profile-detail-card">
              <div class="profile-detail-card__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
              </div>
              <div>
                <label>YEAR LEVEL</label>
                <span>{{ auth.user?.year_level || 'Not Set' }}</span>
              </div>
            </div>

            <div class="profile-detail-card profile-detail-card--full">
              <div class="profile-detail-card__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
              </div>
              <div>
                <label>COURSE</label>
                <span>{{ auth.user?.course || 'Not Set' }}</span>
              </div>
            </div>

            <div class="profile-detail-card profile-detail-card--full">
              <div class="profile-detail-card__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              </div>
              <div>
                <label>DEPARTMENT / COLLEGE</label>
                <span>{{ auth.user?.department || 'Not Set' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity -->
        <div class="profile-section">
          <div class="profile-section__head">
            <h3 class="profile-section__title">Activity</h3>
          </div>
          <div class="profile-activity-grid">
            <div class="profile-activity-card">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              <span class="profile-activity-card__num">{{ myListings }}</span>
              <span class="profile-activity-card__label">Active Listings</span>
            </div>
            <div class="profile-activity-card">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
              <span class="profile-activity-card__num">{{ cartItemCount }}</span>
              <span class="profile-activity-card__label">Cart Items</span>
            </div>
            <div class="profile-activity-card">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.5"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              <span class="profile-activity-card__num">{{ messageCount }}</span>
              <span class="profile-activity-card__label">Messages</span>
            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const auth   = useAuthStore()
const router = useRouter()

const picInput      = ref(null)
const uploadingPic  = ref(false)
const localProfilePic = ref(null)
const myListings    = ref(0)
const cartItemCount = ref(0)
const messageCount  = ref(0)

const initials = computed(() => {
  if (!auth.user?.name) return '?'
  return auth.user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
})

const triggerPicUpload = () => picInput.value?.click()

const handlePicUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  // Preview immediately
  const reader = new FileReader()
  reader.onload = (ev) => { localProfilePic.value = ev.target.result }
  reader.readAsDataURL(file)

  uploadingPic.value = true
  try {
    const fd = new FormData()
    fd.append('profile_pic', file)
    const res = await api.uploadProfilePic(auth.user.user_id, fd)
    const newUrl = res.data.profile_pic

    // Update auth store and localStorage
    auth.user = { ...auth.user, profile_pic: newUrl }
    localStorage.setItem('user', JSON.stringify(auth.user))
    localProfilePic.value = newUrl

    // Notify Navbar to update
    window.dispatchEvent(new Event('profile-pic-updated'))
  } catch (err) {
    console.error('Profile pic upload error:', err)
    alert('Failed to upload profile picture. Please try again.')
  } finally {
    uploadingPic.value = false
  }
}

const handleLogout = () => {
  auth.logout()
  router.push('/auth')
}

onMounted(async () => {
  // Load profile pic
  localProfilePic.value = auth.user?.profile_pic || null

  // Load activity stats
  try {
    const [prods, cart, threads] = await Promise.all([
      api.getMyProducts(auth.user.user_id).catch(() => ({ data: [] })),
      api.getCart(auth.user.user_id).catch(() => ({ data: [] })),
      api.getThreads(auth.user.user_id).catch(() => ({ data: [] })),
    ])
    myListings.value    = Array.isArray(prods.data) ? prods.data.length : 0
    cartItemCount.value = Array.isArray(cart.data) ? cart.data.length : 0
    messageCount.value  = Array.isArray(threads.data) ? threads.data.length : 0
  } catch {}
})
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; transform-origin: center; }

.profile-page { background: #f4f7fb; min-height: calc(100vh - 62px); padding: 2rem 1.5rem; }

.profile-layout {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 1.5rem;
  align-items: start;
}

/* ── SIDEBAR ── */
.profile-sidebar {
  background: #fff;
  border-radius: 16px;
  padding: 2rem 1.5rem;
  border: 1px solid #e8edf4;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,51,102,0.05);
}

.profile-sidebar__avatar-wrap { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; }

.profile-avatar-ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  border: 3px solid #FFD700;
  padding: 3px;
  background: #fff;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #003366;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-avatar__img      { width: 100%; height: 100%; object-fit: cover; }
.profile-avatar__initials { color: #FFD700; font-size: 1.4rem; font-weight: 900; }
.profile-avatar__overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.45);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.profile-avatar:hover .profile-avatar__overlay { opacity: 1; }

.profile-sidebar__change-pic {
  font-size: 0.75rem;
  font-weight: 600;
  color: #003366;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
  margin: 0;
}
.profile-sidebar__change-pic:hover { color: #002244; }

.profile-sidebar__uploading {
  font-size: 0.75rem;
  color: #888;
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0;
}

.profile-sidebar__name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #003366;
  margin: 4px 0 0;
  text-align: center;
}

.profile-sidebar__badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #eef3ff;
  color: #003366;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
}

.profile-sidebar__nav { display: flex; flex-direction: column; gap: 2px; border-top: 1px solid #f0f4f8; padding-top: 1rem; }

.profile-sidebar__link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  color: #555;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: 0.15s;
}
.profile-sidebar__link:hover { background: #eef3ff; color: #003366; }
.profile-sidebar__link svg { color: #aaa; flex-shrink: 0; }
.profile-sidebar__link:hover svg { color: #003366; }

.profile-sidebar__logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 11px;
  background: transparent;
  border: 1.5px solid #fca5a5;
  color: #c0392b;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  transition: 0.15s;
  font-family: inherit;
}
.profile-sidebar__logout:hover { background: #c0392b; color: #fff; border-color: #c0392b; }

/* ── MAIN ── */
.profile-main { display: flex; flex-direction: column; gap: 1.25rem; }

.profile-section {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #e8edf4;
  box-shadow: 0 2px 12px rgba(0,51,102,0.05);
}

.profile-section__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f0f4f8;
}
.profile-section__title { font-size: 1rem; font-weight: 700; color: #003366; margin: 0; }
.profile-section__verified {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #e8f8f0;
  color: #15803d;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.profile-details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.profile-detail-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e8edf4;
}
.profile-detail-card--full { grid-column: 1 / -1; }

.profile-detail-card__icon {
  width: 36px;
  height: 36px;
  background: #eef3ff;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003366;
  flex-shrink: 0;
}

.profile-detail-card > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.profile-detail-card label { font-size: 0.68rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
.profile-detail-card span  { font-size: 0.9rem; color: #1a1a2e; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Activity */
.profile-activity-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }

.profile-activity-card {
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e8edf4;
  padding: 1.25rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.profile-activity-card svg { color: #003366; }
.profile-activity-card__num   { font-size: 1.6rem; font-weight: 800; color: #003366; }
.profile-activity-card__label { font-size: 0.75rem; color: #888; }

@media (max-width: 700px) {
  .profile-layout { grid-template-columns: 1fr; }
  .profile-details-grid { grid-template-columns: 1fr; }
  .profile-activity-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>