<template>
  <div>
    <NavBar />

    <div class="container">
      <h2>Checkout</h2>

      <div class="checkout-layout">

        <!-- FORM -->
        <div class="checkout-form panel">

          <h3>📅 Preferred Schedule</h3>

          <div class="field">
            <label>Date</label>
            <input type="date" v-model="date" />
          </div>

          <div class="field">
            <label>Time Range</label>
            <select v-model="timeRange">
              <option disabled value="">Select Time Range</option>
              <option>Morning (8AM–12PM)</option>
              <option>Afternoon (12PM–5PM)</option>
              <option>Evening (5PM–8PM)</option>
            </select>
          </div>

          <div class="field">
            <label>Preferred Location</label>
            <input placeholder="e.g. Library entrance, Canteen..." v-model="location" />
          </div>

          <h3>💳 Payment Method</h3>

          <div class="payment-options">
            <label :class="['pay-option', payment === 'cod' ? 'active' : '']">
              <input type="radio" value="cod" v-model="payment" />
              💵 Cash on Meetup
            </label>
            <label :class="['pay-option', payment === 'gcash' ? 'active' : '']">
              <input type="radio" value="gcash" v-model="payment" />
              📱 GCash
            </label>
          </div>

          <button class="btn-request" @click="placeRequest">
            Send Request
          </button>

        </div>

        <!-- ORDER SUMMARY -->
        <div class="checkout-summary panel">
          <h3>🛍️ Order Summary</h3>

          <div v-if="cart.length === 0" class="empty-note">
            No items in cart.
          </div>

          <div v-for="item in cart" :key="item.id" class="summary-item">
            <img :src="item.image || '/placeholder.png'" :alt="item.name" />
            <div>
              <p class="item-name">{{ item.name }}</p>
              <p class="item-price">₱{{ item.price }}</p>
            </div>
          </div>

          <div class="summary-divider"></div>

          <div class="summary-total">
            <span>Total</span>
            <span>₱{{ total }}</span>
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
      cart: JSON.parse(localStorage.getItem("cart")) || [],
      currentUser: JSON.parse(localStorage.getItem("currentUser")),
      date: "",
      timeRange: "",
      location: "",
      payment: "cod"
    };
  },

  computed: {
    total() {
      return this.cart.reduce((sum, item) => sum + Number(item.price), 0);
    }
  },

  methods: {
    placeRequest() {
      if (!this.date || !this.timeRange || !this.location) {
        alert("Please complete all schedule details.");
        return;
      }

      const requests = JSON.parse(localStorage.getItem("requests")) || [];

      this.cart.forEach(item => {
        requests.push({
          id: Date.now() + Math.random(),
          product: item,
          buyer: this.currentUser.email,
          seller: item.owner,
          date: this.date,
          timeRange: this.timeRange,
          location: this.location,
          payment: this.payment,
          status: "pending"
        });
      });

      localStorage.setItem("requests", JSON.stringify(requests));
      localStorage.removeItem("cart");

      alert("Request sent! Waiting for seller approval.");
      this.$router.push("/");
    },

    logout() {
      localStorage.removeItem("currentUser");
      this.$router.push("/auth");
    }
  }
};
</script>

<style scoped>
.checkout-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  align-items: start;
}

@media (max-width: 768px) {
  .checkout-layout {
    grid-template-columns: 1fr;
  }
}

.checkout-form h3,
.checkout-summary h3 {
  font-size: 16px;
  margin: 0 0 16px;
}

.checkout-form h3:not(:first-child) {
  margin-top: 24px;
}

.field {
  margin-bottom: 14px;
}

.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

/* PAYMENT OPTIONS */
.payment-options {
  display: flex;
  gap: 12px;
}

.pay-option {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border: 2px solid #eee;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: 0.2s;
}

.pay-option input[type="radio"] {
  width: auto;
  margin: 0;
  padding: 0;
  accent-color: #03120E;
}

.pay-option.active {
  border-color: #03120E;
  background: #f5f9f8;
}

.btn-request {
  width: 100%;
  margin-top: 24px;
  padding: 14px;
  background: #03120E;
  color: white;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
}

.btn-request:hover {
  background: #0a2a23;
}

/* SUMMARY */
.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.summary-item img {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: 8px;
  background: #f0f0f0;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 4px;
  color: #222;
}

.item-price {
  font-size: 14px;
  font-weight: 700;
  color: #e60023;
  margin: 0;
}

.summary-divider {
  border-top: 1px solid #eee;
  margin: 16px 0;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 700;
  color: #111;
}

.empty-note {
  color: #aaa;
  font-size: 14px;
}
</style>