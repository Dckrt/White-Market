<template>
  <div class="wm-add-page">
    <div class="wm-add-card">
      <div class="wm-add-card__head">
        <h2 class="wm-add-card__title">Sell an Item</h2>
        <p class="wm-add-card__sub">Fill in the details to post on ADNU Market</p>
      </div>

      <!-- ── MULTI-IMAGE UPLOAD ── -->
      <div class="wm-form-group">
        <label class="wm-form-label">Product Images <span class="wm-form-hint">(up to 5)</span></label>
        <div class="wm-img-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
          <div v-if="!imagePreviews.length" class="wm-img-upload-placeholder">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            <p>Click or drag images here</p>
            <span>JPG, PNG, WEBP — max 5 images, 5MB each</span>
          </div>
          <div v-else class="wm-img-preview-grid">
            <div v-for="(prev, i) in imagePreviews" :key="i" class="wm-img-preview-item">
              <img :src="prev" alt="preview" class="wm-img-preview-thumb" />
              <button class="wm-img-preview-remove" @click.stop="removeImage(i)">✕</button>
              <span v-if="i === 0" class="wm-img-preview-main">Main</span>
            </div>
            <div v-if="imagePreviews.length < 5" class="wm-img-add-more" @click.stop="triggerFileInput">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003366" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              <span>Add more</span>
            </div>
          </div>
        </div>
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          multiple
          style="display:none"
          @change="handleFileChange"
        />
      </div>

      <!-- Title -->
      <div class="wm-form-group">
        <label class="wm-form-label">Title <span class="wm-required">*</span></label>
        <input v-model="form.title" type="text" placeholder="e.g. Casio Scientific Calculator FX-991" class="wm-form-input" />
      </div>

      <!-- Price -->
      <div class="wm-form-group">
        <label class="wm-form-label">Price (₱) <span class="wm-required">*</span></label>
        <input v-model="form.price" type="number" placeholder="e.g. 350" inputmode="numeric" class="wm-form-input" min="0" />
      </div>

      <!-- Category -->
      <div class="wm-form-group">
        <label class="wm-form-label">Category <span class="wm-required">*</span></label>
        <select v-model="form.category" class="wm-form-select">
          <option value="" disabled>Select a category</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <!-- Tags -->
      <div class="wm-form-group">
        <label class="wm-form-label">Tags <span class="wm-form-hint">(helps buyers find your item)</span></label>
        <div class="wm-tags-input-wrap">
          <div class="wm-tags-input-row">
            <div class="wm-tag-chip" v-for="(tag, i) in tagsList" :key="i">
              #{{ tag }}<button @click="removeTag(i)" class="wm-tag-chip__remove">✕</button>
            </div>
            <input
              v-model="tagInput"
              type="text"
              placeholder="Type a tag and press Enter…"
              class="wm-tags-text-input"
              @keydown.enter.prevent="addTag"
              @keydown.comma.prevent="addTag"
            />
          </div>
        </div>
        <p class="wm-form-hint-text">e.g. scientific-calculator, casio, fx-991, math</p>
        <!-- Quick tag suggestions -->
        <div class="wm-tag-suggestions">
          <span
            v-for="s in tagSuggestions[form.category] || []"
            :key="s"
            class="wm-tag-sug"
            @click="addTagDirect(s)"
          >+ {{ s }}</span>
        </div>
      </div>

      <!-- Description -->
      <div class="wm-form-group">
        <label class="wm-form-label">Description</label>
        <textarea v-model="form.description" placeholder="Condition, brand, details, reason for selling…" rows="4" class="wm-form-textarea"></textarea>
      </div>

      <!-- Meetup note -->
      <div class="wm-meetup-note">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Buyers will contact you via chat to arrange meetup details.
      </div>

      <!-- Buttons -->
      <div class="wm-form-btns">
        <button class="wm-btn-cancel" @click="router.push('/dashboard')">Cancel</button>
        <button class="wm-btn-submit" @click="submit" :disabled="loading">
          {{ loading ? 'Posting…' : 'Post Product' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const fileInputRef = ref(null)
const loading = ref(false)
const imageFiles = ref([])
const imagePreviews = ref([])
const tagInput = ref('')
const tagsList = ref([])

const form = ref({
  title: '', price: '', category: '', description: ''
})

const categories = [
  'Textbooks', 'Electronics', 'Dorm Items', 'Uniforms',
  'School Supplies', 'Food', 'Services', 'Others'
]

// Tag suggestions per category
const tagSuggestions = {
  'Textbooks':        ['engineering', 'accounting', 'nursing', 'biology', 'algebra', 'politics'],
  'Electronics':      ['laptop', 'phone', 'charger', 'calculator', 'casio', 'scientific'],
  'Dorm Items':       ['bedsheet', 'pillow', 'fan', 'lamp', 'extension'],
  'Uniforms':         ['adnu', 'pe-uniform', 'laboratory', 'nursing-uniform'],
  'School Supplies':  ['ruler', 'protractor', 'notebook', 'ballpen', 'folder'],
  'Food':             ['homemade', 'snacks', 'drinks', 'ulam', 'packed-meal'],
}

const triggerFileInput = () => fileInputRef.value?.click()

const processFiles = (files) => {
  const arr = Array.from(files).slice(0, 5 - imageFiles.value.length)
  arr.forEach(file => {
    if (!file.type.startsWith('image/')) return
    if (file.size > 5 * 1024 * 1024) { alert(`${file.name} is too large (max 5MB)`); return }
    imageFiles.value.push(file)
    imagePreviews.value.push(URL.createObjectURL(file))
  })
}

const handleFileChange = (e) => processFiles(e.target.files)
const handleDrop = (e)    => processFiles(e.dataTransfer.files)

const removeImage = (i) => {
  imageFiles.value.splice(i, 1)
  imagePreviews.value.splice(i, 1)
}

const addTag = () => {
  const t = tagInput.value.trim().toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-')
  if (t && !tagsList.value.includes(t) && tagsList.value.length < 10) {
    tagsList.value.push(t)
  }
  tagInput.value = ''
}

const addTagDirect = (s) => {
  if (!tagsList.value.includes(s) && tagsList.value.length < 10) tagsList.value.push(s)
}

const removeTag = (i) => tagsList.value.splice(i, 1)

const submit = async () => {
  if (!form.value.title || !form.value.price || !form.value.category) {
    alert('Please fill all required fields ❌'); return
  }
  if (isNaN(form.value.price) || Number(form.value.price) <= 0) {
    alert('Please enter a valid price ❌'); return
  }
  const user = JSON.parse(localStorage.getItem('user'))
  if (!user) return router.push('/auth')

  try {
    loading.value = true
    const fd = new FormData()
    fd.append('title',       form.value.title)
    fd.append('description', form.value.description)
    fd.append('price',       Number(form.value.price))
    fd.append('category',    form.value.category)
    fd.append('user_id',     user.user_id)
    fd.append('tags',        tagsList.value.join(','))
    imageFiles.value.forEach(file => fd.append('images', file))

    await api.createProduct(fd)
    alert('Product posted successfully! 🎉')
    router.push('/dashboard')
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to add product ❌')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.wm-add-page {
  background: #f4f7fb; min-height: 100vh;
  display: flex; justify-content: center; padding: 2rem 1rem;
}
.wm-add-card {
  background: #fff; width: 100%; max-width: 560px;
  padding: 2rem; border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0,51,102,0.08);
  height: fit-content; display: flex; flex-direction: column; gap: 1.25rem;
  border: 1px solid #e8edf4;
}
.wm-add-card__head { border-left: 4px solid #FFD700; padding-left: 12px; }
.wm-add-card__title { font-size: 1.5rem; font-weight: 800; color: #003366; margin: 0 0 4px; }
.wm-add-card__sub { font-size: 0.875rem; color: #888; margin: 0; }

/* Image upload */
.wm-img-upload-area {
  border: 2px dashed #c8d8ea; border-radius: 12px; cursor: pointer;
  min-height: 140px; transition: border-color 0.2s; overflow: hidden;
}
.wm-img-upload-area:hover { border-color: #003366; }
.wm-img-upload-placeholder {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; padding: 2rem; color: #aaa; text-align: center; min-height: 140px;
}
.wm-img-upload-placeholder p { font-size: 0.9rem; font-weight: 600; color: #555; margin: 0; }
.wm-img-upload-placeholder span { font-size: 0.75rem; color: #bbb; }

.wm-img-preview-grid {
  display: flex; flex-wrap: wrap; gap: 8px; padding: 12px;
}
.wm-img-preview-item { position: relative; width: 90px; height: 90px; border-radius: 9px; overflow: hidden; border: 1.5px solid #e0e8f4; }
.wm-img-preview-thumb { width: 100%; height: 100%; object-fit: cover; }
.wm-img-preview-remove {
  position: absolute; top: 4px; right: 4px; width: 20px; height: 20px;
  background: rgba(0,0,0,0.6); color: #fff; border: none; border-radius: 50%;
  font-size: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.wm-img-preview-main {
  position: absolute; bottom: 4px; left: 4px;
  background: #003366; color: #FFD700; font-size: 9px; font-weight: 700;
  padding: 2px 6px; border-radius: 4px;
}
.wm-img-add-more {
  width: 90px; height: 90px; border-radius: 9px; border: 2px dashed #c8d8ea;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 4px; cursor: pointer; color: #003366; font-size: 0.7rem; font-weight: 600;
  transition: 0.15s;
}
.wm-img-add-more:hover { border-color: #003366; background: #f0f5ff; }

/* Form */
.wm-form-group { display: flex; flex-direction: column; gap: 6px; }
.wm-form-label { font-size: 0.78rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.4px; display: flex; align-items: center; gap: 6px; }
.wm-form-hint { font-size: 0.72rem; color: #aaa; font-weight: 400; text-transform: none; letter-spacing: 0; }
.wm-required { color: #e74c3c; }
.wm-form-hint-text { font-size: 0.72rem; color: #bbb; margin: 2px 0 0; }

.wm-form-input, .wm-form-select, .wm-form-textarea {
  padding: 10px 12px; border: 1.5px solid #e0e8f4; border-radius: 9px;
  font-size: 0.95rem; width: 100%; color: #1a1a2e;
  transition: border-color 0.15s; outline: none; font-family: inherit;
  background: #fafcff;
}
.wm-form-input:focus, .wm-form-select:focus, .wm-form-textarea:focus { border-color: #003366; background: #fff; }
.wm-form-textarea { resize: vertical; }

/* Tags */
.wm-tags-input-wrap {
  border: 1.5px solid #e0e8f4; border-radius: 9px; padding: 8px 10px;
  background: #fafcff; transition: border-color 0.15s;
}
.wm-tags-input-wrap:focus-within { border-color: #003366; }
.wm-tags-input-row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.wm-tag-chip {
  display: flex; align-items: center; gap: 4px;
  background: #e8f0fe; color: #003366; font-size: 0.78rem; font-weight: 600;
  padding: 3px 10px; border-radius: 14px;
}
.wm-tag-chip__remove { background: none; border: none; color: #888; cursor: pointer; padding: 0; font-size: 11px; line-height: 1; font-family: inherit; }
.wm-tags-text-input { border: none; outline: none; font-size: 0.875rem; color: #333; background: transparent; min-width: 120px; flex: 1; font-family: inherit; }
.wm-tags-text-input::placeholder { color: #bbb; }

.wm-tag-suggestions { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.wm-tag-sug {
  font-size: 0.72rem; font-weight: 600; color: #888; background: #f8faff;
  border: 1px solid #e0e8f4; padding: 2px 9px; border-radius: 10px; cursor: pointer; transition: 0.12s;
}
.wm-tag-sug:hover { background: #003366; color: #FFD700; border-color: #003366; }

.wm-meetup-note {
  display: flex; align-items: center; gap: 8px;
  background: #f0f5ff; color: #003366; font-size: 0.82rem; font-weight: 600;
  padding: 10px 14px; border-radius: 9px; border-left: 3px solid #003366;
}

.wm-form-btns { display: flex; gap: 10px; }
.wm-btn-cancel {
  flex: 1; background: #fff; color: #003366; border: 1.5px solid #e0e8f4;
  padding: 12px; border-radius: 9px; font-weight: 700; cursor: pointer;
  transition: 0.15s; font-family: inherit;
}
.wm-btn-cancel:hover { background: #f0f5ff; }
.wm-btn-submit {
  flex: 2; background: #003366; color: #FFD700; border: none;
  padding: 12px; border-radius: 9px; font-weight: 800;
  font-size: 1rem; cursor: pointer; transition: 0.15s; font-family: inherit;
}
.wm-btn-submit:hover:not(:disabled) { background: #002244; }
.wm-btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>