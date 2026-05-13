<template>
  <div class="dash-page">
    <div class="dash-inner">

      <!-- Header -->
      <div class="dash-header">
        <div class="dash-header__left">
          <h1>My <span>Shop</span></h1>
          <p>Manage your campus listings</p>
        </div>
        <button class="add-btn" @click="router.push('/add-product')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add New Product
        </button>
      </div>

      <!-- Stats -->
      <div class="dash-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.8"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
          </div>
          <div>
            <span class="stat-num">{{ allProducts.length }}</span>
            <span class="stat-lbl">Total Listings</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="1.8"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <div>
            <span class="stat-num">{{ allProducts.filter(p => p.status==='Available').length }}</span>
            <span class="stat-lbl">Available</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--gold">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#b45309" stroke-width="1.8"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/></svg>
          </div>
          <div>
            <span class="stat-num">{{ allProducts.filter(p => p.status!=='Available').length }}</span>
            <span class="stat-lbl">Sold</span>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="product-grid">
        <div v-for="n in 6" :key="n" class="product-card-skel">
          <div class="skel skel--img"></div>
          <div style="padding:12px;display:flex;flex-direction:column;gap:8px">
            <div class="skel skel--line"></div>
            <div class="skel skel--line" style="width:60%"></div>
            <div class="skel skel--line" style="width:40%"></div>
          </div>
        </div>
      </div>

      <!-- Grid -->
      <div v-else-if="allProducts.length" class="product-grid">
        <div v-for="p in allProducts" :key="p.id" class="product-card">
          <div class="product-card__img-wrap">
            <img v-if="p.image_url" :src="p.image_url" class="product-card__img" :alt="p.title" @error="e=>e.target.style.display='none'" />
            <div v-else class="product-card__img-empty">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            </div>
            <div class="product-card__badges">
              <span class="product-card__cat">{{ p.category }}</span>
              <span :class="['product-card__status', p.status==='Available' ? 'product-card__status--avail' : 'product-card__status--sold']">
                ● {{ p.status }}
              </span>
            </div>
          </div>
          <div class="product-card__body">
            <h3 class="product-card__title">{{ p.title }}</h3>
            <p class="product-card__desc">{{ p.description || '—' }}</p>
            <p class="product-card__price">₱{{ Number(p.price).toLocaleString('en-PH', {minimumFractionDigits:2}) }}</p>
            <div v-if="p.tags && p.tags.length" class="product-card__tags">
              <span v-for="tag in (Array.isArray(p.tags) ? p.tags : p.tags.split(',')).slice(0,3)" :key="tag" class="product-card__tag">{{ tag.trim() }}</span>
            </div>
          </div>
          <div class="product-card__actions">
            <button class="btn-edit" @click="openEdit(p)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              Edit
            </button>
            <button class="btn-del" @click="confirmDelete(p)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="dash-empty">
        <div class="dash-empty__icon">🏪</div>
        <h3>No listings yet</h3>
        <p>Start selling to ADNU students!</p>
        <button class="add-btn" @click="router.push('/add-product')">Post Your First Item</button>
      </div>

    </div>

    <!-- ── EDIT MODAL ── -->
    <Transition name="modal">
      <div v-if="showEdit" class="modal-backdrop" @click.self="showEdit=false">
        <div class="modal-box">
          <button class="modal-close-btn" @click="showEdit=false">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>

          <div class="modal-head">
            <div class="modal-head__icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </div>
            <div>
              <h2 class="modal-head__title">Edit Product</h2>
              <p class="modal-head__sub">Update your listing details</p>
            </div>
          </div>

          <!-- Images -->
          <div class="mf">
            <label class="mf__label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              Product Images <span class="mf__hint">up to 5</span>
            </label>
            <div class="img-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
              <div v-if="!editPreviews.length" class="img-upload-placeholder">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.5"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/></svg>
                <p>Click or drag images here</p>
                <span>JPG, PNG, WEBP — max 5MB each</span>
              </div>
              <div v-else class="img-preview-grid">
                <div v-for="(prev, i) in editPreviews" :key="i" class="img-preview-item">
                  <img :src="prev" class="img-preview-thumb" />
                  <button class="img-preview-remove" @click.stop="removeEditImage(i)">×</button>
                  <span v-if="i===0" class="img-preview-main">Main</span>
                </div>
                <div v-if="editPreviews.length < 5" class="img-add-more" @click.stop="triggerFileInput">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  <span>Add</span>
                </div>
              </div>
            </div>
            <input ref="fileInputRef" type="file" accept="image/*" multiple style="display:none" @change="handleFileChange" />
          </div>

          <!-- Title -->
          <div class="mf">
            <label class="mf__label">Title <span class="mf__req">*</span></label>
            <input v-model="editForm.title" class="mf__input" placeholder="Product title" />
          </div>

          <!-- Price -->
          <div class="mf">
            <label class="mf__label">Price (₱) <span class="mf__req">*</span></label>
            <input v-model="editForm.price" type="number" class="mf__input" placeholder="e.g. 350" min="0" />
          </div>

          <!-- Category -->
          <div class="mf">
            <label class="mf__label">Category <span class="mf__req">*</span></label>
            <select v-model="editForm.category" class="mf__select">
              <option value="" disabled>Select category</option>
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <!-- Tags -->
          <div class="mf">
            <label class="mf__label">
              Tags <span class="mf__hint">press Enter to add</span>
            </label>
            <div class="tags-wrap">
              <div class="tags-row">
                <span v-for="(tag, i) in editTagsList" :key="i" class="tag-chip">
                  {{ tag }}
                  <button @click="removeEditTag(i)" class="tag-chip__rm">×</button>
                </span>
                <input v-model="editTagInput" class="tags-text-input" placeholder="Type a tag…" @keydown.enter.prevent="addEditTag" />
              </div>
            </div>
            <div v-if="tagSuggestions[editForm.category]" class="tag-suggestions">
              <span v-for="s in tagSuggestions[editForm.category]" :key="s" class="tag-sug" @click="addEditTagDirect(s)">+ {{ s }}</span>
            </div>
          </div>

          <!-- Description -->
          <div class="mf">
            <label class="mf__label">Description</label>
            <textarea v-model="editForm.description" class="mf__textarea" rows="3" placeholder="Condition, brand, details…"></textarea>
          </div>

          <!-- Buttons -->
          <div class="modal-btns">
            <button class="btn-cancel" @click="showEdit=false">Cancel</button>
            <button class="btn-save" @click="saveEdit" :disabled="saving">
              <svg v-if="!saving" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
              {{ saving ? 'Saving…' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── DELETE MODAL ── -->
    <Transition name="modal">
      <div v-if="showDelete" class="modal-backdrop" @click.self="showDelete=false">
        <div class="modal-box modal-box--sm">
          <div class="del-icon">🗑️</div>
          <h3 class="del-title">Delete Product?</h3>
          <p class="del-msg">Are you sure you want to delete <strong>{{ deleteTarget?.title }}</strong>? This cannot be undone.</p>
          <div class="modal-btns">
            <button class="btn-cancel" @click="showDelete=false">Cancel</button>
            <button class="btn-delete" @click="doDelete" :disabled="deleting">
              {{ deleting ? 'Deleting…' : 'Yes, Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router      = useRouter()
const allProducts = ref([])
const loading     = ref(true)

// Edit
const showEdit     = ref(false)
const saving       = ref(false)
const editForm     = ref({ id: null, title: '', price: '', category: '', description: '' })
const editFiles    = ref([])
const editPreviews = ref([])
const editTagsList = ref([])
const editTagInput = ref('')
const fileInputRef = ref(null)

// Delete
const showDelete  = ref(false)
const deleting    = ref(false)
const deleteTarget = ref(null)

const user = JSON.parse(localStorage.getItem('user') || 'null')

const categories = ['Textbooks','Electronics','Dorm Items','Uniforms','School Supplies','Food','Services','Others']

const tagSuggestions = {
  'Textbooks':       ['engineering','accounting','nursing','biology','algebra'],
  'Electronics':     ['laptop','phone','charger','calculator','casio','scientific'],
  'Dorm Items':      ['bedsheet','pillow','fan','lamp','extension'],
  'Uniforms':        ['adnu','pe-uniform','laboratory','nursing-uniform'],
  'School Supplies': ['ruler','notebook','ballpen','folder','protractor'],
  'Food':            ['homemade','snacks','drinks','packed-meal'],
}

const fetchProducts = async () => {
  if (!user) return
  loading.value = true
  try {
    const r = await api.getMyProducts(user.user_id)
    allProducts.value = Array.isArray(r.data) ? r.data : []
  } catch { allProducts.value = [] }
  finally { loading.value = false }
}

// ── Edit ──────────────────────────────────────────────────────────────────
const openEdit = (p) => {
  editForm.value = { id: p.id, title: p.title, price: p.price, category: p.category, description: p.description || '' }
  editFiles.value = []
  // Load existing images as previews
  if (p.images && p.images.length) editPreviews.value = [...p.images]
  else if (p.image_url) editPreviews.value = [p.image_url]
  else editPreviews.value = []
  // Load existing tags
  if (Array.isArray(p.tags)) editTagsList.value = [...p.tags.filter(Boolean)]
  else if (p.tags) editTagsList.value = p.tags.split(',').map(t => t.trim()).filter(Boolean)
  else editTagsList.value = []
  editTagInput.value = ''
  showEdit.value = true
}

const triggerFileInput = () => fileInputRef.value?.click()

const handleFileChange = (e) => processFiles(e.target.files)
const handleDrop       = (e) => processFiles(e.dataTransfer.files)

const processFiles = (files) => {
  // Only allow new uploads (replacing server images)
  const arr = Array.from(files).slice(0, 5)
  editFiles.value = []
  editPreviews.value = []
  arr.forEach(file => {
    if (!file.type.startsWith('image/')) return
    if (file.size > 5 * 1024 * 1024) { alert(`${file.name} too large (max 5MB)`); return }
    editFiles.value.push(file)
    editPreviews.value.push(URL.createObjectURL(file))
  })
}

const removeEditImage = (i) => {
  editFiles.value.splice(i, 1)
  editPreviews.value.splice(i, 1)
}

const addEditTag = () => {
  const t = editTagInput.value.trim().toLowerCase().replace(/[^a-z0-9-]/g,'-').replace(/-+/g,'-')
  if (t && !editTagsList.value.includes(t) && editTagsList.value.length < 10) editTagsList.value.push(t)
  editTagInput.value = ''
}
const addEditTagDirect = (s) => { if (!editTagsList.value.includes(s) && editTagsList.value.length < 10) editTagsList.value.push(s) }
const removeEditTag    = (i) => editTagsList.value.splice(i, 1)

const saveEdit = async () => {
  if (!editForm.value.title || !editForm.value.price || !editForm.value.category) {
    return alert('Please fill all required fields')
  }
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('title',       editForm.value.title)
    fd.append('description', editForm.value.description || '')
    fd.append('price',       Number(editForm.value.price))
    fd.append('category',    editForm.value.category)
    fd.append('user_id',     user.user_id)
    fd.append('tags',        editTagsList.value.join(','))
    editFiles.value.forEach(file => fd.append('images', file))
    await api.updateProductWithImage(editForm.value.id, fd)
    showEdit.value = false
    await fetchProducts()
    alert('Product updated! ✅')
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to update')
  } finally { saving.value = false }
}

// ── Delete ────────────────────────────────────────────────────────────────
const confirmDelete = (p) => { deleteTarget.value = p; showDelete.value = true }

const doDelete = async () => {
  deleting.value = true
  try {
    await api.deleteProduct(deleteTarget.value.id, user.user_id)
    showDelete.value = false
    await fetchProducts()
    alert('Product deleted ✅')
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to delete')
  } finally { deleting.value = false }
}

onMounted(fetchProducts)
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes sk   { to { background-position-x: -200%; } }
.spin { animation: spin 0.8s linear infinite; transform-origin: center; }

.dash-page  { background: #f4f7fb; min-height: 100vh; padding: 2rem 1.5rem; }
.dash-inner { max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem; }

.dash-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-left: 4px solid #FFD700; padding-left: 1.25rem; }
.dash-header__left h1 { font-size: 1.6rem; font-weight: 800; color: #003366; margin: 0 0 4px; }
.dash-header__left h1 span { color: #64748b; font-weight: 300; }
.dash-header__left p { font-size: 0.82rem; color: #888; margin: 0; }

.add-btn { display: inline-flex; align-items: center; gap: 7px; background: #003366; color: #FFD700; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; font-size: 0.875rem; cursor: pointer; transition: 0.15s; font-family: inherit; }
.add-btn:hover { background: #002244; transform: translateY(-1px); }

.dash-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr)); gap: 12px; }
.stat-card { background: #fff; border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 12px; border: 1px solid #e8edf4; }
.stat-icon { width: 40px; height: 40px; background: #e8f0fe; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon--green { background: #f0fdf4; }
.stat-icon--gold  { background: #fffbeb; }
.stat-num { display: block; font-size: 1.5rem; font-weight: 800; color: #003366; line-height: 1; }
.stat-lbl { display: block; font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: 0.4px; }

.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px,1fr)); gap: 1.25rem; }

.product-card-skel { background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #e8edf4; }
.skel { background: linear-gradient(110deg,#f0f0f0 8%,#f8f8f8 18%,#f0f0f0 33%); background-size: 200% 100%; animation: sk 1.5s linear infinite; border-radius: 6px; }
.skel--img  { height: 140px; border-radius: 0; }
.skel--line { height: 14px; }

.product-card { background: #fff; border-radius: 12px; border: 1px solid #e8edf4; overflow: hidden; transition: box-shadow 0.2s, transform 0.2s; }
.product-card:hover { box-shadow: 0 4px 20px rgba(0,51,102,0.1); transform: translateY(-2px); }
.product-card__img-wrap { position: relative; }
.product-card__img { width: 100%; height: 140px; object-fit: cover; display: block; }
.product-card__img-empty { height: 140px; background: #f0f4f8; display: flex; align-items: center; justify-content: center; }
.product-card__badges { position: absolute; top: 8px; left: 8px; right: 8px; display: flex; justify-content: space-between; }
.product-card__cat { background: rgba(0,51,102,0.85); color: #fff; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }
.product-card__status { font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }
.product-card__status--avail { background: #e8f8f0; color: #15803d; }
.product-card__status--sold  { background: #fee8e8; color: #b91c1c; }
.product-card__body { padding: 12px; }
.product-card__title { font-size: 0.9rem; font-weight: 700; color: #003366; margin: 0 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.product-card__desc  { font-size: 0.78rem; color: #888; margin: 0 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.product-card__price { font-size: 1rem; font-weight: 800; color: #003366; margin: 0 0 6px; }
.product-card__tags  { display: flex; flex-wrap: wrap; gap: 4px; }
.product-card__tag   { font-size: 10px; background: #e8f0fe; color: #003366; padding: 2px 7px; border-radius: 10px; font-weight: 600; }
.product-card__actions { display: flex; gap: 8px; padding: 10px 12px; border-top: 1px solid #f0f4f8; }
.btn-edit { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; background: #f0f4ff; color: #003366; border: none; padding: 8px; border-radius: 7px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.btn-edit:hover { background: #003366; color: #FFD700; }
.btn-del  { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; background: #fff5f5; color: #e74c3c; border: none; padding: 8px; border-radius: 7px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.btn-del:hover { background: #e74c3c; color: #fff; }

.dash-empty { text-align: center; padding: 5rem 2rem; background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1; }
.dash-empty__icon { font-size: 3rem; margin-bottom: 1rem; }
.dash-empty h3 { color: #003366; font-size: 1.1rem; margin: 0 0 8px; }
.dash-empty p  { color: #888; font-size: 0.875rem; margin: 0 0 1.5rem; }

/* MODAL */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-box { background: #fff; border-radius: 18px; width: 100%; max-width: 520px; padding: 1.75rem; position: relative; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.18); display: flex; flex-direction: column; gap: 1rem; }
.modal-box--sm { max-width: 400px; }
.modal-close-btn { position: absolute; top: 16px; right: 16px; width: 32px; height: 32px; background: #f0f4f8; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.15s; color: #666; }
.modal-close-btn:hover { background: #e74c3c; color: #fff; }
.modal-head { display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #f0f4f8; padding-bottom: 1rem; }
.modal-head__icon { width: 40px; height: 40px; background: #003366; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #FFD700; flex-shrink: 0; }
.modal-head__title { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0 0 3px; }
.modal-head__sub   { font-size: 0.78rem; color: #888; margin: 0; }

.mf { display: flex; flex-direction: column; gap: 6px; }
.mf__label { font-size: 0.75rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.4px; display: flex; align-items: center; gap: 6px; }
.mf__hint  { font-size: 0.72rem; color: #aaa; font-weight: 400; text-transform: none; letter-spacing: 0; }
.mf__req   { color: #e74c3c; }
.mf__input, .mf__select, .mf__textarea { padding: 10px 12px; border: 1.5px solid #e0e8f4; border-radius: 9px; font-size: 0.9rem; color: #1a1a2e; outline: none; font-family: inherit; background: #fafcff; transition: border-color 0.15s; width: 100%; box-sizing: border-box; }
.mf__input:focus, .mf__select:focus, .mf__textarea:focus { border-color: #003366; }
.mf__textarea { resize: vertical; }

.img-upload-area { border: 2px dashed #c8d8ea; border-radius: 12px; cursor: pointer; min-height: 120px; transition: border-color 0.2s; overflow: hidden; }
.img-upload-area:hover { border-color: #003366; }
.img-upload-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 1.5rem; color: #aaa; text-align: center; min-height: 120px; }
.img-upload-placeholder p { font-size: 0.875rem; font-weight: 600; color: #555; margin: 0; }
.img-upload-placeholder span { font-size: 0.75rem; }
.img-preview-grid { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px; }
.img-preview-item { position: relative; width: 80px; height: 80px; border-radius: 8px; overflow: hidden; border: 1.5px solid #e0e8f4; }
.img-preview-thumb { width: 100%; height: 100%; object-fit: cover; }
.img-preview-remove { position: absolute; top: 3px; right: 3px; width: 18px; height: 18px; background: rgba(0,0,0,0.6); color: #fff; border: none; border-radius: 50%; cursor: pointer; font-size: 12px; display: flex; align-items: center; justify-content: center; line-height: 1; }
.img-preview-main { position: absolute; bottom: 3px; left: 3px; background: #003366; color: #FFD700; font-size: 8px; font-weight: 700; padding: 2px 5px; border-radius: 4px; }
.img-add-more { width: 80px; height: 80px; border-radius: 8px; border: 2px dashed #c8d8ea; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; cursor: pointer; color: #003366; font-size: 0.65rem; font-weight: 600; transition: 0.15s; }
.img-add-more:hover { border-color: #003366; background: #f0f5ff; }

.tags-wrap { border: 1.5px solid #e0e8f4; border-radius: 9px; padding: 8px 10px; background: #fafcff; }
.tags-wrap:focus-within { border-color: #003366; }
.tags-row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.tag-chip { display: inline-flex; align-items: center; gap: 4px; background: #e8f0fe; color: #003366; font-size: 0.78rem; font-weight: 600; padding: 4px 9px; border-radius: 14px; }
.tag-chip__rm { background: none; border: none; cursor: pointer; color: #668; font-size: 14px; line-height: 1; padding: 0; }
.tags-text-input { border: none; outline: none; font-size: 0.875rem; color: #333; background: transparent; min-width: 110px; flex: 1; font-family: inherit; }
.tag-suggestions { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 4px; }
.tag-sug { font-size: 0.72rem; font-weight: 600; color: #888; background: #f8faff; border: 1px solid #e0e8f4; padding: 3px 8px; border-radius: 10px; cursor: pointer; transition: 0.12s; }
.tag-sug:hover { background: #003366; color: #FFD700; border-color: #003366; }

.modal-btns { display: flex; gap: 10px; }
.btn-cancel { flex: 1; background: #fff; color: #555; border: 1.5px solid #e0e8f4; padding: 11px; border-radius: 9px; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.btn-cancel:hover { background: #f0f0f0; }
.btn-save   { flex: 2; background: #003366; color: #FFD700; border: none; padding: 11px; border-radius: 9px; font-weight: 800; font-size: 0.95rem; cursor: pointer; transition: 0.15s; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 7px; }
.btn-save:hover:not(:disabled) { background: #002244; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-delete { flex: 1; background: #e74c3c; color: #fff; border: none; padding: 11px; border-radius: 9px; font-weight: 700; cursor: pointer; transition: 0.15s; font-family: inherit; }
.btn-delete:hover:not(:disabled) { background: #c0392b; }
.btn-delete:disabled { opacity: 0.6; cursor: not-allowed; }

.del-icon  { font-size: 2.5rem; text-align: center; }
.del-title { font-size: 1.1rem; font-weight: 800; color: #003366; margin: 0; text-align: center; }
.del-msg   { color: #555; font-size: 0.875rem; text-align: center; margin: 0; }

.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }

@media (max-width: 640px) {
  .dash-header { flex-direction: column; align-items: flex-start; }
}
</style>