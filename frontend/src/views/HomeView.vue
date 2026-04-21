<template>
  <div class="wm-home">

    <!-- ── HERO ── -->
    <section class="wm-hero">
      <div class="wm-hero__content">
        <div class="wm-hero__badge">🎓 ADNU Students Only — Verified Sellers</div>
        <h1 class="wm-hero__title">
          Buy & Sell Within<br />
          <span class="wm-hero__gold">Your Campus</span>
        </h1>
        <p class="wm-hero__sub">The official peer-to-peer marketplace of Ateneo de Naga University.</p>

        <!-- SEARCHBAR in Hero -->
        <div class="wm-hero__search">
          <div class="wm-hero__search-box">
            <svg class="wm-hero__search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
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

          <!-- Live suggestions -->
          <div v-if="suggestions.length && heroSearch.length > 1" class="wm-hero__suggestions">
            <div
              v-for="s in suggestions.slice(0, 5)"
              :key="s.id"
              class="wm-hero__suggestion"
              @click="goToProduct(s.id)"
            >
              <img :src="s.image_url || '/placeholder.png'" class="wm-hero__sug-img" alt="" @error="e=>e.target.src='/placeholder.png'" />
              <div class="wm-hero__sug-info">
                <p class="wm-hero__sug-title">{{ s.title }}</p>
                <span class="wm-hero__sug-price">₱{{ fmtPrice(s.price) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="wm-hero__actions">
          <router-link to="/products" class="wm-hero__btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Browse Marketplace
          </router-link>
          <router-link to="/add-product" class="wm-hero__btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Sell an Item
          </router-link>
        </div>
      </div>

      <div class="wm-hero__stats">
        <div class="wm-stat"><span class="wm-stat__num">{{ stats.products || '—' }}</span><span class="wm-stat__lbl">Listings</span></div>
        <div class="wm-stat-div"></div>
        <div class="wm-stat"><span class="wm-stat__num">{{ stats.users || '—' }}</span><span class="wm-stat__lbl">Students</span></div>
        <div class="wm-stat-div"></div>
        <div class="wm-stat"><span class="wm-stat__num">6</span><span class="wm-stat__lbl">Colleges</span></div>
      </div>
    </section>

    <!-- ── CATEGORIES ── -->
    <section class="wm-section">
      <div class="wm-section__head">
        <h2 class="wm-section__title">Browse by Category</h2>
        <router-link to="/products" class="wm-section__link">See all →</router-link>
      </div>
      <div class="wm-cat-grid">
        <div
          v-for="cat in categories"
          :key="cat.label"
          class="wm-cat-card"
          @click="goCategory(cat.label)"
        >
          <span class="wm-cat-card__icon">{{ cat.icon }}</span>
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
        <span
          v-for="tag in popularTags"
          :key="tag"
          class="wm-tag-pill"
          @click="goTag(tag)"
        >#{{ tag }}</span>
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
          @added-to-cart="() => {}"
        />
      </div>
      <div v-else class="wm-empty">
        <p>No products yet. Be the first to sell!</p>
        <router-link to="/add-product" class="wm-empty__btn">Post an Item</router-link>
      </div>
    </section>

    <!-- ── CTA ── -->
    <section class="wm-cta">
      <div class="wm-cta__text">
        <h3>Have something to sell?</h3>
        <p>Post your item in seconds and reach hundreds of ADNU students.</p>
      </div>
      <router-link to="/add-product" class="wm-cta__btn">Start Selling</router-link>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProductCard  from '@/components/ProductCard.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import api from '@/services/api'

const router     = useRouter()
const products   = ref([])
const loading    = ref(true)
const heroSearch = ref('')
const suggestions = ref([])
const popularTags = ref([])
const stats      = ref({ products: 0, users: 0 })
let debounceTimer = null

const categories = [
  { icon: '📚', label: 'Textbooks' },
  { icon: '📱', label: 'Electronics' },
  { icon: '🛏️', label: 'Dorm Items' },
  { icon: '👕', label: 'Uniforms' },
  { icon: '✏️', label: 'School Supplies' },
  { icon: '🍱', label: 'Food' },
  { icon: '🛠️', label: 'Services' },
  { icon: '📦', label: 'Others' },
]

const fmtPrice = (v) => parseFloat(v).toLocaleString('en-PH', { minimumFractionDigits: 2 })

// Compute lowest price per category
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

const goSearch = () => {
  if (heroSearch.value.trim()) {
    router.push({ path: '/products', query: { search: heroSearch.value.trim() } })
  } else {
    router.push('/products')
  }
  suggestions.value = []
}

const goToProduct = (id) => { router.push('/products/' + id); suggestions.value = [] }
const goCategory  = (cat) => router.push({ path: '/products', query: { category: cat } })
const goTag       = (tag) => router.push({ path: '/products', query: { tag } })

const debouncedSearch = () => {
  clearTimeout(debounceTimer)
  if (heroSearch.value.length < 2) { suggestions.value = []; return }
  debounceTimer = setTimeout(async () => {
    try {
      const r = await api.getProducts({ search: heroSearch.value })
      suggestions.value = Array.isArray(r.data) ? r.data.slice(0, 5) : []
    } catch {}
  }, 300)
}

onMounted(async () => {
  try {
    const [prodRes, tagsRes, statsRes] = await Promise.all([
      api.getProducts({ sort: 'newest' }),
      api.getAllTags(),
      api.adminStats().catch(() => ({ data: {} }))
    ])
    products.value  = Array.isArray(prodRes.data) ? prodRes.data.slice(0, 8) : []
    popularTags.value = Array.isArray(tagsRes.data) ? tagsRes.data.slice(0, 15) : []
    stats.value = statsRes.data || {}
  } catch (err) {
    console.error('Home load error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.wm-home { background: #f4f7fb; min-height: 100vh; }

/* HERO */
.wm-hero {
  background: #003366;
  color: #fff;
  padding: 4rem 2rem 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.wm-hero::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 300px; height: 300px;
  background: rgba(255,215,0,0.05);
  border-radius: 50%;
  pointer-events: none;
}
.wm-hero__badge {
  display: inline-block;
  background: rgba(255,215,0,0.15);
  color: #FFD700;
  border: 1px solid rgba(255,215,0,0.3);
  padding: 5px 16px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
}
.wm-hero__title {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 1rem;
}
.wm-hero__gold { color: #FFD700; }
.wm-hero__sub {
  color: rgba(255,255,255,0.7);
  font-size: 1rem;
  max-width: 480px;
  margin: 0 auto 2rem;
  line-height: 1.6;
}

/* Search */
.wm-hero__search {
  max-width: 600px;
  margin: 0 auto 1.75rem;
  position: relative;
}
.wm-hero__search-box {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 12px;
  padding: 6px 6px 6px 16px;
  gap: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.wm-hero__search-icon { color: #aaa; flex-shrink: 0; }
.wm-hero__search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.95rem;
  color: #333;
  font-family: inherit;
  background: transparent;
}
.wm-hero__search-input::placeholder { color: #bbb; }
.wm-hero__search-btn {
  background: #003366;
  color: #FFD700;
  border: none;
  border-radius: 8px;
  padding: 9px 22px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: 0.15s;
  white-space: nowrap;
  font-family: inherit;
}
.wm-hero__search-btn:hover { background: #002244; }

/* Suggestions */
.wm-hero__suggestions {
  position: absolute;
  top: calc(100% + 6px);
  left: 0; right: 0;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  overflow: hidden;
  z-index: 100;
  text-align: left;
}
.wm-hero__suggestion {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.12s;
  border-bottom: 1px solid #f5f5f5;
}
.wm-hero__suggestion:last-child { border-bottom: none; }
.wm-hero__suggestion:hover { background: #f0f5ff; }
.wm-hero__sug-img { width: 38px; height: 38px; border-radius: 7px; object-fit: cover; background: #f0f4f8; flex-shrink: 0; }
.wm-hero__sug-info { flex: 1; min-width: 0; }
.wm-hero__sug-title { font-size: 0.85rem; font-weight: 600; color: #003366; margin: 0 0 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.wm-hero__sug-price { font-size: 0.78rem; color: #888; }

/* Actions */
.wm-hero__actions { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
.wm-hero__btn-primary {
  background: #FFD700;
  color: #003366;
  padding: 11px 24px;
  border-radius: 9px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  transition: 0.15s;
}
.wm-hero__btn-primary:hover { background: #e6c200; }
.wm-hero__btn-secondary {
  background: transparent;
  border: 1.5px solid rgba(255,255,255,0.45);
  color: #fff;
  padding: 11px 24px;
  border-radius: 9px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  transition: 0.15s;
}
.wm-hero__btn-secondary:hover { border-color: #fff; background: rgba(255,255,255,0.08); }

/* Stats */
.wm-hero__stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.wm-stat { display: flex; flex-direction: column; align-items: center; }
.wm-stat__num { font-size: 1.8rem; font-weight: 800; color: #FFD700; }
.wm-stat__lbl { font-size: 0.75rem; color: rgba(255,255,255,0.6); margin-top: 2px; }
.wm-stat-div { width: 1px; height: 36px; background: rgba(255,255,255,0.15); }

/* Sections */
.wm-section { max-width: 1200px; margin: 0 auto; padding: 2.5rem 1.5rem; }
.wm-section__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.wm-section__title { font-size: 1.2rem; font-weight: 800; color: #003366; margin: 0; }
.wm-section__link { font-size: 0.875rem; color: #003366; font-weight: 600; text-decoration: none; }
.wm-section__link:hover { text-decoration: underline; }

/* Categories */
.wm-cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
}
.wm-cat-card {
  background: #fff;
  border: 1px solid #e8edf4;
  padding: 1.1rem 0.5rem;
  border-radius: 14px;
  text-align: center;
  cursor: pointer;
  transition: 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.wm-cat-card:hover { border-color: #003366; background: #eef3ff; transform: translateY(-2px); }
.wm-cat-card__icon { font-size: 1.8rem; }
.wm-cat-card__label { font-size: 0.75rem; font-weight: 700; color: #003366; }

/* Tags */
.wm-tags-row { display: flex; flex-wrap: wrap; gap: 8px; }
.wm-tag-pill {
  background: #e8f0fe;
  color: #003366;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 5px 14px;
  border-radius: 20px;
  cursor: pointer;
  transition: 0.15s;
  border: 1px solid transparent;
}
.wm-tag-pill:hover { background: #003366; color: #FFD700; }

/* Product grid */
.wm-product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.25rem;
}

/* Empty */
.wm-empty { text-align: center; padding: 3rem; background: #fff; border-radius: 14px; }
.wm-empty p { color: #888; margin: 0 0 1rem; }
.wm-empty__btn {
  background: #003366;
  color: #fff;
  padding: 10px 24px;
  border-radius: 9px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-block;
}

/* CTA */
.wm-cta {
  background: linear-gradient(135deg, #003366, #0055aa);
  color: #fff;
  padding: 2.5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  flex-wrap: wrap;
}
.wm-cta__text h3 { font-size: 1.3rem; font-weight: 800; margin: 0 0 6px; }
.wm-cta__text p  { color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; }
.wm-cta__btn {
  background: #FFD700;
  color: #003366;
  padding: 12px 28px;
  border-radius: 9px;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  transition: 0.15s;
}
.wm-cta__btn:hover { background: #e6c200; }
</style>