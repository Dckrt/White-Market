import { createRouter, createWebHistory } from 'vue-router'
import AuthPage      from '@/views/AuthPage.vue'
import HomeView      from '@/views/HomeView.vue'
import Marketplace   from '@/views/Marketplace.vue'
import Dashboard     from '@/views/Dashboard.vue'
import CartView      from '@/views/CartView.vue'
import Profile       from '@/views/Profile.vue'
import AddProduct    from '@/views/AddProduct.vue'
import ProductDetails from '@/views/ProductDetails.vue'
import MessagesPage  from '@/views/MessagesPage.vue'
import ProductView   from '@/views/ProductView.vue'
import AdminView     from '@/views/AdminView.vue'

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
  { path: '/messages',         name: 'Messages',       component: MessagesPage },
  { path: '/chat',             redirect: '/messages' },
  { path: '/admin',            name: 'Admin',          component: AdminView },
  { path: '/:pathMatch(.*)*',  redirect: '/' }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const protectedRoutes = ['Dashboard', 'Cart', 'Profile', 'AddProduct', 'Messages']
  const user = localStorage.getItem('user')
  if (protectedRoutes.includes(to.name) && !user) next('/auth')
  else next()
})

export default router