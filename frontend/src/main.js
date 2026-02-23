// frontend/src/main.js (GÜNCELLENMİŞ HALİ)

import { createApp } from 'vue'
import './style.css' // Eğer varsa varsayılan stiller
import App from './App.vue'
import router from './router' // <-- Adım 2'de oluşturduğumuz router'ı içe aktar

const app = createApp(App)

app.use(router) // <-- Uygulamaya router'ı kullanmasını söyle
app.mount('#app')
