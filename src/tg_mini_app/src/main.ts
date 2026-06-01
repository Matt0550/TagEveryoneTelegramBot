import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { VueTelegramPlugin } from 'vue-tg'
import { setupApiClient } from '@/services/apiRuntime'

setupApiClient()

const app = createApp(App)
app.use(router)
app.use(VueTelegramPlugin)
app.mount('#app')
