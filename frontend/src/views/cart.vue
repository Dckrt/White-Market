<template>
  <div>
    <NavBar />

    <div class="container">
      <h2>Your Cart</h2>

      <!-- EMPTY STATE -->
      <div v-if="cart.length === 0" class="empty-state">
        <p>🛒 Your cart is empty.</p>
        <button @click="$router.push('/browse')" class="btn-browse">Browse Products</button>
      </div>

      <!-- CART CONTENT -->
      <div v-else class="cart-layout">

        <!-- ITEMS -->
        <div class="cart-items">
          <div v-for="(item, i) in cart" :key="i" class="cart-card">
            <img :src="item.image || '/placeholder.png'" :alt="item.name" class="cart-img" />
            <div class="cart-info">
              <p class="cart-category">{{ item.category }}</p>
              <h3>{{ item.name }}</h3>
              <p class="price">₱{{ item.price }}</p>
            </div>
            <button class="btn-remove" @click="remove(i)">✕</button>
          </div>
        </div>

        <!-- ORDER SUMMARY -->
        <div class="cart-summary">
          <h3>Order Summary</h3>
          <div class="summary-row" v-for="(item, i) in cart" :key="i">
            <span>{{ item.name }}</span>
            <span>₱{{ item.price }}</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-row total">
            <span>Total</span>
            <span>₱{{ total }}</span>
          </div>
          <button class="btn-checkout" @click="$router.push('/checkout')">
            Proceed to Checkout
          </button>
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
      cart: JSON.parse(localStorage.getItem("cart")) || []
    };
  },

  computed: {
    total() {
      return this.cart.reduce((sum, item) => sum + Number(item.price), 0);
    }
  },

  methods: {
    remove(i) {
      this.cart.splice(i, 1);
      localStorage.setItem("cart", JSON.stringify(this.cart));
    }
  }
};
</script>

<style scoped>
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: start;
}

@media (max-width: 768px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }
}

.cart-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.cart-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 10px;
  background: #f0f0f0;
}

.cart-info {
  flex: 1;
}

.cart-info h3 {
  margin: 0 0 4px;
  font-size: 15px;
}

.cart-category {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #999;
  margin: 0 0 4px;
}

.btn-remove {
  background: #f5f5f5;
  color: #888;
  border: none;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
  width: auto;
}

.btn-remove:hover {
  background: #ffe0e0;
  color: #e63946;
  transform: none;
}

/* SUMMARY */
.cart-summary {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 20px;
}

.cart-summary h3 {
  margin: 0 0 16px;
  font-size: 17px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #555;
  margin-bottom: 10px;
}

.summary-row span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}

.summary-divider {
  border-top: 1px solid #eee;
  margin: 14px 0;
}

.summary-row.total {
  font-size: 16px;
  font-weight: 700;
  color: #111;
}

.btn-checkout {
  width: 100%;
  margin-top: 18px;
  padding: 13px;
  background: #03120E;
  color: white;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
}

.btn-checkout:hover {
  background: #0a2a23;
}

/* EMPTY STATE */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.empty-state p {
  font-size: 18px;
  margin-bottom: 20px;
}

.btn-browse {
  background: #03120E;
  color: white;
  padding: 12px 28px;
  border-radius: 10px;
  font-weight: 600;
  width: auto;
}
</style>