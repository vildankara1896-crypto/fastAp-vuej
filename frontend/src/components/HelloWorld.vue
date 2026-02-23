<script setup>
import { ref } from 'vue'
import axios from 'axios'

const message = ref("Veri yüklenmedi");

async function getMessage() {
  try {
    const response = await axios.get("http://127.0.0.1:8000/");
    console.log("Gelen veri:", response.data);
    message.value = response.data.message;
  } catch (error) {
    console.error("HATA:", error);
  }
}
</script>

