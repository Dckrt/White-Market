<template>
  <div>

    <!-- NAVBAR -->
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
      <h2>Featured Products</h2>

      <div class="products">
<div v-for="p in products" :key="p.id" class="card">
  <div class="image-wrapper">
    <img :src="p.image">

    <!-- STATUS BADGE -->
    <span class="badge" :class="p.status">
      {{ p.status }}
    </span>
  </div>

  <div class="card-content">
    <h3 class="title">{{ p.name }}</h3>

    <p class="price">₱{{ p.price }}</p>

    <div class="card-actions">
      <button @click="addToCart(p)">Add to Cart</button>
    </div>
  </div>
</div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
  return {
    products: JSON.parse(localStorage.getItem("products")) || [],
    currentUser: JSON.parse(localStorage.getItem("currentUser"))
  };
},

  methods: {
    logout() {
      localStorage.removeItem("currentUser");
      this.$router.push("/auth");
    },

    addToCart(product) {
      const cart = JSON.parse(localStorage.getItem("cart")) || [];
      cart.push(product);
      localStorage.setItem("cart", JSON.stringify(cart));
      alert("Added to cart");
    }
  }
};
</script>

<style>
.nav {
  display: flex;
  justify-content: space-between;
  background: #111;
  color: white;
  padding: 15px;
}

.nav-links button {
  margin-left: 10px;
}

.container {
  padding: 20px;
}

.products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  padding: 10px;
  border-radius: 10px;
}
</style>