import { createApp } from 'vue'
import './style.css'
import 'vue-sonner/style.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { VueTelegramPlugin } from 'vue-tg'
import { setupApiClient } from '@/services/apiRuntime'
import { useColorMode } from '@vueuse/core'

setupApiClient()
useColorMode()

const app = createApp(App)
app.use(router)
app.use(VueTelegramPlugin)
app.mount('#app')
app.use(i18n)
