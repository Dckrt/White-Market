import { createRouter, createWebHistory } from 'vue-router'

// Lazy load all views
const AuthPage       = () => import('@/views/AuthPage.vue')
const HomeView       = () => import('@/views/HomeView.vue')
const Marketplace    = () => import('@/views/Marketplace.vue')
const ProductDetails = () => import('@/views/ProductDetails.vue')
const Dashboard      = () => import('@/views/Dashboard.vue')
const CartView       = () => import('@/views/CartView.vue')
const Profile        = () => import('@/views/Profile.vue')
const AddProduct     = () => import('@/views/AddProduct.vue')
const MessagesPage   = () => import('@/views/MessagesPage.vue')
const AdminView      = () => import('@/views/AdminView.vue')
const OrdersView     = () => import('@/views/OrdersView.vue')

const routes = [
  // ── Public ──────────────────────────────────────────────────────
  { path: '/auth', name: 'Auth', component: AuthPage },
  { path: '/',     name: 'Home', component: HomeView },

  // ── IMPORTANT: /products/:id MUST come BEFORE /products ─────────
  // If /products is first, Vue Router matches it and ignores /:id
  { path: '/products/:id', name: 'ProductDetails', component: ProductDetails, props: true },
  { path: '/products',     name: 'Marketplace',    component: Marketplace },

  // ── Protected ───────────────────────────────────────────────────
  { path: '/cart',        name: 'Cart',       component: CartView    },
  { path: '/profile',     name: 'Profile',    component: Profile     },
  { path: '/dashboard',   name: 'Dashboard',  component: Dashboard   },
  { path: '/add-product', name: 'AddProduct', component: AddProduct  },
  { path: '/messages',    name: 'Messages',   component: MessagesPage },
  { path: '/orders',      name: 'Orders',     component: OrdersView  },

  // ── Admin (no auth guard — dashboard agad) ───────────────────────
  { path: '/admin', name: 'Admin', component: AdminView },

  // ── Catch all ───────────────────────────────────────────────────
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // Scroll to top on every navigation
  scrollBehavior() {
    return { top: 0 }
  }
})

// Route guard — redirect to /auth if not logged in
const protectedRoutes = ['Cart', 'Profile', 'Dashboard', 'AddProduct', 'Messages', 'Orders']

router.beforeEach((to, from, next) => {
  const user = localStorage.getItem('user')
  if (protectedRoutes.includes(to.name) && !user) {
    next('/auth')
  } else {
    next()
  }
})

export default router