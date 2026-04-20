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
// Admin has its own sidebar header; Auth has its own full-page layout
const showNavbar = computed(() => route.path !== '/auth' && route.path !== '/admin')
</script>

<style>
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Inter', 'Plus Jakarta Sans', system-ui, sans-serif; background: #f4f7fb; -webkit-font-smoothing: antialiased; }
#wm-app { display: flex; flex-direction: column; min-height: 100vh; }
</style>