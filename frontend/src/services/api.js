import axios from 'axios'

// ── BASE URL ───────────────────────────────────────────────────────────────
// LOCAL:  leave VITE_API_URL unset → uses localhost:5000
// DEPLOY: set VITE_API_URL=https://your-app.onrender.com/api in Vercel env vars
const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

const api = axios.create({ baseURL: BASE })

export default {
  // Auth
  register:      (data) => api.post('/register', data),
  login:         (data) => api.post('/login', data),
  googleAuth:    (data) => api.post('/auth/google', data),
  uploadProfilePic: (uid, fd) => api.post(`/users/${uid}/profile-pic`, fd),

  // Stats
  getStats: () => api.get('/stats'),

  // Products
  getProducts:    (params) => api.get('/products', { params }),
  getProduct:     (id)     => api.get(`/products/${id}`),
  getMyProducts:  (sid)    => api.get('/products', { params: { seller_id: sid } }),
  createProduct:  (fd)     => api.post('/products', fd),
  updateProduct:  (id, data) => api.put(`/products/${id}`, data),
  updateProductWithImage: (id, fd) => api.put(`/products/${id}`, fd),
  deleteProduct:  (id, uid) => api.delete(`/products/${id}`, { params: { user_id: uid } }),
  getPriceHistory: (id)    => api.get(`/products/${id}/price-history`),
  getTags:         ()      => api.get('/tags'),
  compareByTag:    (tag)   => api.get('/products/compare', { params: { tag } }),

  // Cart
  getCart:       (uid)   => api.get('/cart', { params: { user_id: uid } }),
  addToCart:     (data)  => api.post('/cart', data),
  removeFromCart:(id)    => api.delete(`/cart/${id}`),

  // Checkout & Orders
  checkout:        (data) => api.post('/checkout', data),
  getOrders:       (uid)  => api.get('/orders', { params: { buyer_id: uid } }),
  getSellerOrders: (uid)  => api.get('/orders/seller', { params: { seller_id: uid } }),

  // Messages
  sendMessage:       (data)  => api.post('/messages', data),
  getMessages:       (s, r)  => api.get('/messages', { params: { sender_id: s, receiver_id: r } }),
  getThreads:        (uid)   => api.get('/messages/threads', { params: { user_id: uid } }),
  markMessagesRead:  (data)  => api.post('/messages/mark-read', data),
  getUnreadCount:    (uid)   => api.get('/messages/unread-count', { params: { user_id: uid } }),

  // Notifications
  getNotifications:     (uid) => api.get('/notifications', { params: { user_id: uid } }),
  markNotificationsRead:(uid) => api.post('/notifications/read', { user_id: uid }),

  // Payment
  getSellerPayment:  (uid)  => api.get(`/users/${uid}/payment`),
  updatePayment:     (uid, data) => api.put(`/users/${uid}/payment`, data),

  // Admin
  adminLogin:         (pw)   => api.post('/admin/login', { password: pw }),
  adminStats:         ()     => api.get('/admin/stats'),
  adminUsers:         ()     => api.get('/admin/users'),
  adminCreateUser:    (data) => api.post('/admin/users', data),
  adminUpdateUser:    (id, data) => api.put(`/admin/users/${id}`, data),
  adminDeleteUser:    (id)   => api.delete(`/admin/users/${id}`),
  adminProducts:      ()     => api.get('/admin/products'),
  adminCreateProduct: (data) => api.post('/admin/products', data),
  adminDeleteProduct: (id)   => api.delete(`/admin/products/${id}`),
  adminOrders:        ()     => api.get('/admin/orders'),
  adminMessages:      ()     => api.get('/admin/messages'),
}