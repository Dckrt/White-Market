<template>
  <div class="cart-wrapper">
    <div class="cart-container">

      <!-- Header with proper logo -->
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon-box">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/>
            </svg>
          </div>
          <div>
            <h1 class="page-title">My Cart</h1>
            <p class="page-sub" v-if="cartItems.length">
              {{ cartItems.length }} item{{ cartItems.length > 1 ? 's' : '' }} — tap an item to place order
            </p>
            <p class="page-sub" v-else>Your saved items</p>
          </div>
        </div>
        <router-link to="/products" class="continue-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          Continue Shopping
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your cart…</p>
      </div>

      <!-- Cart Items -->
      <div v-else-if="cartItems.length" class="items-col">
        <TransitionGroup name="cart-item" tag="div">
          <div v-for="item in cartItems" :key="item.cart_id" class="cart-card" @click="openOrder(item)">
            <div class="card-img-wrap">
              <img :src="item.image_url || '/placeholder.png'" class="cart-img" :alt="item.title" @error="e=>e.target.src='/placeholder.png'" />
              <span class="cat-badge">{{ item.category }}</span>
            </div>
            <div class="card-info">
              <div class="card-top">
                <div>
                  <h3 class="item-title">{{ item.title }}</h3>
                  <p class="item-seller">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
                    {{ item.seller_name || 'ADNU Student' }}
                  </p>
                </div>
                <button @click.stop="removeItem(item.cart_id)" class="remove-btn" title="Remove">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
              <div class="card-bottom">
                <span class="item-price">₱{{ fmtPrice(item.price) }}</span>
                <div class="item-actions">
                  <span class="status-chip">
                    <span class="status-dot"></span> Available
                  </span>
                  <button class="msg-btn" @click.stop="chatSeller(item)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                    Chat Seller
                  </button>
                  <span class="tap-hint">Tap to order</span>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <!-- Empty -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#c0cdd8" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
        </div>
        <h3>Your cart is empty</h3>
        <p>Looks like you haven't added anything yet.</p>
        <button @click="router.push('/products')" class="browse-btn">Browse Marketplace</button>
      </div>

    </div>

    <!-- ORDER MODAL -->
    <Transition name="modal">
      <div v-if="selectedItem" class="modal-backdrop" @click.self="selectedItem = null">
        <div class="modal-box">
          <button class="modal-close" @click="selectedItem = null">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          <h2 class="modal-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
            Place Order
          </h2>
          <div class="modal-preview">
            <img :src="selectedItem.image_url||'/placeholder.png'" class="modal-img" @error="e=>e.target.src='/placeholder.png'" />
            <div>
              <p class="modal-prod-title">{{ selectedItem.title }}</p>
              <p class="modal-seller">Seller: {{ selectedItem.seller_name }}</p>
              <p class="modal-price">₱{{ fmtPrice(selectedItem.price) }}</p>
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
            <div class="pay-opts">
              <button v-for="m in payMethods" :key="m" type="button"
                :class="['pay-opt', checkout.payment===m && 'pay-opt--on']"
                @click="checkout.payment = m">{{ m }}</button>
            </div>
          </div>
          <div class="modal-pay-info" v-if="checkout.payment==='Cash'">Pay in cash upon meetup at the pickup location.</div>
          <div class="modal-pay-info modal-pay-info--gcash" v-else-if="checkout.payment==='GCash'">
            <span v-if="sellerPay.gcash">GCash: <strong>{{ sellerPay.gcash }}</strong></span>
            <span v-else>GCash not set — coordinate via chat.</span>
          </div>
          <div class="modal-pay-info modal-pay-info--bank" v-else>
            <span v-if="sellerPay.bank">Bank: <strong>{{ sellerPay.bank }}</strong></span>
            <span v-else>Bank details not set — coordinate via chat.</span>
          </div>
          <div class="modal-total">
            <span>Total</span>
            <span class="modal-total__price">₱{{ fmtPrice(selectedItem.price) }}</span>
          </div>
          <button class="checkout-btn" @click="processOrder" :disabled="checkingOut">
            <svg v-if="!checkingOut" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
            {{ checkingOut ? 'Processing…' : 'Confirm Order' }}
          </button>
          <p class="safety-note">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
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

const router       = useRouter()
const cartItems    = ref([])
const loading      = ref(true)
const checkingOut  = ref(false)
const selectedItem = ref(null)
const sellerPay    = ref({ gcash: null, bank: null })
const checkout     = ref({ location: 'Xavier Hall', payment: 'Cash' })
const payMethods   = ['Cash', 'GCash', 'Bank Transfer']
const user         = JSON.parse(localStorage.getItem('user'))

const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })

const fetchCart = async () => {
  if (!user) return router.push('/auth')
  try { loading.value = true; const r = await api.getCart(user.user_id); cartItems.value = Array.isArray(r.data) ? r.data : [] }
  catch { cartItems.value = [] } finally { loading.value = false }
}

const removeItem = async (id) => {
  try { await api.removeFromCart(id); cartItems.value = cartItems.value.filter(i => i.cart_id !== id) }
  catch { alert('Failed to remove item.') }
}

const chatSeller = (item) => {
  router.push({ path: '/messages', query: { seller_id: item.seller_id, seller_name: item.seller_name } })
}

const openOrder = async (item) => {
  selectedItem.value = item
  checkout.value = { location: 'Xavier Hall', payment: 'Cash' }
  sellerPay.value = { gcash: null, bank: null }
  try { const r = await api.getSellerPayment(item.seller_id); sellerPay.value = r.data || { gcash: null, bank: null } } catch {}
}

const processOrder = async () => {
  checkingOut.value = true
  try {
    await api.checkout({
      user_id:    user.user_id,
      product_id: selectedItem.value.id,
      cart_id:    selectedItem.value.cart_id,
      payment:    checkout.value.payment,
      location:   checkout.value.location,
    })
    alert(`Order placed! Meet seller at: ${checkout.value.location}`)
    cartItems.value = cartItems.value.filter(i => i.cart_id !== selectedItem.value.cart_id)
    selectedItem.value = null
  } catch (err) {
    alert(err.response?.data?.message || 'Checkout failed.')
  } finally { checkingOut.value = false }
}

onMounted(fetchCart)
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; transform-origin: center; }

.cart-wrapper { background:#f0f4f8; min-height:100vh; padding:2rem 1.5rem; }
.cart-container { max-width:780px; margin:0 auto; }

/* Header */
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:2rem; flex-wrap:wrap; gap:12px; }
.header-left { display:flex; align-items:center; gap:14px; }
.header-icon-box {
  width:52px; height:52px;
  background:#fff;
  border:1.5px solid #e0e8f4;
  border-radius:14px;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0;
}
.page-title { font-size:1.5rem; font-weight:800; color:#003366; margin:0; }
.page-sub   { font-size:0.82rem; color:#888; margin:2px 0 0; }
.continue-link { display:flex; align-items:center; gap:7px; font-size:0.85rem; font-weight:600; color:#003366; text-decoration:none; padding:8px 16px; border:1.5px solid #d0dbe8; border-radius:8px; background:#fff; transition:0.2s; }
.continue-link:hover { background:#003366; color:#fff; border-color:#003366; }

/* Loading */
.loading-state { text-align:center; padding:5rem; color:#888; }
.spinner { width:36px; height:36px; border:3px solid #e0e0e0; border-top-color:#003366; border-radius:50%; animation:spin 0.7s linear infinite; margin:0 auto 1rem; }

/* Cart Card */
.items-col { display:flex; flex-direction:column; gap:12px; }
.cart-card { display:flex; gap:16px; background:#fff; border-radius:14px; border:1px solid #e8eef4; padding:14px; cursor:pointer; transition:box-shadow 0.2s,transform 0.2s,border-color 0.2s; }
.cart-card:hover { box-shadow:0 4px 20px rgba(0,51,102,0.1); transform:translateY(-2px); border-color:#003366; }

.card-img-wrap { position:relative; flex-shrink:0; }
.cart-img { width:96px; height:96px; object-fit:cover; border-radius:10px; background:#f0f4f8; display:block; }
.cat-badge { position:absolute; bottom:5px; left:5px; background:rgba(0,51,102,0.85); color:#fff; font-size:9px; font-weight:700; padding:2px 6px; border-radius:4px; text-transform:uppercase; }

.card-info { flex:1; display:flex; flex-direction:column; gap:8px; min-width:0; }
.card-top  { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }
.item-title  { font-size:0.97rem; font-weight:700; color:#003366; margin:0 0 4px; }
.item-seller { font-size:0.78rem; color:#999; margin:0; display:flex; align-items:center; gap:4px; }
.remove-btn  { width:30px; height:30px; border:1px solid #e8eef4; border-radius:7px; background:none; color:#bbb; cursor:pointer; display:flex; align-items:center; justify-content:center; flex-shrink:0; transition:0.2s; }
.remove-btn:hover { background:#fff0f0; color:#e74c3c; border-color:#e74c3c; }

.card-bottom { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-top:auto; }
.item-price  { font-size:1.05rem; font-weight:800; color:#003366; }
.item-actions { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.status-chip { font-size:0.72rem; font-weight:700; color:#16a34a; background:#f0fdf4; padding:4px 8px; border-radius:20px; display:flex; align-items:center; gap:5px; }
.status-dot  { width:6px; height:6px; border-radius:50%; background:#16a34a; flex-shrink:0; }
.msg-btn { font-size:0.75rem; font-weight:700; color:#003366; background:#f0f4ff; border:none; padding:5px 10px; border-radius:20px; cursor:pointer; display:flex; align-items:center; gap:5px; transition:0.2s; }
.msg-btn:hover { background:#003366; color:#FFD700; }
.tap-hint { font-size:0.7rem; color:#bbb; }

/* Empty */
.empty-state { text-align:center; padding:5rem 2rem; background:#fff; border-radius:16px; border:1px solid #e8eef4; }
.empty-icon { width:80px; height:80px; background:#f0f4f8; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 1.25rem; }
.empty-state h3 { font-size:1.2rem; font-weight:800; color:#003366; margin:0 0 6px; }
.empty-state p  { color:#aaa; font-size:0.9rem; margin:0 0 1.5rem; }
.browse-btn { background:#003366; color:#fff; border:none; padding:12px 28px; border-radius:10px; font-weight:700; font-size:0.9rem; cursor:pointer; font-family:inherit; transition:0.2s; }
.browse-btn:hover { background:#002244; }

/* Modal */
.modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.5); backdrop-filter:blur(3px); z-index:1000; display:flex; align-items:center; justify-content:center; padding:1rem; }
.modal-box { background:#fff; border-radius:20px; width:100%; max-width:440px; padding:1.75rem; position:relative; max-height:90vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.2); }
.modal-close { position:absolute; top:16px; right:16px; width:32px; height:32px; background:#f0f4f8; border:none; border-radius:8px; color:#666; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:0.15s; }
.modal-close:hover { background:#e74c3c; color:#fff; }
.modal-title { font-size:1.15rem; font-weight:800; color:#003366; margin:0 0 1.25rem; display:flex; align-items:center; gap:8px; }

.modal-preview { display:flex; gap:12px; background:#f8fafc; border-radius:12px; padding:12px; margin-bottom:1rem; border:1px solid #e8edf4; }
.modal-img { width:72px; height:72px; object-fit:cover; border-radius:9px; flex-shrink:0; }
.modal-prod-title { font-size:0.9rem; font-weight:700; color:#003366; margin:0 0 4px; }
.modal-seller { font-size:0.72rem; color:#888; margin:0 0 4px; }
.modal-price  { font-size:1.1rem; font-weight:800; color:#003366; margin:0; }
.modal-divider { height:1px; background:#eee; margin:0.5rem 0 1rem; }

.modal-field { margin-bottom:14px; }
.modal-field label { display:flex; align-items:center; gap:6px; font-size:0.72rem; font-weight:700; color:#003366; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:7px; }
.modal-select { width:100%; padding:10px 12px; border:1.5px solid #dce4ee; border-radius:9px; font-size:0.875rem; color:#333; background:#f8fafc; outline:none; font-family:inherit; }
.modal-select:focus { border-color:#003366; }

.pay-opts { display:flex; gap:8px; }
.pay-opt { flex:1; padding:9px 4px; border:1.5px solid #e5e7eb; border-radius:8px; background:#f8fafc; font-size:0.72rem; font-weight:700; color:#666; cursor:pointer; transition:0.15s; font-family:inherit; }
.pay-opt:hover { border-color:#003366; color:#003366; }
.pay-opt--on   { background:#003366; color:#FFD700; border-color:#003366; }

.modal-pay-info { font-size:0.8rem; font-weight:600; padding:10px 12px; border-radius:8px; margin-bottom:14px; background:#f0fdf4; color:#15803d; }
.modal-pay-info--gcash { background:#e8f0fe; color:#185FA5; }
.modal-pay-info--bank  { background:#fffbeb; color:#92400e; }

.modal-total { display:flex; justify-content:space-between; align-items:center; font-weight:800; color:#003366; background:#f8fafc; border-radius:10px; padding:12px 16px; margin-bottom:1rem; }
.modal-total__price { font-size:1.2rem; }

.checkout-btn { width:100%; background:#FFD700; color:#003366; border:none; padding:14px; border-radius:12px; font-weight:800; font-size:1rem; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; transition:0.15s; margin-bottom:10px; font-family:inherit; }
.checkout-btn:hover:not(:disabled) { background:#e6c200; transform:translateY(-1px); }
.checkout-btn:disabled { opacity:0.65; cursor:not-allowed; }

.safety-note { text-align:center; font-size:0.72rem; color:#aaa; display:flex; align-items:center; justify-content:center; gap:5px; margin:0; }

.modal-enter-active,.modal-leave-active { transition:all 0.25s ease; }
.modal-enter-from,.modal-leave-to { opacity:0; transform:scale(0.95); }
.cart-item-enter-active,.cart-item-leave-active { transition:all 0.3s ease; }
.cart-item-enter-from { opacity:0; transform:translateY(-10px); }
.cart-item-leave-to   { opacity:0; transform:translateX(20px); }

@media(max-width:600px) {
  .cart-card { flex-direction:column; }
  .cart-img  { width:100%; height:180px; border-radius:10px; }
  .card-img-wrap { width:100%; }
}
</style>