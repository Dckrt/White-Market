<template>
  <div class="card">
    <!-- Category & Status -->
    <div class="category-header">
      <span class="category-tag">{{ product.category }}</span>
      <span class="status-tag">● Available</span>
    </div>

    <!-- Product Image -->
    <div class="image-container">
      <img :src="getImage(product.image_url)" :alt="product.title" class="product-image" />
    </div>

    <!-- Content -->
    <div class="card-body">
      <h3 class="product-title">{{ product.title }}</h3>
      <p class="product-desc">{{ product.description || 'No description' }}</p>
      <p class="price">₱{{ formatPrice(product.price) }}</p>

      <!-- Buttons -->
      <div class="button-group">
        <button @click="handleAddToCart" class="cart-btn" title="Add to Cart" :disabled="product.status !== 'Available'">
          <i class="fa-solid fa-cart-shopping"></i>
        </button>
        <!-- ✅ Buy Now → ProductDetails (full page with cart + chat) -->
        <button @click="router.push('/products/' + product.id)" class="buy-btn" :disabled="product.status !== 'Available'">
          Buy Now
        </button>
      </div>

      <!-- ✅ View Details → ProductView (read-only view page) -->
      <button @click="router.push('/product-view/' + product.id)" class="details-link">
        View Details
      </button>
    </div>
  </div>
</template>

<script setup>
import api from '@/services/api'
import { useRouter } from 'vue-router'

const props = defineProps(['product'])
const router = useRouter()

const formatPrice = (value) =>
  parseFloat(value).toLocaleString(undefined, { minimumFractionDigits: 2 })

const getImage = (url) => url || '/placeholder-image.png'

const handleAddToCart = async () => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (!user) return router.push('/auth')
  try {
    await api.addToCart({ user_id: user.user_id, product_id: props.product.id })
    alert(`"${props.product.title}" added to cart! ✅`)
  } catch (err) {
    alert((err.response?.data?.message || 'Failed to add to cart') + ' ❌')
  }
}
</script>

<style scoped>
.card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  border: 0.5px solid #eee;
  transition: 0.2s;
  display: flex;
  flex-direction: column;
}

.card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,51,102,0.1); }

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px 6px;
}

.category-tag {
  font-size: 0.68rem;
  font-weight: 700;
  background: #f0f4f8;
  color: #555;
  padding: 3px 8px;
  border-radius: 4px;
}

.status-tag { font-size: 0.68rem; font-weight: 700; color: #16a34a; }

.image-container { height: 170px; overflow: hidden; background: #f8fafc; }

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.card:hover .product-image { transform: scale(1.04); }

.card-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.product-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #003366;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-desc {
  font-size: 0.8rem;
  color: #888;
  margin: 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.price { color: #e74c3c; font-weight: 800; font-size: 1rem; margin: 0 0 10px; }

.button-group { display: flex; gap: 8px; margin-bottom: 8px; }

.cart-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003366;
  font-size: 15px;
  transition: 0.2s;
  flex-shrink: 0;
}

.cart-btn:hover:not(:disabled) { background: #003366; color: white; border-color: #003366; }
.cart-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.buy-btn {
  flex: 1;
  background: #003366;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  height: 40px;
  transition: 0.2s;
}

.buy-btn:hover:not(:disabled) { background: #002244; }
.buy-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.details-link {
  width: 100%;
  background: none;
  border: 1px solid #e2e8f0;
  color: #003366;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  padding: 7px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.2s;
}

.details-link:hover { background: #f0f4ff; border-color: #003366; }
</style>