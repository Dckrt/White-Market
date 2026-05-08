<template>
  <div class="orders-page">
    <div class="orders-container">

      <div class="orders-header">
        <div class="orders-header__left">
          <div class="orders-header__icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/><path d="M9 12h6M9 16h4"/></svg>
          </div>
          <div>
            <h1 class="orders-header__title">My Orders</h1>
            <p class="orders-header__sub">Items you've purchased</p>
          </div>
        </div>
        <router-link to="/products" class="orders-header__btn">Browse More</router-link>
      </div>

      <div v-if="loading" class="orders-loading">
        <div class="orders-spinner"></div>
        <p>Loading orders…</p>
      </div>

      <div v-else-if="!orders.length" class="orders-empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2" stroke-linecap="round"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/></svg>
        <h3>No orders yet</h3>
        <p>Items you buy will appear here.</p>
        <router-link to="/products" class="orders-empty__btn">Start Shopping</router-link>
      </div>

      <div v-else class="orders-list">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-card__img-wrap">
            <img
              v-if="order.product_image"
              :src="order.product_image"
              class="order-card__img"
              :alt="order.product_title"
              @error="e => e.target.style.opacity = '0.1'"
            />
            <div v-else class="order-card__img order-card__img--empty">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            </div>
          </div>

          <div class="order-card__body">
            <div class="order-card__top">
              <div>
                <h3 class="order-card__title">{{ order.product_title }}</h3>
                <p class="order-card__seller">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
                  Seller: {{ order.seller_name || '—' }}
                </p>
              </div>
              <span :class="['order-card__status', `order-card__status--${order.status?.toLowerCase()}`]">
                {{ order.status }}
              </span>
            </div>

            <div class="order-card__details">
              <div class="order-card__detail">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
                ₱{{ fmtPrice(order.product_price) }}
              </div>
              <div class="order-card__detail">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
                {{ order.payment_method }}
              </div>
              <div class="order-card__detail" v-if="order.pickup_location">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ order.pickup_location }}
              </div>
              <div class="order-card__detail">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                {{ fmtDate(order.ordered_at) }}
              </div>
            </div>

            <div class="order-card__actions">
              <button class="order-card__chat-btn" @click="chatSeller(order)">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                Chat Seller
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const orders = ref([])
const loading = ref(true)
const user = JSON.parse(localStorage.getItem('user'))

const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })
const fmtDate  = (d) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
  catch { return d }
}

const chatSeller = (order) => {
  router.push({ path: '/messages', query: { seller_id: order.seller_id, seller_name: order.seller_name } })
}

onMounted(async () => {
  if (!user) return router.push('/auth')
  try {
    const res = await api.getMyOrders(user.user_id)
    orders.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('Orders fetch error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.orders-page { background: #f4f7fb; min-height: calc(100vh - 62px); padding: 2rem 1.5rem; }
.orders-container { max-width: 780px; margin: 0 auto; }

.orders-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 12px; }
.orders-header__left { display: flex; align-items: center; gap: 14px; }
.orders-header__icon { width: 50px; height: 50px; background: #eef3ff; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.orders-header__title { font-size: 1.4rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.orders-header__sub { font-size: 0.82rem; color: #888; margin: 0; }
.orders-header__btn { background: #003366; color: #FFD700; padding: 9px 20px; border-radius: 9px; font-weight: 700; font-size: 0.875rem; text-decoration: none; transition: 0.15s; }
.orders-header__btn:hover { background: #002244; }

.orders-loading { text-align: center; padding: 4rem; color: #888; }
.orders-spinner { width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #003366; border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

.orders-empty { text-align: center; padding: 4rem 2rem; background: #fff; border-radius: 16px; border: 1px solid #e8edf4; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.orders-empty h3 { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0; }
.orders-empty p  { color: #aaa; font-size: 0.9rem; margin: 0; }
.orders-empty__btn { background: #003366; color: #fff; padding: 10px 24px; border-radius: 9px; font-weight: 700; text-decoration: none; font-size: 0.9rem; }

.orders-list { display: flex; flex-direction: column; gap: 12px; }

.order-card { background: #fff; border: 1px solid #e8edf4; border-radius: 14px; padding: 16px; display: flex; gap: 16px; transition: box-shadow 0.15s; }
.order-card:hover { box-shadow: 0 4px 20px rgba(0,51,102,0.08); }

.order-card__img-wrap { flex-shrink: 0; }
.order-card__img { width: 90px; height: 90px; object-fit: cover; border-radius: 10px; background: #f0f4f8; display: flex; align-items: center; justify-content: center; }
.order-card__img--empty { border: 1px solid #e8edf4; }

.order-card__body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 8px; }
.order-card__top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.order-card__title { font-size: 0.975rem; font-weight: 700; color: #003366; margin: 0 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }
.order-card__seller { font-size: 0.78rem; color: #888; display: flex; align-items: center; gap: 4px; margin: 0; }

.order-card__status { font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; }
.order-card__status--pending   { background: #fef9e0; color: #854d0e; }
.order-card__status--completed { background: #e8f8f0; color: #15803d; }
.order-card__status--cancelled { background: #fee8e8; color: #b91c1c; }

.order-card__details { display: flex; flex-wrap: wrap; gap: 12px; }
.order-card__detail { display: flex; align-items: center; gap: 5px; font-size: 0.8rem; color: #555; }
.order-card__detail svg { color: #aaa; flex-shrink: 0; }

.order-card__actions { display: flex; gap: 8px; margin-top: auto; }
.order-card__chat-btn { display: inline-flex; align-items: center; gap: 6px; background: #eef3ff; color: #003366; border: none; padding: 7px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.order-card__chat-btn:hover { background: #003366; color: #FFD700; }

@media (max-width: 500px) {
  .order-card { flex-direction: column; }
  .order-card__img { width: 100%; height: 160px; }
}
</style>