import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/',             component: () => import('@/views/HomeView.vue') },
  { path: '/auth',         component: () => import('@/views/AuthPage.vue') },

  // ⚠️ IMPORTANT: /products/:id MUST come BEFORE /products
  { path: '/products/:id', component: () => import('@/views/ProductDetails.vue') },
  { path: '/products',     component: () => import('@/views/Marketplace.vue') },

  { path: '/dashboard',    component: () => import('@/views/Dashboard.vue'),   meta: { requiresAuth: true } },
  { path: '/add-product',  component: () => import('@/views/AddProduct.vue'),  meta: { requiresAuth: true } },
  { path: '/cart',         component: () => import('@/views/CartView.vue'),    meta: { requiresAuth: true } },
  { path: '/messages',     component: () => import('@/views/MessagesPage.vue'), meta: { requiresAuth: true } },
  { path: '/profile',      component: () => import('@/views/Profile.vue'),     meta: { requiresAuth: true } },
  { path: '/orders',       component: () => import('@/views/OrdersView.vue'),  meta: { requiresAuth: true } },
  { path: '/notifications', component: () => import('@/views/NotificationsPage.vue'), meta: { requiresAuth: true } },
  { path: '/admin',        component: () => import('@/views/AdminView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    auth.loadFromStorage()
    if (!auth.user) return next('/auth')
  }
  next()
})

export default router