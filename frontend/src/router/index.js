import { createRouter, createWebHistory } from 'vue-router'
import AuthPage from '@/views/AuthPage.vue'
import HomeView from '@/views/HomeView.vue'
import Marketplace from '@/views/Marketplace.vue'
import Dashboard from '@/views/Dashboard.vue'
import CartView from '@/views/CartView.vue'
import Profile from '@/views/Profile.vue'
import AddProduct from '@/views/AddProduct.vue'
import ProductDetails from '@/views/ProductDetails.vue'
import MessagesPage from '@/views/MessagesPage.vue'
import ProductView from '@/views/ProductView.vue'

const routes = [
  { path: '/auth',             name: 'Auth',           component: AuthPage },
  { path: '/',                 name: 'Home',           component: HomeView },
  { path: '/products',         name: 'Products',       component: Marketplace },
  { path: '/products/:id',     name: 'ProductDetails', component: ProductDetails, props: true },
  { path: '/product-view/:id', name: 'ProductView',    component: ProductView },
  { path: '/cart',             name: 'Cart',           component: CartView },
  { path: '/profile',          name: 'Profile',        component: Profile },
  { path: '/dashboard',        name: 'Dashboard',      component: Dashboard },
  { path: '/add-product',      name: 'AddProduct',     component: AddProduct },
  { path: '/chat',             name: 'Chat',           component: MessagesPage },
  { path: '/messages',         redirect: '/chat' },
  { path: '/:pathMatch(.*)*',  redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router