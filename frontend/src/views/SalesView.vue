<template>
  <div class="sales-page">

    <!-- HEADER -->
    <div class="sales-header">
      <div>
        <h1>Sales</h1>
        <p>Manage orders from buyers</p>
      </div>
    </div>

    <!-- EMPTY -->
    <div v-if="loading" class="sales-loading">
      Loading sales...
    </div>

    <div v-else-if="orders.length === 0" class="sales-empty">
      <h3>No sales yet</h3>
      <p>Your sold products will appear here.</p>
    </div>

    <!-- SALES LIST -->
    <div v-else class="sales-grid">

      <div
        v-for="o in orders"
        :key="o.id"
        class="sale-card"
      >

        <!-- TOP -->
        <div class="sale-top">

          <div>
            <h3>{{ o.product_title }}</h3>

            <p class="sale-date">
              {{ formatDate(o.ordered_at) }}
            </p>
          </div>

          <span
            class="sale-status"
            :class="o.status?.toLowerCase()"
          >
            {{ o.status }}
          </span>

        </div>

        <!-- BODY -->
        <div class="sale-body">

          <div class="sale-row">
            <span>Buyer</span>
            <strong>{{ o.buyer_name }}</strong>
          </div>

          <div class="sale-row">
            <span>Price</span>
            <strong>₱{{ Number(o.product_price).toLocaleString() }}</strong>
          </div>

          <div class="sale-row">
            <span>Payment</span>
            <strong>{{ o.payment_method }}</strong>
          </div>

          <div class="sale-row">
            <span>Pickup</span>
            <strong>{{ o.pickup_location || 'N/A' }}</strong>
          </div>

        </div>

        <!-- ACTIONS -->
        <div class="sale-actions">

          <button
            class="done-btn"
            @click="markDone(o)"
            v-if="o.status !== 'Completed'"
          >
            Mark Completed
          </button>

          <button
            class="msg-btn"
            @click="goMessage(o)"
          >
            Message Buyer
          </button>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const orders = ref([])
const loading = ref(true)

const user = JSON.parse(localStorage.getItem('user'))

const loadSales = async () => {

  try {

    const res = await api.getSellerOrders(user.user_id)

    orders.value = res.data || []

  } catch (err) {

    console.error(err)
    alert('Failed loading sales')

  } finally {

    loading.value = false
  }
}

const markDone = async (order) => {

  try {

    await api.updateOrderStatus(order.id, {
      status: 'Completed'
    })

    order.status = 'Completed'

    alert('Order marked completed ✅')

  } catch (err) {

    console.error(err)
    alert('Failed updating order')
  }
}

const goMessage = (order) => {

  router.push({
    path: '/messages',
    query: {
      user: order.buyer_id
    }
  })
}

const formatDate = (date) => {

  if (!date) return 'N/A'

  return new Date(date).toLocaleString()
}

onMounted(loadSales)
</script>

<style scoped>
.sales-page {
  padding: 2rem;
  max-width: 1200px;
  margin: auto;
}

.sales-header {
  margin-bottom: 2rem;
}

.sales-header h1 {
  font-size: 2rem;
  color: #003366;
  margin-bottom: 6px;
}

.sales-header p {
  color: #666;
}

.sales-loading,
.sales-empty {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  border: 1px solid #e5e7eb;
}

.sales-grid {
  display: grid;
  gap: 1rem;
}

.sale-card {
  background: white;
  border-radius: 18px;
  padding: 1.3rem;
  border: 1px solid #e5e7eb;
}

.sale-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.sale-top h3 {
  color: #003366;
  margin-bottom: 4px;
}

.sale-date {
  color: #777;
  font-size: 0.9rem;
}

.sale-status {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  height: fit-content;
}

.pending {
  background: #fff7ed;
  color: #c2410c;
}

.completed {
  background: #ecfdf5;
  color: #15803d;
}

.sale-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sale-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.sale-row span {
  color: #666;
}

.sale-actions {
  margin-top: 1.2rem;
  display: flex;
  gap: 10px;
}

.done-btn,
.msg-btn {
  border: none;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
}

.done-btn {
  background: #003366;
  color: white;
}

.msg-btn {
  background: #FFD700;
  color: #003366;
}
</style>