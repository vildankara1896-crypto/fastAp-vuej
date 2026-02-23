<template>
  <div class="login-container">
    <h2 style="color: #42b883;">Giriş Yap</h2>
    
    <form @submit.prevent="girisYap" class="login-form">
      
      <div class="form-group">
        <label for="username">Kullanıcı Adı:</label>
        <input type="text" id="username" v-model="username" required placeholder="Kullanıcı adınızı girin">
      </div>
      
      <div class="form-group">
        <label for="password">Şifre:</label>
        <input type="password" id="password" v-model="password" required placeholder="Şifrenizi girin">
      </div>
      
      <button type="submit" class="submit-btn" :disabled="yukleniyor">
        {{ yukleniyor ? 'Giriş Yapılıyor...' : 'Giriş Yap' }}
      </button>

      <p v-if="hataMesaji" class="error-message">{{ hataMesaji }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// Değişkenler
const username = ref('');
const password = ref('');
const yukleniyor = ref(false);
const hataMesaji = ref('');

const router = useRouter();
const API_URL = "http://127.0.0.1:8000";

// --- Giriş Yap Fonksiyonu ---
const girisYap = async () => {
  hataMesaji.value = '';
  yukleniyor.value = true;

  try {
    // *** ÖNEMLİ FARK ***
    // Backend'deki /token endpoint'i JSON değil, form verisi bekler.
    // Bu yüzden verileri URLSearchParams ile paketliyoruz.
    const params = new URLSearchParams();
    params.append('username', username.value);
    params.append('password', password.value);

    // Backend'e POST isteği gönder (Form verisi olarak)
    // Axios, URLSearchParams nesnesini görünce otomatik olarak doğru başlığı (header) ayarlar.
    const response = await axios.post(`${API_URL}/token`, params);

    // --- BAŞARILI OLURSA ---
    console.log("Giriş başarılı. Token alındı:", response.data);
    
    // 1. Gelen Token'ı tarayıcının güvenli deposuna (localStorage) kaydet
    // Bu token'ı daha sonra ürün eklerken/silerken kullanacağız.
    const token = response.data.access_token;
    localStorage.setItem('userToken', token);
    localStorage.setItem('userName', username.value); // Kullanıcı adını da saklayalım (isteğe bağlı)

    alert("Giriş başarılı! Ana sayfaya yönlendiriliyorsunuz.");

    // 2. Formu temizle ve Ana Sayfaya yönlendir
    username.value = '';
    password.value = '';
    router.push('/'); // Ana sayfaya git

  } catch (error) {
    // --- HATA OLURSA ---
    console.error("Giriş hatası:", error);
    if (error.response && error.response.status === 401) {
      // 401 hatası: Kullanıcı adı veya şifre yanlış
      hataMesaji.value = "Kullanıcı adı veya şifre hatalı.";
    } else {
      hataMesaji.value = "Giriş yapılırken bir sorun oluştu. Lütfen tekrar deneyin.";
    }
  } finally {
    yukleniyor.value = false;
  }
};
</script>

<style scoped>
/* Tasarım RegisterView ile aynı tutuldu */
.login-container {
  text-align: left;
  padding: 20px 0;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}

.submit-btn {
  padding: 12px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-btn:hover {
  background-color: #3aa876;
}

.submit-btn:disabled {
  background-color: #a0d9c0;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 15px;
  font-size: 14px;
}
</style>