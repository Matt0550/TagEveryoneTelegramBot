<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Toaster } from '@/components/ui/sonner'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { LoginWidget } from 'vue-tg'
import type { LoginWidgetUser } from 'vue-tg'
import { client } from '@/api/client.gen'
import { setupApiClient, setCookie, getCookie, authenticateWithTma, authenticateWithTgl } from '@/services/apiRuntime'

const isAuthenticated = ref(false)
const isLoading = ref(true)
const botUsername = import.meta.env.VITE_BOT_USERNAME || 'TagEveryoneBot'

onMounted(async () => {
  // Check if we already have a JWT
  const existingToken = getCookie('auth_token')
  if (existingToken) {
    isAuthenticated.value = true
    setupApiClient()
  } else {
    // If we're inside Telegram, auto-authenticate
    const initData = window.Telegram?.WebApp?.initData
    if (initData) {
      const token = await authenticateWithTma(initData)
      if (token) {
        setCookie('auth_token', token, 7)
        setupApiClient()
        isAuthenticated.value = true
      }
    }
  }
  
  isLoading.value = false
  
  // Setup interceptor for global errors
  client.interceptors.response.use((response) => {
    if (response.status === 401) {
      isAuthenticated.value = false
      setCookie('auth_token', '', -1) // Clear invalid token
    }
    return response
  })
})

async function handleUserAuth(user: LoginWidgetUser) {
  isLoading.value = true
  const token = await authenticateWithTgl(user)
  if (token) {
    setCookie('auth_token', token, 7)
    setupApiClient()
    isAuthenticated.value = true
  } else {
    // Auth failed
    console.error("Authentication failed")
  }
  isLoading.value = false
}
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-50 font-sans p-4">
    <div v-if="isLoading" class="flex items-center justify-center min-h-[80vh]">
      <div class="w-12 h-12 border-4 border-zinc-700 border-t-zinc-300 rounded-full animate-spin"></div>
    </div>
    
    <template v-else>
      <template v-if="isAuthenticated">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </template>
      
      <template v-else>
        <div class="flex items-center justify-center min-h-[80vh]">
          <Card class="w-full max-w-sm bg-zinc-900 border-zinc-800 shadow-xl overflow-hidden">
            <div class="h-32 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 relative">
               <div class="absolute -bottom-10 left-1/2 -translate-x-1/2 w-20 h-20 bg-zinc-900 rounded-full border-4 border-zinc-900 flex items-center justify-center text-3xl shadow-lg">
                  🤖
               </div>
            </div>
            <CardHeader class="pt-14 text-center">
              <CardTitle class="text-2xl font-bold tracking-tight text-white">TagEveryone</CardTitle>
              <CardDescription class="text-zinc-400">Log in to manage your Telegram group mentions.</CardDescription>
            </CardHeader>
            <CardContent class="flex justify-center pb-8">
              <LoginWidget 
                :bot-username="botUsername"
                @auth="handleUserAuth"
                corner-radius="12"
                request-access="write"
              />
            </CardContent>
          </Card>
        </div>
      </template>
    </template>
    
    <Toaster />
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
