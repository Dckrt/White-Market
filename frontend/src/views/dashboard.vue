<template>
  <div>

    <!-- NAV -->
    <header class="nav">
      <h1>White Market - Seller</h1>

      <div class="nav-links">
        <button @click="goHome">Home</button>
        <button @click="logout">Logout</button>
      </div>
    </header>

    <div class="container dashboard">

      <!-- LEFT: ADD PRODUCT -->
      <div class="panel">
        <h2>Add Product</h2>

        <input v-model="name" placeholder="Product name">
        <input v-model.number="price" type="number" placeholder="Price">
        <input v-model="category" placeholder="Category">
        <input type="file" @change="handleImage">

        <button type="button" @click="addProduct">
  Add Product
</button>
      </div>

      <!-- RIGHT: PRODUCT LIST -->
<div class="panel">

  <h2>My Listings</h2>

  <div class="products">
    <div v-for="p in myProducts" :key="p.id" class="card">

      <img :src="p.image">

      <div class="card-content">
        <h3>{{ p.name }}</h3>
        <p class="price">₱{{ p.price }}</p>

        <div class="dashboard-actions">
          <button @click="editProduct(p)">Edit</button>
          <button @click="deleteProduct(p.id)">Delete</button>
        </div>
      </div>

    </div>
  </div>

  <h2 style="margin-top: 30px;">Order Requests</h2>

  <div v-if="sellerRequests.length === 0">
    No requests yet
  </div>

  <div class="products">
    <div v-for="r in sellerRequests" :key="r.id" class="card">

      <div class="card-content">
        <h3>{{ r.product.name }}</h3>

        <p><strong>Buyer:</strong> {{ r.buyer }}</p>
        <p>{{ r.date }} | {{ r.timeRange }}</p>
        <p>{{ r.location }}</p>
        <p><strong>Payment:</strong> {{ r.payment }}</p>
        <p><strong>Status:</strong> {{ r.status }}</p>

        <div v-if="r.status === 'pending'" class="dashboard-actions">
          <button @click="acceptRequest(r)">Accept</button>
          <button @click="rejectRequest(r)">Reject</button>
        </div>

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
    currentUser: JSON.parse(localStorage.getItem("currentUser")),
    products: JSON.parse(localStorage.getItem("products")) || [],
    requests: JSON.parse(localStorage.getItem("requests")) || [],

    name: "",
    price: "",
    image: "",
    category: ""
  };
},

computed: {
  myProducts() {
    return this.products.filter(
      p => p.owner === this.currentUser.email
    );
  },

  sellerRequests() {
    return this.requests.filter(
      r => r.seller === this.currentUser.email
    );
  }
},

methods: {

  goHome() {
    this.$router.push("/");
  },

  logout() {
    localStorage.removeItem("currentUser");
    this.$router.push("/auth");
  },

  handleImage(e) {
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = () => {
      this.image = reader.result;
    };

    reader.readAsDataURL(file);
  },

addProduct() {
  console.log("ADD PRODUCT CLICKED");

  if (!this.currentUser) {
    alert("You must be logged in");
    return;
  }

  if (!this.name || !this.price || !this.category) {
    alert("Fill all fields");
    return;
  }

  this.products.push({
    id: Date.now(),
    name: this.name,
    price: this.price,
    image: this.image || "",
    category: this.category,
    status: "available",
    owner: this.currentUser.email
  });

  localStorage.setItem("products", JSON.stringify(this.products));

  this.name = "";
  this.price = "";
  this.image = "";
  this.category = "";
},

  deleteProduct(id) {
    this.products = this.products.filter(p => p.id !== id);
    localStorage.setItem("products", JSON.stringify(this.products));
  },

  editProduct(p) {
    const name = prompt("Name", p.name);
    const price = prompt("Price", p.price);
    const status = prompt("Status (available/reserved/sold)", p.status);

    if (name && price && status) {
      p.name = name;
      p.price = Number(price);
      p.status = status;

      localStorage.setItem("products", JSON.stringify(this.products));
    }
  },

  acceptRequest(r) {
    r.status = "accepted";

    // mark product as reserved
    const product = this.products.find(p => p.id === r.product.id);
    if (product) {
      product.status = "reserved";
    }

    localStorage.setItem("products", JSON.stringify(this.products));
    localStorage.setItem("requests", JSON.stringify(this.requests));
  },

  rejectRequest(r) {
    r.status = "rejected";
    localStorage.setItem("requests", JSON.stringify(this.requests));
  }

},
  
  mounted() {
    if (!this.currentUser || this.currentUser.role !== "seller") {
      this.$router.push("/");
    }
  }
};
</script>

<style>
form {
  margin-bottom: 20px;
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

.dashboard {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
}

/* PANEL */
.panel {
  background: white;
  padding: 20px;
  border-radius: 12px;
}

/* DASHBOARD BUTTONS */
.dashboard-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.dashboard-actions button {
  flex: 1;
}
</style>