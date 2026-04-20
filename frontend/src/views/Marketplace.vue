<template>
  <div class="marketplace-wrapper">
    <div class="container">

      <!-- Header -->
      <header class="marketplace-header">
        <div class="title-section">
          <h1>University <span>Market</span></h1>
          <p>Verified essentials for Ateneo de Naga Students</p>
        </div>

        <div class="search-bar">
          <i class="fa-solid fa-magnifying-glass search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search items..."
            @input="debouncedFetch"
          />
          <button v-if="searchQuery" @click="clearSearch" class="clear-btn">✕</button>
        </div>
      </header>

      <!-- Category Pills -->
      <div class="category-pills">
        <button
          v-for="cat in categories"
          :key="cat"
          class="pill"
          :class="{ active: selectedCategory === cat }"
          @click="selectCategory(cat)"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Results Info -->
      <div class="results-info" v-if="!loading">
        <span>{{ products.length }} item{{ products.length !== 1 ? 's' : '' }} found</span>
        <span v-if="searchQuery || selectedCategory !== 'All'" class="filter-tag">
          {{ selectedCategory !== 'All' ? selectedCategory : '' }}
          {{ searchQuery ? `"${searchQuery}"` : '' }}
          <button @click="clearSearch">✕</button>
        </span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="product-grid">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>

      <!-- Products -->
      <div v-else-if="products.length > 0" class="product-grid">
        <ProductCard v-for="p in products" :key="p.id" :product="p" />
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🔎</div>
        <h3>No items found</h3>
        <p v-if="searchQuery || selectedCategory !== 'All'">
          No matches for
          <strong v-if="searchQuery">"{{ searchQuery }}"</strong>
          <span v-if="selectedCategory !== 'All'"> in {{ selectedCategory }}</span>.
        </p>
        <p v-else>The marketplace is currently empty. Check back later!</p>
        <button @click="clearSearch" class="link-btn">Clear filters</button>
      </div>

      <!-- Pagination -->
      <div class="pagination-footer" v-if="products.length > 0">
        <button @click="prevPage" :disabled="page === 1" class="page-btn">
          <i class="fa-solid fa-chevron-left"></i> Prev
        </button>
        <div class="page-numbers">
          <button
            v-for="p in totalPages"
            :key="p"
            class="page-num"
            :class="{ active: p === page }"
            @click="page = p; fetchProducts()"
          >{{ p }}</button>
        </div>
        <button @click="nextPage" :disabled="page >= totalPages" class="page-btn">
          Next <i class="fa-solid fa-chevron-right"></i>
        </button>
      </div>

    </div>
  </div>
</template>

<script>
import API from '../services/api'
import ProductCard from '../components/ProductCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'

export default {
  components: { ProductCard, SkeletonCard },

  data() {
    return {
      products: [],
      loading: true,
      page: 1,
      limit: 12,
      totalProducts: 0,
      searchQuery: '',
      selectedCategory: 'All',
      timer: null,
      categories: ['All', 'Textbooks', 'Electronics', 'Dorm Items', 'Uniforms', 'School Supplies', 'Food', 'Services', 'Others']
    }
  },

  computed: {
    totalPages() {
      return Math.max(1, Math.ceil(this.totalProducts / this.limit))
    }
  },

  mounted() {
    // Check if category was passed via query param from HomeView
    if (this.$route.query.category) {
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
          category: this.selectedCategory !== 'All' ? this.selectedCategory : null
        })

        if (Array.isArray(res.data)) {
          this.products = res.data
          this.totalProducts = res.data.length
        } else {
          this.products = res.data.products || []
          this.totalProducts = res.data.total || 0
        }
      } catch (err) {
        console.error('Marketplace Fetch Error:', err)
        this.products = []
      } finally {
        this.loading = false
      }
    },

    selectCategory(cat) {
      this.selectedCategory = cat
      this.page = 1
      this.fetchProducts()
    },

    clearSearch() {
      this.searchQuery = ''
      this.selectedCategory = 'All'
      this.page = 1
      this.fetchProducts()
    },

    nextPage() { if (this.page < this.totalPages) { this.page++; this.fetchProducts() } },
    prevPage() { if (this.page > 1) { this.page--; this.fetchProducts() } },

    debouncedFetch() {
      clearTimeout(this.timer)
      this.timer = setTimeout(() => {
        this.page = 1
        this.fetchProducts()
      }, 500)
    }
  }
}
</script>

<style scoped>
.marketplace-wrapper {
  background-color: #f8fafc;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* Header */
.marketplace-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 2rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  border-left: 5px solid #FFD700;
  padding-left: 1.5rem;
}

.title-section h1 {
  color: #003366;
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0 0 4px;
}

.title-section span { color: #64748b; font-weight: 300; }
.title-section p { color: #888; margin: 0; font-size: 0.875rem; }

/* Search */
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  min-width: 280px;
  flex: 1;
  max-width: 420px;
}

.search-icon { color: #aaa; font-size: 14px; }

.search-bar input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.9rem;
  background: transparent;
  color: #333;
}

.clear-btn {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
}

.clear-btn:hover { color: #666; background: #f0f0f0; }

/* Category Pills */
.category-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.pill {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: white;
  font-size: 0.82rem;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  transition: 0.2s;
}

.pill:hover { border-color: #003366; color: #003366; }

.pill.active {
  background: #003366;
  color: white;
  border-color: #003366;
}

/* Results Info */
.results-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.25rem;
  font-size: 0.85rem;
  color: #888;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #e8f0fe;
  color: #003366;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 600;
}

.filter-tag button {
  background: none;
  border: none;
  cursor: pointer;
  color: #003366;
  font-size: 11px;
  padding: 0;
  line-height: 1;
}

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: white;
  border-radius: 16px;
  border: 1px dashed #cbd5e1;
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }

.empty-state h3 {
  color: #003366;
  margin: 0 0 8px;
}

.empty-state p { color: #888; font-size: 0.9rem; margin: 0 0 1rem; }

.link-btn {
  background: none;
  border: 1px solid #003366;
  color: #003366;
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.link-btn:hover { background: #003366; color: white; }

/* Pagination */
.pagination-footer {
  margin-top: 3rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding-bottom: 3rem;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #003366;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  transition: 0.2s;
}

.page-btn:hover:not(:disabled) { background: #003366; color: white; border-color: #003366; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.page-numbers { display: flex; gap: 6px; }

.page-num {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #555;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
  font-size: 0.875rem;
}

.page-num:hover { border-color: #003366; color: #003366; }
.page-num.active { background: #003366; color: white; border-color: #003366; }
</style>