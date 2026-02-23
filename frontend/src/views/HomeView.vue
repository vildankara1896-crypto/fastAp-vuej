<template>
  <div class="dashboard-layout">
    
    <Transition name="toast">
      <div v-if="toast.gorunur" class="toast-notification" :class="toast.tip">
        <span class="toast-icon">{{ toast.tip === 'success' ? '✅' : '⚠️' }}</span>
        <span class="toast-message">{{ toast.mesaj }}</span>
      </div>
    </Transition>

    <header class="header-bar">
      <div class="brand-section">
        <span class="brand-icon">⚡</span>
        <h1 class="brand-title">Stok Takip Paneli</h1>
      </div>
      <div class="user-menu">
        <span class="user-name">👤 {{ aktifKullanici }}</span>
        <button @click="cikisYap" class="btn-logout">Çıkış Yap</button>
      </div>
    </header>

    <div class="content-wrapper">
      
      <div class="stats-container">
        <div class="stat-card blue-card">
          <div class="stat-icon">📦</div>
          <div class="stat-info">
            <h3>Toplam Ürün</h3>
            <p class="stat-value">{{ toplamUrunSayisi }} Adet</p>
          </div>
        </div>
        
        <div class="stat-card orange-card">
          <div class="stat-icon">🏷️</div>
          <div class="stat-info">
            <h3>Kategori</h3>
            <p class="stat-value">{{ toplamKategoriSayisi }} Çeşit</p>
          </div>
        </div>

        <div class="stat-card green-card">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <h3>Toplam Değer</h3>
            <p class="stat-value">{{ formatPrice(toplamStokDegeri) }} TL</p>
          </div>
        </div>

        <div class="stat-card purple-card">
          <div class="stat-icon">🏆</div>
          <div class="stat-info">
            <h3>En Değerli</h3>
            <p class="stat-value">{{ enPahaliUrun }}</p>
          </div>
        </div>
      </div>

      <div class="main-grid">
        
        <div class="pro-card form-card" :class="{ 'edit-mode-border': editModu }">
          <div class="card-header">
            <h2>{{ editModu ? '✏️ Ürünü Düzenle' : '✨ Yeni Ürün Ekle' }}</h2>
            <p>{{ editModu ? 'Bilgileri güncelleyip kaydedin.' : 'Envantere yeni ürün girişi yapın.' }}</p>
          </div>
          <div class="card-body">
            <div class="form-container">
              
              <div class="input-group">
                <label>Ürün Adı</label>
                <input v-model="formUrunAd" placeholder="Örn: Laptop" class="pro-input" />
              </div>

              <div class="input-group">
                <label>Kategori</label>
                <select v-model="formKategori" class="pro-input select-input">
                  <option disabled value="">Seçiniz</option>
                  <option value="Elektronik">Elektronik</option>
                  <option value="Giyim">Giyim</option>
                  <option value="Ev/Yaşam">Ev/Yaşam</option>
                  <option value="Kırtasiye">Kırtasiye</option>
                  <option value="Diğer">Diğer</option>
                </select>
              </div>

              <div class="input-group">
                <label>Fiyat (TL)</label>
                <input v-model="formUrunFiyat" type="number" placeholder="0" class="pro-input price-input" />
              </div>

              <div class="button-group">
                <button v-if="editModu" @click="editModunuIptalEt" class="pro-btn btn-cancel">İptal</button>
                <button @click="formuGönder" class="pro-btn btn-submit" :disabled="islemYapiliyor">
                  {{ islemYapiliyor ? '...' : (editModu ? 'Güncelle' : 'Ekle') }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="pro-card list-card">
          <div class="card-header list-header-row">
            <div><h2>📦 Ürün Listesi</h2></div>
            <div class="search-box">
              <input v-model="aramaMetni" placeholder="İsim veya kategori ara..." class="search-input" />
              <span class="search-icon">🔍</span>
            </div>
          </div>
          
          <div class="card-body no-padding">
            <div v-if="yukleniyor" class="status-message">Yükleniyor...</div>
            
            <div v-else-if="urunler.length === 0" class="status-message empty">
              Henüz ürün eklemediniz.
            </div>

            <div v-else-if="filtrelenmisUrunler.length === 0" class="status-message empty">
              Aradığınız kriterde ürün bulunamadı.
            </div>

            <ul v-else class="pro-list">
              <li v-for="urun in filtrelenmisUrunler" :key="urun.id" class="pro-list-item">
                <div class="item-visual">
                   <span class="category-badge" :class="getKategoriClass(urun.category)">
                      {{ urun.category ? urun.category.charAt(0) : 'D' }}
                   </span>
                </div>
                <div class="item-info">
                  <strong class="item-name">{{ urun.name }}</strong>
                  <span class="item-category-text">{{ urun.category }}</span>
                </div>
                <div class="item-actions">
                  <span class="item-price">{{ formatPrice(urun.price) }} TL</span>
                  <button @click="editModunuBaslat(urun)" class="btn-action btn-edit" title="Düzenle">✏️</button>
                  <button @click="urunSil(urun.id)" class="btn-action btn-delete" title="Sil">🗑️</button>
                </div>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router';

const router = useRouter();
const API_URL = "http://127.0.0.1:8000" 

// --- STATE ---
const urunler = ref([])
const formUrunAd = ref("")
const formUrunFiyat = ref(null)
const formKategori = ref("") 
const aramaMetni = ref("")
const duzenlenecekUrunId = ref(null)
const editModu = computed(() => duzenlenecekUrunId.value !== null)
const yukleniyor = ref(true)
const islemYapiliyor = ref(false)
const aktifKullanici = localStorage.getItem('userName') || 'Kullanıcı'

// --- TOAST ---
const toast = ref({ gorunur: false, mesaj: "", tip: "success" })
const bildirimGoster = (mesaj, tip = 'success') => {
  toast.value = { gorunur: true, mesaj: mesaj, tip: tip }
  setTimeout(() => { toast.value.gorunur = false }, 3000)
}

// --- COMPUTED (HESAPLAMALAR) ---
const filtrelenmisUrunler = computed(() => {
  if (!aramaMetni.value) return urunler.value;
  const arama = aramaMetni.value.toLowerCase();
  return urunler.value.filter(urun => 
    urun.name.toLowerCase().includes(arama) || 
    (urun.category && urun.category.toLowerCase().includes(arama))
  );
});

const toplamUrunSayisi = computed(() => urunler.value.length);

// YENİ: Toplam Benzersiz Kategori Sayısı
const toplamKategoriSayisi = computed(() => {
  // Ürünlerin kategorilerini al, boş olmayanları filtrele
  const kategoriler = urunler.value.map(u => u.category).filter(c => c);
  // 'Set' kullanarak sadece benzersiz olanları say (Örn: 3 tane 'Elektronik' varsa 1 sayar)
  return new Set(kategoriler).size;
});

const toplamStokDegeri = computed(() => urunler.value.reduce((toplam, urun) => toplam + (urun.price || 0), 0));

const enPahaliUrun = computed(() => {
  if (urunler.value.length === 0) return "-";
  const enPahali = [...urunler.value].sort((a, b) => b.price - a.price)[0];
  return enPahali.name;
});

// --- HELPER FUNCTIONS ---
const getAuthHeader = () => {
  const token = localStorage.getItem('userToken');
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
};

const formatPrice = (price) => {
    if (price === null || price === undefined) return "0";
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

const getKategoriClass = (kat) => {
    if(!kat) return 'cat-other';
    const map = {
        'Elektronik': 'cat-elec',
        'Giyim': 'cat-cloth',
        'Ev/Yaşam': 'cat-home',
        'Kırtasiye': 'cat-paper'
    }
    return map[kat] || 'cat-other';
}

const handleAuthError = (error) => {
    if (error.response && error.response.status === 401) {
        localStorage.removeItem('userToken');
        router.push('/login');
    }
};

const cikisYap = () => {
  localStorage.removeItem('userToken');
  localStorage.removeItem('userName');
  router.push('/login');
}

const editModunuBaslat = (urun) => {
  formUrunAd.value = urun.name
  formUrunFiyat.value = urun.price
  formKategori.value = urun.category || "" 
  duzenlenecekUrunId.value = urun.id
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

const editModunuIptalEt = () => {
  formUrunAd.value = ""
  formUrunFiyat.value = null
  formKategori.value = "" 
  duzenlenecekUrunId.value = null
}

const urunleriGetir = async () => {
  yukleniyor.value = true;
  try {
    const response = await axios.get(`${API_URL}/products`, getAuthHeader())
    urunler.value = response.data
  } catch (error) {
    handleAuthError(error);
  } finally {
    yukleniyor.value = false;
  }
}

const formuGönder = async () => {
  if (!formUrunAd.value.trim() || !formUrunFiyat.value || formUrunFiyat.value <= 0 || !formKategori.value) {
    bildirimGoster("Lütfen tüm alanları (Kategori dahil) doldurun!", "error")
    return
  }
  islemYapiliyor.value = true;
  
  const data = { 
      name: formUrunAd.value, 
      price: Number(formUrunFiyat.value),
      category: formKategori.value
  }

  try {
    if (editModu.value) {
      await axios.put(`${API_URL}/products/${duzenlenecekUrunId.value}`, data, getAuthHeader())
      bildirimGoster("Ürün güncellendi!", "success")
    } else {
      await axios.post(`${API_URL}/products`, data, getAuthHeader())
      bildirimGoster("Ürün eklendi!", "success")
    }
    editModunuIptalEt()
    urunleriGetir()
  } catch (error) { 
      handleAuthError(error);
      console.error(error); 
      bildirimGoster("Hata oluştu. Backend loglarını kontrol edin.", "error")
  } finally { 
      islemYapiliyor.value = false; 
  }
}

const urunSil = async (id) => {
  if (!confirm("Silmek istediğinize emin misiniz?")) return;
  try {
    await axios.delete(`${API_URL}/products/${id}`, getAuthHeader())
    if (duzenlenecekUrunId.value === id) editModunuIptalEt()
    urunleriGetir()
    bildirimGoster("Ürün silindi.", "success")
  } catch (error) { 
      handleAuthError(error);
      bildirimGoster("Silme işlemi başarısız.", "error")
  }
}

onMounted(() => {
  urunleriGetir()
})
</script>

<style scoped>
/* TOAST */
.toast-notification { position: fixed; top: 20px; right: 20px; background: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 12px; z-index: 9999; min-width: 300px; border-left: 5px solid; }
.toast-notification.success { border-left-color: #22c55e; }
.toast-notification.error { border-left-color: #ef4444; }
.toast-message { font-weight: 600; color: #334155; font-size: 0.95rem; }
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(-20px); }

/* LAYOUT */
.dashboard-layout { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; min-height: 100vh; display: flex; flex-direction: column; }
.header-bar { background: #fff; padding: 0.8rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100; }
.brand-section { display: flex; align-items: center; gap: 10px; }
.brand-title { font-size: 1.2rem; font-weight: 700; color: #1a1a1a; margin: 0; }
.user-menu { display: flex; align-items: center; gap: 15px; font-size: 0.9rem; }
.btn-logout { background: #fee2e2; color: #ef4444; border: none; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-weight: 600; }
.content-wrapper { max-width: 1100px; margin: 0 auto; width: 100%; padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }

/* STATS */
.stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.stat-card { background: #fff; border-radius: 12px; padding: 20px; display: flex; align-items: center; gap: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.05); transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-3px); }
.stat-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }

/* Renkler */
.blue-card .stat-icon { background: #e0f2fe; color: #0284c7; }
.green-card .stat-icon { background: #dcfce7; color: #16a34a; }
.purple-card .stat-icon { background: #f3e8ff; color: #9333ea; }
/* YENİ RENK */
.orange-card .stat-icon { background: #ffedd5; color: #f97316; }

.stat-info h3 { margin: 0; font-size: 0.9rem; color: #64748b; font-weight: 600; }
.stat-value { margin: 5px 0 0; font-size: 1.5rem; font-weight: 800; color: #0f172a; }

/* GRID */
.main-grid { display: grid; gap: 20px; }
.pro-card { background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.card-header h2 { margin: 0; font-size: 1.1rem; color: #1e293b; }
.card-header p { margin: 5px 0 0; font-size: 0.85rem; color: #64748b; }
.form-card { background: #fff; }
.edit-mode-border { border: 2px solid #f59e0b; }

/* FORM */
.form-container { padding: 1.5rem; display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 15px; align-items: end; }
.input-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 5px; }

/* YAZI RENGİ DÜZELTMESİ EKLENDİ */
.pro-input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; background: white; color: #1e293b; }
.pro-input option { color: #1e293b; background: white; }

.select-input { cursor: pointer; }
.pro-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.button-group { display: flex; gap: 10px; }
.pro-btn { height: 42px; padding: 0 20px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
.btn-submit { background: #3b82f6; color: white; }
.btn-submit:hover { background: #2563eb; }
.btn-submit:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-cancel { background: #e2e8f0; color: #475569; }

/* LIST */
.list-header-row { display: flex; justify-content: space-between; align-items: center; }
.search-box { position: relative; width: 250px; }
.search-input { width: 100%; padding: 8px 10px 8px 35px; border: 1px solid #cbd5e1; border-radius: 20px; font-size: 0.9rem; box-sizing: border-box; background: white; color: #1e293b; }
.search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.pro-list { list-style: none; padding: 0; margin: 0; }
.pro-list-item { display: flex; align-items: center; padding: 1rem 1.5rem; border-bottom: 1px solid #f1f5f9; gap: 15px; }
.pro-list-item:hover { background: #f8fafc; }

/* ITEM VISUALS (BADGES) */
.item-visual { display: flex; align-items: center; }
.category-badge { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; font-size: 1.1rem; }
.cat-elec { background-color: #3b82f6; } /* Mavi */
.cat-cloth { background-color: #eab308; } /* Sarı */
.cat-home { background-color: #10b981; } /* Yeşil */
.cat-paper { background-color: #f97316; } /* Turuncu */
.cat-other { background-color: #94a3b8; } /* Gri */

.item-info { flex: 1; }
.item-name { display: block; font-weight: 600; color: #334155; }
.item-category-text { font-size: 0.85rem; color: #64748b; }
.item-price { font-weight: 700; color: #16a34a; margin-right: 15px; }
.btn-action { border: none; background: transparent; cursor: pointer; font-size: 1.1rem; padding: 5px; border-radius: 4px; transition: background 0.2s; }
.btn-edit:hover { background: #fef3c7; }
.btn-delete:hover { background: #fee2e2; }
.status-message { padding: 2rem; text-align: center; color: #94a3b8; }

@media (max-width: 900px) { 
    .form-container { grid-template-columns: 1fr; gap: 10px; } 
    .button-group { width: 100%; } .pro-btn { width: 100%; }
    .list-header-row { flex-direction: column; align-items: flex-start; gap: 10px; }
    .search-box { width: 100%; }
}
</style>