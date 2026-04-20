<template>
  <div class="profile-wrapper">
    <div class="profile-layout">

      <!-- Left Card: Avatar + Quick Actions -->
      <div class="profile-sidebar">
        <div class="avatar-section">
          <div class="avatar-circle" @click="$refs.fileInput.click()">
            <img v-if="auth.user?.profile_pic" :src="auth.user.profile_pic" class="avatar-img" />
            <span v-else class="avatar-initials">{{ initials }}</span>
            <div class="avatar-overlay">
              <i class="fa-solid fa-camera"></i>
            </div>
          </div>
          <input type="file" ref="fileInput" @change="handlePictureUpload" accept="image/*" style="display: none;" />
          <h2 class="user-name">{{ auth.user?.name || 'Student' }}</h2>
          <span class="account-badge">
            <i class="fa-solid fa-graduation-cap"></i> Student Account
          </span>
        </div>

        <div class="sidebar-links">
          <router-link to="/dashboard" class="sidebar-link">
            <i class="fa-solid fa-store"></i> My Shop
          </router-link>
          <router-link to="/cart" class="sidebar-link">
            <i class="fa-solid fa-cart-shopping"></i> My Cart
          </router-link>
          <router-link to="/add-product" class="sidebar-link">
            <i class="fa-solid fa-plus"></i> Sell an Item
          </router-link>
        </div>

        <button @click="handleLogout" class="signout-btn">
          <i class="fa-solid fa-right-from-bracket"></i> Log Out
        </button>
      </div>

      <!-- Right Card: Details -->
      <div class="profile-main">
        <div class="section-title">
          <h3>Account Information</h3>
          <span class="verified-badge"><i class="fa-solid fa-circle-check"></i> Verified Student</span>
        </div>

        <div class="details-grid">
          <div class="detail-card">
            <div class="detail-icon">
              <i class="fa-solid fa-user"></i>
            </div>
            <div>
              <label>Full Name</label>
              <span>{{ auth.user?.name || 'N/A' }}</span>
            </div>
          </div>

          <div class="detail-card">
            <div class="detail-icon">
              <i class="fa-solid fa-envelope"></i>
            </div>
            <div>
              <label>School Email</label>
              <span>{{ auth.user?.email || 'N/A' }}</span>
            </div>
          </div>

          <div class="detail-card">
            <div class="detail-icon">
              <i class="fa-solid fa-id-card"></i>
            </div>
            <div>
              <label>Student ID</label>
              <span>{{ auth.user?.student_id_number || '2024-XXXXX' }}</span>
            </div>
          </div>

          <div class="detail-card">
            <div class="detail-icon">
              <i class="fa-solid fa-layer-group"></i>
            </div>
            <div>
              <label>Year Level</label>
              <span>{{ auth.user?.year_level || 'Not Set' }}</span>
            </div>
          </div>

          <div class="detail-card full-width">
            <div class="detail-icon">
              <i class="fa-solid fa-book"></i>
            </div>
            <div>
              <label>Course</label>
              <span>{{ auth.user?.course || 'Not Set' }}</span>
            </div>
          </div>

          <div class="detail-card full-width">
            <div class="detail-icon">
              <i class="fa-solid fa-building-columns"></i>
            </div>
            <div>
              <label>Department / College</label>
              <span>{{ auth.user?.department || 'Not Set' }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="section-title" style="margin-top: 2rem;">
          <h3>Activity</h3>
        </div>
        <div class="activity-grid">
          <div class="activity-card">
            <span class="activity-num">0</span>
            <span class="activity-label">Items Sold</span>
          </div>
          <div class="activity-card">
            <span class="activity-num">0</span>
            <span class="activity-label">Active Listings</span>
          </div>
          <div class="activity-card">
            <span class="activity-num">0</span>
            <span class="activity-label">Orders Placed</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const initials = computed(() => {
  if (!auth.user?.name) return '?'
  return auth.user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
})

const handlePictureUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    auth.user.profile_pic = e.target.result
    localStorage.setItem('user', JSON.stringify(auth.user))
  }
  reader.readAsDataURL(file)
}

const handleLogout = () => {
  auth.logout ? auth.logout() : (auth.user = null)
  localStorage.removeItem('user')
  router.push('/auth')
}
</script>

<style scoped>
.profile-wrapper {
  background: #f8fafc;
  min-height: 100vh;
  padding: 2rem 1.5rem;
}

.profile-layout {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 700px) {
  .profile-layout { grid-template-columns: 1fr; }
}

/* Sidebar */
.profile-sidebar {
  background: white;
  border-radius: 16px;
  padding: 2rem 1.5rem;
  border: 0.5px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.avatar-section { text-align: center; }

.avatar-circle {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  margin: 0 auto 12px;
  border: 3px solid #FFD700;
  background: #f0f4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  font-size: 1.5rem;
  font-weight: 800;
  color: #003366;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: 0.2s;
  color: white;
  font-size: 1.2rem;
}

.avatar-circle:hover .avatar-overlay { opacity: 1; }

.user-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: #003366;
  margin: 0 0 8px;
}

.account-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #f0f4ff;
  color: #003366;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
}

/* Sidebar Links */
.sidebar-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-top: 1px solid #f1f5f9;
  padding-top: 1rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #555;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
  transition: 0.2s;
}

.sidebar-link:hover {
  background: #f0f4ff;
  color: #003366;
}

.sidebar-link i { width: 16px; color: #888; }

.signout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 11px;
  background: transparent;
  border: 1.5px solid #ef4444;
  color: #ef4444;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  transition: 0.2s;
}

.signout-btn:hover { background: #ef4444; color: white; }

/* Main Card */
.profile-main {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  border: 0.5px solid #eee;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.section-title h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #003366;
  margin: 0;
}

.verified-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #f0fdf4;
  color: #16a34a;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

/* Details Grid */
.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.full-width { grid-column: 1 / -1; }

.detail-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 10px;
  border: 0.5px solid #eee;
}

.detail-icon {
  width: 36px;
  height: 36px;
  background: #f0f4ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003366;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.detail-card div { display: flex; flex-direction: column; gap: 2px; }

.detail-card label {
  font-size: 0.72rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.detail-card span {
  font-size: 0.9rem;
  color: #1e293b;
  font-weight: 600;
}

/* Activity */
.activity-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.activity-card {
  background: #f8fafc;
  border-radius: 10px;
  border: 0.5px solid #eee;
  padding: 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: #003366;
}

.activity-label {
  font-size: 0.75rem;
  color: #888;
}
</style>