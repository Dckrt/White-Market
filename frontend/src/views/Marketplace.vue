<template>
  <div class="mp">

    <!-- ── HERO SEARCH BAR ─────────────────────────────────────────────── -->
    <div class="mp-hero">
      <div class="mp-hero__inner">
        <div class="mp-hero__text">
          <h1 class="mp-hero__title">University<br/><em>Market</em></h1>
          <p class="mp-hero__sub">Verified essentials for Ateneo de Naga students</p>
        </div>
        <div class="mp-search-wrap">
          <div class="mp-search">
            <svg class="mp-search__icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search for textbooks, uniforms, electronics…"
              @input="debouncedFetch"
              class="mp-search__input"
            />
            <button v-if="searchQuery" @click="clearSearch" class="mp-search__clear">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- Price filter inline with search -->
          <div class="mp-price-filter">
            <div class="mp-price-field">
              <span class="mp-price-field__label">Min</span>
              <input type="number" v-model="minPrice" placeholder="₱0" min="0" class="mp-price-input"/>
            </div>
            <span class="mp-price-dash">—</span>
            <div class="mp-price-field">
              <span class="mp-price-field__label">Max</span>
              <input type="number" v-model="maxPrice" placeholder="Any" min="0" class="mp-price-input"/>
            </div>
            <button @click="applyAdvancedFilter" class="mp-apply-btn">Apply</button>
            <button v-if="appliedMinPrice || appliedMaxPrice" @click="clearPriceFilter" class="mp-clear-price-btn">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── TOOLBAR ─────────────────────────────────────────────────────── -->
    <div class="mp-toolbar-wrap">
      <div class="mp-toolbar">

        <!-- Category pills -->
        <div class="mp-cats">
          <button
            v-for="cat in categories"
            :key="cat"
            class="mp-cat"
            :class="{ 'mp-cat--on': selectedCategory === cat }"
            @click="selectCategory(cat)"
          >{{ cat }}</button>
        </div>

        <!-- Sort + count -->
        <div class="mp-sort-row">
          <span class="mp-count" v-if="!loading">
            <strong>{{ displayedProducts.length }}</strong>
            {{ displayedProducts.length === 1 ? 'item' : 'items' }}
          </span>
          <div class="mp-sort-wrap">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mp-sort-icon"><line x1="3" y1="6" x2="21" y2="6"/><line x1="7" y1="12" x2="17" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/></svg>
            <select v-model="sortBy" @change="applySorting" class="mp-sort">
              <option value="">Sort by</option>
              <option value="az">A → Z</option>
              <option value="za">Z → A</option>
              <option value="low-high">Price: Low → High</option>
              <option value="high-low">Price: High → Low</option>
            </select>
          </div>
        </div>

      </div>

      <!-- Active filter tags -->
      <div class="mp-active-filters" v-if="searchQuery || selectedCategory !== 'All' || appliedMinPrice || appliedMaxPrice">
        <span class="mp-filter-label">Active:</span>
        <span v-if="selectedCategory !== 'All'" class="mp-ftag">
          {{ selectedCategory }}
          <button @click="selectCategory('All')">×</button>
        </span>
        <span v-if="searchQuery" class="mp-ftag">
          "{{ searchQuery }}"
          <button @click="clearSearchOnly">×</button>
        </span>
        <span v-if="appliedMinPrice || appliedMaxPrice" class="mp-ftag">
          ₱{{ appliedMinPrice || '0' }} – ₱{{ appliedMaxPrice || '∞' }}
          <button @click="clearPriceFilter">×</button>
        </span>
        <button class="mp-clear-all" @click="clearSearch">Clear all</button>
      </div>
    </div>

    <!-- ── CONTENT ──────────────────────────────────────────────────────── -->
    <div class="mp-content">

      <!-- Loading skeletons -->
      <div v-if="loading" class="mp-grid">
        <div v-for="n in 12" :key="n" class="mp-skeleton">
          <div class="mp-skeleton__img"></div>
          <div class="mp-skeleton__body">
            <div class="mp-skeleton__line mp-skeleton__line--wide"></div>
            <div class="mp-skeleton__line mp-skeleton__line--narrow"></div>
            <div class="mp-skeleton__line mp-skeleton__line--mid"></div>
          </div>
        </div>
      </div>

      <!-- Products -->
      <div v-else-if="displayedProducts.length > 0" class="mp-grid">
        <ProductCard
          v-for="p in displayedProducts"
          :key="p.id"
          :product="p"
          :isCheap="p.isCheap"
        />
      </div>

      <!-- Empty state -->
      <div v-else class="mp-empty">
        <div class="mp-empty__blob"></div>
        <div class="mp-empty__content">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <h3>Nothing here yet</h3>
          <p v-if="searchQuery || selectedCategory !== 'All'">
            No matches for
            <strong v-if="searchQuery">"{{ searchQuery }}"</strong>
            <span v-if="selectedCategory !== 'All'"> in <em>{{ selectedCategory }}</em></span>.
          </p>
          <p v-else>The marketplace is empty right now. Check back later!</p>
          <button @click="clearSearch" class="mp-empty__btn">Clear filters</button>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mp-pagination" v-if="!loading && displayedProducts.length > 0 && totalPages > 1">
        <button @click="prevPage" :disabled="page === 1" class="mp-pg-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div class="mp-pg-nums">
          <button
            v-for="p in visiblePages"
            :key="p"
            class="mp-pg-num"
            :class="{ 'mp-pg-num--on': p === page, 'mp-pg-num--dots': p === '…' }"
            @click="p !== '…' && goToPage(p)"
          >{{ p }}</button>
        </div>
        <button @click="nextPage" :disabled="page >= totalPages" class="mp-pg-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>

    </div>
  </div>
</template>

<script>
import API from '../services/api'
import ProductCard from '../components/ProductCard.vue'

export default {
  name: 'Marketplace',
  components: { ProductCard },

  data() {
    return {
      baseProducts: [],
      loading: true,
      page: 1,
      limit: 12,
      totalProducts: 0,
      searchQuery: '',
      selectedCategory: 'All',
      sortBy: '',
      minPrice: '',
      maxPrice: '',
      appliedMinPrice: '',
      appliedMaxPrice: '',
      timer: null,
      categories: ['All','Textbooks','Electronics','Dorm Items','Uniforms','School Supplies','Food','Services','Others'],
    }
  },

  computed: {
    totalPages() {
      return Math.max(1, Math.ceil(this.totalProducts / this.limit))
    },

    displayedProducts() {
      let list = [...this.baseProducts]
      if (this.appliedMinPrice !== '') list = list.filter(p => Number(p.price) >= Number(this.appliedMinPrice))
      if (this.appliedMaxPrice !== '') list = list.filter(p => Number(p.price) <= Number(this.appliedMaxPrice))
      if (this.sortBy === 'az')        list.sort((a,b) => a.title.localeCompare(b.title))
      else if (this.sortBy === 'za')   list.sort((a,b) => b.title.localeCompare(a.title))
      else if (this.sortBy === 'low-high') list.sort((a,b) => Number(a.price) - Number(b.price))
      else if (this.sortBy === 'high-low') list.sort((a,b) => Number(b.price) - Number(a.price))
      return list
    },

    // Windowed page numbers with ellipsis
    visiblePages() {
      const total = this.totalPages
      const cur   = this.page
      if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
      const pages = []
      pages.push(1)
      if (cur > 3) pages.push('…')
      for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i)
      if (cur < total - 2) pages.push('…')
      pages.push(total)
      return pages
    }
  },

  mounted() {
    if (this.$route?.query?.category) {
      this.selectedCategory = this.$route.query.category
    }
    this.fetchProducts()
  },

  methods: {
    async fetchProducts() {
      this.loading = true
      try {
        const res = await API.getProducts({
          page: this.page,
          limit: this.limit,
          search: this.searchQuery,
          category: this.selectedCategory !== 'All' ? this.selectedCategory : null,
        })
        const raw   = Array.isArray(res.data) ? res.data : (res.data.products || [])
        const total = Array.isArray(res.data) ? res.data.length : (res.data.total || 0)

        this.baseProducts = raw.map(p => {
          const sameTag = raw.filter(x =>
            x.tags && p.tags &&
            String(x.tags).trim().toLowerCase() === String(p.tags).trim().toLowerCase()
          )
          const lowest = Math.min(...sameTag.map(x => Number(x.price)))
          return { ...p, isCheap: Number(p.price) === lowest }
        })
        this.totalProducts = total
      } catch (err) {
        console.error('Marketplace fetch error:', err)
        this.baseProducts = []
      } finally {
        this.loading = false
      }
    },

    applyAdvancedFilter() {
      this.appliedMinPrice = this.minPrice
      this.appliedMaxPrice = this.maxPrice
    },

    clearPriceFilter() {
      this.minPrice = ''
      this.maxPrice = ''
      this.appliedMinPrice = ''
      this.appliedMaxPrice = ''
    },

    applySorting() {},

    selectCategory(cat) {
      this.selectedCategory = cat
      this.page = 1
      this.fetchProducts()
    },

    clearSearchOnly() {
      this.searchQuery = ''
      this.page = 1
      this.fetchProducts()
    },

    clearSearch() {
      this.searchQuery    = ''
      this.selectedCategory = 'All'
      this.minPrice       = ''
      this.maxPrice       = ''
      this.appliedMinPrice = ''
      this.appliedMaxPrice = ''
      this.sortBy         = ''
      this.page           = 1
      this.fetchProducts()
    },

    goToPage(p) { this.page = p; this.fetchProducts() },
    nextPage()  { if (this.page < this.totalPages) { this.page++; this.fetchProducts() } },
    prevPage()  { if (this.page > 1) { this.page--; this.fetchProducts() } },

    debouncedFetch() {
      clearTimeout(this.timer)
      this.timer = setTimeout(() => { this.page = 1; this.fetchProducts() }, 450)
    },
  }
}
</script>

<style scoped>
/* ── Tokens ─────────────────────────────────────────────────────────────── */
.mp {
  --navy:   #003366;
  --gold:   #FFD700;
  --gold2:  #E6C200;
  --ink:    #1a2236;
  --muted:  #64748b;
  --light:  #f1f5f9;
  --border: #e2e8f0;
  --white:  #ffffff;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 12px rgba(0,0,0,0.06);

  min-height: 100vh;
  background: #f8fafc;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}

/* ── Hero ───────────────────────────────────────────────────────────────── */
.mp-hero {
  background: var(--navy);
  padding: 3rem 0 2.5rem;
  position: relative;
  overflow: hidden;
}

/* Subtle diagonal accent */
.mp-hero::before {
  content: '';
  position: absolute;
  top: -60px; right: -80px;
  width: 400px; height: 400px;
  background: rgba(255,215,0,0.07);
  border-radius: 50%;
  pointer-events: none;
}
.mp-hero::after {
  content: '';
  position: absolute;
  bottom: -100px; left: -60px;
  width: 300px; height: 300px;
  background: rgba(255,255,255,0.03);
  border-radius: 50%;
  pointer-events: none;
}

.mp-hero__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.mp-hero__text { flex-shrink: 0; }

.mp-hero__title {
  font-size: 2.4rem;
  font-weight: 900;
  color: var(--white);
  margin: 0 0 6px;
  line-height: 1.05;
  letter-spacing: -0.5px;
}
.mp-hero__title em {
  font-style: normal;
  color: var(--gold);
}
.mp-hero__sub {
  color: rgba(255,255,255,0.55);
  font-size: 0.85rem;
  margin: 0;
  font-weight: 400;
}

.mp-search-wrap {
  flex: 1;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Search bar */
.mp-search {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.1);
  border: 1.5px solid rgba(255,255,255,0.18);
  border-radius: var(--radius);
  padding: 12px 16px;
  transition: border-color 0.2s, background 0.2s;
}
.mp-search:focus-within {
  background: rgba(255,255,255,0.15);
  border-color: var(--gold);
}
.mp-search__icon { color: rgba(255,255,255,0.5); flex-shrink: 0; }
.mp-search__input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--white);
  font-size: 0.95rem;
  font-family: inherit;
}
.mp-search__input::placeholder { color: rgba(255,255,255,0.4); }
.mp-search__clear {
  background: rgba(255,255,255,0.15);
  border: none;
  border-radius: 6px;
  color: rgba(255,255,255,0.7);
  width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s;
}
.mp-search__clear:hover { background: rgba(255,255,255,0.25); }

/* Price filter */
.mp-price-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.mp-price-field {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  padding: 7px 11px;
}
.mp-price-field__label {
  font-size: 0.72rem;
  font-weight: 700;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.mp-price-input {
  background: none;
  border: none;
  outline: none;
  color: var(--white);
  font-size: 0.875rem;
  font-family: inherit;
  width: 72px;
}
.mp-price-input::placeholder { color: rgba(255,255,255,0.35); }
/* hide number spinners */
.mp-price-input::-webkit-inner-spin-button,
.mp-price-input::-webkit-outer-spin-button { -webkit-appearance: none; }
.mp-price-dash { color: rgba(255,255,255,0.3); font-size: 0.9rem; }
.mp-apply-btn {
  background: var(--gold);
  color: var(--navy);
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 0.8rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, transform 0.1s;
  white-space: nowrap;
}
.mp-apply-btn:hover { background: var(--gold2); }
.mp-apply-btn:active { transform: scale(0.97); }
.mp-clear-price-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.55);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: 0.15s;
}
.mp-clear-price-btn:hover { border-color: rgba(255,255,255,0.5); color: var(--white); }

/* ── Toolbar ────────────────────────────────────────────────────────────── */
.mp-toolbar-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 0;
}

.mp-toolbar {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: space-between;
}

/* Category pills */
.mp-cats {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.mp-cat {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: var(--white);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted);
  cursor: pointer;
  transition: 0.18s;
  font-family: inherit;
  white-space: nowrap;
}
.mp-cat:hover { border-color: var(--navy); color: var(--navy); }
.mp-cat--on {
  background: var(--navy);
  color: var(--white);
  border-color: var(--navy);
}

/* Sort row */
.mp-sort-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.mp-count {
  font-size: 0.82rem;
  color: var(--muted);
}
.mp-count strong { color: var(--navy); font-weight: 800; }

.mp-sort-wrap {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: 9px;
  padding: 7px 12px;
  transition: border-color 0.15s;
}
.mp-sort-wrap:focus-within { border-color: var(--navy); }
.mp-sort-icon { color: var(--muted); flex-shrink: 0; }
.mp-sort {
  border: none;
  outline: none;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--navy);
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  appearance: none;
  -webkit-appearance: none;
  padding-right: 4px;
}

/* Active filter tags */
.mp-active-filters {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}
.mp-filter-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.mp-ftag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #e8f0fe;
  color: var(--navy);
  font-size: 0.78rem;
  font-weight: 600;
  padding: 3px 10px 3px 10px;
  border-radius: 20px;
}
.mp-ftag button {
  background: none;
  border: none;
  color: var(--navy);
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
  padding: 0;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.mp-ftag button:hover { opacity: 1; }
.mp-clear-all {
  background: none;
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  cursor: pointer;
  font-family: inherit;
  transition: 0.15s;
  margin-left: 4px;
}
.mp-clear-all:hover { border-color: var(--navy); color: var(--navy); }

/* ── Content ────────────────────────────────────────────────────────────── */
.mp-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 4rem;
}

/* Product grid */
.mp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.25rem;
}

/* ── Skeleton ───────────────────────────────────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

.mp-skeleton {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}
.mp-skeleton__img {
  width: 100%;
  height: 180px;
  background: linear-gradient(90deg, #f0f4f8 25%, #e2e8f0 50%, #f0f4f8 75%);
  background-size: 800px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}
.mp-skeleton__body { padding: 14px; display: flex; flex-direction: column; gap: 8px; }
.mp-skeleton__line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f0f4f8 25%, #e2e8f0 50%, #f0f4f8 75%);
  background-size: 800px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}
.mp-skeleton__line--wide   { width: 80%; }
.mp-skeleton__line--narrow { width: 40%; }
.mp-skeleton__line--mid    { width: 60%; }

/* ── Empty state ────────────────────────────────────────────────────────── */
.mp-empty {
  position: relative;
  text-align: center;
  padding: 5rem 2rem;
  background: var(--white);
  border-radius: 20px;
  border: 1px dashed var(--border);
  overflow: hidden;
  margin-top: 1rem;
}
.mp-empty__blob {
  position: absolute;
  top: -60px; right: -60px;
  width: 240px; height: 240px;
  background: radial-gradient(circle, rgba(0,51,102,0.05) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.mp-empty__content { position: relative; }
.mp-empty__content svg { opacity: 0.25; margin-bottom: 1rem; }
.mp-empty__content h3 { font-size: 1.2rem; font-weight: 800; color: var(--navy); margin: 0 0 8px; }
.mp-empty__content p  { color: var(--muted); font-size: 0.9rem; margin: 0 0 1.5rem; }
.mp-empty__btn {
  background: var(--navy);
  color: var(--white);
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: 0.15s;
}
.mp-empty__btn:hover { background: #002244; }

/* ── Pagination ─────────────────────────────────────────────────────────── */
.mp-pagination {
  margin-top: 2.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
}
.mp-pg-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border: 1.5px solid var(--border);
  background: var(--white);
  border-radius: 9px;
  color: var(--navy);
  cursor: pointer;
  transition: 0.15s;
}
.mp-pg-btn:hover:not(:disabled) { background: var(--navy); color: var(--white); border-color: var(--navy); }
.mp-pg-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.mp-pg-nums { display: flex; gap: 4px; }

.mp-pg-num {
  width: 36px; height: 36px;
  border-radius: 9px;
  border: 1.5px solid var(--border);
  background: var(--white);
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.15s;
  font-family: inherit;
  display: flex; align-items: center; justify-content: center;
}
.mp-pg-num:hover:not(.mp-pg-num--dots):not(.mp-pg-num--on) {
  border-color: var(--navy);
  color: var(--navy);
}
.mp-pg-num--on {
  background: var(--navy);
  color: var(--white);
  border-color: var(--navy);
}
.mp-pg-num--dots { border-color: transparent; background: none; cursor: default; }

/* ── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .mp-hero__inner { flex-direction: column; align-items: flex-start; }
  .mp-hero__title { font-size: 1.8rem; }
  .mp-search-wrap { width: 100%; min-width: unset; }
  .mp-toolbar { flex-direction: column; }
  .mp-sort-row { width: 100%; justify-content: space-between; }
  .mp-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }
}

@media (max-width: 480px) {
  .mp-price-filter { gap: 6px; }
  .mp-price-field { padding: 6px 9px; }
  .mp-price-input { width: 56px; }
}
</style>