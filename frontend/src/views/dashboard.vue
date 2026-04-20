<template>
  <div class="dashboard-wrapper">
    <div class="container">

      <!-- Header -->
      <header class="dashboard-header">
        <div class="title-section">
          <h1>Seller <span>Dashboard</span></h1>
          <p>Manage your campus listings and sales status</p>
        </div>
        <button class="add-btn" @click="router.push('/add-product')">
          <i class="fa-solid fa-plus"></i> Add New Product
        </button>
      </header>

      <!-- Stats Bar -->
      <div class="stats-bar">
        <div class="stat-card">
          <div class="stat-icon"><i class="fa-solid fa-box"></i></div>
          <div>
            <span class="stat-label">Total Listings</span>
            <span class="stat-value">{{ totalProducts }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green"><i class="fa-solid fa-circle-check"></i></div>
          <div>
            <span class="stat-label">Available</span>
            <span class="stat-value">{{ products.length }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon gold"><i class="fa-solid fa-file-lines"></i></div>
          <div>
            <span class="stat-label">Current Page</span>
            <span class="stat-value">{{ page }} / {{ totalPages || 1 }}</span>
          </div>
        </div>
      </div>

      <!-- Section Title -->
      <div class="section-header">
        <h2>Your Listings</h2>
        <span class="item-count">{{ totalProducts }} item{{ totalProducts !== 1 ? 's' : '' }}</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="product-grid">
        <SkeletonCard v-for="n in 8" :key="n" />
      </div>

      <!-- Products Grid -->
      <div v-else-if="products.length > 0" class="product-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="card-top">
            <img
              v-if="product.image_url"
              :src="product.image_url"
              class="card-img"
              alt="Product image"
            />
            <div v-else class="card-img-placeholder">
              <i class="fa-solid fa-image"></i>
            </div>
            <div class="card-badges">
              <span class="cat-badge">{{ product.category }}</span>
              <span class="status-badge">● Available</span>
            </div>
          </div>
          <div class="card-body">
            <h3>{{ product.title }}</h3>
            <p class="card-desc">{{ product.description }}</p>
            <p class="card-price">₱{{ Number(product.price).toLocaleString() }}</p>
          </div>
          <div class="card-actions">
            <button class="edit-btn" @click="openEdit(product)">
              <i class="fa-solid fa-pen"></i> Edit
            </button>
            <button class="delete-btn" @click="confirmDelete(product)">
              <i class="fa-solid fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🏪</div>
        <h3>No listings yet</h3>
        <p>Start selling to ADNU students by posting your first item.</p>
        <button @click="router.push('/add-product')" class="add-btn">
          <i class="fa-solid fa-plus"></i> Post Your First Item
        </button>
      </div>

      <!-- Pagination -->
      <nav v-if="totalPages > 1" class="pagination-container">
        <button @click="prevPage" :disabled="page === 1" class="page-btn">
          <i class="fa-solid fa-chevron-left"></i> Prev
        </button>
        <div class="page-numbers">
          <button v-for="p in totalPages" :key="p" class="page-num"
            :class="{ active: p === page }" @click="page = p">{{ p }}</button>
        </div>
        <button @click="nextPage" :disabled="page >= totalPages" class="page-btn">
          Next <i class="fa-solid fa-chevron-right"></i>
        </button>
      </nav>
    </div>

    <!-- EDIT MODAL -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal">
        <h3><i class="fa-solid fa-pen"></i> Edit Product</h3>

        <!-- Image Upload -->
        <div class="input-group">
          <label>Product Image</label>
          <div
            class="image-upload-area"
            @click="triggerFileInput"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <img
              v-if="imagePreview"
              :src="imagePreview"
              class="image-preview"
              alt="Preview"
            />
            <div v-else class="upload-placeholder">
              <i class="fa-solid fa-cloud-arrow-up upload-icon"></i>
              <p>Click or drag to upload a new photo</p>
              <span>JPG, PNG, WEBP — max 5MB</span>
            </div>
            <div v-if="imagePreview" class="image-overlay">
              <i class="fa-solid fa-camera"></i> Change Photo
            </div>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileChange"
          />
          <button
            v-if="imagePreview && imagePreview !== editForm.existing_image_url"
            class="remove-img-btn"
            @click="removeNewImage"
          >
            <i class="fa-solid fa-xmark"></i> Remove new image
          </button>
        </div>

        <div class="input-group">
          <label>Title</label>
          <input v-model="editForm.title" type="text" />
        </div>
        <div class="input-group">
          <label>Price (₱)</label>
          <input v-model="editForm.price" type="text" inputmode="numeric" />
        </div>
        <div class="input-group">
          <label>Category</label>
          <select v-model="editForm.category">
            <option value="Textbooks">Textbooks</option>
            <option value="Electronics">Electronics</option>
            <option value="Dorm Items">Dorm Items</option>
            <option value="Uniforms">Uniforms</option>
            <option value="School Supplies">School Supplies</option>
            <option value="Food">Food</option>
            <option value="Services">Services</option>
            <option value="Others">Others</option>
          </select>
        </div>
        <div class="input-group">
          <label>Description</label>
          <textarea v-model="editForm.description" rows="3"></textarea>
        </div>

        <div class="modal-btns">
          <button class="cancel-btn" @click="showEditModal = false">Cancel</button>
          <button class="save-btn" @click="saveEdit" :disabled="saving">
            <i class="fa-solid fa-floppy-disk"></i>
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- DELETE CONFIRM MODAL -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal">
        <div class="delete-icon">🗑️</div>
        <h3>Delete Product?</h3>
        <p class="delete-msg">Are you sure you want to delete <strong>{{ deleteTarget?.title }}</strong>? This cannot be undone.</p>
        <div class="modal-btns">
          <button class="cancel-btn" @click="showDeleteModal = false">Cancel</button>
          <button class="delete-confirm-btn" @click="deleteProduct" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Yes, Delete' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import API from '../services/api'
import SkeletonCard from '../components/SkeletonCard.vue'

const router = useRouter()
const products = ref([])
const loading = ref(true)
const page = ref(1)
const limit = 8
const totalProducts = ref(0)

// Edit
const showEditModal = ref(false)
const saving = ref(false)
const editForm = ref({
  id: null,
  title: '',
  price: '',
  category: '',
  description: '',
  existing_image_url: ''
})

// Image upload
const fileInputRef = ref(null)
const imagePreview = ref(null)
const selectedFile = ref(null)

// Delete
const showDeleteModal = ref(false)
const deleting = ref(false)
const deleteTarget = ref(null)

const user = JSON.parse(localStorage.getItem('user'))

const totalPages = computed(() => Math.max(1, Math.ceil(totalProducts.value / limit)))

// ✅ FIXED: uses getMyProducts so ALL your listings show up regardless of pagination
const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await API.getMyProducts(user.user_id)
    const data = Array.isArray(res.data) ? res.data : (res.data.products || [])
    products.value = data
    totalProducts.value = data.length
  } catch (err) {
    console.error('Dashboard Fetch Error:', err)
  } finally {
    loading.value = false
  }
}

const openEdit = (product) => {
  editForm.value = {
    id: product.id,
    title: product.title,
    price: product.price,
    category: product.category,
    description: product.description,
    existing_image_url: product.image_url || ''
  }
  imagePreview.value = product.image_url || null
  selectedFile.value = null
  showEditModal.value = true
}

// Image handling
const triggerFileInput = () => fileInputRef.value?.click()

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) processFile(file)
}

const handleDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) processFile(file)
}

const processFile = (file) => {
  if (file.size > 5 * 1024 * 1024) {
    alert('Image must be under 5MB.')
    return
  }
  selectedFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

const removeNewImage = () => {
  selectedFile.value = null
  imagePreview.value = editForm.value.existing_image_url || null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

const saveEdit = async () => {
  try {
    saving.value = true

    if (selectedFile.value) {
      const formData = new FormData()
      formData.append('title', editForm.value.title)
      formData.append('price', Number(editForm.value.price))
      formData.append('category', editForm.value.category)
      formData.append('description', editForm.value.description)
      formData.append('user_id', user.user_id)
      formData.append('image', selectedFile.value)
      await API.updateProductWithImage(editForm.value.id, formData)
    } else {
      await API.updateProduct(editForm.value.id, {
        title: editForm.value.title,
        price: Number(editForm.value.price),
        category: editForm.value.category,
        description: editForm.value.description,
        user_id: user.user_id
      })
    }

    alert('Product updated! ✅')
    showEditModal.value = false
    fetchProducts()
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to update ❌')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (product) => {
  deleteTarget.value = product
  showDeleteModal.value = true
}

const deleteProduct = async () => {
  try {
    deleting.value = true
    await API.deleteProduct(deleteTarget.value.id, user.user_id)
    alert('Product deleted! ✅')
    showDeleteModal.value = false
    fetchProducts()
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to delete ❌')
  } finally {
    deleting.value = false
  }
}

const nextPage = () => { if (page.value < totalPages.value) page.value++ }
const prevPage = () => { if (page.value > 1) page.value-- }

onMounted(fetchProducts)
watch(page, fetchProducts)
</script>

<style scoped>
.dashboard-wrapper { background-color: #f8fafc; min-height: 100vh; }
.container { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }

.dashboard-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 2rem; border-left: 5px solid #FFD700;
  padding-left: 1.5rem; flex-wrap: wrap; gap: 1rem;
}

.title-section h1 { margin: 0; color: #003366; font-size: 1.8rem; font-weight: 800; }
.title-section h1 span { color: #64748b; font-weight: 300; }
.title-section p { color: #888; margin: 4px 0 0; font-size: 0.875rem; }

.add-btn {
  display: inline-flex; align-items: center; gap: 8px;
  background-color: #003366; color: white; border: none;
  padding: 11px 22px; border-radius: 8px; font-weight: 700;
  font-size: 0.9rem; cursor: pointer; transition: 0.2s;
}
.add-btn:hover { background-color: #002244; transform: translateY(-2px); }

.stats-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 2rem; }
.stat-card { background: white; border-radius: 12px; padding: 1rem 1.25rem; display: flex; align-items: center; gap: 14px; border: 0.5px solid #eee; }
.stat-icon { width: 40px; height: 40px; background: #f0f4ff; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #003366; font-size: 1rem; flex-shrink: 0; }
.stat-icon.green { color: #16a34a; background: #f0fdf4; }
.stat-icon.gold { color: #b45309; background: #fffbeb; }
.stat-card div { display: flex; flex-direction: column; }
.stat-label { font-size: 0.72rem; text-transform: uppercase; color: #888; letter-spacing: 0.5px; }
.stat-value { font-size: 1.3rem; font-weight: 800; color: #003366; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.section-header h2 { font-size: 1.1rem; font-weight: 700; color: #003366; margin: 0; }
.item-count { font-size: 0.82rem; color: #888; background: #f1f5f9; padding: 3px 10px; border-radius: 20px; }

.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.5rem; }

.product-card { background: white; border-radius: 12px; border: 0.5px solid #eee; overflow: hidden; transition: 0.2s; }
.product-card:hover { transform: translateY(-3px); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

.card-img { width: 100%; height: 140px; object-fit: cover; display: block; }
.card-img-placeholder { height: 140px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; color: #ccc; font-size: 2rem; }

.card-badges { display: flex; justify-content: space-between; padding: 8px 12px; }
.cat-badge { font-size: 0.7rem; font-weight: 700; background: #f0f4f8; color: #555; padding: 3px 8px; border-radius: 4px; }
.status-badge { font-size: 0.7rem; font-weight: 700; color: #16a34a; }

.card-body { padding: 0 12px 12px; }
.card-body h3 { font-size: 0.95rem; font-weight: 700; color: #003366; margin: 0 0 4px; }
.card-desc { font-size: 0.8rem; color: #888; margin: 0 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-price { font-size: 1rem; font-weight: 800; color: #e74c3c; margin: 0; }

.card-actions { display: flex; gap: 8px; padding: 10px 12px; border-top: 1px solid #f1f5f9; }

.edit-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  background: #f0f4ff; color: #003366; border: none; padding: 8px;
  border-radius: 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.2s;
}
.edit-btn:hover { background: #003366; color: white; }

.delete-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  background: #fff5f5; color: #e74c3c; border: none; padding: 8px;
  border-radius: 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.2s;
}
.delete-btn:hover { background: #e74c3c; color: white; }

.empty-state { text-align: center; padding: 5rem 2rem; background: white; border-radius: 16px; border: 1px dashed #cbd5e1; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h3 { color: #003366; font-size: 1.1rem; margin: 0 0 8px; }
.empty-state p { color: #888; font-size: 0.9rem; margin: 0 0 1.5rem; }

.pagination-container { display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 3rem; padding-bottom: 2rem; }
.page-btn { display: flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 8px; cursor: pointer; font-weight: 600; color: #003366; font-size: 0.875rem; transition: 0.2s; }
.page-btn:hover:not(:disabled) { background-color: #003366; color: white; border-color: #003366; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-numbers { display: flex; gap: 6px; }
.page-num { width: 36px; height: 36px; border-radius: 8px; border: 1px solid #e2e8f0; background: white; color: #555; font-weight: 600; cursor: pointer; transition: 0.2s; font-size: 0.875rem; }
.page-num:hover { border-color: #003366; color: #003366; }
.page-num.active { background: #003366; color: white; border-color: #003366; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
.modal { background: white; border-radius: 16px; padding: 2rem; width: 100%; max-width: 480px; display: flex; flex-direction: column; gap: 1rem; max-height: 90vh; overflow-y: auto; }
.modal h3 { color: #003366; font-size: 1.1rem; margin: 0; display: flex; align-items: center; gap: 8px; }

.image-upload-area {
  position: relative; border: 2px dashed #cbd5e1; border-radius: 10px;
  cursor: pointer; overflow: hidden; transition: border-color 0.2s;
  min-height: 140px; display: flex; align-items: center; justify-content: center;
}
.image-upload-area:hover { border-color: #003366; }

.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 1.5rem; color: #888; text-align: center; }
.upload-icon { font-size: 2rem; color: #003366; margin-bottom: 4px; }
.upload-placeholder p { margin: 0; font-size: 0.875rem; font-weight: 600; color: #555; }
.upload-placeholder span { font-size: 0.75rem; color: #aaa; }

.image-preview { width: 100%; height: 180px; object-fit: cover; display: block; }

.image-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 0.875rem; font-weight: 700; gap: 8px;
  opacity: 0; transition: opacity 0.2s;
}
.image-upload-area:hover .image-overlay { opacity: 1; }

.remove-img-btn {
  background: none; border: none; color: #e74c3c; font-size: 0.8rem;
  font-weight: 700; cursor: pointer; padding: 4px 0;
  display: flex; align-items: center; gap: 5px;
}
.remove-img-btn:hover { text-decoration: underline; }

.input-group { display: flex; flex-direction: column; gap: 5px; }
.input-group label { font-size: 0.78rem; font-weight: 700; color: #003366; text-transform: uppercase; }
.input-group input, .input-group select, .input-group textarea { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 0.9rem; width: 100%; box-sizing: border-box; }
.input-group textarea { resize: vertical; }

.modal-btns { display: flex; gap: 10px; margin-top: 0.5rem; }
.cancel-btn { flex: 1; background: white; color: #555; border: 1px solid #ddd; padding: 11px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
.cancel-btn:hover { background: #f0f0f0; }
.save-btn { flex: 1; background: #003366; color: white; border: none; padding: 11px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
.save-btn:hover:not(:disabled) { background: #002244; }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.delete-icon { font-size: 2.5rem; text-align: center; }
.delete-msg { color: #555; font-size: 0.9rem; text-align: center; margin: 0; }
.delete-confirm-btn { flex: 1; background: #e74c3c; color: white; border: none; padding: 11px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
.delete-confirm-btn:hover:not(:disabled) { background: #c0392b; }
.delete-confirm-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>