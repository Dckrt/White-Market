import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({ items: [] }),
  actions: {
    addToCart(product) { this.items.push(product) },
    removeFromCart(id) { this.items = this.items.filter(p => p.id !== id) }
  }
})