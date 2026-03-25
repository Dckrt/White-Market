<template>
  <div>

<header class="nav">

  <h1 class="logo">White Market</h1>

<div class="nav-center">
  <button @click="$router.push('/')">Home</button>
  <button @click="$router.push('/browse')">Browse</button>

  <!-- SELLER ONLY -->
  <button v-if="currentUser?.role === 'seller'" 
          @click="$router.push('/dashboard')">
    Dashboard
  </button>

  <button class="cart-btn" @click="$router.push('/cart')">
    <img src="/cart.png">
  </button>
</div>

  <button class="logout" @click="logout">Logout</button>

</header>

    <div class="container">

      <h2>Your Cart</h2>

      <div v-if="cart.length === 0">
        Cart is empty
      </div>

      <div class="products">
        <div v-for="(item, i) in cart" :key="i" class="card">
          <div class="card-content">
            <h3>{{ item.name }}</h3>
            <p>₱{{ item.price }}</p>

            <button @click="remove(i)">Remove</button>
          </div>
        </div>
      </div>

      <button @click="$router.push('/checkout')">
  Checkout
</button>

    </div>
  </div>
</template>

<script>
export default {
 data() {
  return {
    cart: JSON.parse(localStorage.getItem("cart")) || [],
    currentUser: JSON.parse(localStorage.getItem("currentUser"))
  };
},

  methods: {
    remove(i) {
      this.cart.splice(i, 1);
      localStorage.setItem("cart", JSON.stringify(this.cart));
    },

    checkout() {
      alert("Order placed!");
      localStorage.removeItem("cart");
      this.cart = [];
    },

     logout() {
    localStorage.removeItem("currentUser");
    this.$router.push("/auth");
  }
  }
};
</script>