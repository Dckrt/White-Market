<template>
  <div class="wm-card" @click="goToProduct">
    <!-- Image Carousel -->
    <div class="wm-card__img-wrap">
      <div class="wm-card__slides" :style="{ transform: `translateX(-${activeSlide * 100}%)` }">
        <img
          v-for="(img, i) in displayImages"
          :key="i"
          :src="img"
          :alt="product.title"
          class="wm-card__slide"
          @error="e => e.target.src = '/placeholder.png'"
        />
      </div>

      <!-- Arrows -->
      <button v-if="displayImages.length > 1" class="wm-card__arrow wm-card__arrow--l" @click.stop="prevSlide">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <button v-if="displayImages.length > 1" class="wm-card__arrow wm-card__arrow--r" @click.stop="nextSlide">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="9 18 15 12 9 6"/></svg>
      </button>

      <!-- Slide dots -->
      <div v-if="displayImages.length > 1" class="wm-card__dots" @click.stop>
        <span
          v-for="(_, i) in displayImages"
          :key="i"
          :class="['wm-card__dot', i === activeSlide && 'wm-card__dot--on']"
          @click.stop="activeSlide = i"
        ></span>
      </div>

      <!-- Badges top-left -->
      <div class="wm-card__badges-top">
        <span class="wm-card__cat-badge">{{ product.category }}</span>
        <span v-if="isCheap" class="wm-card__cheap-badge">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z"/></svg>
          Best Price
        </span>
      </div>

      <!-- Available badge -->
      <span class="wm-card__status-badge">
        <span class="wm-card__status-dot"></span>Available
      </span>

      <!-- Image count -->
      <span v-if="displayImages.length > 1" class="wm-card__img-count">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        {{ activeSlide + 1 }}/{{ displayImages.length }}
      </span>
    </div>

    <!-- Body -->
    <div class="wm-card__body">
      <h3 class="wm-card__title">{{ product.title }}</h3>
      <p class="wm-card__desc">{{ product.description || 'No description provided.' }}</p>

      <!-- Tags -->
      <div v-if="productTags.length" class="wm-card__tags" @click.stop>
        <span
          v-for="tag in productTags.slice(0, 3)"
          :key="tag"
          class="wm-card__tag"
          @click.stop="$emit('tag-click', tag.trim())"
        >
          <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/></svg>
          {{ tag.trim() }}
        </span>
      </div>

      <!-- Seller -->
      <div class="wm-card__seller-wrap">

      <div class="wm-card__seller">
        <div class="wm-card__seller-av">
          {{ sellerInitial }}
        </div>

        <span class="wm-card__seller-name">
          {{ product.seller_name || 'ADNU Student' }}
        </span>
      </div>

      <SellerRating :rating="product.seller_rating || 0" />

    </div>

      <!-- Footer -->
      <div class="wm-card__footer">
        <div class="wm-card__price-wrap">
          <span class="wm-card__price">₱{{ fmtPrice(product.price) }}</span>
          <span v-if="isCheap" class="wm-card__cheap-label">Lowest price</span>
        </div>
        <div class="wm-card__actions" @click.stop>
          <button class="wm-card__cart-btn" @click.stop="addToCart" :disabled="product.status !== 'Available'" title="Add to Cart">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
          </button>
          <button class="wm-card__buy-btn" @click.stop="goToProduct" :disabled="product.status !== 'Available'">
            Buy Now
          </button>
        </div>
      </div>
    </div>
  </div>
  
</template>





<script setup>
import SellerRating from '@/components/RatingStars.vue'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const props  = defineProps({ product: { type: Object, required: true }, isCheap: { type: Boolean, default: false } })
const emit   = defineEmits(['tag-click', 'added-to-cart'])
const router = useRouter()
const activeSlide = ref(0)

const displayImages = computed(() => {
  if (props.product.images?.length) return props.product.images
  if (props.product.image_url) return [props.product.image_url]
  return ['/placeholder.png']
})
const productTags = computed(() => {
  if (Array.isArray(props.product.tags)) return props.product.tags.filter(Boolean)
  if (typeof props.product.tags === 'string') return props.product.tags.split(',').filter(Boolean)
  return []
})
const sellerInitial = computed(() => (props.product.seller_name || 'A').charAt(0).toUpperCase())
const fmtPrice = (v) => parseFloat(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })
const goToProduct = () => router.push('/products/' + props.product.id)
const prevSlide = () => activeSlide.value = activeSlide.value === 0 ? displayImages.value.length - 1 : activeSlide.value - 1
const nextSlide = () => activeSlide.value = activeSlide.value === displayImages.value.length - 1 ? 0 : activeSlide.value + 1

const addToCart = async () => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (!user) return router.push('/auth')
  try {
    await api.addToCart({ user_id: user.user_id, product_id: props.product.id })
    emit('added-to-cart')
    alert(`"${props.product.title}" added to cart! ✅`)
  } catch (err) {
    alert((err.response?.data?.message || 'Failed to add to cart') + ' ❌')
  }
}
</script>

<style scoped>
.wm-card { background:#fff; border-radius:16px; border:1px solid #e8edf4; overflow:hidden; cursor:pointer; transition:transform 0.2s, box-shadow 0.2s, border-color 0.2s; display:flex; flex-direction:column; }
.wm-card:hover { transform:translateY(-4px); box-shadow:0 12px 32px rgba(0,51,102,0.11); border-color:#bdd0e8; }

/* Carousel */
.wm-card__img-wrap { position:relative; height:190px; overflow:hidden; background:#f0f4f8; }
.wm-card__slides { display:flex; height:100%; transition:transform 0.35s ease; }
.wm-card__slide { min-width:100%; height:100%; object-fit:cover; flex-shrink:0; }

.wm-card__arrow { position:absolute; top:50%; transform:translateY(-50%); background:rgba(0,51,102,0.65); color:#FFD700; border:none; width:28px; height:28px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; opacity:0; transition:opacity 0.2s; z-index:5; }
.wm-card:hover .wm-card__arrow { opacity:1; }
.wm-card__arrow--l { left:8px; }
.wm-card__arrow--r { right:8px; }
.wm-card__arrow:hover { background:#003366; }

.wm-card__dots { position:absolute; bottom:8px; left:50%; transform:translateX(-50%); display:flex; gap:4px; z-index:5; }
.wm-card__dot { width:6px; height:6px; border-radius:50%; background:rgba(255,255,255,0.5); cursor:pointer; transition:background 0.2s; }
.wm-card__dot--on { background:#fff; }

.wm-card__img-count { position:absolute; bottom:8px; right:10px; background:rgba(0,0,0,0.5); color:#fff; font-size:10px; font-weight:600; padding:2px 8px; border-radius:10px; z-index:5; display:flex; align-items:center; gap:4px; }

.wm-card__badges-top { position:absolute; top:10px; left:10px; display:flex; flex-direction:column; gap:4px; z-index:5; }
.wm-card__cat-badge { background:#003366; color:#FFD700; font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px; display:inline-block; }
.wm-card__cheap-badge { background:#dc2626; color:#fff; font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px; display:inline-flex; align-items:center; gap:4px; animation:pulse-b 2s infinite; }
@keyframes pulse-b { 0%,100%{opacity:1}50%{opacity:0.78} }

.wm-card__status-badge { position:absolute; top:10px; right:10px; background:rgba(255,255,255,0.94); color:#16a34a; font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px; z-index:5; display:flex; align-items:center; gap:5px; }
.wm-card__status-dot { width:5px; height:5px; border-radius:50%; background:#16a34a; flex-shrink:0; }

/* Body */
.wm-card__body { padding:14px; display:flex; flex-direction:column; flex:1; gap:7px; }
.wm-card__title { font-size:0.95rem; font-weight:700; color:#003366; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.wm-card__desc  { font-size:0.78rem; color:#999; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.wm-card__tags { display:flex; flex-wrap:wrap; gap:4px; }
.wm-card__tag { font-size:10px; font-weight:600; color:#003366; background:#e8f0fe; padding:2px 8px; border-radius:10px; cursor:pointer; transition:0.15s; display:inline-flex; align-items:center; gap:4px; }
.wm-card__tag:hover { background:#003366; color:#FFD700; }

.wm-card__seller { display:flex; align-items:center; gap:6px; font-size:0.78rem; color:#888; }
.wm-card__seller-av { width:20px; height:20px; border-radius:50%; background:#003366; color:#FFD700; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:800; flex-shrink:0; }
.wm-card__seller-name { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:120px; }

.wm-card__footer { display:flex; align-items:center; justify-content:space-between; margin-top:auto; padding-top:8px; border-top:1px solid #f0f4f8; }
.wm-card__price-wrap { display:flex; flex-direction:column; gap:2px; }
.wm-card__price { font-size:1.05rem; font-weight:800; color:#003366; }
.wm-card__cheap-label { font-size:10px; font-weight:700; color:#dc2626; }
.wm-card__actions { display:flex; gap:6px; }

.wm-card__cart-btn { width:34px; height:34px; border-radius:8px; border:1.5px solid #e0e8f4; background:#f8faff; color:#003366; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:0.15s; }
.wm-card__cart-btn:hover:not(:disabled) { background:#003366; color:#FFD700; border-color:#003366; }
.wm-card__cart-btn:disabled { opacity:0.4; cursor:not-allowed; }

.wm-card__buy-btn { background:#003366; color:#fff; border:none; border-radius:8px; padding:0 14px; height:34px; font-weight:700; font-size:0.82rem; cursor:pointer; transition:0.15s; font-family:inherit; }
.wm-card__buy-btn:hover:not(:disabled) { background:#002244; }
.wm-card__buy-btn:disabled { opacity:0.4; cursor:not-allowed; }

.wm-card__seller-wrap{
  display:flex;
  flex-direction:column;
  gap:6px;
}
</style>