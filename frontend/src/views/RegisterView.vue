<template>
  <div class="register-container">
    <h2 style="color: #42b883;">Kayıt Ol</h2>
    
    <form @submit.prevent="kayitOl" class="register-form">
      
      <div class="form-group">
        <label for="username">Kullanıcı Adı:</label>
        <input type="text" id="username" v-model="username" required placeholder="Kullanıcı adınızı girin">
      </div>
      
      <div class="form-group">
        <label for="password">Şifre:</label>
        <input type="password" id="password" v-model="password" required placeholder="Şifrenizi girin">
      </div>
      
      <button type="submit" class="submit-btn" :disabled="yukleniyor">
        {{ yukleniyor ? 'Kaydediliyor...' : 'Kayıt Ol' }}
      </button>

      <p v-if="hataMesaji" class="error-message">{{ hataMesaji }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // Sayfa yönlendirmesi için

// Form verilerini tutacak değişkenler
const username = ref('');
const password = ref('');
// İşlem durumunu ve hataları takip edecek değişkenler
const yukleniyor = ref(false);
const hataMesaji = ref('');

// Router'ı kullanmak için (Başarılı kayıttan sonra yönlendirme için)
const router = useRouter();
// Backend API adresi (sabit)
const API_URL = "http://127.0.0.1:8000";

// --- Kayıt Ol Fonksiyonu (Backend'e İstek Atar) ---
const kayitOl = async () => {
  // Her işlem öncesi hata mesajını temizle ve yükleniyor durumunu başlat
  hataMesaji.value = '';
  yukleniyor.value = true;

  try {
    // Backend'e gönderilecek veri paketi
    const gonderilecekVeri = {
      username: username.value,
      password: password.value
    };

    // Backend'in /register endpoint'ine POST isteği gönder
    const response = await axios.post(`${API_URL}/register`, gonderilecekVeri);

    // --- BAŞARILI OLURSA ---
    console.log("Kayıt başarılı:", response.data);
    alert("Kayıt işlemi başarılı! Giriş sayfasına yönlendiriliyorsunuz.");
    
    // Formu temizle
    username.value = '';
    password.value = '';
    
    // Kullanıcıyı otomatik olarak 'Giriş Yap' sayfasına yönlendir
    router.push('/login');

  } catch (error) {
    // --- HATA OLURSA ---
    console.error("Kayıt hatası:", error);
    // Backend'den gelen özel bir hata mesajı varsa onu göster, yoksa genel mesajı
    if (error.response && error.response.data && error.response.data.detail) {
      hataMesaji.value = error.response.data.detail; // Örn: "Kullanıcı adı zaten alınmış"
    } else {
      hataMesaji.value = "Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.";
    }
  } finally {
    // İşlem bitti (başarılı veya hatalı), yükleniyor durumunu kapat
    yukleniyor.value = false;
  }
};
</script>

<style scoped>
/* --- Form Tasarımı --- */
.register-container {
  text-align: left;
  padding: 20px 0;
}

.register-form {
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
  box-sizing: border-box; /* Padding'in genişliği etkilememesi için */
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