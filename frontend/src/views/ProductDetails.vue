<template>
  <div v-if="product" class="details-wrapper">
    <div class="container">

      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <button @click="$router.push('/')" class="crumb">Home</button>
        <span class="crumb-sep">/</span>
        <button @click="$router.push('/products')" class="crumb">Market</button>
        <span class="crumb-sep">/</span>
        <span class="crumb active">{{ product.title }}</span>
      </div>

      <div class="details-grid">

        <!-- LEFT -->
        <div class="left-col">
          <div class="image-box">
            <img :src="product.image_url || '/placeholder.png'" class="main-img" :alt="product.title" />
            <span class="cat-badge">{{ product.category }}</span>
          </div>

          <div class="desc-card">
            <h3 class="section-label">
              <i class="fa-solid fa-align-left"></i> Product Description
            </h3>
            <p class="product-desc">{{ product.description || 'No description provided.' }}</p>
            <div class="meta-row">
              <div class="meta-item">
                <i class="fa-solid fa-tag"></i>
                <span>{{ product.category }}</span>
              </div>
              <div class="meta-item">
                <i class="fa-solid fa-calendar-days"></i>
                <span>Posted {{ formatDate(product.created_at) }}</span>
              </div>
              <div class="meta-item">
                <i class="fa-solid fa-circle-check" style="color:#16a34a"></i>
                <span style="color:#16a34a">Available</span>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT -->
        <div class="right-col">
          <div class="product-header-card">
            <h1 class="product-title">{{ product.title }}</h1>
            <p class="product-price">₱{{ formatPrice(product.price) }}</p>
          </div>

          <div class="seller-card">
            <p class="card-label"><i class="fa-solid fa-store"></i> Sold by</p>
            <div class="seller-row">
              <div class="seller-avatar">
                {{ product.seller_name?.charAt(0)?.toUpperCase() || 'S' }}
              </div>
              <div>
                <p class="seller-name">{{ product.seller_name || 'ADNU Student' }}</p>
                <p class="seller-sub">
                  <i class="fa-solid fa-circle-check"></i> ADNU Verified Student
                </p>
              </div>
              <button
                v-if="!isOwnProduct"
                @click="handleChat"
                class="chat-quick-btn"
                title="Message Seller"
              >
                <i class="fa-solid fa-comment-dots"></i>
              </button>
            </div>
          </div>

          <div class="action-card">
            <div v-if="isOwnProduct" class="own-listing-banner">
              <i class="fa-solid fa-store"></i>
              This is your listing
            </div>

            <template v-else>
              <!-- Buy Now → opens Place Order modal directly -->
              <button @click="handleBuyNow" class="btn-buy">
                <i class="fa-solid fa-bolt"></i>
                Buy Now
              </button>

              <button @click="handleChat" class="btn-chat">
                <i class="fa-solid fa-comment-dots"></i>
                Chat with Seller
              </button>
            </template>

            <p class="safety-note">
              <i class="fa-solid fa-shield-halved"></i>
              Arrange meetup details through chat
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Loading Skeleton -->
  <div v-else class="loading-wrapper">
    <div class="container">
      <div class="loading-grid">
        <div class="skeleton img-sk"></div>
        <div class="loading-right">
          <div class="skeleton title-sk"></div>
          <div class="skeleton price-sk"></div>
          <div class="skeleton btn-sk"></div>
          <div class="skeleton btn-sk"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── PLACE ORDER MODAL (Buy Now) ── -->
  <Transition name="modal">
    <div v-if="showOrderModal && product" class="modal-backdrop" @click.self="showOrderModal = false">
      <div class="modal-box">

        <button class="modal-close" @click="showOrderModal = false">
          <i class="fa-solid fa-xmark"></i>
        </button>

        <h2 class="modal-title">
          <i class="fa-solid fa-bolt"></i> Place Order
        </h2>

        <!-- Product Preview — always visible at top of modal -->
        <div class="modal-item-preview">
          <img
            :src="product.image_url || '/placeholder.png'"
            class="preview-img"
            :alt="product.title"
          />
          <div class="preview-info">
            <p class="preview-title">{{ product.title }}</p>
            <p class="preview-seller">
              <i class="fa-solid fa-store"></i>
              {{ product.seller_name || 'ADNU Student' }}
            </p>
            <p class="preview-price">₱{{ formatPrice(product.price) }}</p>
          </div>
        </div>

        <div class="modal-divider"></div>

        <!-- Pickup Location -->
        <div class="field-group">
          <label><i class="fa-solid fa-location-dot"></i> Pickup Location</label>
          <div class="select-wrap">
            <select v-model="orderForm.location">
              <option>Richards Hall Lobby</option>
              <option>University Gazebo</option>
              <option>O'Brien Library Entrance</option>
              <option>Dormitory Gate A</option>
            </select>
            <i class="fa-solid fa-chevron-down select-arrow"></i>
          </div>
        </div>

        <!-- Payment Method -->
        <div class="field-group">
          <label><i class="fa-solid fa-wallet"></i> Payment Method</label>
          <div class="pay-options">
            <button
              v-for="method in paymentMethods"
              :key="method.value"
              class="pay-option"
              :class="{ active: orderForm.payment === method.value }"
              @click="orderForm.payment = method.value"
              type="button"
            >
              <i :class="method.icon"></i>
              {{ method.label }}
            </button>
          </div>
        </div>

        <!-- Payment Info -->
        <div class="payment-info" v-if="orderForm.payment === 'Cash on Delivery'">
          <i class="fa-solid fa-money-bill-wave"></i>
          Pay in cash upon meetup at pickup location
        </div>
        <div class="payment-info gcash" v-else-if="orderForm.payment === 'GCash'">
          <i class="fa-solid fa-mobile-screen-button"></i>
          <span v-if="sellerPayment.gcash">GCash: <strong>{{ sellerPayment.gcash }}</strong></span>
          <span v-else>GCash details not available — coordinate with seller via chat</span>
        </div>
        <div class="payment-info bank" v-else-if="orderForm.payment === 'Bank Transfer'">
          <i class="fa-solid fa-building-columns"></i>
          <span v-if="sellerPayment.bank">Bank: <strong>{{ sellerPayment.bank }}</strong></span>
          <span v-else>Bank details not available — coordinate with seller via chat</span>
        </div>

        <!-- Total -->
        <div class="modal-total">
          <span>Total</span>
          <span class="total-amount">₱{{ formatPrice(product.price) }}</span>
        </div>

        <button @click="confirmBuyNow" class="checkout-btn" :disabled="placingOrder">
          <i class="fa-solid fa-circle-notch fa-spin" v-if="placingOrder"></i>
          <i class="fa-solid fa-bolt" v-else></i>
          {{ placingOrder ? 'Processing...' : 'Confirm Order' }}
        </button>

        <p class="safety-note">
          <i class="fa-solid fa-shield-halved"></i>
          Meet only in safe, public campus areas
        </p>

      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const product      = ref(null)
const addingToCart = ref(false)
const placingOrder = ref(false)
const showOrderModal = ref(false)
const currentUser  = JSON.parse(localStorage.getItem('user'))

const orderForm = ref({ location: 'Richards Hall Lobby', payment: 'Cash on Delivery' })
const sellerPayment = ref({ gcash: null, bank: null })

const paymentMethods = [
  { value: 'Cash on Delivery', label: 'Cash',  icon: 'fa-solid fa-money-bill-wave' },
  { value: 'GCash',            label: 'GCash', icon: 'fa-solid fa-mobile-screen-button' },
  { value: 'Bank Transfer',    label: 'Bank',  icon: 'fa-solid fa-building-columns' }
]

const isOwnProduct = computed(() =>
  currentUser && product.value && product.value.seller_id === currentUser.user_id
)

const loadDetails = async () => {
  product.value = null
  try {
    const res = await api.getProduct(route.params.id)
    product.value = res.data
    window.scrollTo(0, 0)
  } catch (err) {
    console.error('Fetch error:', err)
  }
}

onMounted(loadDetails)
watch(() => route.params.id, loadDetails)

// Add to Cart → redirect straight to /cart after adding
const handleAddToCart = async () => {
  if (!currentUser) return router.push('/auth')
  try {
    addingToCart.value = true
    await api.addToCart({ user_id: currentUser.user_id, product_id: product.value.id })
    router.push('/cart')
  } catch (err) {
    const msg = err.response?.data?.message || ''
    // Already in cart? Just go there
    if (msg.toLowerCase().includes('already')) {
      router.push('/cart')
    } else {
      alert((msg || 'Failed to add to cart') + ' ❌')
    }
  } finally {
    addingToCart.value = false
  }
}

// Buy Now → open Place Order modal directly (no cart involved)
const handleBuyNow = () => {
  if (!currentUser) return router.push('/auth')
  orderForm.value = { location: 'Richards Hall Lobby', payment: 'Cash on Delivery' }
  sellerPayment.value = { gcash: null, bank: null }
  if (api.getSellerPayment) {
    api.getSellerPayment(product.value.seller_id)
      .then(res => { sellerPayment.value = res.data || { gcash: null, bank: null } })
      .catch(() => { sellerPayment.value = { gcash: null, bank: null } })
  }
  showOrderModal.value = true
}

const confirmBuyNow = async () => {
  try {
    placingOrder.value = true
    await api.checkout({
      user_id:    currentUser.user_id,
      product_id: product.value.id,
      total:      product.value.price,
      location:   orderForm.value.location,
      payment:    orderForm.value.payment
    })
    showOrderModal.value = false
    alert('Order placed successfully! 🎉 Coordinate with the seller for pickup.')
    router.push('/')
  } catch (err) {
    alert(err.response?.data?.message || 'Checkout failed. Please try again.')
  } finally {
    placingOrder.value = false
  }
}

const handleChat = () => {
  if (!currentUser) return router.push('/auth')
  router.push({ path: '/messages', query: { seller_id: product.value.seller_id, seller_name: product.value.seller_name } })
}

const formatPrice = (v) => parseFloat(v).toLocaleString(undefined, { minimumFractionDigits: 2 })
const formatDate  = (d) => d ? new Date(d).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A'
</script>

<style scoped>
.details-wrapper { background: #f8fafc; min-height: 100vh; padding: 1.5rem; }
.container { max-width: 1100px; margin: 0 auto; }

.breadcrumb { display: flex; align-items: center; gap: 6px; margin-bottom: 1.5rem; font-size: 0.82rem; }
.crumb { background: none; border: none; color: #003366; cursor: pointer; font-weight: 600; padding: 0; font-size: 0.82rem; }
.crumb:hover { text-decoration: underline; }
.crumb.active { color: #888; cursor: default; font-weight: 400; }
.crumb.active:hover { text-decoration: none; }
.crumb-sep { color: #ccc; }

.details-grid { display: grid; grid-template-columns: 1fr 360px; gap: 1.5rem; align-items: start; }
.left-col { display: flex; flex-direction: column; gap: 16px; }

.image-box { position: relative; height: 380px; background: #f1f5f9; border-radius: 16px; overflow: hidden; border: 0.5px solid #eee; }
.main-img { width: 100%; height: 100%; object-fit: cover; }
.cat-badge { position: absolute; top: 14px; left: 14px; background: white; color: #003366; font-size: 0.75rem; font-weight: 700; padding: 5px 12px; border-radius: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

.desc-card { background: white; border-radius: 14px; border: 0.5px solid #eee; padding: 1.25rem; }
.section-label { font-size: 0.85rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 0.75rem; display: flex; align-items: center; gap: 7px; }
.product-desc { color: #555; line-height: 1.7; font-size: 0.9rem; margin: 0 0 1rem; }
.meta-row { display: flex; flex-wrap: wrap; gap: 16px; padding-top: 0.75rem; border-top: 1px solid #f1f5f9; }
.meta-item { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #666; }
.meta-item i { color: #003366; font-size: 0.75rem; }

.right-col { display: flex; flex-direction: column; gap: 12px; position: sticky; top: 80px; }
.product-header-card { background: white; border-radius: 14px; border: 0.5px solid #eee; padding: 1.25rem; }
.product-title { font-size: 1.4rem; font-weight: 800; color: #003366; margin: 0 0 8px; line-height: 1.3; }
.product-price { font-size: 1.6rem; font-weight: 800; color: #e74c3c; margin: 0; }

.seller-card { background: white; border-radius: 14px; border: 0.5px solid #eee; padding: 1.25rem; }
.card-label { font-size: 0.72rem; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 0.75rem; display: flex; align-items: center; gap: 6px; }
.seller-row { display: flex; align-items: center; gap: 12px; }
.seller-avatar { width: 42px; height: 42px; border-radius: 50%; background: #003366; color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1rem; flex-shrink: 0; }
.seller-name { font-size: 0.95rem; font-weight: 700; color: #003366; margin: 0 0 3px; }
.seller-sub { font-size: 0.75rem; color: #16a34a; margin: 0; display: flex; align-items: center; gap: 4px; }
.chat-quick-btn { margin-left: auto; width: 36px; height: 36px; border-radius: 50%; background: #f0f4ff; color: #003366; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; transition: 0.2s; flex-shrink: 0; }
.chat-quick-btn:hover { background: #003366; color: white; }

.action-card { background: white; border-radius: 14px; border: 0.5px solid #eee; padding: 1.25rem; display: flex; flex-direction: column; gap: 10px; }
.own-listing-banner { display: flex; align-items: center; gap: 8px; background: #f0f4ff; color: #003366; font-size: 0.875rem; font-weight: 700; padding: 12px 16px; border-radius: 10px; border: 1px solid #d0ddf5; }

.btn-buy { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; background: #003366; color: white; border: none; padding: 14px; border-radius: 10px; font-weight: 800; font-size: 0.98rem; cursor: pointer; transition: 0.2s; }
.btn-buy:hover { background: #002244; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(0,51,102,0.25); }

.btn-cart { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; background: #FFD700; color: #003366; border: none; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: 0.2s; }
.btn-cart:hover:not(:disabled) { background: #e6c200; transform: translateY(-1px); }
.btn-cart:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-chat { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; background: white; color: #003366; border: 1.5px solid #003366; padding: 11px; border-radius: 10px; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: 0.2s; }
.btn-chat:hover { background: #f0f4ff; }

.safety-note { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #aaa; margin: 2px 0 0; }
.safety-note i { color: #16a34a; }

/* Loading */
.loading-wrapper { background: #f8fafc; min-height: 100vh; padding: 1.5rem; }
.loading-grid { display: grid; grid-template-columns: 1fr 360px; gap: 1.5rem; }
.loading-right { display: flex; flex-direction: column; gap: 12px; }
.skeleton { background: #e8ecef; border-radius: 10px; animation: pulse 1.5s infinite; }
.img-sk { height: 380px; }
.title-sk { height: 28px; width: 80%; }
.price-sk { height: 32px; width: 40%; }
.btn-sk { height: 48px; border-radius: 10px; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-box { background: white; border-radius: 20px; width: 100%; max-width: 460px; padding: 1.75rem; position: relative; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
.modal-close { position: absolute; top: 16px; right: 16px; width: 32px; height: 32px; background: #f0f4f8; border: none; border-radius: 8px; color: #666; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
.modal-close:hover { background: #e74c3c; color: white; }
.modal-title { font-size: 1.2rem; font-weight: 800; color: #003366; margin: 0 0 1.25rem; display: flex; align-items: center; gap: 8px; }

/* Product preview in modal */
.modal-item-preview { display: flex; gap: 14px; background: #f8fafc; border-radius: 14px; padding: 14px; margin-bottom: 1rem; border: 1px solid #eef2f7; }
.preview-img { width: 80px; height: 80px; object-fit: cover; border-radius: 10px; flex-shrink: 0; border: 1px solid #eee; }
.preview-info { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 5px; }
.preview-title { font-size: 0.95rem; font-weight: 700; color: #003366; margin: 0; line-height: 1.3; }
.preview-seller { font-size: 0.75rem; color: #999; margin: 0; display: flex; align-items: center; gap: 4px; }
.preview-price { font-size: 1.15rem; font-weight: 800; color: #e74c3c; margin: 0; }

.modal-divider { height: 1px; background: #eee; margin: 0.25rem 0 1rem; }

.field-group { margin-bottom: 14px; }
.field-group label { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 7px; }
.select-wrap { position: relative; }
select { width: 100%; padding: 10px 36px 10px 12px; border: 1.5px solid #dce4ee; border-radius: 8px; font-size: 0.875rem; color: #333; background: #f8fafc; appearance: none; cursor: pointer; outline: none; transition: border-color 0.2s; }
select:focus { border-color: #003366; }
.select-arrow { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); font-size: 10px; color: #999; pointer-events: none; }

.pay-options { display: flex; gap: 8px; }
.pay-option { flex: 1; padding: 8px 6px; border: 1.5px solid #e5e7eb; border-radius: 8px; background: #f8fafc; font-size: 0.75rem; font-weight: 700; color: #666; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 5px; transition: 0.2s; }
.pay-option:hover { border-color: #003366; color: #003366; }
.pay-option.active { background: #003366; color: white; border-color: #003366; }

.payment-info { background: #f0fdf4; color: #15803d; font-size: 0.8rem; font-weight: 600; padding: 10px 12px; border-radius: 8px; display: flex; align-items: center; gap: 7px; margin-bottom: 14px; flex-wrap: wrap; }
.payment-info.gcash { background: #e8f0fe; color: #185FA5; }
.payment-info.bank  { background: #fffbeb; color: #92400e; }

.modal-total { display: flex; justify-content: space-between; align-items: center; font-weight: 800; color: #003366; font-size: 0.95rem; background: #f8fafc; border-radius: 10px; padding: 12px 16px; margin-bottom: 1rem; }
.total-amount { color: #e74c3c; font-size: 1.1rem; }

.checkout-btn { width: 100%; background: #003366; color: white; padding: 14px; border: none; border-radius: 10px; font-weight: 800; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.2s; margin-bottom: 10px; }
.checkout-btn:hover:not(:disabled) { background: #002244; transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,51,102,0.25); }
.checkout-btn:disabled { opacity: 0.65; cursor: not-allowed; }

.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }

@media (max-width: 768px) {
  .details-grid, .loading-grid { grid-template-columns: 1fr; }
  .right-col { position: static; }
}
</style>