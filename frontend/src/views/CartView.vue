<template>
  <div class="cart-wrapper">
    <div class="cart-container">

      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon-box">
            <i class="fa-solid fa-cart-shopping"></i>
          </div>
          <div>
            <h1 class="page-title">My Cart</h1>
            <p class="page-sub" v-if="cartItems.length">
              {{ cartItems.length }} item{{ cartItems.length > 1 ? 's' : '' }} — tap an item to place order
            </p>
          </div>
        </div>
        <router-link to="/products" class="continue-link">
          <i class="fa-solid fa-arrow-left"></i> Continue Shopping
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your cart...</p>
      </div>

      <!-- Cart Items -->
      <div v-else-if="cartItems.length" class="items-col">
        <TransitionGroup name="cart-item" tag="div">
          <div
            v-for="item in cartItems"
            :key="item.cart_id"
            class="cart-card"
            @click="openOrderSummary(item)"
          >
            <div class="card-img-wrap">
              <img :src="item.image_url || '/placeholder.png'" class="cart-img" :alt="item.title" />
              <span class="cat-badge">{{ item.category }}</span>
            </div>

            <div class="card-info">
              <div class="card-info-top">
                <div>
                  <h3 class="item-title">{{ item.title }}</h3>
                  <p class="item-seller">
                    <i class="fa-solid fa-store"></i>
                    {{ item.seller_name || 'ADNU Student' }}
                  </p>
                </div>
                <button @click.stop="removeItem(item.cart_id)" class="remove-btn" title="Remove">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>

              <div class="card-info-bottom">
                <span class="item-price">₱{{ formatPrice(item.price) }}</span>
                <div class="item-actions">
                  <span class="status-chip">
                    <i class="fa-solid fa-circle-check"></i> Available
                  </span>
                  <button class="msg-btn" @click.stop="chatSeller(item)">
                    <i class="fa-solid fa-comment-dots"></i> Chat Seller
                  </button>
                  <span class="tap-hint">
                    <i class="fa-solid fa-hand-pointer"></i> Tap to order
                  </span>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon-wrap">
          <i class="fa-solid fa-cart-shopping"></i>
        </div>
        <h3>Your cart is empty</h3>
        <p>Looks like you haven't added anything yet.</p>
        <button @click="router.push('/products')" class="browse-btn">
          <i class="fa-solid fa-store"></i> Browse Marketplace
        </button>
      </div>

    </div>

    <!-- ── ORDER SUMMARY MODAL ── -->
    <Transition name="modal">
      <div v-if="selectedItem" class="modal-backdrop" @click.self="closeOrderSummary">
        <div class="modal-box">

          <button class="modal-close" @click="closeOrderSummary">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <h2 class="modal-title">
            <i class="fa-solid fa-bag-shopping"></i> Place Order
          </h2>

          <!-- Product Preview — always visible, big and clear -->
          <div class="modal-item-preview">
            <img
              :src="selectedItem.image_url || '/placeholder.png'"
              class="preview-img"
              :alt="selectedItem.title"
            />
            <div class="preview-info">
              <p class="preview-title">{{ selectedItem.title }}</p>
              <p class="preview-seller">
                <i class="fa-solid fa-store"></i>
                {{ selectedItem.seller_name || 'ADNU Student' }}
              </p>
              <p class="preview-price">₱{{ formatPrice(selectedItem.price) }}</p>
            </div>
          </div>

          <div class="modal-divider"></div>

          <!-- Pickup Location -->
          <div class="field-group">
            <label><i class="fa-solid fa-location-dot"></i> Pickup Location</label>
            <div class="select-wrap">
              <select v-model="checkout.location">
                <option>Xavier Hall</option>
                <option>Library</option>
                <option>Bonoan</option>
                <option>Coko Cafe</option>
                <option>Alingal</option>
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
                :class="{ active: checkout.payment === method.value }"
                @click="checkout.payment = method.value"
                type="button"
              >
                <i :class="method.icon"></i>
                {{ method.label }}
              </button>
            </div>
          </div>

          <!-- Payment Info -->
          <div class="payment-info" v-if="checkout.payment === 'Cash on Delivery'">
            <i class="fa-solid fa-money-bill-wave"></i>
            Pay in cash upon meetup at pickup location
          </div>
          <div class="payment-info gcash" v-else-if="checkout.payment === 'GCash'">
            <i class="fa-solid fa-mobile-screen-button"></i>
            <span v-if="sellerPayment.gcash">GCash: <strong>{{ sellerPayment.gcash }}</strong></span>
            <span v-else>GCash details not available — coordinate with seller via chat</span>
          </div>
          <div class="payment-info bank" v-else-if="checkout.payment === 'Bank Transfer'">
            <i class="fa-solid fa-building-columns"></i>
            <span v-if="sellerPayment.bank">Bank: <strong>{{ sellerPayment.bank }}</strong></span>
            <span v-else>Bank details not available — coordinate with seller via chat</span>
          </div>

          <!-- Order Total -->
          <div class="modal-total">
            <span>Total</span>
            <span class="total-amount">₱{{ formatPrice(selectedItem.price) }}</span>
          </div>

          <button @click="processOrder" class="checkout-btn" :disabled="checkingOut">
            <i class="fa-solid fa-circle-notch fa-spin" v-if="checkingOut"></i>
            <i class="fa-solid fa-bag-shopping" v-else></i>
            {{ checkingOut ? 'Processing...' : 'Place Order' }}
          </button>

          <p class="safety-note">
            <i class="fa-solid fa-shield-halved"></i>
            Meet only in safe, public campus areas
          </p>

        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router      = useRouter()
const cartItems   = ref([])
const loading     = ref(true)
const checkingOut = ref(false)
const selectedItem = ref(null)
const user = JSON.parse(localStorage.getItem('user'))

const checkout = ref({ location: 'Richards Hall Lobby', payment: 'Cash on Delivery' })
const sellerPayment = ref({ gcash: null, bank: null })

const paymentMethods = [
  { value: 'Cash on Delivery', label: 'Cash',  icon: 'fa-solid fa-money-bill-wave' },
  { value: 'GCash',            label: 'GCash', icon: 'fa-solid fa-mobile-screen-button' },
  { value: 'Bank Transfer',    label: 'Bank',  icon: 'fa-solid fa-building-columns' }
]

const fetchCart = async () => {
  if (!user) return router.push('/auth')
  try {
    loading.value = true
    const res = await api.getCart(user.user_id)
    cartItems.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('Cart fetch error:', err)
    cartItems.value = []
  } finally {
    loading.value = false
  }
}

const formatPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })

const removeItem = async (id) => {
  try {
    await api.removeFromCart(id)
    cartItems.value = cartItems.value.filter(i => i.cart_id !== id)
    if (selectedItem.value?.cart_id === id) closeOrderSummary()
  } catch {
    alert('Failed to remove item.')
  }
}

const chatSeller = (item) => {
  if (!user) return router.push('/auth')
  router.push({ path: '/messages', query: { seller_id: item.seller_id, seller_name: item.seller_name } })
}

const openOrderSummary = (item) => {
  selectedItem.value = item
  checkout.value = { location: 'Richards Hall Lobby', payment: 'Cash on Delivery' }
  sellerPayment.value = { gcash: null, bank: null }
  if (api.getSellerPayment) {
    api.getSellerPayment(item.seller_id)
      .then(res => { sellerPayment.value = res.data || { gcash: null, bank: null } })
      .catch(() => { sellerPayment.value = { gcash: null, bank: null } })
  }
}

const closeOrderSummary = () => { selectedItem.value = null }

const processOrder = async () => {
  try {
    checkingOut.value = true
    await api.checkout({
      user_id:    user.user_id,
      product_id: selectedItem.value.id,
      cart_id:    selectedItem.value.cart_id,
      total:      selectedItem.value.price,
      location:   checkout.value.location,
      payment:    checkout.value.payment
    })
    alert('Order placed successfully! 🎉 Coordinate with the seller for pickup.')
    cartItems.value = cartItems.value.filter(i => i.cart_id !== selectedItem.value.cart_id)
    closeOrderSummary()
  } catch (err) {
    alert(err.response?.data?.message || 'Checkout failed. Please try again.')
  } finally {
    checkingOut.value = false
  }
}

onMounted(fetchCart)
</script>

<style scoped>
.cart-wrapper { background: #f0f4f8; min-height: 100vh; padding: 2rem 1.5rem 4rem; }
.cart-container { max-width: 780px; margin: 0 auto; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon-box { width: 52px; height: 52px; background: #FFD700; color: #003366; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 800; color: #003366; margin: 0; }
.page-sub { font-size: 0.82rem; color: #888; margin: 2px 0 0; }
.continue-link { display: flex; align-items: center; gap: 7px; font-size: 0.85rem; font-weight: 600; color: #003366; text-decoration: none; padding: 8px 16px; border: 1.5px solid #d0dbe8; border-radius: 8px; background: white; transition: 0.2s; }
.continue-link:hover { background: #003366; color: white; border-color: #003366; }

/* Loading */
.loading-state { text-align: center; padding: 5rem; color: #888; }
.spinner { width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #003366; border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Items */
.items-col { display: flex; flex-direction: column; }
.cart-card { display: flex; gap: 16px; background: white; border-radius: 14px; border: 1px solid #e8eef4; padding: 14px; margin-bottom: 12px; cursor: pointer; transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s; }
.cart-card:hover { box-shadow: 0 4px 20px rgba(0,51,102,0.1); transform: translateY(-2px); border-color: #003366; }

.card-img-wrap { position: relative; flex-shrink: 0; }
.cart-img { width: 96px; height: 96px; object-fit: cover; border-radius: 10px; background: #f0f4f8; display: block; }
.cat-badge { position: absolute; bottom: 5px; left: 5px; background: rgba(0,51,102,0.85); color: white; font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

.card-info { flex: 1; display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.card-info-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.item-title { font-size: 0.97rem; font-weight: 700; color: #003366; margin: 0 0 4px; }
.item-seller { font-size: 0.78rem; color: #999; margin: 0; display: flex; align-items: center; gap: 5px; }
.remove-btn { width: 30px; height: 30px; border: 1px solid #e8eef4; border-radius: 7px; background: none; color: #bbb; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; transition: 0.2s; }
.remove-btn:hover { background: #fff0f0; color: #e74c3c; border-color: #e74c3c; }

.card-info-bottom { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-top: auto; }
.item-price { font-size: 1.05rem; font-weight: 800; color: #e74c3c; }
.item-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.status-chip { font-size: 0.72rem; font-weight: 700; color: #16a34a; background: #f0fdf4; padding: 4px 8px; border-radius: 20px; display: flex; align-items: center; gap: 4px; }
.msg-btn { font-size: 0.75rem; font-weight: 700; color: #003366; background: #f0f4ff; border: none; padding: 5px 10px; border-radius: 20px; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: 0.2s; }
.msg-btn:hover { background: #003366; color: white; }
.tap-hint { font-size: 0.7rem; color: #bbb; display: flex; align-items: center; gap: 4px; }

/* Empty */
.empty-state { text-align: center; padding: 5rem 2rem; background: white; border-radius: 16px; border: 1px solid #e8eef4; }
.empty-icon-wrap { width: 80px; height: 80px; background: #f0f4f8; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem; font-size: 2rem; color: #c0cdd8; }
.empty-state h3 { font-size: 1.2rem; font-weight: 800; color: #003366; margin: 0 0 6px; }
.empty-state p { color: #aaa; font-size: 0.9rem; margin: 0 0 1.5rem; }
.browse-btn { background: #003366; color: white; border: none; padding: 12px 28px; border-radius: 10px; font-weight: 700; font-size: 0.9rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: 0.2s; }
.browse-btn:hover { background: #002244; transform: translateY(-1px); }

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

.safety-note { text-align: center; font-size: 0.75rem; color: #aaa; margin: 0; display: flex; align-items: center; justify-content: center; gap: 5px; }

/* Transitions */
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
.cart-item-enter-active, .cart-item-leave-active { transition: all 0.3s ease; }
.cart-item-enter-from { opacity: 0; transform: translateY(-10px); }
.cart-item-leave-to { opacity: 0; transform: translateX(20px); }

@media (max-width: 600px) {
  .cart-card { flex-direction: column; }
  .cart-img { width: 100%; height: 180px; }
  .card-img-wrap { width: 100%; }
}
</style>