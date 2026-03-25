<template>
  <div>

    <!-- NAV -->
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

      <input v-model="search" placeholder="Search products..." class="search">

      <div class="categories">
        <div v-for="cat in categories" :key="cat" @click="filterCategory(cat)">
          {{ cat }}
        </div>
      </div>

      <div class="products">
  <div v-for="p in filtered" :key="p.id" class="card">
    <div class="image-wrapper">
      <img :src="p.image">

      <span class="badge" :class="p.status">
        {{ p.status }}
      </span>
    </div>

    <div class="card-content">
      <h3 class="title">{{ p.name }}</h3>
      <p class="price">₱{{ p.price }}</p>
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
    search: "",
    selectedCategory: "",
    categories: ["Clothing", "School Essentials", "Electronics"],
    currentUser: JSON.parse(localStorage.getItem("currentUser"))
  };
},

  computed: {
    filtered() {
      return this.products
        .filter(p => p.name.toLowerCase().includes(this.search.toLowerCase()))
        .filter(p => this.selectedCategory ? p.category === this.selectedCategory : true);
    }
  },

  methods: {
    filterCategory(cat) {
      this.selectedCategory = cat;
    },

     logout() {
    localStorage.removeItem("currentUser");
    this.$router.push("/auth");
  }
  }
};
</script>