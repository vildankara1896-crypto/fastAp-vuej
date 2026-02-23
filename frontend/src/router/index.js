// frontend/src/router/index.js (GÜNCELLENMİŞ HALİ)

import { createRouter, createWebHistory } from 'vue-router'
// Oluşturduğumuz sayfa bileşenlerini içe aktaralım
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const routes = [
  {
    path: '/', // Ana sayfa adresi (http://localhost:5173/)
    name: 'home',
    component: HomeView // Bu adrese gidince HomeView.vue'yu göster
  },
  {
    path: '/login', // Giriş sayfası adresi
    name: 'login',
    component: LoginView // Bu adrese gidince LoginView.vue'yu göster
  },
  {
    path: '/register', // Kayıt sayfası adresi
    name: 'register',
    component: RegisterView // Bu adrese gidince RegisterView.vue'yu göster
  }
]

const router = createRouter({
  history: createWebHistory(), // Tarayıcı geçmişini yönet
  routes // Yukarıdaki rota listesini kullan
})

export default router