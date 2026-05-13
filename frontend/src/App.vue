<template>
  <div>
    <Navbar v-if="showNav" />
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const route   = useRoute()
const showNav = computed(() => route.path !== '/admin')
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f4f7fb;
  color: #1a1a2e;
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c8d8ea; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #003366; }

a { text-decoration: none; color: inherit; }
button, input, select, textarea { font-family: inherit; }
</style>