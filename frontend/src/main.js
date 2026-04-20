import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/styles.css'; // Deckert's styles

const app = createApp(App);
app.use(createPinia()); // Handles the 'Auth' store
app.use(router);        // Handles /products, /dashboard, etc.
app.mount('#app');
