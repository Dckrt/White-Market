<template>
  <div class="orders-page">
    <div class="orders-container">

      <!-- Header -->
      <div class="orders-header">
        <div class="orders-header__left">
          <div class="orders-header__icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
              <rect x="9" y="3" width="6" height="4" rx="2"/>
              <path d="M9 12h6M9 16h4"/>
            </svg>
          </div>
          <div>
            <h1 class="orders-header__title">My Orders</h1>
            <p class="orders-header__sub">
              {{ orders.length }} order{{ orders.length !== 1 ? 's' : '' }} placed
            </p>
          </div>
        </div>
        <router-link to="/products" class="orders-header__btn">Browse More</router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="orders-loading">
        <div class="orders-spinner"></div>
        <p>Loading orders…</p>
      </div>

      <!-- Empty -->
      <div v-else-if="!orders.length" class="orders-empty">
        <div class="orders-empty__icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#c0cdd8" stroke-width="1.4" stroke-linecap="round">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="2"/>
          </svg>
        </div>
        <h3>No orders yet</h3>
        <p>Items you buy will appear here.</p>
        <router-link to="/products" class="orders-empty__btn">Start Shopping</router-link>
      </div>

      <!-- Orders List -->
      <div v-else class="orders-list">
        <TransitionGroup name="order-item">
          <div v-for="order in orders" :key="order.id" class="order-card">

            <!-- Image -->
            <div class="order-card__img-wrap">
              <img
                v-if="order.product_image"
                :src="order.product_image"
                class="order-card__img"
                :alt="order.product_title"
                @error="e => e.target.style.opacity = '0.1'"
              />
              <div v-else class="order-card__img order-card__img--empty">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
            </div>

            <!-- Body -->
            <div class="order-card__body">
              <div class="order-card__top">
                <div class="order-card__title-wrap">
                  <h3 class="order-card__title">{{ order.product_title }}</h3>
                  <p class="order-card__seller">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                    </svg>
                    {{ order.seller_name || '—' }}
                  </p>
                </div>
                <span :class="['order-card__status', statusClass(order.status)]">
                  <span class="order-card__status-dot"></span>
                  {{ order.status }}
                </span>
              </div>

              <!-- Details -->
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

              <!-- Actions -->
              <div class="order-card__actions">
                <button class="order-card__chat-btn" @click="chatSeller(order)">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                  Chat Seller
                </button>
                <button
                  v-if="order.status === 'Completed'"
                  class="order-card__rate-btn"
                  @click="openReview(order)"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z"/></svg>
                  Rate Seller
                </button>
              </div>
            </div>

          </div>
        </TransitionGroup>
      </div>

    </div>
  </div>

  <!-- ── REVIEW MODAL ── -->
  <Transition name="modal">
    <div v-if="showReviewModal" class="modal-backdrop" @click.self="closeReview">
      <div class="modal-box">
        <button class="modal-close" @click="closeReview">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>

        <div class="modal-head">
          <div class="modal-head__icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#FFD700"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z"/></svg>
          </div>
          <div>
            <h2 class="modal-title">Rate Seller</h2>
            <p class="modal-sub">{{ selectedOrder?.seller_name }}</p>
          </div>
        </div>

        <!-- Product preview -->
        <div class="modal-product">
          <img
            v-if="selectedOrder?.product_image"
            :src="selectedOrder.product_image"
            class="modal-product__img"
            @error="e => e.target.style.display='none'"
          />
          <div class="modal-product__info">
            <p class="modal-product__title">{{ selectedOrder?.product_title }}</p>
            <p class="modal-product__price">₱{{ fmtPrice(selectedOrder?.product_price) }}</p>
          </div>
        </div>

        <div class="modal-divider"></div>

        <!-- Star rating -->
        <div class="review-section">
          <label class="review-label">Your Rating <span class="review-req">*</span></label>
          <div class="stars-wrap">
            <button
              v-for="i in 5"
              :key="i"
              class="star-btn"
              :class="{ 'star-btn--on': i <= selectedRating, 'star-btn--hover': i <= hoverRating }"
              @click="selectedRating = i"
              @mouseenter="hoverRating = i"
              @mouseleave="hoverRating = 0"
              type="button"
            >
              <svg width="28" height="28" viewBox="0 0 24 24" :fill="i <= (hoverRating || selectedRating) ? '#FFD700' : 'none'" :stroke="i <= (hoverRating || selectedRating) ? '#FFD700' : '#d1d5db'" stroke-width="1.5">
                <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z"/>
              </svg>
            </button>
          </div>
          <p class="rating-label">
            {{ ratingLabel }}
          </p>
        </div>

        <!-- Comment -->
        <div class="review-section">
          <label class="review-label">Your Review <span class="review-hint">(optional)</span></label>
          <textarea
            v-model="reviewComment"
            class="review-textarea"
            placeholder="Share your experience with this seller…"
            rows="3"
            maxlength="500"
          ></textarea>
          <p class="char-count">{{ reviewComment.length }}/500</p>
        </div>

        <!-- Submit -->
        <button class="submit-btn" @click="submitReview" :disabled="submitting || selectedRating === 0">
          <svg v-if="!submitting" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
          <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          {{ submitting ? 'Submitting…' : 'Submit Review' }}
        </button>

        <p v-if="selectedRating === 0" class="review-warn">Please select a star rating to continue.</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const orders         = ref([])
const loading        = ref(true)
const showReviewModal = ref(false)
const selectedOrder  = ref(null)
const selectedRating = ref(0)
const hoverRating    = ref(0)
const reviewComment  = ref('')
const submitting     = ref(false)
const user = JSON.parse(localStorage.getItem('user'))

const ratingLabels = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
const ratingLabel = computed(() => ratingLabels[hoverRating.value || selectedRating.value] || 'Select a rating')

const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })
const fmtDate  = (d) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
  catch { return d }
}

const statusClass = (status) => ({
  'pending':   'order-card__status--pending',
  'completed': 'order-card__status--completed',
  'cancelled': 'order-card__status--cancelled',
}[status?.toLowerCase()] || 'order-card__status--pending')

const chatSeller = (order) => {
  router.push({ path: '/messages', query: { seller_id: order.seller_id, seller_name: order.seller_name } })
}

const openReview = (order) => {
  selectedOrder.value  = order
  selectedRating.value = 0
  hoverRating.value    = 0
  reviewComment.value  = ''
  showReviewModal.value = true
}

const closeReview = () => {
  showReviewModal.value = false
  selectedOrder.value   = null
}

const submitReview = async () => {
  if (selectedRating.value === 0) return
  submitting.value = true
  try {
    await api.addReview({
      reviewer_id:  user.user_id,
      seller_id:    selectedOrder.value.seller_id,
      rating:       selectedRating.value,
      comment_text: reviewComment.value,
    })
    alert('Review submitted! ⭐')
    closeReview()
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to submit review')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if (!user) return router.push('/auth')
  try {
    const res = await api.getOrders(user.user_id)
    orders.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('Orders fetch error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; transform-origin: center; }

.orders-page { background: #f4f7fb; min-height: calc(100vh - 62px); padding: 2rem 1.5rem; }
.orders-container { max-width: 780px; margin: 0 auto; }

/* Header */
.orders-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 12px; }
.orders-header__left { display: flex; align-items: center; gap: 14px; }
.orders-header__icon { width: 50px; height: 50px; background: #eef3ff; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.orders-header__title { font-size: 1.4rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.orders-header__sub { font-size: 0.82rem; color: #888; margin: 0; }
.orders-header__btn { background: #003366; color: #FFD700; padding: 9px 20px; border-radius: 9px; font-weight: 700; font-size: 0.875rem; text-decoration: none; transition: 0.15s; }
.orders-header__btn:hover { background: #002244; }

/* Loading */
.orders-loading { text-align: center; padding: 4rem; color: #888; }
.orders-spinner { width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #003366; border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto 1rem; }

/* Empty */
.orders-empty { text-align: center; padding: 4rem 2rem; background: #fff; border-radius: 16px; border: 1px solid #e8edf4; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.orders-empty__icon { width: 80px; height: 80px; background: #f0f4f8; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 4px; }
.orders-empty h3 { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0; }
.orders-empty p  { color: #aaa; font-size: 0.9rem; margin: 0; }
.orders-empty__btn { background: #003366; color: #fff; padding: 10px 24px; border-radius: 9px; font-weight: 700; text-decoration: none; font-size: 0.9rem; transition: 0.15s; }
.orders-empty__btn:hover { background: #002244; }

/* List */
.orders-list { display: flex; flex-direction: column; gap: 12px; }

.order-card { background: #fff; border: 1px solid #e8edf4; border-radius: 14px; padding: 16px; display: flex; gap: 16px; transition: box-shadow 0.15s, transform 0.15s; }
.order-card:hover { box-shadow: 0 4px 20px rgba(0,51,102,0.08); transform: translateY(-1px); }

.order-card__img-wrap { flex-shrink: 0; }
.order-card__img { width: 90px; height: 90px; object-fit: cover; border-radius: 10px; background: #f0f4f8; display: flex; align-items: center; justify-content: center; }
.order-card__img--empty { border: 1px solid #e8edf4; }

.order-card__body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 8px; }
.order-card__top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.order-card__title-wrap { min-width: 0; flex: 1; }
.order-card__title { font-size: 0.975rem; font-weight: 700; color: #003366; margin: 0 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.order-card__seller { font-size: 0.78rem; color: #888; display: flex; align-items: center; gap: 4px; margin: 0; }

.order-card__status { font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; display: flex; align-items: center; gap: 5px; }
.order-card__status-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; flex-shrink: 0; }
.order-card__status--pending   { background: #fef9e0; color: #854d0e; }
.order-card__status--completed { background: #e8f8f0; color: #15803d; }
.order-card__status--cancelled { background: #fee8e8; color: #b91c1c; }

.order-card__details { display: flex; flex-wrap: wrap; gap: 12px; }
.order-card__detail { display: flex; align-items: center; gap: 5px; font-size: 0.8rem; color: #555; }
.order-card__detail svg { color: #aaa; flex-shrink: 0; }

.order-card__actions { display: flex; gap: 8px; margin-top: auto; flex-wrap: wrap; }
.order-card__chat-btn { display: inline-flex; align-items: center; gap: 6px; background: #eef3ff; color: #003366; border: none; padding: 7px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.order-card__chat-btn:hover { background: #003366; color: #FFD700; }
.order-card__rate-btn { display: inline-flex; align-items: center; gap: 6px; background: #fff8e0; color: #b45309; border: 1px solid #fcd34d; padding: 7px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.order-card__rate-btn:hover { background: #FFD700; color: #003366; border-color: #FFD700; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-box { background: #fff; border-radius: 20px; width: 100%; max-width: 440px; padding: 1.75rem; position: relative; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.2); display: flex; flex-direction: column; gap: 1rem; }
.modal-close { position: absolute; top: 16px; right: 16px; width: 32px; height: 32px; background: #f0f4f8; border: none; border-radius: 8px; color: #666; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.15s; }
.modal-close:hover { background: #e74c3c; color: #fff; }

.modal-head { display: flex; align-items: center; gap: 12px; }
.modal-head__icon { width: 44px; height: 44px; background: #fff8e0; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.modal-title { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.modal-sub { font-size: 0.8rem; color: #888; margin: 0; }

.modal-product { display: flex; gap: 12px; background: #f8fafc; border-radius: 12px; padding: 12px; border: 1px solid #e8edf4; }
.modal-product__img { width: 56px; height: 56px; object-fit: cover; border-radius: 8px; flex-shrink: 0; }
.modal-product__title { font-size: 0.875rem; font-weight: 700; color: #003366; margin: 0 0 4px; }
.modal-product__price { font-size: 0.9rem; font-weight: 800; color: #003366; margin: 0; }
.modal-divider { height: 1px; background: #f0f4f8; }

.review-section { display: flex; flex-direction: column; gap: 6px; }
.review-label { font-size: 0.75rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.4px; }
.review-req   { color: #e74c3c; }
.review-hint  { color: #aaa; font-weight: 400; text-transform: none; letter-spacing: 0; }

.stars-wrap { display: flex; gap: 4px; }
.star-btn { background: none; border: none; cursor: pointer; padding: 2px; transition: transform 0.12s; }
.star-btn:hover { transform: scale(1.15); }

.rating-label { font-size: 0.82rem; font-weight: 600; color: #b45309; margin: 0; min-height: 1.2em; }

.review-textarea { padding: 10px 12px; border: 1.5px solid #e0e8f4; border-radius: 9px; font-size: 0.875rem; color: #1a1a2e; outline: none; font-family: inherit; resize: vertical; transition: border-color 0.15s; width: 100%; box-sizing: border-box; }
.review-textarea:focus { border-color: #003366; }
.char-count { font-size: 0.72rem; color: #aaa; text-align: right; margin: 0; }

.submit-btn { width: 100%; background: #FFD700; color: #003366; border: none; padding: 13px; border-radius: 12px; font-weight: 800; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.15s; font-family: inherit; }
.submit-btn:hover:not(:disabled) { background: #e6c200; transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.review-warn { text-align: center; font-size: 0.78rem; color: #e74c3c; margin: 0; }

/* Transitions */
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
.order-item-enter-active, .order-item-leave-active { transition: all 0.3s ease; }
.order-item-enter-from { opacity: 0; transform: translateY(-8px); }
.order-item-leave-to   { opacity: 0; transform: translateX(20px); }

@media (max-width: 500px) {
  .order-card { flex-direction: column; }
  .order-card__img { width: 100%; height: 160px; }
}
</style>