import { createRouter, createWebHistory } from 'vue-router';

import Home from './views/home.vue';
import Auth from './views/auth.vue';
import Dashboard from './views/dashboard.vue';
import Browse from './views/browse.vue';
import Cart from './views/cart.vue';
import Checkout from './views/checkout.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/auth', component: Auth },
  { path: '/dashboard', component: Dashboard },
  { path: '/browse', component: Browse },
  { path: '/cart', component: Cart },
  { path: '/checkout', component: Checkout }
];

export default createRouter({
  history: createWebHistory(),
  routes
});