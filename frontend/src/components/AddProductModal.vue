<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h3>Post New Product</h3>

      <input v-model="product.title" placeholder="Title (e.g., Math Textbook)" />
      <textarea v-model="product.description" placeholder="Description"></textarea>
      <input v-model.number="product.price" type="number" placeholder="Price (₱)" />

      <select v-model="product.category">
        <option value="Textbooks">Textbooks</option>
        <option value="Electronics">Electronics</option>
        <option value="Dorm Items">Dorm Items</option>
      </select>

      <input v-model="product.pickup_location" placeholder="Pickup Location (e.g., Library)" />

      <div class="modal-buttons">
        <button class="submit-btn" @click="submit" :disabled="loading">
          {{ loading ? 'Posting...' : 'Post to Marketplace' }}
        </button>
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const emit = defineEmits(['close', 'refresh'])

const user = JSON.parse(localStorage.getItem('user'))
const loading = ref(false)

const product = ref({
  title: '',
  description: '',
  price: 0,
  category: 'Textbooks',
  pickup_location: '',
  user_id: user.user_id
})

const submit = async () => {
  if (!product.value.title || !product.value.description || !product.value.price) {
    alert('Please fill in all fields ❌')
    return
  }

  try {
    loading.value = true
    await api.createProduct(product.value)
    alert('Product posted successfully! ✅')
    emit('refresh')
    emit('close')
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to post product ❌')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

h3 {
  color: #003366;
  font-size: 1.3rem;
  margin: 0;
  border-left: 4px solid #FFD700;
  padding-left: 10px;
}

input, textarea, select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  width: 100%;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  margin-top: 0.5rem;
}

.submit-btn {
  flex: 1;
  background-color: #FFD700;
  color: #003366;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #e6c200;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  flex: 1;
  background-color: white;
  color: #003366;
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.3s;
}

.cancel-btn:hover {
  background-color: #f0f0f0;
}
</style>