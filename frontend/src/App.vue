<template>
  <div id="white-market-app">
    <Navbar v-if="showNavbar" />
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const route = useRoute()

// Hide navbar on auth page and admin page (admin has its own header)
const showNavbar = computed(() =>
  route.path !== '/auth' && route.path !== '/admin'
)
</script>

<style>
:root {
  --ateneo-blue: #003366;
  --ateneo-gold: #FFD700;
  --bg-soft: #f8fafc;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', 'Plus Jakarta Sans', sans-serif;
  background: var(--bg-soft);
}

#white-market-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-content {
  flex: 1;
}
</style>