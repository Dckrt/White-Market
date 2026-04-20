<template>
  <div id="white-market-app">
    <!-- This is the ONLY Navbar tag that should exist in the whole project -->
    <Navbar v-if="showNavbar" />
    
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from '@/components/Navbar.vue';

const route = useRoute();
// Hide navbar on login (/auth) or startup (/)
const showNavbar = computed(() => route.path !== '/auth' && route.path !== '/');
</script>


<style>
/* 1. Global Reset & Theme Variables */
:root {
  --ateneo-blue: #003366;
  --ateneo-gold: #FFD700;
  --bg-soft: #f8fafc;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
}

/* 2. Organized Layout Wrapper */
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--bg-soft);
}

.main-content {
  flex: 1; /* Pushes footer down */
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  box-sizing: border-box;
}

/* Special centering for the Auth/Login card */
.main-content.auth-layout {
  max-width: 100%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--ateneo-blue) 0%, #001a33 100%);
}

/* 3. Smooth Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 4. Organized Footer */
.app-footer {
  text-align: center;
  padding: 2rem;
  background: white;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .main-content { padding: 1rem; }
}
</style>
