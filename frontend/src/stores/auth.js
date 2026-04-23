import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)

  const loadFromStorage = () => {
    try {
      const saved = localStorage.getItem('user')
      if (saved) user.value = JSON.parse(saved)
    } catch {}
  }

  const setUser = (u) => {
    user.value = u
    if (u) localStorage.setItem('user', JSON.stringify(u))
    else localStorage.removeItem('user')
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('user')
  }

  return { user, setUser, loadFromStorage, logout }
})