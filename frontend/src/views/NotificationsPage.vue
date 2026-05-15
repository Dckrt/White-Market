<template>
  <div class="notifications-page">

    <div class="header">
      <h1>Notifications</h1>
      <p>{{ notifications.length }} notifications</p>
    </div>

    <div v-if="loading" class="loading">
      Loading notifications...
    </div>

    <div v-else-if="notifications.length === 0" class="empty">
      No notifications yet 🔔
    </div>

    <div v-else class="notif-list">

      <div
        v-for="notif in notifications"
        :key="notif.id"
        class="notif-card"
      >
        <div class="notif-message">
          {{ notif.message }}
        </div>

        <div class="notif-time">
          {{ formatDate(notif.created_at) }}
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const notifications = ref([])
const loading = ref(true)

const user = JSON.parse(localStorage.getItem('user'))

const fetchNotifications = async () => {
  try {
    const res = await api.getNotifications(user.user_id)

    notifications.value = res.data || []

  } catch (err) {
    console.error(err)
    notifications.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  if (!date) return ''

  return new Date(date).toLocaleString()
}

onMounted(fetchNotifications)
</script>

<style scoped>
.notifications-page {
  padding: 2rem;
  max-width: 700px;
  margin: auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  color: #003366;
  font-size: 2rem;
}

.header p {
  color: #777;
  margin-top: 5px;
}

.loading,
.empty {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  color: #777;
}

.notif-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notif-card {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  border-left: 5px solid #FFD700;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.notif-message {
  font-weight: 600;
  color: #1a1a1a;
}

.notif-time {
  margin-top: 8px;
  font-size: 0.85rem;
  color: #999;
}
</style>