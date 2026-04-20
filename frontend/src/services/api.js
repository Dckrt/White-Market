import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.request.use((config) => {
  try {
    const user = JSON.parse(localStorage.getItem('user'))
    if (user && user.user_id) config.headers['X-User-ID'] = user.user_id
  } catch (e) {
    console.warn('Invalid user in localStorage')
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API Error:', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export default {
  // AUTH
  register: (data) => apiClient.post('/register', data),
  login:    (data) => apiClient.post('/login', data),

  // PRODUCTS
  getProducts:          (params = {}) => apiClient.get('/products', { params }),
  getMyProducts:        (userId)      => apiClient.get('/products', { params: { seller_id: userId } }),
  getProduct:           (id)          => apiClient.get(`/products/${id}`),
  createProduct:        (data)        => apiClient.post('/products', data),
  updateProduct:        (id, data)    => apiClient.put(`/products/${id}`, data),
  updateProductWithImage: (id, formData) => apiClient.put(`/products/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteProduct: (id, userId) => apiClient.delete(`/products/${id}`, { params: { user_id: userId } }),

  // CART
  addToCart:      (data)   => apiClient.post('/cart', data),
  getCart:        (userId) => apiClient.get('/cart', { params: { user_id: userId } }),
  removeFromCart: (id)     => apiClient.delete(`/cart/${id}`),

  // CHECKOUT
  checkout: (data) => apiClient.post('/checkout', data),

  // SELLER PAYMENT INFO
  // Returns { gcash: '09XXXXXXXXX', bank: 'BDO - 0000000000' } or nulls if not set
  getSellerPayment: (sellerId) => apiClient.get(`/users/${sellerId}/payment`),

  // MESSAGES
  sendMessage:   (data)                => apiClient.post('/messages', data),
  getMessages:   (userId, partnerId)   => apiClient.get('/messages', {
    params: { sender_id: Number(userId), receiver_id: Number(partnerId) }
  }),
  getThreads:    (userId) => apiClient.get('/messages/threads', { params: { user_id: userId } }),
  getUnreadCount:(userId) => apiClient.get('/messages/unread-count', { params: { user_id: userId } }),

  // NOTIFICATIONS
  getNotifications:      (userId) => apiClient.get('/notifications', { params: { user_id: userId } }),
  markNotificationsRead: (userId) => apiClient.post('/notifications/read', { user_id: userId }),

  // REVIEWS
  addReview: (data) => apiClient.post('/reviews', data),
}