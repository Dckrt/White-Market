<template>
  <div v-if="product" class="view-wrapper">
    <div class="container">

      <!-- Back -->
      <button @click="$router.back()" class="back-link">
        <i class="fa-solid fa-arrow-left"></i> Back
      </button>

      <div class="view-card">

        <!-- Image -->
        <div class="image-section">
          <img :src="product.image_url || '/placeholder.png'" class="product-img" :alt="product.title" />
        </div>

        <!-- Details -->
        <div class="info-section">

          <div class="badges">
            <span class="cat-badge">{{ product.category }}</span>
            <span class="status-badge">● Available</span>
          </div>

          <h1 class="title">{{ product.title }}</h1>
          <p class="price">₱{{ formatPrice(product.price) }}</p>

          <div class="divider"></div>

          <div class="detail-block">
            <p class="detail-label"><i class="fa-solid fa-align-left"></i> Description</p>
            <p class="detail-value">{{ product.description || 'No description provided.' }}</p>
          </div>

          <div class="detail-block">
            <p class="detail-label"><i class="fa-solid fa-store"></i> Seller</p>
            <p class="detail-value">{{ product.seller_name || 'ADNU Student' }}</p>
          </div>

          <div class="detail-block">
            <p class="detail-label"><i class="fa-solid fa-calendar-days"></i> Posted</p>
            <p class="detail-value">{{ formatDate(product.created_at) }}</p>
          </div>

          <div class="divider"></div>

          <button @click="$router.push('/products/' + product.id)" class="go-buy-btn">
            <i class="fa-solid fa-bolt"></i> Buy This Item
          </button>

        </div>
      </div>
    </div>
  </div>

  <!-- Loading -->
  <div v-else class="view-wrapper">
    <div class="container">
      <div class="skeleton-card">
        <div class="skeleton img-sk"></div>
        <div class="skeleton-body">
          <div class="skeleton title-sk"></div>
          <div class="skeleton price-sk"></div>
          <div class="skeleton desc-sk"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const product = ref(null)

onMounted(async () => {
  try {
    const res = await api.getProduct(route.params.id)
    product.value = res.data
    window.scrollTo(0, 0)
  } catch (err) {
    console.error('Fetch error:', err)
  }
})

const formatPrice = (v) =>
  parseFloat(v).toLocaleString(undefined, { minimumFractionDigits: 2 })

const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' }) : 'N/A'
</script>

<style scoped>
.view-wrapper {
  background: #f8fafc;
  min-height: 100vh;
  padding: 2rem 1.5rem;
}

.container { max-width: 860px; margin: 0 auto; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: #003366;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  margin-bottom: 1.5rem;
  padding: 0;
  transition: 0.2s;
}
.back-link:hover { opacity: 0.7; }

.view-card {
  background: white;
  border-radius: 16px;
  border: 0.5px solid #eee;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.image-section {
  background: #f1f5f9;
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-img {
  width: 100%;
  height: 420px;
  object-fit: cover;
  display: block;
}

.info-section { padding: 2rem; display: flex; flex-direction: column; gap: 0; }

.badges {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
}

.cat-badge {
  background: #f0f4ff;
  color: #003366;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
}

.status-badge { font-size: 0.78rem; font-weight: 700; color: #16a34a; }

.title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #003366;
  margin: 0 0 8px;
  line-height: 1.3;
}

.price {
  font-size: 1.6rem;
  font-weight: 800;
  color: #e74c3c;
  margin: 0 0 1rem;
}

.divider {
  height: 1px;
  background: #f1f5f9;
  margin: 1rem 0;
}

.detail-block { margin-bottom: 1rem; }

.detail-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #003366;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-value {
  font-size: 0.9rem;
  color: #555;
  line-height: 1.6;
  margin: 0;
}

.go-buy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  background: #003366;
  color: white;
  border: none;
  padding: 13px;
  border-radius: 10px;
  font-weight: 800;
  font-size: 0.95rem;
  cursor: pointer;
  transition: 0.2s;
  margin-top: auto;
}
.go-buy-btn:hover { background: #002244; transform: translateY(-1px); }

/* Loading */
.skeleton-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 1fr;
  border: 0.5px solid #eee;
}

.skeleton-body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton {
  background: #e8ecef;
  border-radius: 8px;
  animation: pulse 1.5s infinite;
}

.img-sk { height: 420px; }
.title-sk { height: 28px; width: 80%; }
.price-sk { height: 32px; width: 40%; }
.desc-sk { height: 80px; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 640px) {
  .view-card, .skeleton-card { grid-template-columns: 1fr; }
  .image-section, .product-img { height: 260px; min-height: 260px; }
  .img-sk { height: 260px; }
}
</style>