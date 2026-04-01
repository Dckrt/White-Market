<template>
  <header class="nav">
    <h1 class="logo">White Market</h1>
 
    <div class="nav-center">
      <button @click="$router.push('/')">Home</button>
      <button @click="$router.push('/browse')">Browse</button>
 
      <button
        v-if="currentUser?.role === 'seller'"
        @click="$router.push('/dashboard')"
      >
        Dashboard
      </button>
 
      <button class="cart-btn" @click="$router.push('/cart')">
        <img src="/cart.png" alt="cart" />
        <span v-if="cartCount > 0" class="cart-count">{{ cartCount }}</span>
      </button>
    </div>
 
    <button class="logout" @click="logout">Logout</button>
  </header>
</template>
 
<script>
export default {
  name: "NavBar",
  computed: {
    currentUser() {
      return JSON.parse(localStorage.getItem("currentUser"));
    },
    cartCount() {
      const cart = JSON.parse(localStorage.getItem("cart")) || [];
      return cart.length;
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("currentUser");
      this.$router.push("/auth");
    }
  }
};
</script>