<template>
  <div class="auth-wrapper">

    <!-- Left Panel -->
    <div class="left-panel">
      <div class="left-content">
        <div class="brand">
          <span class="brand-icon">🛍️</span>
          <span class="brand-name">ADNU <strong>Market</strong></span>
        </div>
        <h1 class="tagline">Buy & sell within<br/>the Golden Knights community.</h1>
        <p class="sub-tagline">The official peer-to-peer marketplace for Ateneo de Naga University students.</p>
        <div class="trust-badges">
          <div class="badge"><span>✓</span> ADNU Students Only</div>
          <div class="badge"><span>✓</span> Safe Campus Meetups</div>
          <div class="badge"><span>✓</span> Verified Sellers</div>
        </div>
      </div>
      <div class="left-deco">
        <div class="deco-circle c1"></div>
        <div class="deco-circle c2"></div>
        <div class="deco-circle c3"></div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <div class="form-card">

        <!-- DEV QUICK LOGIN (only visible in development) -->
        <div class="dev-panel" v-if="isDev">
          <p class="dev-label">⚡ Dev Quick Login</p>
          <div class="dev-btns">
            <button class="dev-btn seller" @click="quickLogin('seller')" type="button">
              Login as Seller
            </button>
            <button class="dev-btn buyer" @click="quickLogin('buyer')" type="button">
              Login as Buyer
            </button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button class="tab" :class="{ active: isLogin }" @click="isLogin = true">Login</button>
          <button class="tab" :class="{ active: !isLogin }" @click="isLogin = false">Register</button>
          <div class="tab-indicator" :class="{ right: !isLogin }"></div>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">

          <div class="field">
            <label>University Email</label>
            <div class="input-wrap">
              <i class="fa-solid fa-envelope field-icon"></i>
              <input v-model="form.email" type="email" placeholder="username@gbox.adnu.edu.ph" required />
            </div>
          </div>

          <div class="field">
            <label>Password</label>
            <div class="input-wrap">
              <i class="fa-solid fa-lock field-icon"></i>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                required
              />
              <button type="button" class="eye-btn" @click="showPassword = !showPassword">
                <i :class="showPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
              </button>
            </div>
          </div>

          <transition name="slide">
            <div v-if="!isLogin" class="reg-fields">

              <div class="field">
                <label>Confirm Password</label>
                <div class="input-wrap">
                  <i class="fa-solid fa-lock field-icon"></i>
                  <input
                    v-model="form.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="••••••••"
                    required
                  />
                  <button type="button" class="eye-btn" @click="showConfirmPassword = !showConfirmPassword">
                    <i :class="showConfirmPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="field">
                <label>Full Name</label>
                <div class="input-wrap">
                  <i class="fa-solid fa-user field-icon"></i>
                  <input v-model="form.name" type="text" placeholder="Juan Dela Cruz" required />
                </div>
              </div>

              <div class="field">
                <label>Student ID Number</label>
                <div class="input-wrap">
                  <i class="fa-solid fa-id-card field-icon"></i>
                  <input v-model="form.student_id_number" type="text" placeholder="2024-00000" required />
                </div>
              </div>

              <div class="field">
                <label>Year Level</label>
                <div class="input-wrap">
                  <i class="fa-solid fa-graduation-cap field-icon"></i>
                  <select v-model="form.year_level" required>
                    <option value="" disabled>Select Year</option>
                    <option value="1st Year">1st Year</option>
                    <option value="2nd Year">2nd Year</option>
                    <option value="3rd Year">3rd Year</option>
                    <option value="4th Year">4th Year</option>
                  </select>
                </div>
              </div>

              <div class="field">
                <label>Department / College</label>
                <div class="input-wrap">
                  <i class="fa-solid fa-building-columns field-icon"></i>
                  <select v-model="form.department" @change="form.course = ''" required>
                    <option value="" disabled>Select College</option>
                    <option v-for="(courses, dept) in departmentMap" :key="dept" :value="dept">{{ dept }}</option>
                  </select>
                </div>
              </div>

              <div class="field" v-if="form.department">
                <label>Course / Program</label>
                <div class="input-wrap">
                  <i class="fa-solid fa-book field-icon"></i>
                  <select v-model="form.course" required>
                    <option value="" disabled>Select program</option>
                    <option v-for="course in filteredCourses" :key="course" :value="course">{{ course }}</option>
                  </select>
                </div>
              </div>

            </div>
          </transition>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>
              {{ isLogin ? 'Login to Market' : 'Create Account' }}
              <i class="fa-solid fa-arrow-right"></i>
            </span>
          </button>

        </form>

        <p class="toggle-text">
          {{ isLogin ? "Don't have an account?" : "Already a member?" }}
          <span @click="isLogin = !isLogin">{{ isLogin ? 'Register' : 'Login' }}</span>
        </p>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// ✅ Show dev panel only on localhost
const isDev = computed(() => window.location.hostname === 'localhost')

// ✅ Pre-configured test accounts — change emails/passwords to match your DB
const DEV_ACCOUNTS = {
  seller: { email: 'dtdotado@gbox.adnu.edu.ph', password: '202400926' },
  buyer:  { email: 'deckertdotado@gbox.adnu.edu.ph',     password: 'kentrocky09' }
}

const quickLogin = async (role) => {
  const account = DEV_ACCOUNTS[role]
  try {
    loading.value = true
    const res = await api.login(account)
    auth.user = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    router.push('/')
  } catch (err) {
    alert(`Quick login failed. Make sure the ${role} account exists in your DB.`)
  } finally {
    loading.value = false
  }
}

const form = ref({
  name: '', email: '', password: '', confirmPassword: '',
  student_id_number: '', department: '', course: '', year_level: ''
})

const departmentMap = {
  "COLLEGE OF BUSINESS AND ACCOUNTANCY": [
    "BS Accountancy", "BS BA Accounting Information Management",
    "BS BA Financial Management and Accounting",
    "BS Entrepreneurship with specialized track on Tourism",
    "BS Tourism Management", "BS BA Banking and Finance",
    "BS BA Business Management Honors Program", "BS BA Legal Management",
    "BS BA Management", "BS BA Marketing Management"
  ],
  "COLLEGE OF COMPUTER STUDIES": [
    "Bachelor of Library and Information Science", "BS Computer Science",
    "BS Digital Illustration and Animation", "BS Information Systems",
    "BS Information Technology"
  ],
  "COLLEGE OF EDUCATION": [
    "Bachelor of Early Childhood Education", "Bachelor of Elementary Education",
    "Bachelor of Physical Education",
    "Bachelor of Secondary Education major in English",
    "Bachelor of Secondary Education major in Filipino",
    "Bachelor of Secondary Education major in Mathematics",
    "Bachelor of Secondary Education major in Science",
    "Bachelor of Secondary Education major in Social Studies",
    "Bachelor of Special Needs Education – Generalist"
  ],
  "COLLEGE OF HUMANITIES AND SOCIAL SCIENCES": [
    "AB Communication", "AB Economics", "AB English Language Studies",
    "AB Literature", "AB Philosophy Track 2: Pre-Law",
    "AB Philosophy Track 3: Foreign Service/International Relations",
    "AB Political Science", "AB Religious and Values Education",
    "BS Development Communication", "BS Psychology"
  ],
  "COLLEGE OF SCIENCE AND ENGINEERING": [
    "BS Biology", "BS Civil Engineering", "BS Architecture",
    "BS Computer Engineering", "BS Electronics Engineering",
    "BS Environmental Management", "BS Mathematics",
    "Bachelor of Engineering Technology major in Computer Engineering Technology"
  ],
  "COLLEGE OF NURSING": ["BS Nursing"]
}

const filteredCourses = computed(() =>
  form.value.department ? departmentMap[form.value.department] : []
)

const handleSubmit = async () => {
  if (!form.value.email.endsWith('@gbox.adnu.edu.ph')) {
    alert('Use your official ADNU GBOX email only')
    return
  }
  if (!isLogin.value) {
    if (!form.value.name || !form.value.student_id_number || !form.value.department || !form.value.course || !form.value.year_level) {
      alert('Please fill all fields ❌')
      return
    }
    if (!form.value.student_id_number.includes('-')) {
      alert("Student ID must contain '-' (example: 2024-12345)")
      return
    }
    if (form.value.password !== form.value.confirmPassword) {
      alert('Passwords do not match ❌')
      return
    }
  }

  try {
    loading.value = true
    if (isLogin.value) {
      const res = await api.login({ email: form.value.email, password: form.value.password })
      auth.user = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
      router.push('/')
    } else {
      await api.register({
        name: form.value.name, email: form.value.email,
        password: form.value.password,
        student_id_number: form.value.student_id_number,
        course: form.value.course, year_level: form.value.year_level,
        department: form.value.department
      })
      alert('Registered successfully! 🎉 Please login.')
      isLogin.value = true
    }
  } catch (err) {
    alert(err.response?.data?.message || 'Authentication failed ❌')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

.auth-wrapper {
  min-height: 100vh;
  display: flex;
  font-family: 'Plus Jakarta Sans', sans-serif;
  background: #f8fafc;
}

.left-panel {
  width: 45%;
  background: #003366;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  position: relative;
  overflow: hidden;
}

.left-content { position: relative; z-index: 2; }

.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 2.5rem; }
.brand-icon { font-size: 1.8rem; }
.brand-name { font-size: 1.2rem; color: rgba(255,255,255,0.7); font-weight: 500; }
.brand-name strong { color: #FFD700; font-weight: 800; }

.tagline { font-size: 2.4rem; font-weight: 800; color: white; line-height: 1.2; margin: 0 0 1.25rem; }
.sub-tagline { font-size: 0.95rem; color: rgba(255,255,255,0.6); line-height: 1.7; margin: 0 0 2.5rem; max-width: 340px; }

.trust-badges { display: flex; flex-direction: column; gap: 10px; }
.badge { display: inline-flex; align-items: center; gap: 8px; color: rgba(255,255,255,0.85); font-size: 0.875rem; font-weight: 600; }
.badge span { width: 20px; height: 20px; background: #FFD700; color: #003366; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 900; flex-shrink: 0; }

.left-deco { position: absolute; inset: 0; z-index: 1; }
.deco-circle { position: absolute; border-radius: 50%; border: 1px solid rgba(255,255,255,0.08); }
.c1 { width: 400px; height: 400px; bottom: -120px; right: -120px; }
.c2 { width: 260px; height: 260px; bottom: -60px; right: -60px; background: rgba(255,215,0,0.06); }
.c3 { width: 140px; height: 140px; top: 40px; right: 40px; border-color: rgba(255,215,0,0.15); }

.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow-y: auto;
}

.form-card {
  width: 100%;
  max-width: 440px;
  background: white;
  border-radius: 20px;
  padding: 2rem 2.25rem;
  border: 0.5px solid #e5e7eb;
}

/* Dev Panel */
.dev-panel {
  background: #fffbeb;
  border: 1px dashed #f59e0b;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 1.25rem;
}

.dev-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #b45309;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px;
}

.dev-btns { display: flex; gap: 8px; }

.dev-btn {
  flex: 1;
  padding: 8px;
  border-radius: 7px;
  border: none;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
}

.dev-btn.seller { background: #003366; color: white; }
.dev-btn.seller:hover { background: #002244; }
.dev-btn.buyer { background: #FFD700; color: #003366; }
.dev-btn.buyer:hover { background: #e6c200; }

/* Tabs */
.tabs {
  display: flex;
  position: relative;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 1.75rem;
}

.tab {
  flex: 1; padding: 9px; border: none; background: none;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.875rem; font-weight: 600; color: #888;
  cursor: pointer; border-radius: 8px; transition: color 0.2s; position: relative; z-index: 1;
}
.tab.active { color: #003366; }

.tab-indicator {
  position: absolute; top: 4px; left: 4px;
  width: calc(50% - 4px); height: calc(100% - 8px);
  background: white; border-radius: 7px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.tab-indicator.right { transform: translateX(100%); }

/* Form */
.auth-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 0.78rem; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: 0.4px; }

.input-wrap { position: relative; display: flex; align-items: center; }
.field-icon { position: absolute; left: 12px; color: #9ca3af; font-size: 0.85rem; pointer-events: none; }

.input-wrap input,
.input-wrap select {
  width: 100%; padding: 10px 12px 10px 36px;
  border: 1px solid #e5e7eb; border-radius: 9px;
  font-size: 0.9rem; font-family: 'Plus Jakarta Sans', sans-serif;
  color: #111; background: #fafafa;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none; appearance: none;
}
.input-wrap input:focus,
.input-wrap select:focus {
  border-color: #003366; background: white;
  box-shadow: 0 0 0 3px rgba(0,51,102,0.08);
}

.eye-btn {
  position: absolute; right: 12px; background: none; border: none;
  color: #9ca3af; cursor: pointer; padding: 0; font-size: 0.85rem;
  display: flex; align-items: center; transition: color 0.2s;
}
.eye-btn:hover { color: #003366; }

.reg-fields { display: flex; flex-direction: column; gap: 1rem; }

.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { opacity: 0; max-height: 0; }
.slide-enter-to, .slide-leave-from { opacity: 1; max-height: 2000px; }

.submit-btn {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  width: 100%; padding: 13px; background: #003366; color: white;
  border: none; border-radius: 10px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.95rem; font-weight: 700; cursor: pointer;
  transition: background 0.2s, transform 0.15s; margin-top: 0.5rem;
}
.submit-btn:hover:not(:disabled) { background: #002244; transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.65; cursor: not-allowed; }

.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.toggle-text { margin-top: 1.25rem; text-align: center; font-size: 0.85rem; color: #6b7280; }
.toggle-text span { color: #003366; font-weight: 700; cursor: pointer; margin-left: 4px; }
.toggle-text span:hover { text-decoration: underline; }

@media (max-width: 768px) {
  .auth-wrapper { flex-direction: column; }
  .left-panel { width: 100%; padding: 2rem 1.5rem; min-height: auto; }
  .tagline { font-size: 1.6rem; }
  .right-panel { padding: 1.5rem 1rem; }
  .form-card { padding: 1.5rem; }
}
</style>