<script setup lang="ts">
import { onMounted } from 'vue'
import { Toaster } from '@/components/ui/sonner'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { LoginWidget, BackButton, useMiniApp } from 'vue-tg'
import { useRouter, useRoute } from 'vue-router'
import { client } from '@/api/client.gen'
import { setCookie } from '@/services/apiRuntime'
import { useAuth } from '@/composables/useAuth'
import { useI18n } from 'vue-i18n'

import Navbar from '@/components/Navbar.vue'
import GlobalConfirmDialog from '@/components/GlobalConfirmDialog.vue'

const router = useRouter()
const route = useRoute()

const botUsername = import.meta.env.VITE_BOT_USERNAME || 'TagEveryoneBot'

const { isAuthenticated, isLoading, initAuth, loginWithWidget } = useAuth()
const { t } = useI18n()
const webApp = useMiniApp()

onMounted(async () => {
  await initAuth()

  // Setup interceptor for global errors
  client.interceptors.response.use((response) => {
    if (response.status === 401) {
      isAuthenticated.value = false
      setCookie('auth_token', '', -1) // Clear invalid token
    }
    return response
  })

  // Handle Telegram startapp parameter (tgWebAppStartParam)
  if (isAuthenticated.value && webApp.initDataUnsafe?.start_param) {
    if (route.path === '/') {
      router.push(`/groups/${webApp.initDataUnsafe.start_param}`)
    }
  }
})
</script>

<template>
  <div class="bg-background text-foreground min-h-screen">
    <BackButton v-if="route.path !== '/'" @click="router.back()" />
    <Navbar v-if="isAuthenticated" />

    <div class="px-3 pt-6 pb-10">
      <div v-if="isLoading" class="flex items-center justify-center min-h-[80vh]">
        <div class="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
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
            <Card class="w-full max-w-sm shadow-xl overflow-hidden">
              <div class="h-32 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 relative">
                <div
                  class="absolute -bottom-10 left-1/2 -translate-x-1/2 w-20 h-20 bg-card rounded-full border-4 border-background flex items-center justify-center text-3xl shadow-lg">
                  🤖
                </div>
              </div>
              <CardHeader class="pt-14 text-center">
                <CardTitle class="text-2xl font-bold tracking-tight">{{ t('nav.brand') }}</CardTitle>
                <CardDescription>{{ t('app.loginDesc') }}</CardDescription>
              </CardHeader>
              <CardContent class="flex justify-center pb-8">
                <LoginWidget :bot-username="botUsername" @auth="loginWithWidget" corner-radius="12"
                  request-access="write" />
              </CardContent>
            </Card>
          </div>
        </template>
      </template>
    </div>

    <Toaster />
    <GlobalConfirmDialog />
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
