<template>
  <div class="home">

    <!-- HERO SECTION -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">🎓 ADNU Students Only</div>
        <h1>Buy & Sell Within<br /><span class="gold">Your Campus</span></h1>
        <p>The official marketplace of Ateneo de Naga University. Find textbooks, electronics, dorm essentials, and more.</p>
        <div class="hero-actions">
          <router-link to="/products" class="btn-primary">
            <i class="fa-solid fa-store"></i> Browse Marketplace
          </router-link>
          <router-link to="/add-product" class="btn-secondary">
            <i class="fa-solid fa-plus"></i> Sell an Item
          </router-link>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat">
          <span class="stat-num">100+</span>
          <span class="stat-label">Listings</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-num">50+</span>
          <span class="stat-label">Sellers</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-num">6</span>
          <span class="stat-label">Colleges</span>
        </div>
      </div>
    </section>

    <!-- CATEGORIES -->
    <section class="section">
      <div class="section-header">
        <h2>Browse by Category</h2>
        <router-link to="/products" class="see-all">See all →</router-link>
      </div>
      <div class="category-grid">
        <div
          v-for="cat in categories"
          :key="cat.label"
          class="category-card"
          @click="$router.push('/products?category=' + cat.label)"
        >
          <span class="cat-icon">{{ cat.icon }}</span>
          <span class="cat-label">{{ cat.label }}</span>
        </div>
      </div>
    </section>

    <!-- LATEST PRODUCTS -->
    <section class="section">
      <div class="section-header">
        <h2>Latest Listings</h2>
        <router-link to="/products" class="see-all">See all →</router-link>
      </div>

      <div v-if="loading" class="product-grid">
        <div v-for="n in 8" :key="n" class="skeleton-card">
          <div class="skeleton img"></div>
          <div class="skeleton title"></div>
          <div class="skeleton price"></div>
        </div>
      </div>

      <div v-else-if="products.length" class="product-grid">
        <ProductCard
          v-for="product in products"
          :key="product.id"
          :product="product"
        />
      </div>

      <div v-else class="empty">
        <p>No products yet. Be the first to sell!</p>
        <router-link to="/add-product" class="btn-primary" style="display:inline-block; margin-top:1rem;">Post an Item</router-link>
      </div>
    </section>

    <!-- CTA BANNER -->
    <section class="cta-banner">
      <div class="cta-content">
        <h3>Have something to sell?</h3>
        <p>Post your item in seconds and reach hundreds of ADNU students.</p>
      </div>
      <router-link to="/add-product" class="btn-primary">
        Start Selling
      </router-link>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProductCard from '@/components/ProductCard.vue'
import api from '@/services/api'

const products = ref([])
const loading = ref(true)

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

onMounted(async () => {
  try {
    const res = await api.getProducts({ page: 1, limit: 8 })
    if (Array.isArray(res.data)) {
      products.value = res.data
    } else {
      products.value = res.data.products || []
    }
  } catch (err) {
    console.error('Error fetching products', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home {
  background: #f8fafc;
  min-height: 100vh;
}

/* HERO */
.hero {
  background: #003366;
  color: white;
  padding: 4rem 2rem 2rem;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  background: rgba(255, 215, 0, 0.15);
  color: #FFD700;
  border: 1px solid rgba(255,215,0,0.3);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.hero h1 {
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 1rem;
}

.gold { color: #FFD700; }

.hero p {
  color: rgba(255,255,255,0.75);
  font-size: 1rem;
  max-width: 480px;
  margin: 0 auto 1.8rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-primary {
  background: #FFD700;
  color: #003366;
  padding: 11px 22px;
  border-radius: 8px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.9rem;
  transition: 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary:hover { background: #e6c200; transform: translateY(-1px); }

.btn-secondary {
  background: transparent;
  border: 1.5px solid rgba(255,255,255,0.5);
  color: white;
  padding: 11px 22px;
  border-radius: 8px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.9rem;
  transition: 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary:hover { border-color: white; background: rgba(255,255,255,0.08); }

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.stat { display: flex; flex-direction: column; align-items: center; }
.stat-num { font-size: 1.6rem; font-weight: 800; color: #FFD700; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.6); margin-top: 2px; }
.stat-divider { width: 1px; height: 36px; background: rgba(255,255,255,0.15); }

/* SECTIONS */
.section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.section-header h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #003366;
  margin: 0;
}

.see-all {
  font-size: 0.85rem;
  color: #003366;
  text-decoration: none;
  font-weight: 600;
}

.see-all:hover { text-decoration: underline; }

/* CATEGORIES */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.category-card {
  background: white;
  border: 0.5px solid #eee;
  padding: 1.2rem 0.5rem;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.category-card:hover {
  border-color: #003366;
  background: #f0f4ff;
  transform: translateY(-2px);
}

.cat-icon { font-size: 1.8rem; }
.cat-label { font-size: 0.78rem; font-weight: 600; color: #003366; }

/* PRODUCTS */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}

/* Skeleton */
.skeleton-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton {
  background: #e8ecef;
  border-radius: 6px;
  animation: pulse 1.5s infinite;
}

.skeleton.img { height: 160px; border-radius: 10px; }
.skeleton.title { height: 16px; width: 80%; }
.skeleton.price { height: 14px; width: 40%; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* EMPTY */
.empty {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  color: #888;
}

/* CTA BANNER */
.cta-banner {
  background: linear-gradient(135deg, #003366, #0055aa);
  color: white;
  padding: 2.5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  flex-wrap: wrap;
}

.cta-content h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 6px;
}

.cta-content p {
  color: rgba(255,255,255,0.7);
  font-size: 0.9rem;
  margin: 0;
}
</style>