<template>
  <div>
    <NavBar />
    <div class="container">
      <div class="browse-header">
        <h2>Browse Products</h2>
        <p class="browse-sub">{{ filtered.length }} item{{ filtered.length !== 1 ? 's' : '' }} found</p>
      </div>
      <input v-model="search" placeholder="Search products..." class="search" />
      <div class="categories">
        <div
          :class="['cat-chip', selectedCategory === '' ? 'active' : '']"
          @click="selectedCategory = ''"
        >All</div>
        <div
          v-for="cat in categories"
          :key="cat"
          :class="['cat-chip', selectedCategory === cat ? 'active' : '']"
          @click="filterCategory(cat)"
        >
          {{ cat }}
        </div>
      </div>
      <div v-if="loading" class="empty-state">
        <p>Loading products...</p>
      </div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <p>😕 No products match your search.</p>
      </div>
      <div class="products">
        <div v-for="p in filtered" :key="p.id" class="card">
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

const API = "http://localhost:5000";

export default {
  components: { NavBar },

  data() {
    return {
      products: [],
      loading: true,
      search: "",
      selectedCategory: "",
      categories: ["Clothing", "School Essentials", "Electronics"]
    };
  },

  computed: {
    filtered() {
      return this.products
        .filter(p => p.name.toLowerCase().includes(this.search.toLowerCase()))
        .filter(p => this.selectedCategory ? p.category === this.selectedCategory : true);
    }
  },

  async mounted() {
    try {
      const res = await fetch(`${API}/api/products`);
      this.products = await res.json();
    } catch (err) {
      alert("Could not load products. Is Flask running?");
    } finally {
      this.loading = false;
    }
  },

  methods: {
    filterCategory(cat) {
      this.selectedCategory = this.selectedCategory === cat ? "" : cat;
    },

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
.browse-header {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 16px;
}
.browse-header h2 {
  margin: 0;
}
.browse-sub {
  color: #999;
  font-size: 14px;
  margin: 0;
}
.cat-chip {
  padding: 9px 18px;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: 0.2s;
  border: 2px solid transparent;
}
.cat-chip:hover {
  transform: translateY(-2px);
  background: #f0f0f0;
}
.cat-chip.active {
  background: #03120E;
  color: white;
  border-color: #03120E;
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