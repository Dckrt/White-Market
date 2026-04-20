// ============================================================
// FILE 1: frontend/src/services/api.js
// ============================================================
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.request.use((config) => {
  try {
    const user = JSON.parse(localStorage.getItem('user'))
    if (user?.user_id) config.headers['X-User-ID'] = user.user_id
  } catch {}
  return config
})

apiClient.interceptors.response.use(
  res => res,
  err => { console.error('API Error:', err.response?.data || err.message); return Promise.reject(err) }
)

export default {
  // AUTH
  register: (data) => apiClient.post('/register', data),
  login:    (data) => apiClient.post('/login', data),

  // PRODUCTS
  getProducts:            (params = {}) => apiClient.get('/products', { params }),
  getMyProducts:          (userId)      => apiClient.get('/products', { params: { seller_id: userId } }),
  getProduct:             (id)          => apiClient.get(`/products/${id}`),
  createProduct:          (data)        => data instanceof FormData
    ? apiClient.post('/products', data, { headers: { 'Content-Type': 'multipart/form-data' } })
    : apiClient.post('/products', data),
  updateProduct:          (id, data)    => apiClient.put(`/products/${id}`, data),
  updateProductWithImage: (id, fd)      => apiClient.put(`/products/${id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteProduct:          (id, userId)  => apiClient.delete(`/products/${id}`, { params: { user_id: userId } }),

  // CART
  addToCart:      (data)   => apiClient.post('/cart', data),
  getCart:        (userId) => apiClient.get('/cart', { params: { user_id: userId } }),
  removeFromCart: (id)     => apiClient.delete(`/cart/${id}`),

  // CHECKOUT
  checkout: (data) => apiClient.post('/checkout', data),

  // SELLER PAYMENT
  getSellerPayment:    (sellerId) => apiClient.get(`/users/${sellerId}/payment`),
  updateSellerPayment: (id, data) => apiClient.put(`/users/${id}/payment`, data),

  // MESSAGES
  sendMessage:      (data)           => apiClient.post('/messages', data),
  getMessages:      (uid, pid)       => apiClient.get('/messages', { params: { sender_id: Number(uid), receiver_id: Number(pid) } }),
  getThreads:       (userId)         => apiClient.get('/messages/threads', { params: { user_id: userId } }),
  getUnreadCount:   (userId)         => apiClient.get('/messages/unread-count', { params: { user_id: userId } }),
  markMessagesRead: (data)           => apiClient.post('/messages/mark-read', data).catch(() => {}),

  // NOTIFICATIONS
  getNotifications:      (userId) => apiClient.get('/notifications', { params: { user_id: userId } }),
  markNotificationsRead: (userId) => apiClient.post('/notifications/read', { user_id: userId }),

  // ADMIN
  adminLogin:         (password) => apiClient.post('/admin/login', { password }),
  adminStats:         ()         => apiClient.get('/admin/stats'),
  adminProducts:      ()         => apiClient.get('/admin/products'),
  adminUsers:         ()         => apiClient.get('/admin/users'),
  adminMessages:      ()         => apiClient.get('/admin/messages'),
  adminDeleteProduct: (id)       => apiClient.delete(`/admin/products/${id}`),
  adminDeleteUser:    (id)       => apiClient.delete(`/admin/users/${id}`),
}