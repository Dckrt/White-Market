<template>
  <div class="wm-home">

    <!-- ── HERO ── -->
    <section class="wm-hero">
      <div class="wm-hero__content">
        <div class="wm-hero__badge">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
          ADNU Students Only — Verified Sellers
        </div>
        <h1 class="wm-hero__title">
          Buy &amp; Sell Within<br />
          <span class="wm-hero__gold">Your Campus</span>
        </h1>
        <p class="wm-hero__sub">The official peer-to-peer marketplace of Ateneo de Naga University.</p>

        <!-- Search -->
        <div class="wm-hero__search">
          <div class="wm-hero__search-box">
            <svg class="wm-hero__search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              v-model="heroSearch"
              type="text"
              placeholder="Search for textbooks, electronics, uniforms…"
              class="wm-hero__search-input"
              @keyup.enter="goSearch"
              @input="debouncedSearch"
            />
            <button class="wm-hero__search-btn" @click="goSearch">Search</button>
          </div>
          <div v-if="suggestions.length && heroSearch.length > 1" class="wm-hero__suggestions">
            <div
              v-for="s in suggestions.slice(0, 5)"
              :key="s.id"
              class="wm-hero__suggestion"
              @click="goToProduct(s.id)"
            >
              <img :src="s.image_url || '/placeholder.png'" class="wm-hero__sug-img" alt="" @error="e => e.target.src='/placeholder.png'" />
              <div class="wm-hero__sug-info">
                <p class="wm-hero__sug-title">{{ s.title }}</p>
                <span class="wm-hero__sug-price">₱{{ fmtPrice(s.price) }}</span>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>
        </div>

        <div class="wm-hero__actions">
          <router-link to="/products" class="wm-hero__btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
            Browse Marketplace
          </router-link>
          <router-link to="/add-product" class="wm-hero__btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Sell an Item
          </router-link>
        </div>
      </div>

      <div class="wm-hero__stats">
        <div class="wm-stat">
          <span class="wm-stat__num">{{ stats.products || '—' }}</span>
          <span class="wm-stat__lbl">Listings</span>
        </div>
        <div class="wm-stat-div"></div>
        <div class="wm-stat">
          <span class="wm-stat__num">{{ stats.users || '—' }}</span>
          <span class="wm-stat__lbl">Students</span>
        </div>
        <div class="wm-stat-div"></div>
        <div class="wm-stat">
          <span class="wm-stat__num">6</span>
          <span class="wm-stat__lbl">Colleges</span>
        </div>
      </div>
    </section>

    <!-- ── CATEGORIES ── -->
    <section class="wm-section">
      <div class="wm-section__head">
        <h2 class="wm-section__title">Browse by Category</h2>
        <router-link to="/products" class="wm-section__link">See all →</router-link>
      </div>
      <div class="wm-cat-grid">
        <div v-for="cat in categories" :key="cat.label" class="wm-cat-card" @click="goCategory(cat.label)">
          <div class="wm-cat-card__icon-wrap">
            <component :is="cat.icon" />
          </div>
          <span class="wm-cat-card__label">{{ cat.label }}</span>
        </div>
      </div>
    </section>

    <!-- ── POPULAR TAGS ── -->
    <section class="wm-section" v-if="popularTags.length">
      <div class="wm-section__head">
        <h2 class="wm-section__title">Popular Tags</h2>
      </div>
      <div class="wm-tags-row">
        <span v-for="tag in popularTags" :key="tag" class="wm-tag-pill" @click="goTag(tag)">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          {{ tag }}
        </span>
      </div>
    </section>

    <!-- ── LATEST LISTINGS ── -->
    <section class="wm-section">
      <div class="wm-section__head">
        <h2 class="wm-section__title">Latest Listings</h2>
        <router-link to="/products" class="wm-section__link">See all →</router-link>
      </div>
      <div v-if="loading" class="wm-product-grid">
        <SkeletonCard v-for="n in 8" :key="n" />
      </div>
      <div v-else-if="products.length" class="wm-product-grid">
        <ProductCard
          v-for="p in products"
          :key="p.id"
          :product="p"
          :isCheap="isLowestInCategory(p)"
          @tag-click="goTag"
        />
      </div>
      <div v-else class="wm-empty">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
        <p>No products yet. Be the first to sell!</p>
        <router-link to="/add-product" class="wm-empty__btn">Post an Item</router-link>
      </div>
    </section>

    <!-- ── CTA ── -->
    <section class="wm-cta">
      <div class="wm-cta__icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#FFD700" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
      </div>
      <div class="wm-cta__text">
        <h3>Have something to sell?</h3>
        <p>Post your item in seconds and reach hundreds of ADNU students.</p>
      </div>
      <router-link to="/add-product" class="wm-cta__btn">Start Selling</router-link>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import ProductCard  from '@/components/ProductCard.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import api from '@/services/api'

const router      = useRouter()
const products    = ref([])
const loading     = ref(true)
const heroSearch  = ref('')
const suggestions = ref([])
const popularTags = ref([])
const stats       = ref({})
let debounceTimer = null

// ── Category SVG icons (inline render functions) ──────────────────────────
const IconBook = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M4 19.5A2.5 2.5 0 016.5 17H20'}),h('path',{d:'M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z'})]) }
const IconLaptop = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('rect',{x:'2',y:'3',width:'20',height:'14',rx:'2',ry:'2'}),h('line',{x1:'8',y1:'21',x2:'16',y2:'21'}),h('line',{x1:'12',y1:'17',x2:'12',y2:'21'})]) }
const IconHome = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z'}),h('polyline',{points:'9 22 9 12 15 12 15 22'})]) }
const IconShirt = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M20.38 3.46L16 2a4 4 0 01-8 0L3.62 3.46a2 2 0 00-1.34 2.23l.58 3.57a1 1 0 00.99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 002-2V10h2.15a1 1 0 00.99-.84l.58-3.57a2 2 0 00-1.34-2.23z'})]) }
const IconPencil = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M12 20h9'}),h('path',{d:'M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z'})]) }
const IconCoffee = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M18 8h1a4 4 0 010 8h-1'}),h('path',{d:'M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8z'}),h('line',{x1:'6',y1:'1',x2:'6',y2:'4'}),h('line',{x1:'10',y1:'1',x2:'10',y2:'4'}),h('line',{x1:'14',y1:'1',x2:'14',y2:'4'})]) }
const IconTool = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z'})]) }
const IconBox = { render: () => h('svg', { width:22, height:22, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, [h('path',{d:'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z'}),h('polyline',{points:'3.27 6.96 12 12.01 20.73 6.96'}),h('line',{x1:'12',y1:'22.08',x2:'12',y2:'12'})]) }

const categories = [
  { label: 'Textbooks',       icon: IconBook },
  { label: 'Electronics',     icon: IconLaptop },
  { label: 'Dorm Items',      icon: IconHome },
  { label: 'Uniforms',        icon: IconShirt },
  { label: 'School Supplies', icon: IconPencil },
  { label: 'Food',            icon: IconCoffee },
  { label: 'Services',        icon: IconTool },
  { label: 'Others',          icon: IconBox },
]

const fmtPrice = (v) => parseFloat(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })

const categoryMinPrices = computed(() => {
  const map = {}
  products.value.forEach(p => {
    if (!map[p.category] || p.price < map[p.category]) map[p.category] = p.price
  })
  return map
})
const isLowestInCategory = (p) => {
  const min = categoryMinPrices.value[p.category]
  return min !== undefined && p.price === min
}

const goSearch    = () => { if (heroSearch.value.trim()) router.push({ path: '/products', query: { search: heroSearch.value.trim() } }); else router.push('/products'); suggestions.value = [] }
const goToProduct = (id) => { router.push('/products/' + id); suggestions.value = [] }
const goCategory  = (cat) => router.push({ path: '/products', query: { category: cat } })
const goTag       = (tag) => router.push({ path: '/products', query: { tag } })

const debouncedSearch = () => {
  clearTimeout(debounceTimer)
  if (heroSearch.value.length < 2) { suggestions.value = []; return }
  debounceTimer = setTimeout(async () => {
    try { const r = await api.getProducts({ search: heroSearch.value }); suggestions.value = Array.isArray(r.data) ? r.data.slice(0, 5) : [] } catch {}
  }, 300)
}

onMounted(async () => {
  try {
    const [prodRes, tagsRes, statsRes] = await Promise.all([
      api.getProducts({ sort: 'newest' }),
      api.getAllTags().catch(() => ({ data: [] })),
      api.adminStats().catch(() => ({ data: {} }))
    ])
    products.value   = Array.isArray(prodRes.data) ? prodRes.data.slice(0, 8) : []
    popularTags.value = Array.isArray(tagsRes.data) ? tagsRes.data.slice(0, 14) : []
    stats.value      = statsRes.data || {}
  } catch (err) { console.error('Home error:', err) }
  finally { loading.value = false }
})
</script>

<style scoped>
.wm-home { background:#f4f7fb; min-height:100vh; }

/* HERO */
.wm-hero { background:#003366; color:#fff; padding:4rem 2rem 2.5rem; text-align:center; position:relative; overflow:hidden; }
.wm-hero::before { content:''; position:absolute; top:-80px; right:-80px; width:360px; height:360px; background:rgba(255,215,0,0.04); border-radius:50%; pointer-events:none; }
.wm-hero::after  { content:''; position:absolute; bottom:-60px; left:-60px; width:240px; height:240px; background:rgba(255,255,255,0.03); border-radius:50%; pointer-events:none; }

.wm-hero__badge { display:inline-flex; align-items:center; gap:6px; background:rgba(255,215,0,0.13); color:#FFD700; border:1px solid rgba(255,215,0,0.28); padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:600; margin-bottom:1.25rem; }
.wm-hero__title { font-size:clamp(1.8rem,4vw,2.8rem); font-weight:800; line-height:1.2; margin:0 0 1rem; }
.wm-hero__gold  { color:#FFD700; }
.wm-hero__sub   { color:rgba(255,255,255,0.7); font-size:1rem; max-width:480px; margin:0 auto 2rem; line-height:1.6; }

/* Search */
.wm-hero__search { max-width:600px; margin:0 auto 1.75rem; position:relative; }
.wm-hero__search-box { display:flex; align-items:center; background:#fff; border-radius:12px; padding:6px 6px 6px 16px; gap:10px; box-shadow:0 4px 24px rgba(0,0,0,0.22); }
.wm-hero__search-icon { color:#aaa; flex-shrink:0; }
.wm-hero__search-input { flex:1; border:none; outline:none; font-size:0.95rem; color:#333; font-family:inherit; background:transparent; }
.wm-hero__search-input::placeholder { color:#bbb; }
.wm-hero__search-btn { background:#003366; color:#FFD700; border:none; border-radius:8px; padding:9px 22px; font-weight:700; font-size:0.9rem; cursor:pointer; transition:0.15s; white-space:nowrap; font-family:inherit; }
.wm-hero__search-btn:hover { background:#002244; }

.wm-hero__suggestions { position:absolute; top:calc(100% + 6px); left:0; right:0; background:#fff; border-radius:12px; box-shadow:0 8px 32px rgba(0,0,0,0.15); overflow:hidden; z-index:100; text-align:left; }
.wm-hero__suggestion { display:flex; align-items:center; gap:10px; padding:10px 14px; cursor:pointer; transition:background 0.12s; border-bottom:1px solid #f5f5f5; }
.wm-hero__suggestion:last-child { border-bottom:none; }
.wm-hero__suggestion:hover { background:#f0f5ff; }
.wm-hero__sug-img { width:38px; height:38px; border-radius:7px; object-fit:cover; background:#f0f4f8; flex-shrink:0; }
.wm-hero__sug-info { flex:1; min-width:0; }
.wm-hero__sug-title { font-size:0.85rem; font-weight:600; color:#003366; margin:0 0 2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.wm-hero__sug-price { font-size:0.78rem; color:#888; }

.wm-hero__actions { display:flex; justify-content:center; gap:12px; flex-wrap:wrap; }
.wm-hero__btn-primary { background:#FFD700; color:#003366; padding:11px 24px; border-radius:9px; font-weight:700; text-decoration:none; font-size:0.9rem; display:inline-flex; align-items:center; gap:7px; transition:0.15s; }
.wm-hero__btn-primary:hover { background:#e6c200; }
.wm-hero__btn-secondary { background:transparent; border:1.5px solid rgba(255,255,255,0.4); color:#fff; padding:11px 24px; border-radius:9px; font-weight:700; text-decoration:none; font-size:0.9rem; display:inline-flex; align-items:center; gap:7px; transition:0.15s; }
.wm-hero__btn-secondary:hover { border-color:#fff; background:rgba(255,255,255,0.08); }

.wm-hero__stats { display:flex; justify-content:center; align-items:center; gap:32px; margin-top:3rem; padding-top:2rem; border-top:1px solid rgba(255,255,255,0.1); }
.wm-stat { display:flex; flex-direction:column; align-items:center; }
.wm-stat__num { font-size:1.8rem; font-weight:800; color:#FFD700; }
.wm-stat__lbl { font-size:0.75rem; color:rgba(255,255,255,0.6); margin-top:2px; }
.wm-stat-div { width:1px; height:36px; background:rgba(255,255,255,0.15); }

/* Sections */
.wm-section { max-width:1200px; margin:0 auto; padding:2.5rem 1.5rem; }
.wm-section__head { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; }
.wm-section__title { font-size:1.2rem; font-weight:800; color:#003366; margin:0; }
.wm-section__link { font-size:0.875rem; color:#003366; font-weight:600; text-decoration:none; }
.wm-section__link:hover { text-decoration:underline; }

/* Categories */
.wm-cat-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(110px,1fr)); gap:10px; }
.wm-cat-card { background:#fff; border:1px solid #e8edf4; padding:1.1rem 0.5rem; border-radius:14px; text-align:center; cursor:pointer; transition:0.2s; display:flex; flex-direction:column; align-items:center; gap:10px; }
.wm-cat-card:hover { border-color:#003366; background:#eef3ff; transform:translateY(-2px); box-shadow:0 4px 16px rgba(0,51,102,0.08); }
.wm-cat-card__icon-wrap { width:44px; height:44px; background:#eef3ff; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#003366; transition:0.2s; }
.wm-cat-card:hover .wm-cat-card__icon-wrap { background:#003366; color:#FFD700; }
.wm-cat-card__label { font-size:0.75rem; font-weight:700; color:#003366; }

/* Tags */
.wm-tags-row { display:flex; flex-wrap:wrap; gap:8px; }
.wm-tag-pill { display:inline-flex; align-items:center; gap:5px; background:#fff; color:#003366; font-size:0.82rem; font-weight:600; padding:6px 14px; border-radius:20px; cursor:pointer; transition:0.15s; border:1px solid #e0e8f4; }
.wm-tag-pill:hover { background:#003366; color:#FFD700; border-color:#003366; }

/* Products */
.wm-product-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:1.25rem; }

/* Empty */
.wm-empty { text-align:center; padding:3rem; background:#fff; border-radius:14px; border:1px solid #e8edf4; display:flex; flex-direction:column; align-items:center; gap:12px; }
.wm-empty p { color:#888; margin:0; font-size:0.9rem; }
.wm-empty__btn { background:#003366; color:#fff; padding:10px 24px; border-radius:9px; font-weight:700; text-decoration:none; font-size:0.9rem; }

/* CTA */
.wm-cta { background:linear-gradient(135deg,#003366,#004d99); color:#fff; padding:2.5rem 2rem; display:flex; align-items:center; justify-content:center; gap:2rem; flex-wrap:wrap; }
.wm-cta__icon { width:64px; height:64px; background:rgba(255,215,0,0.12); border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.wm-cta__text h3 { font-size:1.3rem; font-weight:800; margin:0 0 6px; }
.wm-cta__text p  { color:rgba(255,255,255,0.7); font-size:0.9rem; margin:0; }
.wm-cta__btn { background:#FFD700; color:#003366; padding:12px 28px; border-radius:9px; font-weight:800; text-decoration:none; white-space:nowrap; transition:0.15s; }
.wm-cta__btn:hover { background:#e6c200; }
</style>