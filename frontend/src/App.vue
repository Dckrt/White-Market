<template>
  <div id="wm-app">
    <Navbar v-if="showNavbar" />
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const route = useRoute()
// Admin and Auth have their own full-page layouts — hide navbar
const showNavbar = computed(() =>
  route.path !== '/auth' && route.path !== '/admin'
)
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
  background: #f4f7fb;
  color: #1a1a2e;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#wm-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

a { text-decoration: none; }
button { font-family: inherit; cursor: pointer; }
input, select, textarea { font-family: inherit; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #c5d5e8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #a0b8d0; }
</style>