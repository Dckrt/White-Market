<template>
  <div class="pd-page">

    <!-- LOADING -->
    <div v-if="loading" class="pd-loading">
      <div class="pd-spinner"></div>
      <p>Loading product…</p>
    </div>

    <!-- NOT FOUND -->
    <div v-else-if="!product" class="pd-notfound">
      <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="#c0cdd8" stroke-width="1.2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <h2>Product not found</h2>
      <p>This listing may have been removed.</p>
      <router-link to="/products" class="pd-back-btn">Back to Marketplace</router-link>
    </div>

    <!-- CONTENT -->
    <div v-else class="pd-container">

      <button class="pd-back" @click="router.back()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        Back
      </button>

      <!-- ── MAIN LAYOUT ── -->
      <div class="pd-layout">

        <!-- Images -->
        <div class="pd-images">
          <div class="pd-main-img-wrap">
            <img :src="activeImage" :alt="product.title" class="pd-main-img"
                 @error="e => e.target.src = '/placeholder.png'" />
            <template v-if="images.length > 1">
              <button class="pd-img-arrow pd-img-arrow--l" @click="prevImg">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
              </button>
              <button class="pd-img-arrow pd-img-arrow--r" @click="nextImg">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
              <span class="pd-img-counter">{{ activeIdx + 1 }}/{{ images.length }}</span>
            </template>
          </div>
          <div v-if="images.length > 1" class="pd-thumbs">
            <img v-for="(img, i) in images" :key="i" :src="img"
                 :class="['pd-thumb', i === activeIdx && 'pd-thumb--active']"
                 @click="activeIdx = i"
                 @error="e => e.target.src = '/placeholder.png'" />
          </div>
        </div>

        <!-- Info panel -->
        <div class="pd-info">
          <div class="pd-info__top">
            <span class="pd-category">{{ product.category }}</span>
            <span :class="['pd-status', product.status === 'Available' ? 'pd-status--avail' : 'pd-status--sold']">
              <span class="pd-status__dot"></span>{{ product.status }}
            </span>
          </div>

          <h1 class="pd-title">{{ product.title }}</h1>
          <div class="pd-price">₱{{ fmtPrice(product.price) }}</div>

          <div v-if="tags.length" class="pd-tags">
            <span v-for="tag in tags" :key="tag" class="pd-tag">
              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/></svg>
              {{ tag }}
            </span>
          </div>

          <div class="pd-desc-box" v-if="product.description">
            <h3 class="pd-desc-label">Description</h3>
            <p class="pd-desc-text">{{ product.description }}</p>
          </div>

          <!-- Seller -->
          <div class="pd-seller">
            <div class="pd-seller__av">{{ sellerInitial }}</div>
            <div class="pd-seller__info">
              <p class="pd-seller__name">{{ product.seller_name || 'ADNU Student' }}</p>
              <p class="pd-seller__sub">Verified Seller</p>
            </div>
          </div>

          <p class="pd-posted" v-if="product.created_at">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Posted {{ fmtDate(product.created_at) }}
          </p>

          <!-- Actions -->
          <div class="pd-actions" v-if="product.status === 'Available'">
            <template v-if="!isOwnProduct">
              <button class="pd-btn-buy" @click="showCheckout = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
                Buy Now
              </button>
              <button class="pd-btn-cart" @click="addToCart" :disabled="addingCart">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
                {{ addingCart ? 'Adding…' : 'Add to Cart' }}
              </button>
              <button class="pd-btn-chat" @click="chatSeller">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                Chat Seller
              </button>
            </template>
            <div v-else class="pd-own-notice">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              This is your listing.
              <router-link to="/dashboard">Manage in My Shop</router-link>
            </div>
          </div>
          <div v-else class="pd-sold-notice">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            This item has already been sold.
          </div>

          <div class="pd-safety">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Meet only in safe, public campus areas
          </div>
        </div>
      </div>

      <!-- ── BOTTOM PANELS ── -->
      <div class="pd-bottom">

        <!-- Price history chart -->
        <div class="pd-panel" v-if="history.length">
          <h3 class="pd-panel__title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Price Trend
          </h3>
          <div class="pd-chart-wrap">
            <Line :data="chartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Rate seller -->
        <div class="pd-panel" v-if="!isOwnProduct">
          <h3 class="pd-panel__title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            Rate this Seller
          </h3>

          <div class="pd-stars">
            <button
              v-for="i in 5" :key="i"
              class="pd-star"
              :class="{ 'pd-star--on': i <= (hoverRating || selectedRating) }"
              @click="toggleRating(i)"
              @mouseenter="hoverRating = i"
              @mouseleave="hoverRating = 0"
              type="button"
            >★</button>
          </div>
          <p class="pd-star-hint" v-if="selectedRating">
            {{ ['','Poor','Fair','Good','Great','Excellent!'][selectedRating] }}
          </p>

          <textarea
            v-model="reviewComment"
            class="pd-review-textarea"
            placeholder="Share your experience with this seller (optional)…"
            rows="3"
          ></textarea>

          <button class="pd-submit-review" @click="submitReview" :disabled="submittingReview || !selectedRating">
            <svg v-if="!submittingReview" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span v-else class="pd-btn-spinner"></span>
            {{ submittingReview ? 'Submitting…' : 'Submit Review' }}
          </button>
        </div>

      </div>
    </div>

    <!-- ── CHECKOUT MODAL ── -->
    <Transition name="modal">
      <div v-if="showCheckout && product" class="modal-backdrop" @click.self="showCheckout = false">
        <div class="modal-box">
          <button class="modal-close" @click="showCheckout = false">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>

          <h2 class="modal-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
            Place Order
          </h2>

          <div class="modal-preview">
            <img :src="activeImage" class="modal-preview__img" @error="e => e.target.src = '/placeholder.png'" />
            <div>
              <p class="modal-preview__title">{{ product.title }}</p>
              <p class="modal-preview__seller">Seller: {{ product.seller_name }}</p>
              <p class="modal-preview__price">₱{{ fmtPrice(product.price) }}</p>
            </div>
          </div>

          <div class="modal-divider"></div>

          <div class="modal-field">
            <label>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              Pickup Location
            </label>
            <select v-model="checkout.location" class="modal-select">
              <option>Xavier Hall</option>
              <option>Library</option>
              <option>Bonoan</option>
              <option>Coko Cafe</option>
              <option>Alingal</option>
              <option>CCS Building</option>
              <option>Gonzaga Hall</option>
            </select>
          </div>

          <div class="modal-field">
            <label>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
              Payment Method
            </label>
            <div class="modal-pay-opts">
              <button v-for="m in payMethods" :key="m" type="button"
                :class="['modal-pay-opt', checkout.payment === m && 'modal-pay-opt--on']"
                @click="checkout.payment = m">{{ m }}</button>
            </div>
          </div>

          <div v-if="checkout.payment === 'Cash'" class="modal-pay-info">
            Pay in cash upon meetup at the pickup location.
          </div>
          <div v-else-if="checkout.payment === 'GCash'" class="modal-pay-info modal-pay-info--gcash">
            <span v-if="sellerPayment.gcash">GCash: <strong>{{ sellerPayment.gcash }}</strong></span>
            <span v-else>GCash number not set — coordinate with seller via chat.</span>
          </div>
          <div v-else-if="checkout.payment === 'Bank Transfer'" class="modal-pay-info modal-pay-info--bank">
            <span v-if="sellerPayment.bank">Bank: <strong>{{ sellerPayment.bank }}</strong></span>
            <span v-else>Bank details not set — coordinate with seller via chat.</span>
          </div>

          <div class="modal-total">
            <span>Total Amount</span>
            <span class="modal-total__price">₱{{ fmtPrice(product.price) }}</span>
          </div>

          <button class="modal-submit" @click="placeOrder" :disabled="placingOrder">
            <svg v-if="!placingOrder" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            <span v-else class="pd-btn-spinner"></span>
            {{ placingOrder ? 'Placing Order…' : 'Confirm Order' }}
          </button>

          <p class="modal-safety">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Meet only in safe, public campus areas
          </p>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['pd-toast', `pd-toast--${toast.type}`]">
        <svg v-if="toast.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ toast.text }}
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart, CategoryScale, LinearScale,
  PointElement, LineElement, Tooltip, Legend, Filler
} from 'chart.js'
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const route  = useRoute()
const user   = JSON.parse(localStorage.getItem('user') || 'null')

// ── State ──────────────────────────────────────────────────────────────────
const product         = ref(null)
const loading         = ref(true)
const activeIdx       = ref(0)
const addingCart      = ref(false)
const showCheckout    = ref(false)
const placingOrder    = ref(false)
const sellerPayment   = ref({ gcash: null, bank: null })
const history         = ref([])
const chartData       = ref(null)
const selectedRating  = ref(0)
const hoverRating     = ref(0)
const reviewComment   = ref('')
const submittingReview = ref(false)
const checkout        = ref({ location: 'Xavier Hall', payment: 'Cash' })
const payMethods      = ['Cash', 'GCash', 'Bank Transfer']
const toast           = ref({ show: false, text: '', type: 'success' })
let toastTimer        = null

// ── Toast (replaces all alert() calls) ────────────────────────────────────
const showToast = (text, type = 'success') => {
  clearTimeout(toastTimer)
  toast.value = { show: true, text, type }
  toastTimer  = setTimeout(() => toast.value.show = false, 3200)
}

// ── Computed ───────────────────────────────────────────────────────────────
const images = computed(() => {
  if (!product.value) return []
  if (product.value.images?.length) return product.value.images
  if (product.value.image_url) return [product.value.image_url]
  return ['/placeholder.png']
})
const activeImage = computed(() => images.value[activeIdx.value] || '/placeholder.png')
const tags = computed(() => {
  if (!product.value) return []
  if (Array.isArray(product.value.tags)) return product.value.tags.filter(Boolean)
  if (typeof product.value.tags === 'string') return product.value.tags.split(',').map(t => t.trim()).filter(Boolean)
  return []
})
const sellerInitial = computed(() => (product.value?.seller_name || 'A').charAt(0).toUpperCase())
const isOwnProduct  = computed(() => user && product.value && Number(user.user_id) === Number(product.value.seller_id))

// ── Chart options ──────────────────────────────────────────────────────────
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: ctx => ` ₱${Number(ctx.parsed.y).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
      }
    }
  },
  scales: {
    x: { grid: { display: false } },
    y: {
      beginAtZero: false,
      ticks: { callback: v => `₱${Number(v).toLocaleString('en-PH')}` }
    }
  }
}

// ── Image navigation ───────────────────────────────────────────────────────
const prevImg = () => activeIdx.value = activeIdx.value === 0 ? images.value.length - 1 : activeIdx.value - 1
const nextImg = () => activeIdx.value = activeIdx.value === images.value.length - 1 ? 0 : activeIdx.value + 1

// ── Formatters ─────────────────────────────────────────────────────────────
const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })
const fmtDate  = (d) => {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' }) }
  catch { return d }
}

// ── Cart ───────────────────────────────────────────────────────────────────
const addToCart = async () => {
  if (!user) return router.push('/auth')
  addingCart.value = true
  try {
    await api.addToCart({ user_id: user.user_id, product_id: product.value.id })
    showToast(`"${product.value.title}" added to cart!`)
  } catch (err) {
    showToast(err.response?.data?.message || 'Failed to add to cart', 'error')
  } finally {
    addingCart.value = false
  }
}

// ── Chat ───────────────────────────────────────────────────────────────────
const chatSeller = () => {
  if (!user) return router.push('/auth')
  router.push({ path: '/messages', query: { seller_id: product.value.seller_id, seller_name: product.value.seller_name } })
}

// ── Checkout ───────────────────────────────────────────────────────────────
const placeOrder = async () => {
  if (!user) { showCheckout.value = false; return router.push('/auth') }
  placingOrder.value = true
  try {
    await api.checkout({
      user_id:    user.user_id,
      product_id: product.value.id,
      payment:    checkout.value.payment,
      location:   checkout.value.location,
    })
    showCheckout.value = false
    showToast(`Order placed! Meet seller at ${checkout.value.location}`)
    // Refresh product status
    const res = await api.getProduct(product.value.id)
    product.value = res.data
  } catch (err) {
    showToast(err.response?.data?.message || 'Failed to place order', 'error')
  } finally {
    placingOrder.value = false
  }
}

// ── Rating ─────────────────────────────────────────────────────────────────
const toggleRating = (i) => {
  selectedRating.value = selectedRating.value === i ? 0 : i
}

// ── Submit review ──────────────────────────────────────────────────────────
// FIX: was previously defined inside placeOrder() — now correctly at top level
const submitReview = async () => {
  if (!user) return router.push('/auth')
  if (!selectedRating.value) {
    showToast('Please select a star rating first', 'error')
    return
  }
  submittingReview.value = true
  try {
    await api.addReview({
      reviewer_id:  user.user_id,
      seller_id:    product.value.seller_id,
      rating:       selectedRating.value,
      comment_text: reviewComment.value,
    })
    showToast('Review submitted! ⭐')
    selectedRating.value = 0
    reviewComment.value  = ''
  } catch (err) {
    showToast(err.response?.data?.message || 'Failed to submit review', 'error')
  } finally {
    submittingReview.value = false
  }
}

// ── Load ───────────────────────────────────────────────────────────────────
onMounted(async () => {
  const id = route.params.id
  if (!id) { loading.value = false; return }
  try {
    // FIX: fetch product first, THEN build chartData — previous code built
    // chartData before product.value was set which caused silent failures.
    const [productRes, histRes] = await Promise.all([
      api.getProduct(id),
      api.getPriceHistory(id).catch(() => ({ data: [] })),
    ])

    product.value = productRes.data
    history.value = histRes.data || []

    // Build chart only if there's more than one data point (single point = no trend)
    if (history.value.length > 1) {
      chartData.value = {
        labels: history.value.map(h =>
          new Date(h.recorded_at || h.changed_at || h.date)
            .toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
        ),
        datasets: [{
          label: 'Price',
          data: history.value.map(h => Number(h.price || h.new_price)),
          borderColor: '#003366',
          backgroundColor: 'rgba(0,51,102,0.08)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#FFD700',
          pointBorderColor: '#003366',
          pointBorderWidth: 2,
          pointRadius: 4,
        }]
      }
    }

    // Load seller payment details (non-blocking)
    if (product.value?.seller_id) {
      api.getSellerPayment(product.value.seller_id)
        .then(r => { sellerPayment.value = r.data || { gcash: null, bank: null } })
        .catch(() => {})
    }
  } catch {
    product.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@keyframes spin    { to { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -600px 0; } 100% { background-position: 600px 0; } }

.pd-page {
  background: #f4f7fb;
  min-height: calc(100vh - 62px);
  padding: 1.5rem;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}

/* ── Loading / Not found ──────────────────────────────────────────────── */
.pd-loading { text-align: center; padding: 5rem; color: #888; }
.pd-spinner { width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #003366; border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto 1rem; }

.pd-notfound { text-align: center; padding: 5rem 2rem; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.pd-notfound h2 { font-size: 1.3rem; font-weight: 800; color: #003366; margin: 0; }
.pd-notfound p  { color: #aaa; font-size: 0.875rem; margin: 0; }
.pd-back-btn { background: #003366; color: #FFD700; padding: 10px 24px; border-radius: 9px; font-weight: 700; text-decoration: none; font-size: 0.875rem; margin-top: 4px; }

/* ── Container ────────────────────────────────────────────────────────── */
.pd-container { max-width: 1020px; margin: 0 auto; }

.pd-back {
  display: inline-flex; align-items: center; gap: 6px;
  background: #fff; border: 1px solid #e0e8f4; color: #003366;
  padding: 7px 14px; border-radius: 8px; font-size: 0.85rem;
  font-weight: 600; cursor: pointer; margin-bottom: 1.25rem;
  transition: 0.15s; font-family: inherit;
}
.pd-back:hover { background: #eef3ff; }

/* ── Main layout ──────────────────────────────────────────────────────── */
.pd-layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
  background: #fff; border-radius: 20px; padding: 2rem;
  border: 1px solid #e8edf4; box-shadow: 0 4px 24px rgba(0,51,102,0.06);
}

/* ── Images ───────────────────────────────────────────────────────────── */
.pd-images { display: flex; flex-direction: column; gap: 12px; }
.pd-main-img-wrap { position: relative; border-radius: 14px; overflow: hidden; aspect-ratio: 1; background: #f0f4f8; }
.pd-main-img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s; }
.pd-main-img:hover { transform: scale(1.02); }
.pd-img-arrow { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,51,102,0.75); color: #FFD700; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.15s; z-index: 5; }
.pd-img-arrow--l { left: 10px; }
.pd-img-arrow--r { right: 10px; }
.pd-img-arrow:hover { background: #003366; transform: translateY(-50%) scale(1.05); }
.pd-img-counter { position: absolute; bottom: 10px; right: 12px; background: rgba(0,0,0,0.5); color: #fff; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 10px; }
.pd-thumbs { display: flex; gap: 8px; flex-wrap: wrap; }
.pd-thumb { width: 64px; height: 64px; object-fit: cover; border-radius: 9px; cursor: pointer; border: 2.5px solid transparent; transition: 0.15s; opacity: 0.65; }
.pd-thumb:hover { opacity: 0.9; }
.pd-thumb--active { border-color: #003366; opacity: 1; }

/* ── Info panel ───────────────────────────────────────────────────────── */
.pd-info { display: flex; flex-direction: column; gap: 14px; }
.pd-info__top { display: flex; align-items: center; gap: 8px; }
.pd-category { background: #e8f0fe; color: #003366; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; }
.pd-status { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
.pd-status--avail { background: #e8f8f0; color: #15803d; }
.pd-status--sold  { background: #fee8e8; color: #b91c1c; }
.pd-status__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

.pd-title { font-size: 1.55rem; font-weight: 900; color: #003366; margin: 0; line-height: 1.25; letter-spacing: -0.3px; }
.pd-price { font-size: 2rem; font-weight: 900; color: #003366; letter-spacing: -0.5px; }

.pd-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.pd-tag { display: inline-flex; align-items: center; gap: 4px; background: #eef3ff; color: #003366; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }

.pd-desc-box { background: #f8fafc; border-radius: 12px; padding: 14px 16px; border: 1px solid #e8edf4; }
.pd-desc-label { font-size: 0.72rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 7px; }
.pd-desc-text  { font-size: 0.9rem; color: #444; margin: 0; line-height: 1.65; white-space: pre-wrap; }

.pd-seller { display: flex; align-items: center; gap: 12px; background: #f8fafc; border-radius: 12px; padding: 12px 14px; border: 1px solid #e8edf4; }
.pd-seller__av { width: 42px; height: 42px; border-radius: 50%; background: #003366; color: #FFD700; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 900; flex-shrink: 0; border: 2px solid #FFD700; }
.pd-seller__name { font-size: 0.9rem; font-weight: 700; color: #003366; margin: 0 0 2px; }
.pd-seller__sub  { font-size: 0.72rem; color: #aaa; margin: 0; }

.pd-posted { display: flex; align-items: center; gap: 5px; font-size: 0.75rem; color: #bbb; margin: 0; }

/* Actions */
.pd-actions { display: flex; flex-direction: column; gap: 10px; }
.pd-btn-buy {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: #FFD700; color: #003366; border: none; padding: 14px;
  border-radius: 12px; font-size: 1rem; font-weight: 800; cursor: pointer;
  transition: 0.15s; font-family: inherit;
}
.pd-btn-buy:hover { background: #e6c200; transform: translateY(-1px); box-shadow: 0 6px 20px rgba(255,215,0,0.35); }

.pd-btn-cart {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: #003366; color: #fff; border: none; padding: 12px;
  border-radius: 12px; font-size: 0.9rem; font-weight: 700; cursor: pointer;
  transition: 0.15s; font-family: inherit;
}
.pd-btn-cart:hover:not(:disabled) { background: #002244; transform: translateY(-1px); }
.pd-btn-cart:disabled { opacity: 0.55; cursor: not-allowed; }

.pd-btn-chat {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: #fff; color: #003366; border: 1.5px solid #d0dbe8;
  padding: 11px; border-radius: 12px; font-size: 0.9rem; font-weight: 700;
  cursor: pointer; transition: 0.15s; font-family: inherit;
}
.pd-btn-chat:hover { background: #eef3ff; border-color: #003366; }

.pd-own-notice { display: flex; align-items: center; gap: 8px; background: #fef9e0; color: #854d0e; font-size: 0.82rem; font-weight: 600; padding: 11px 14px; border-radius: 10px; flex-wrap: wrap; }
.pd-own-notice a { color: #003366; font-weight: 700; }
.pd-sold-notice { display: flex; align-items: center; gap: 8px; background: #fee8e8; color: #b91c1c; font-size: 0.85rem; font-weight: 600; padding: 12px 14px; border-radius: 10px; }
.pd-safety { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #bbb; }

/* ── Bottom panels ────────────────────────────────────────────────────── */
.pd-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-top: 1.25rem; }

.pd-panel { background: #fff; border: 1px solid #e8edf4; border-radius: 16px; padding: 20px; }
.pd-panel__title {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.95rem; font-weight: 800; color: #003366; margin: 0 0 16px;
}

/* Chart */
.pd-chart-wrap { height: 180px; }

/* Stars */
.pd-stars { display: flex; gap: 6px; margin-bottom: 8px; }
.pd-star {
  font-size: 28px; background: none; border: none; cursor: pointer;
  color: #d1d5db; transition: color 0.1s, transform 0.1s; line-height: 1;
  padding: 0;
}
.pd-star--on { color: #fbbf24; }
.pd-star:hover { transform: scale(1.15); }

.pd-star-hint { font-size: 0.78rem; font-weight: 700; color: #fbbf24; margin: 0 0 10px; }

.pd-review-textarea {
  width: 100%; min-height: 80px; border: 1.5px solid #e0e8f4; border-radius: 10px;
  padding: 10px 12px; resize: vertical; font-size: 0.875rem; color: #333;
  font-family: inherit; outline: none; background: #fafcff; transition: 0.15s;
  box-sizing: border-box; margin-bottom: 12px;
}
.pd-review-textarea:focus { border-color: #003366; }

.pd-submit-review {
  display: flex; align-items: center; gap: 7px;
  background: #003366; color: #FFD700; border: none;
  padding: 10px 18px; border-radius: 9px; font-size: 0.85rem;
  font-weight: 700; cursor: pointer; font-family: inherit; transition: 0.15s;
}
.pd-submit-review:hover:not(:disabled) { background: #002244; }
.pd-submit-review:disabled { opacity: 0.5; cursor: not-allowed; }

/* Spinner inside buttons */
.pd-btn-spinner {
  display: inline-block; width: 13px; height: 13px;
  border: 2px solid rgba(255,215,0,0.3); border-top-color: #FFD700;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

/* ── Modal ────────────────────────────────────────────────────────────── */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-box { background: #fff; border-radius: 20px; width: 100%; max-width: 440px; padding: 1.75rem; position: relative; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.modal-close { position: absolute; top: 16px; right: 16px; width: 32px; height: 32px; background: #f0f4f8; border: none; border-radius: 8px; color: #666; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.15s; }
.modal-close:hover { background: #e74c3c; color: #fff; }
.modal-title { font-size: 1.15rem; font-weight: 800; color: #003366; margin: 0 0 1.25rem; display: flex; align-items: center; gap: 8px; }
.modal-preview { display: flex; gap: 12px; background: #f8fafc; border-radius: 12px; padding: 12px; margin-bottom: 1rem; border: 1px solid #e8edf4; }
.modal-preview__img    { width: 72px; height: 72px; object-fit: cover; border-radius: 9px; flex-shrink: 0; }
.modal-preview__title  { font-size: 0.9rem; font-weight: 700; color: #003366; margin: 0 0 4px; }
.modal-preview__seller { font-size: 0.72rem; color: #888; margin: 0 0 4px; }
.modal-preview__price  { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0; }
.modal-divider { height: 1px; background: #f0f0f0; margin: 0.5rem 0 1rem; }
.modal-field { margin-bottom: 14px; }
.modal-field label { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 7px; }
.modal-select { width: 100%; padding: 10px 12px; border: 1.5px solid #dce4ee; border-radius: 9px; font-size: 0.875rem; color: #333; background: #f8fafc; outline: none; font-family: inherit; }
.modal-select:focus { border-color: #003366; }
.modal-pay-opts { display: flex; gap: 8px; }
.modal-pay-opt { flex: 1; padding: 9px 6px; border: 1.5px solid #e5e7eb; border-radius: 8px; background: #f8fafc; font-size: 0.72rem; font-weight: 700; color: #666; cursor: pointer; transition: 0.15s; font-family: inherit; }
.modal-pay-opt:hover { border-color: #003366; color: #003366; }
.modal-pay-opt--on { background: #003366; color: #FFD700; border-color: #003366; }
.modal-pay-info { font-size: 0.8rem; font-weight: 600; padding: 10px 12px; border-radius: 8px; margin-bottom: 14px; background: #f0fdf4; color: #15803d; }
.modal-pay-info--gcash { background: #e8f0fe; color: #185FA5; }
.modal-pay-info--bank  { background: #fffbeb; color: #92400e; }
.modal-total { display: flex; justify-content: space-between; align-items: center; font-weight: 800; color: #003366; background: #f8fafc; border-radius: 10px; padding: 12px 16px; margin-bottom: 1rem; font-size: 0.95rem; }
.modal-total__price { font-size: 1.2rem; }
.modal-submit { width: 100%; background: #FFD700; color: #003366; border: none; padding: 14px; border-radius: 12px; font-weight: 800; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.15s; margin-bottom: 10px; font-family: inherit; }
.modal-submit:hover:not(:disabled) { background: #e6c200; transform: translateY(-1px); }
.modal-submit:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
.modal-safety { text-align: center; font-size: 0.72rem; color: #aaa; display: flex; align-items: center; justify-content: center; gap: 5px; margin: 0; }

/* ── Toast ────────────────────────────────────────────────────────────── */
.pd-toast { position: fixed; bottom: 24px; right: 24px; padding: 12px 16px; border-radius: 10px; font-size: 0.875rem; font-weight: 600; z-index: 9999; box-shadow: 0 8px 24px rgba(0,0,0,0.12); display: flex; align-items: center; gap: 8px; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.pd-toast--success { background: #fff; border: 1.5px solid #16a34a; color: #15803d; }
.pd-toast--error   { background: #fff; border: 1.5px solid #dc2626; color: #991b1b; }

/* ── Transitions ──────────────────────────────────────────────────────── */
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from,   .modal-leave-to     { opacity: 0; transform: scale(0.95); }
.toast-enter-active, .toast-leave-active { transition: all 0.2s; }
.toast-enter-from,   .toast-leave-to     { opacity: 0; transform: translateY(8px); }

/* ── Responsive ───────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .pd-layout { grid-template-columns: 1fr; padding: 1.25rem; gap: 1.25rem; }
  .pd-bottom { grid-template-columns: 1fr; }
  .pd-title  { font-size: 1.25rem; }
  .pd-price  { font-size: 1.5rem; }
}
</style>