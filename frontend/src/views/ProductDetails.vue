<template>
  <div class="pd-page">
    <!-- Loading -->
    <div v-if="loading" class="pd-loading">
      <div class="pd-spinner"></div>
      <p>Loading product…</p>
    </div>

    <!-- Not found -->
    <div v-else-if="!product" class="pd-notfound">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <h2>Product not found</h2>
      <router-link to="/products" class="pd-back-btn">Back to Marketplace</router-link>
    </div>

    <!-- Product -->
    <div v-else class="pd-container">

      <!-- Back -->
      <button class="pd-back" @click="router.back()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Back
      </button>

      <div class="pd-layout">

        <!-- LEFT: Images -->
        <div class="pd-images">
          <div class="pd-main-img-wrap">
            <img
              :src="activeImage"
              :alt="product.title"
              class="pd-main-img"
              @error="e => e.target.src = '/placeholder.png'"
            />
            <!-- Arrow prev -->
            <button v-if="images.length > 1" class="pd-img-arrow pd-img-arrow--l" @click="prevImg">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <!-- Arrow next -->
            <button v-if="images.length > 1" class="pd-img-arrow pd-img-arrow--r" @click="nextImg">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
            <!-- Counter -->
            <span v-if="images.length > 1" class="pd-img-counter">{{ activeIdx + 1 }}/{{ images.length }}</span>
          </div>

          <!-- Thumbnails -->
          <div v-if="images.length > 1" class="pd-thumbs">
            <img
              v-for="(img, i) in images"
              :key="i"
              :src="img"
              :class="['pd-thumb', i === activeIdx && 'pd-thumb--active']"
              @click="activeIdx = i"
              @error="e => e.target.src = '/placeholder.png'"
              :alt="`Image ${i+1}`"
            />
          </div>
        </div>

        <!-- RIGHT: Info -->
        <div class="pd-info">
          <div class="pd-info__top">
            <span class="pd-category">{{ product.category }}</span>
            <span class="pd-status pd-status--available" v-if="product.status === 'Available'">
              <span class="pd-status__dot"></span>Available
            </span>
            <span class="pd-status pd-status--sold" v-else>
              <span class="pd-status__dot"></span>Sold
            </span>
          </div>

          <h1 class="pd-title">{{ product.title }}</h1>

          <div class="pd-price">₱{{ fmtPrice(product.price) }}</div>

          <!-- Tags -->
          <div v-if="tags.length" class="pd-tags">
            <span v-for="tag in tags" :key="tag" class="pd-tag">
              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/></svg>
              {{ tag }}
            </span>
          </div>

          <!-- Description -->
          <div class="pd-desc-box" v-if="product.description">
            <h3 class="pd-desc-box__title">Description</h3>
            <p class="pd-desc-box__text">{{ product.description }}</p>
          </div>

          <!-- Seller -->
          <div class="pd-seller">
            <div class="pd-seller__av">{{ sellerInitial }}</div>
            <div>
              <p class="pd-seller__name">{{ product.seller_name || 'ADNU Student' }}</p>
              <p class="pd-seller__label">Seller</p>
            </div>
          </div>

          <!-- Posted date -->
          <p class="pd-posted" v-if="product.created_at">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Posted {{ fmtDate(product.created_at) }}
          </p>

          <!-- Actions -->
          <div class="pd-actions" v-if="product.status === 'Available'">
            <!-- Don't show if own product -->
            <template v-if="!isOwnProduct">
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
              This is your own listing.
              <router-link to="/dashboard">Manage in My Shop</router-link>
            </div>
          </div>

          <div v-else class="pd-sold-notice">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            This item has already been sold.
          </div>

          <!-- Safety note -->
          <div class="pd-safety">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Meet only in safe, public campus areas
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const route  = useRoute()

const product    = ref(null)
const loading    = ref(true)
const activeIdx  = ref(0)
const addingCart = ref(false)

const user = JSON.parse(localStorage.getItem('user') || 'null')

// ── Computed ─────────────────────────────────────────────────────────────────
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

const sellerInitial = computed(() =>
  (product.value?.seller_name || 'A').charAt(0).toUpperCase()
)

const isOwnProduct = computed(() =>
  user && product.value && Number(user.user_id) === Number(product.value.seller_id)
)

// ── Methods ──────────────────────────────────────────────────────────────────
const prevImg = () => activeIdx.value = activeIdx.value === 0 ? images.value.length - 1 : activeIdx.value - 1
const nextImg = () => activeIdx.value = activeIdx.value === images.value.length - 1 ? 0 : activeIdx.value + 1

const fmtPrice = (v) => Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })
const fmtDate  = (d) => {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' }) }
  catch { return d }
}

const addToCart = async () => {
  if (!user) return router.push('/auth')
  addingCart.value = true
  try {
    await api.addToCart({ user_id: user.user_id, product_id: product.value.id })
    alert(`"${product.value.title}" added to cart!`)
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to add to cart')
  } finally {
    addingCart.value = false
  }
}

const chatSeller = () => {
  if (!user) return router.push('/auth')
  router.push({
    path: '/messages',
    query: {
      seller_id:   product.value.seller_id,
      seller_name: product.value.seller_name
    }
  })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  const id = route.params.id
  if (!id) {
    loading.value = false
    return
  }
  try {
    const res = await api.getProduct(id)
    product.value = res.data
  } catch (err) {
    console.error('Product load error:', err)
    product.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.pd-page { background: #f4f7fb; min-height: calc(100vh - 62px); padding: 1.5rem; }

/* Loading */
.pd-loading { text-align: center; padding: 5rem; color: #888; }
.pd-spinner { width: 36px; height: 36px; border: 3px solid #e0e0e0; border-top-color: #003366; border-radius: 50%; animation: spin 0.7s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Not found */
.pd-notfound { text-align: center; padding: 5rem; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.pd-notfound h2 { font-size: 1.2rem; color: #003366; font-weight: 800; margin: 0; }
.pd-back-btn { background: #003366; color: #FFD700; padding: 10px 24px; border-radius: 9px; font-weight: 700; text-decoration: none; }

/* Container */
.pd-container { max-width: 1000px; margin: 0 auto; }

.pd-back { display: inline-flex; align-items: center; gap: 6px; background: #fff; border: 1px solid #e0e8f4; color: #003366; padding: 7px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; margin-bottom: 1.25rem; transition: 0.15s; font-family: inherit; }
.pd-back:hover { background: #eef3ff; }

.pd-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; background: #fff; border-radius: 18px; padding: 2rem; border: 1px solid #e8edf4; box-shadow: 0 4px 24px rgba(0,51,102,0.07); }

/* Images */
.pd-images { display: flex; flex-direction: column; gap: 12px; }
.pd-main-img-wrap { position: relative; border-radius: 14px; overflow: hidden; aspect-ratio: 1; background: #f0f4f8; }
.pd-main-img { width: 100%; height: 100%; object-fit: cover; display: block; }

.pd-img-arrow { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,51,102,0.7); color: #FFD700; border: none; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.15s; z-index: 5; }
.pd-img-arrow--l { left: 10px; }
.pd-img-arrow--r { right: 10px; }
.pd-img-arrow:hover { background: #003366; }

.pd-img-counter { position: absolute; bottom: 10px; right: 12px; background: rgba(0,0,0,0.5); color: #fff; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 10px; }

.pd-thumbs { display: flex; gap: 8px; flex-wrap: wrap; }
.pd-thumb { width: 64px; height: 64px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 2px solid transparent; transition: 0.15s; opacity: 0.7; }
.pd-thumb--active { border-color: #003366; opacity: 1; }
.pd-thumb:hover { opacity: 1; }

/* Info */
.pd-info { display: flex; flex-direction: column; gap: 14px; }

.pd-info__top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pd-category { background: #e8f0fe; color: #003366; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; }
.pd-status { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
.pd-status--available { background: #e8f8f0; color: #15803d; }
.pd-status--sold      { background: #fee8e8; color: #b91c1c; }
.pd-status__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

.pd-title { font-size: 1.5rem; font-weight: 800; color: #003366; margin: 0; line-height: 1.3; }
.pd-price { font-size: 1.8rem; font-weight: 900; color: #003366; }

.pd-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.pd-tag { display: inline-flex; align-items: center; gap: 4px; background: #eef3ff; color: #003366; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }

.pd-desc-box { background: #f8fafc; border-radius: 12px; padding: 14px; border: 1px solid #e8edf4; }
.pd-desc-box__title { font-size: 0.8rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.4px; margin: 0 0 6px; }
.pd-desc-box__text  { font-size: 0.9rem; color: #444; margin: 0; line-height: 1.6; white-space: pre-wrap; }

.pd-seller { display: flex; align-items: center; gap: 12px; background: #f8fafc; border-radius: 12px; padding: 12px 14px; border: 1px solid #e8edf4; }
.pd-seller__av { width: 40px; height: 40px; border-radius: 50%; background: #003366; color: #FFD700; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; flex-shrink: 0; border: 2px solid #FFD700; }
.pd-seller__name  { font-size: 0.9rem; font-weight: 700; color: #003366; margin: 0 0 2px; }
.pd-seller__label { font-size: 0.72rem; color: #aaa; margin: 0; }

.pd-posted { display: flex; align-items: center; gap: 5px; font-size: 0.78rem; color: #aaa; margin: 0; }

/* Actions */
.pd-actions { display: flex; flex-direction: column; gap: 10px; }

.pd-btn-cart { display: flex; align-items: center; justify-content: center; gap: 8px; background: #003366; color: #FFD700; border: none; padding: 14px; border-radius: 12px; font-size: 0.95rem; font-weight: 800; cursor: pointer; transition: 0.15s; font-family: inherit; }
.pd-btn-cart:hover:not(:disabled) { background: #002244; }
.pd-btn-cart:disabled { opacity: 0.6; cursor: not-allowed; }

.pd-btn-chat { display: flex; align-items: center; justify-content: center; gap: 8px; background: #fff; color: #003366; border: 1.5px solid #003366; padding: 12px; border-radius: 12px; font-size: 0.9rem; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.pd-btn-chat:hover { background: #eef3ff; }

.pd-own-notice { display: flex; align-items: center; gap: 8px; background: #fef9e0; color: #854d0e; font-size: 0.82rem; font-weight: 600; padding: 10px 14px; border-radius: 9px; flex-wrap: wrap; }
.pd-own-notice a { color: #003366; font-weight: 700; }
.pd-own-notice svg { flex-shrink: 0; }

.pd-sold-notice { display: flex; align-items: center; gap: 8px; background: #fee8e8; color: #b91c1c; font-size: 0.85rem; font-weight: 600; padding: 12px 14px; border-radius: 9px; }

.pd-safety { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #aaa; margin-top: auto; }

@media (max-width: 700px) {
  .pd-layout { grid-template-columns: 1fr; padding: 1.25rem; gap: 1.25rem; }
  .pd-title  { font-size: 1.2rem; }
  .pd-price  { font-size: 1.4rem; }
}
</style>