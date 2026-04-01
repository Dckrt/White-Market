<template>
  <div>
    <NavBar />

    <div class="container">

      <!-- HERO -->
      <div class="hero">
        <div class="hero-text">
          <h2>Your Campus.<br>Your Marketplace.</h2>
          <p>Buy and sell with fellow students — clothing, school supplies, electronics, and more.</p>
          <button class="btn-accent" @click="$router.push('/browse')">Browse Products</button>
        </div>
      </div>

      <!-- FEATURED -->
      <div class="section-header">
        <h2>Featured Products</h2>
        <button class="btn-text" @click="$router.push('/browse')">See all →</button>
      </div>

      <div v-if="products.length === 0" class="empty-state">
        <p>🛍️ No products yet. Check back soon!</p>
      </div>

      <div class="products">
        <div v-for="p in products.slice(0, 8)" :key="p.id" class="card">
          <div class="image-wrapper">
            <img :src="p.image || '/placeholder.png'" :alt="p.name" />
            <span class="badge" :class="p.status">{{ p.status }}</span>
          </div>
          <div class="card-content">
            <p class="card-category">{{ p.category }}</p>
            <h3 class="title">{{ p.name }}</h3>
            <p class="price">₱{{ p.price }}</p>
            <div class="card-actions">
              <button
                class="btn-add"
                :disabled="p.status !== 'available'"
                @click="addToCart(p)"
              >
                {{ p.status === 'available' ? 'Add to Cart' : p.status }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import NavBar from "./NavBar.vue";

export default {
  components: { NavBar },

  data() {
    return {
      products: JSON.parse(localStorage.getItem("products")) || []
    };
  },

  methods: {
    addToCart(product) {
      if (product.status !== "available") return;
      const cart = JSON.parse(localStorage.getItem("cart")) || [];
      cart.push(product);
      localStorage.setItem("cart", JSON.stringify(cart));
      alert(`"${product.name}" added to cart!`);
    }
  }
};
</script>

<style scoped>
.hero {
  background: #03120E;
  border-radius: 18px;
  padding: 50px 40px;
  margin-bottom: 40px;
  color: white;
}

.hero-text h2 {
  font-size: 36px;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 14px;
}

.hero-text p {
  font-size: 16px;
  color: #aaa;
  max-width: 420px;
  margin-bottom: 24px;
}

.btn-accent {
  background: white;
  color: #03120E;
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  width: auto;
}

.btn-accent:hover {
  background: #e5e5e5;
  transform: translateY(-1px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
}

.btn-text {
  background: transparent;
  color: #03120E;
  padding: 6px 10px;
  font-size: 14px;
  width: auto;
}

.btn-text:hover {
  background: #eee;
}

.card-category {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #999;
  margin: 0 0 4px;
}

.btn-add {
  width: 100%;
  background: #03120E;
  color: white;
  padding: 9px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.btn-add:disabled {
  background: #ccc;
  color: #888;
  cursor: not-allowed;
  transform: none;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}
</style>