import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  actions: {
    login(credentials) {
      this.token = 'demo-token'
      this.user = { name: credentials.email, role: credentials.role }
      localStorage.setItem('token', this.token)
    },
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    }
  }
})