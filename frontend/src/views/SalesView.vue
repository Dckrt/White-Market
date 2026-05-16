<template>
  <div class="sp">

    <!-- HEADER -->
    <div class="sp-header">
      <div class="sp-header__left">
        <div class="sp-header__icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="2"/>
            <path d="M9 12h6M9 16h4"/>
          </svg>
        </div>
        <div>
          <h1 class="sp-header__title">Sales</h1>
          <p class="sp-header__sub">Manage orders from your buyers</p>
        </div>
      </div>

      <!-- Summary chips -->
      <div class="sp-summary" v-if="!loading && orders.length">
        <div class="sp-chip">
          <span class="sp-chip__num">{{ orders.length }}</span>
          <span class="sp-chip__lbl">Total</span>
        </div>
        <div class="sp-chip sp-chip--warn">
          <span class="sp-chip__num">{{ pendingCount }}</span>
          <span class="sp-chip__lbl">Pending</span>
        </div>
        <div class="sp-chip sp-chip--green">
          <span class="sp-chip__num">{{ completedCount }}</span>
          <span class="sp-chip__lbl">Completed</span>
        </div>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="sp-grid">
      <div v-for="n in 3" :key="n" class="sp-skeleton">
        <div class="sp-skeleton__top">
          <div class="sp-skeleton__line sp-skeleton__line--wide"></div>
          <div class="sp-skeleton__pill"></div>
        </div>
        <div class="sp-skeleton__rows">
          <div class="sp-skeleton__line sp-skeleton__line--mid" v-for="i in 4" :key="i"></div>
        </div>
      </div>
    </div>

    <!-- EMPTY -->
    <div v-else-if="orders.length === 0" class="sp-empty">
      <div class="sp-empty__icon">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#c0cdd8" stroke-width="1.4" stroke-linecap="round">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
          <rect x="9" y="3" width="6" height="4" rx="2"/>
          <path d="M9 12h6M9 16h4"/>
        </svg>
      </div>
      <h3>No sales yet</h3>
      <p>When buyers purchase your listings, orders will appear here.</p>
    </div>

    <!-- SALES LIST -->
    <div v-else class="sp-grid">
      <TransitionGroup name="card">
        <div v-for="o in orders" :key="o.id" class="sp-card" :class="`sp-card--${(o.status || '').toLowerCase()}`">

          <!-- Card header -->
          <div class="sp-card__head">
            <div class="sp-card__title-wrap">
              <div class="sp-card__icon" :class="`sp-card__icon--${(o.status || '').toLowerCase()}`">
                <svg v-if="o.status === 'Completed'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                <svg v-else-if="o.status === 'Cancelled'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              </div>
              <div>
                <h3 class="sp-card__title">{{ o.product_title }}</h3>
                <span class="sp-card__date">{{ formatDate(o.ordered_at) }}</span>
              </div>
            </div>
            <span class="sp-status" :class="`sp-status--${(o.status || '').toLowerCase()}`">
              {{ o.status }}
            </span>
          </div>

          <!-- Divider -->
          <div class="sp-card__divider"></div>

          <!-- Details -->
          <div class="sp-card__body">
            <div class="sp-row">
              <span class="sp-row__label">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                Buyer
              </span>
              <strong class="sp-row__val">{{ o.buyer_name }}</strong>
            </div>
            <div class="sp-row">
              <span class="sp-row__label">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
                Amount
              </span>
              <strong class="sp-row__val sp-row__val--price">₱{{ Number(o.product_price).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</strong>
            </div>
            <div class="sp-row">
              <span class="sp-row__label">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
                Payment
              </span>
              <strong class="sp-row__val">{{ o.payment_method }}</strong>
            </div>
            <div class="sp-row">
              <span class="sp-row__label">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                Pickup
              </span>
              <strong class="sp-row__val">{{ o.pickup_location || 'Not specified' }}</strong>
            </div>
          </div>

          <!-- Actions -->
          <div class="sp-card__actions" v-if="o.status !== 'Completed' && o.status !== 'Cancelled'">
            <button class="sp-btn sp-btn--cancel" @click="cancelOrder(o)" :disabled="o._loading">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              Cancel
            </button>
            <button class="sp-btn sp-btn--done" @click="markDone(o)" :disabled="o._loading">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Mark Completed
            </button>
            <button class="sp-btn sp-btn--msg" @click="goMessage(o)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              Message
            </button>
          </div>

          <!-- Completed/Cancelled state actions -->
          <div class="sp-card__actions" v-else>
            <div class="sp-done-note" v-if="o.status === 'Completed'">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Transaction complete
            </div>
            <div class="sp-cancelled-note" v-else>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              Order cancelled
            </div>
            <button class="sp-btn sp-btn--msg" @click="goMessage(o)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              Message
            </button>
          </div>

        </div>
      </TransitionGroup>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['sp-toast', `sp-toast--${toast.type}`]">
        <svg v-if="toast.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ toast.text }}
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const orders  = ref([])
const loading = ref(true)
const user    = JSON.parse(localStorage.getItem('user'))

// ── Toast (replaces alert()) ───────────────────────────────────────────────
const toast = ref({ show: false, text: '', type: 'success' })
let toastTimer = null
const showToast = (text, type = 'success') => {
  clearTimeout(toastTimer)
  toast.value = { show: true, text, type }
  toastTimer  = setTimeout(() => toast.value.show = false, 3000)
}

// ── Summary counts ─────────────────────────────────────────────────────────
const pendingCount   = computed(() => orders.value.filter(o => o.status === 'Pending').length)
const completedCount = computed(() => orders.value.filter(o => o.status === 'Completed').length)

// ── Load ───────────────────────────────────────────────────────────────────
const loadSales = async () => {
  try {
    const res = await api.getSellerOrders(user.user_id)
    orders.value = (res.data || []).map(o => ({ ...o, _loading: false }))
  } catch (err) {
    console.error(err)
    showToast('Failed to load sales', 'error')
  } finally {
    loading.value = false
  }
}

// ── Cancel ─────────────────────────────────────────────────────────────────
const cancelOrder = async (order) => {
  order._loading = true
  try {
    await api.updateOrderStatus(order.id, { status: 'Cancelled' })
    order.status = 'Cancelled'
    showToast('Order cancelled', 'error')
  } catch (err) {
    console.error(err)
    showToast('Failed to cancel order', 'error')
  } finally {
    order._loading = false
  }
}

// ── Complete ───────────────────────────────────────────────────────────────
const markDone = async (order) => {
  order._loading = true
  try {
    await api.updateOrderStatus(order.id, { status: 'Completed' })
    order.status = 'Completed'
    showToast('Order marked as completed!')
  } catch (err) {
    console.error(err)
    showToast('Failed to update order', 'error')
  } finally {
    order._loading = false
  }
}

// ── Message buyer ──────────────────────────────────────────────────────────
const goMessage = (order) => {
  router.push({ path: '/messages', query: { user: order.buyer_id } })
}

// ── Format date ────────────────────────────────────────────────────────────
const formatDate = (date) => {
  if (!date) return 'N/A'
  const d    = new Date(date)
  const diff = Math.floor((Date.now() - d) / 1000)
  if (diff < 60)    return 'Just now'
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(loadSales)
</script>

<style scoped>
@keyframes spin    { to { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -600px 0; } 100% { background-position: 600px 0; } }

.sp {
  padding: 2rem 1.5rem 4rem;
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.sp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}
.sp-header__left { display: flex; align-items: center; gap: 14px; }
.sp-header__icon {
  width: 48px; height: 48px;
  background: #fff;
  border: 1.5px solid #e0e8f4;
  border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sp-header__title { font-size: 1.4rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.sp-header__sub   { font-size: 0.82rem; color: #888; margin: 0; }

/* Summary chips */
.sp-summary { display: flex; gap: 8px; flex-wrap: wrap; }
.sp-chip {
  display: flex; flex-direction: column; align-items: center;
  background: #fff; border: 1.5px solid #e0e8f4; border-radius: 10px;
  padding: 8px 16px; min-width: 64px;
}
.sp-chip--warn  { border-color: #fed7aa; background: #fff7ed; }
.sp-chip--green { border-color: #bbf7d0; background: #f0fdf4; }
.sp-chip__num { font-size: 1.2rem; font-weight: 800; color: #003366; line-height: 1; }
.sp-chip--warn  .sp-chip__num  { color: #c2410c; }
.sp-chip--green .sp-chip__num  { color: #15803d; }
.sp-chip__lbl { font-size: 0.7rem; color: #888; font-weight: 600; margin-top: 2px; }

/* ── Skeleton ─────────────────────────────────────────────────────────────── */
.sp-grid { display: flex; flex-direction: column; gap: 12px; }
.sp-skeleton {
  background: #fff; border: 1px solid #e8edf4; border-radius: 16px; padding: 20px;
}
.sp-skeleton__top { display: flex; justify-content: space-between; margin-bottom: 16px; }
.sp-skeleton__pill {
  width: 72px; height: 24px; border-radius: 20px;
  background: linear-gradient(90deg, #f0f4f8 25%, #e2e8f0 50%, #f0f4f8 75%);
  background-size: 600px 100%; animation: shimmer 1.3s ease-in-out infinite;
}
.sp-skeleton__rows { display: flex; flex-direction: column; gap: 10px; }
.sp-skeleton__line {
  height: 12px; border-radius: 6px;
  background: linear-gradient(90deg, #f0f4f8 25%, #e2e8f0 50%, #f0f4f8 75%);
  background-size: 600px 100%; animation: shimmer 1.3s ease-in-out infinite;
}
.sp-skeleton__line--wide   { width: 60%; }
.sp-skeleton__line--mid    { width: 40%; }

/* ── Empty ───────────────────────────────────────────────────────────────── */
.sp-empty {
  background: #fff; border: 1px dashed #d0dbe8; border-radius: 18px;
  padding: 4rem 2rem; text-align: center;
}
.sp-empty__icon {
  width: 72px; height: 72px; border-radius: 50%; background: #f0f4f8;
  display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;
}
.sp-empty h3 { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0 0 6px; }
.sp-empty p  { color: #aaa; font-size: 0.875rem; margin: 0; }

/* ── Card ────────────────────────────────────────────────────────────────── */
.sp-card {
  background: #fff;
  border: 1px solid #e8edf4;
  border-radius: 16px;
  padding: 18px 20px;
  transition: box-shadow 0.2s;
}
.sp-card:hover { box-shadow: 0 4px 20px rgba(0,51,102,0.07); }
.sp-card--completed { border-left: 3px solid #22c55e; }
.sp-card--cancelled { border-left: 3px solid #ef4444; opacity: 0.75; }
.sp-card--pending   { border-left: 3px solid #f59e0b; }

.sp-card__head {
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 12px; margin-bottom: 14px;
}
.sp-card__title-wrap { display: flex; align-items: flex-start; gap: 10px; }
.sp-card__icon {
  width: 32px; height: 32px; border-radius: 8px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; margin-top: 2px;
}
.sp-card__icon--pending   { background: #fff7ed; color: #c2410c; }
.sp-card__icon--completed { background: #f0fdf4; color: #15803d; }
.sp-card__icon--cancelled { background: #fee2e2; color: #991b1b; }

.sp-card__title { font-size: 0.95rem; font-weight: 700; color: #003366; margin: 0 0 3px; }
.sp-card__date  { font-size: 0.75rem; color: #aaa; }

/* Status pill */
.sp-status {
  padding: 4px 12px; border-radius: 20px; font-size: 0.72rem;
  font-weight: 800; white-space: nowrap; flex-shrink: 0;
  letter-spacing: 0.2px;
}
.sp-status--pending   { background: #fff7ed; color: #c2410c; }
.sp-status--completed { background: #f0fdf4; color: #15803d; }
.sp-status--cancelled { background: #fee2e2; color: #991b1b; }

.sp-card__divider { height: 1px; background: #f0f4f8; margin: 0 0 14px; }

/* Detail rows */
.sp-card__body { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.sp-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.sp-row__label {
  display: flex; align-items: center; gap: 5px;
  font-size: 0.8rem; color: #888; font-weight: 500;
}
.sp-row__val { font-size: 0.875rem; color: #1a1a2e; font-weight: 600; }
.sp-row__val--price { color: #003366; font-size: 0.95rem; }

/* Actions */
.sp-card__actions { display: flex; gap: 8px; flex-wrap: wrap; }

.sp-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: 9px; border: none;
  font-size: 0.8rem; font-weight: 700; cursor: pointer;
  font-family: inherit; transition: 0.15s; white-space: nowrap;
}
.sp-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.sp-btn--done {
  background: #003366; color: #FFD700;
}
.sp-btn--done:hover:not(:disabled) { background: #002244; }

.sp-btn--cancel {
  background: #fee2e2; color: #991b1b; border: 1px solid #fecaca;
}
.sp-btn--cancel:hover:not(:disabled) { background: #fecaca; }

.sp-btn--msg {
  background: #f0f4f8; color: #003366; border: 1px solid #d0dbe8;
}
.sp-btn--msg:hover { background: #e2eaf4; }

/* Done / cancelled note */
.sp-done-note, .sp-cancelled-note {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.78rem; font-weight: 600; padding: 6px 12px;
  border-radius: 8px; flex: 1;
}
.sp-done-note      { color: #15803d; background: #f0fdf4; }
.sp-cancelled-note { color: #991b1b; background: #fee2e2; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.sp-toast {
  position: fixed; bottom: 24px; right: 24px;
  padding: 12px 16px; border-radius: 10px;
  font-size: 0.875rem; font-weight: 600; z-index: 9999;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  display: flex; align-items: center; gap: 8px;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.sp-toast--success { background: #fff; border: 1.5px solid #16a34a; color: #15803d; }
.sp-toast--error   { background: #fff; border: 1.5px solid #dc2626; color: #991b1b; }

/* ── Transitions ─────────────────────────────────────────────────────────── */
.toast-enter-active, .toast-leave-active { transition: all 0.2s; }
.toast-enter-from,   .toast-leave-to     { opacity: 0; transform: translateY(8px); }
.card-enter-active,  .card-leave-active  { transition: all 0.3s ease; }
.card-enter-from                         { opacity: 0; transform: translateY(-6px); }
.card-leave-to                           { opacity: 0; transform: translateX(20px); }

@media (max-width: 600px) {
  .sp { padding: 1.25rem 1rem 3rem; }
  .sp-card__actions { flex-direction: column; }
  .sp-btn { justify-content: center; }
  .sp-summary { display: none; }
}
</style>