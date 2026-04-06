<template>
  <div>
    <NavBar />
    <div class="container">
      <div class="dashboard">

        <!-- LEFT: ADD PRODUCT -->
        <div class="panel">
          <h2>Add Product</h2>

          <div class="field">
            <label>Product Name</label>
            <input v-model="name" placeholder="e.g. Calculus Textbook" />
          </div>
          <div class="field">
            <label>Price (₱)</label>
            <input v-model.number="price" type="number" placeholder="0.00" />
          </div>
          <div class="field">
            <label>Category</label>
            <select v-model="category">
              <option disabled value="">Select category</option>
              <option>Clothing</option>
              <option>School Essentials</option>
              <option>Electronics</option>
            </select>
          </div>
          <div class="field">
            <label>Product Image</label>
            <div class="file-upload" @click="$refs.fileInput.click()">
              <div v-if="!image" class="file-placeholder">📷 Click to upload image</div>
              <img v-else :src="image" class="image-preview" />
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              style="display:none"
              @change="handleImage"
            />
          </div>

          <button class="btn-add" @click="addProduct" :disabled="saving">
            {{ saving ? 'Adding...' : 'Add Product' }}
          </button>
        </div>

        <!-- RIGHT: LISTINGS + REQUESTS -->
        <div class="panel">

          <!-- MY LISTINGS -->
          <h2>My Listings</h2>
          <div v-if="myProducts.length === 0" class="empty-note">
            No listings yet. Add your first product!
          </div>
          <div class="products">
            <div v-for="p in myProducts" :key="p.id" class="card">
              <div class="image-wrapper">
                <img :src="p.image || '/placeholder.png'" :alt="p.name" />
                <span class="badge" :class="p.status">{{ p.status }}</span>
              </div>
              <div class="card-content">
                <h3>{{ p.name }}</h3>
                <p class="price">₱{{ p.price }}</p>
                <div class="dashboard-actions">
                  <button class="btn-edit" @click="editProduct(p)">Edit</button>
                  <button class="btn-delete" @click="deleteProduct(p.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>

          <!-- ORDER REQUESTS -->
          <h2 style="margin-top: 36px;">Order Requests</h2>
          <div v-if="sellerRequests.length === 0" class="empty-note">
            No requests yet.
          </div>
          <div class="request-list">
            <div v-for="r in sellerRequests" :key="r.id" class="request-card">
              <div class="request-header">
                <h3>{{ r.product.name }}</h3>
                <span class="status-badge" :class="r.status">{{ r.status }}</span>
              </div>
              <p><strong>Buyer:</strong> {{ r.buyer }}</p>
              <p>📅 {{ r.date }} &nbsp;|&nbsp; {{ r.timeRange }}</p>
              <p>📍 {{ r.location }}</p>
              <p>💳 {{ r.payment === 'cod' ? 'Cash on Meetup' : 'GCash' }}</p>
              <div v-if="r.status === 'pending'" class="dashboard-actions">
                <button class="btn-accept" @click="acceptRequest(r)">✓ Accept</button>
                <button class="btn-reject" @click="rejectRequest(r)">✕ Reject</button>
              </div>
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
      currentUser: JSON.parse(localStorage.getItem("currentUser")),
      allProducts: [],
      sellerRequests: [],
      name: "",
      price: "",
      image: "",
      category: "",
      saving: false
    };
  },

  computed: {
    myProducts() {
      return this.allProducts.filter(p => p.owner === this.currentUser.email);
    }
  },

  async mounted() {
    if (!this.currentUser || this.currentUser.role !== "seller") {
      this.$router.push("/");
      return;
    }
    await this.loadProducts();
    await this.loadRequests();
  },

  methods: {
    async loadProducts() {
      try {
        const res = await fetch(`${API}/api/products`);
        this.allProducts = await res.json();
      } catch (err) {
        alert("Could not load products.");
      }
    },

    async loadRequests() {
      try {
        const res = await fetch(`${API}/api/requests/seller/${this.currentUser.email}`);
        this.sellerRequests = await res.json();
      } catch (err) {
        alert("Could not load requests.");
      }
    },

    handleImage(e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => { this.image = reader.result; };
      reader.readAsDataURL(file);
    },

    async addProduct() {
      if (!this.name || !this.price || !this.category) {
        alert("Please fill in all fields.");
        return;
      }
      this.saving = true;
      try {
        const res = await fetch(`${API}/api/products`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: this.name,
            price: this.price,
            category: this.category,
            image: this.image || "",
            owner: this.currentUser.email
          })
        });
        const data = await res.json();
        if (!res.ok) { alert(data.message); return; }
        alert("Product added!");
        this.name = "";
        this.price = "";
        this.image = "";
        this.category = "";
        await this.loadProducts();
      } catch (err) {
        alert("Could not add product.");
      } finally {
        this.saving = false;
      }
    },

    async deleteProduct(id) {
      if (!confirm("Delete this product?")) return;
      try {
        await fetch(`${API}/api/products/${id}`, { method: "DELETE" });
        await this.loadProducts();
      } catch (err) {
        alert("Could not delete product.");
      }
    },

    async editProduct(p) {
      const name   = prompt("Product Name:", p.name);
      const price  = prompt("Price:", p.price);
      const status = prompt("Status (available / reserved / sold):", p.status);
      if (!name || !price || !status) return;
      try {
        await fetch(`${API}/api/products/${p.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, price: Number(price), status })
        });
        await this.loadProducts();
      } catch (err) {
        alert("Could not update product.");
      }
    },

    async acceptRequest(r) {
      try {
        await fetch(`${API}/api/requests/${r.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "accepted" })
        });
        await this.loadRequests();
        await this.loadProducts();
      } catch (err) {
        alert("Could not accept request.");
      }
    },

    async rejectRequest(r) {
      try {
        await fetch(`${API}/api/requests/${r.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "rejected" })
        });
        await this.loadRequests();
      } catch (err) {
        alert("Could not reject request.");
      }
    }
  }
};
</script>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .dashboard { grid-template-columns: 1fr; }
}
.field { margin-bottom: 14px; }
.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}
.file-upload {
  border: 2px dashed #ddd;
  border-radius: 10px;
  cursor: pointer;
  overflow: hidden;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
}
.file-upload:hover { border-color: #03120E; }
.file-placeholder { color: #aaa; font-size: 14px; padding: 20px; }
.image-preview { width: 100%; height: 160px; object-fit: cover; }
.btn-add {
  width: 100%;
  padding: 13px;
  background: #03120E;
  color: white;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 6px;
}
.btn-add:hover { background: #0a2a23; }
.btn-add:disabled { background: #aaa; cursor: not-allowed; }
.btn-edit { flex: 1; background: #f0f0f0; color: #333; }
.btn-edit:hover { background: #e0e0e0; }
.btn-delete { flex: 1; background: #ffe0e0; color: #c0392b; }
.btn-delete:hover { background: #ffc5c5; transform: none; }
.request-list { display: flex; flex-direction: column; gap: 16px; }
.request-card {
  background: #f9f9f9;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #eee;
}
.request-card p { margin: 4px 0; font-size: 14px; color: #555; }
.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.request-header h3 { margin: 0; font-size: 15px; }
.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: capitalize;
}
.status-badge.pending  { background: #fff3cd; color: #856404; }
.status-badge.accepted { background: #d4edda; color: #155724; }
.status-badge.rejected { background: #f8d7da; color: #721c24; }
.btn-accept { flex: 1; background: #d4edda; color: #155724; }
.btn-accept:hover { background: #c3e6cb; transform: none; }
.btn-reject { flex: 1; background: #f8d7da; color: #721c24; }
.btn-reject:hover { background: #f5c6cb; transform: none; }
.empty-note { color: #aaa; font-size: 14px; padding: 10px 0; }
</style>