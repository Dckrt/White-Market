import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)

  function loadFromStorage() {
    try {
      const raw = localStorage.getItem('user')
      if (raw) user.value = JSON.parse(raw)
    } catch { user.value = null }
  }

  function setUser(data) {
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
  }

  function logout() {
    user.value = null
    localStorage.removeItem('user')
  }

  return { user, loadFromStorage, setUser, logout }
})