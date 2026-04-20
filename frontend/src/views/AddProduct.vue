<template>
  <div class="page-wrapper">
    <div class="form-card">
      <h2>Sell an Item</h2>
      <p class="subtitle">Fill in the details below to post your item on ADNU Market</p>

      <!-- Image Upload -->
      <div class="input-group">
        <label>Product Image</label>
        <div class="image-upload-box" @click="triggerFileInput">
          <img v-if="imagePreview" :src="imagePreview" class="preview-img" />
          <div v-else class="upload-placeholder">
            <i class="fa-solid fa-camera upload-icon"></i>
            <span>Click to upload image</span>
            <span class="upload-hint">JPG, PNG — optional</span>
          </div>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleImageChange"
        />
      </div>

      <!-- Title -->
      <div class="input-group">
        <label>Title <span class="required">*</span></label>
        <input v-model="title" type="text" placeholder="e.g. Math Textbook, Calculator" />
      </div>

      <!-- Price -->
      <div class="input-group">
        <label>Price (₱) <span class="required">*</span></label>
        <input v-model="price" type="text" placeholder="e.g. 250" inputmode="numeric" />
      </div>

      <!-- Category -->
      <div class="input-group">
        <label>Category <span class="required">*</span></label>
        <select v-model="category">
          <option value="" disabled>Select a category</option>
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

      <!-- Description -->
      <div class="input-group">
        <label>Description</label>
        <textarea v-model="description" placeholder="Describe your item — condition, details, etc." rows="4"></textarea>
      </div>

      <!-- Meetup note -->
      <div class="meetup-note">
        <i class="fa-solid fa-comments"></i>
        Buyers will contact you via chat to arrange meetup details.
      </div>

      <!-- Buttons -->
      <div class="btn-group">
        <button class="cancel-btn" @click="router.push('/dashboard')">Cancel</button>
        <button class="submit-btn" @click="submit" :disabled="loading">
          {{ loading ? 'Posting...' : 'Post Product' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const title = ref('')
const price = ref('')
const category = ref('')
const description = ref('')
const loading = ref(false)
const imagePreview = ref(null)
const imageFile = ref(null)
const fileInput = ref(null)

const triggerFileInput = () => fileInput.value?.click()

const handleImageChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

const submit = async () => {
  if (!title.value || !price.value || !category.value) {
    alert('Please fill all required fields ❌')
    return
  }
  if (isNaN(price.value) || Number(price.value) <= 0) {
    alert('Please enter a valid price ❌')
    return
  }
  const user = JSON.parse(localStorage.getItem('user'))
  if (!user) {
    alert('Please login first')
    return router.push('/auth')
  }
  try {
    loading.value = true
    await api.createProduct({
      title: title.value,
      description: description.value,
      price: Number(price.value),
      category: category.value,
      user_id: user.user_id
    })
    alert('Product posted successfully! 🎉')
    router.push('/dashboard')
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.message || 'Failed to add product ❌')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-wrapper {
  background-color: #f8fafc;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
}

.form-card {
  background: white;
  width: 100%;
  max-width: 520px;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  height: fit-content;
}

h2 {
  color: #003366;
  font-size: 1.5rem;
  margin: 0;
  border-left: 4px solid #FFD700;
  padding-left: 10px;
}

.subtitle { color: #888; font-size: 0.875rem; margin: 0; }

.input-group { display: flex; flex-direction: column; gap: 6px; }
.input-group label { font-size: 0.82rem; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 0.5px; }
.required { color: #e74c3c; }

input, select, textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  width: 100%;
  box-sizing: border-box;
  transition: border 0.2s;
}

input:focus, select:focus, textarea:focus { outline: none; border-color: #003366; }
textarea { resize: vertical; }

/* Image Upload */
.image-upload-box {
  border: 2px dashed #ddd;
  border-radius: 10px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s;
}
.image-upload-box:hover { border-color: #003366; }

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: #aaa;
  font-size: 0.875rem;
}

.upload-icon { font-size: 1.8rem; color: #003366; }
.upload-hint { font-size: 0.75rem; color: #ccc; }

.preview-img { width: 100%; height: 100%; object-fit: cover; }

/* Meetup note */
.meetup-note {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f0f4ff;
  color: #003366;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 10px 14px;
  border-radius: 8px;
  border-left: 3px solid #003366;
}

/* Buttons */
.btn-group { display: flex; gap: 10px; margin-top: 0.5rem; }

.submit-btn {
  flex: 1;
  background-color: #FFD700;
  color: #003366;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.3s;
}
.submit-btn:hover:not(:disabled) { background-color: #e6c200; transform: translateY(-2px); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.cancel-btn {
  flex: 1;
  background: white;
  color: #003366;
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.3s;
}
.cancel-btn:hover { background-color: #f0f0f0; }
</style>