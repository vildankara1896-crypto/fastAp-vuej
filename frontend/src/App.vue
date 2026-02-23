<template>
  <div class="app-container">
    <div class="main-card">
      <header class="app-header">
        <div class="logo-area">
            <img src="./assets/vue.svg" alt="Vue Logo" class="logo" />
            <h1 class="app-title">FastAPI <span class="vue-green">+ Vue.js</span></h1>
        </div>
        <p class="app-subtitle">Full Stack Entegrasyon Projesi</p>
      </header>

      <nav class="nav-menu">
        <router-link to="/" class="nav-link">Ana Sayfa</router-link>
        <template v-if="!girisYapildiMi">
          <router-link to="/login" class="nav-link">Giriş Yap</router-link>
          <router-link to="/register" class="nav-link">Kayıt Ol</router-link>
        </template>
        <template v-else>
          <a href="#" @click.prevent="cikisYap" class="nav-link logout-link">Çıkış Yap</a>
        </template>
      </nav>

      <main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
// Kullanıcının giriş durumunu tutan değişken
const girisYapildiMi = ref(false);

// Giriş durumunu localStorage'daki token'a göre kontrol et
const girisDurumunuKontrolEt = () => {
  // Token varsa true, yoksa false döner
  girisYapildiMi.value = !!localStorage.getItem('userToken');
};

// Çıkış yapma fonksiyonu
const cikisYap = () => {
  if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
    // Token ve kullanıcı adını sil
    localStorage.removeItem('userToken');
    localStorage.removeItem('userName');
    // Durumu güncelle
    girisDurumunuKontrolEt();
    // Giriş sayfasına yönlendir
    router.push('/login');
  }
};

// Sayfa ilk yüklendiğinde kontrol et
onMounted(() => {
  girisDurumunuKontrolEt();
});

// Rota değiştiğinde (örn: giriş yaptıktan sonra) kontrol et
watch(route, () => {
   girisDurumunuKontrolEt();
});
</script>

<style>
/* --- GLOBAL CSS DEĞİŞKENLERİ --- */
:root {
    --primary: #42b883;
    --primary-dark: #33a06f;
    --secondary: #35495e;
    --text-dark: #2c3e50;
    --text-light: #94a3b8;
    --bg-light: #f8fafc;
    --white: #ffffff;
    --danger: #e74c3c;
    --shadow-md: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --radius-lg: 16px;
    --radius-md: 8px;
}

/* Modern Font İçe Aktarma */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Genel Sayfa Stili */
body {
  margin: 0;
  font-family: 'Plus Jakarta Sans', Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  /* Arka plan gradyanı */
  background: linear-gradient(135deg, #f0f2f5 0%, #e6efff 100%);
  color: var(--text-dark);
}

/* Ortalamayı sağlayan dış kapsayıcı */
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh; /* Tam ekran yüksekliği */
  padding: 20px;
  box-sizing: border-box;
}

/* Ortadaki beyaz kart */
.main-card {
  background-color: var(--white);
  width: 100%;
  max-width: 600px; /* Maksimum genişlik */
  padding: 40px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  text-align: center; /* İçeriği ortala */
}

/* --- BAŞLIK ALANI --- */
.app-header { margin-bottom: 30px; }
.logo-area { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 5px; }
.logo { height: 32px; }
.app-title { margin: 0; font-size: 26px; font-weight: 800; color: var(--secondary); letter-spacing: -0.5px; }
.vue-green { color: var(--primary); }
.app-subtitle { margin: 5px 0 0; color: var(--text-light); font-size: 15px; font-weight: 500; }

/* --- NAVİGASYON MENÜSÜ (DÜZELTİLDİ) --- */
.nav-menu {
  display: inline-flex; /* İçindekiler kadar genişle */
  align-items: center;
  background-color: var(--bg-light);
  padding: 5px;
  border-radius: 12px;
  margin-bottom: 35px;
  /* KRİTİK DÜZELTME: Linkler arasına 10px boşluk ekler */
  gap: 10px;
}

/* Navigasyon Linkleri (Hap Görünümü) */
.nav-link {
  text-decoration: none;
  color: var(--text-light);
  font-weight: 600;
  padding: 10px 20px; /* Hap şekli için dolgu */
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  font-size: 14px;
  white-space: nowrap; /* Metnin alt satıra kaymasını önle */
}

.nav-link:hover { color: var(--primary); background-color: rgba(66, 184, 131, 0.05); }

/* Aktif sayfa linki stili */
.router-link-active {
  color: var(--primary-dark) !important;
  background-color: var(--white) !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Çıkış yap butonu için özel hover stili */
.logout-link:hover { color: var(--danger) !important; background-color: rgba(231, 76, 60, 0.05) !important; }

/* --- İÇERİK ALANI & ANİMASYON --- */
.content-area { text-align: left; min-height: 200px; }

/* Sayfa geçiş animasyonu (Yumuşak kayma ve solma) */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(10px); opacity: 0; }
</style>