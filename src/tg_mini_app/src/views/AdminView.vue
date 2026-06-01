<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, CardContent } from '@/components/ui/card'

import { adminService } from '@/services/adminService'
import { useBackButton, usePopup, useHapticFeedback } from 'vue-tg/latest'

const router = useRouter()
const { showAlert } = usePopup()
const { notificationOccurred } = useHapticFeedback()
const backButton = useBackButton()

const logs = ref<any[]>([])
const isLoading = ref(true)

const loadAdminPanel = async () => {
  isLoading.value = true
  try {
    const data = await adminService.getWeeklyLogs()
    logs.value = data?.logs || []
  } catch (e: any) {
    notificationOccurred('error')
    showAlert(`Error: ${e.message || 'Unknown error'}`)
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.back()
}

let offClick: { off: () => void }

onMounted(() => {
  backButton.show()
  offClick = backButton.onClick(goBack)
  loadAdminPanel()
})

onUnmounted(() => {
  if (offClick) offClick.off()
  backButton.hide()
})
</script>

<template>
  <div v-if="isLoading" class="flex items-center justify-center h-64">
    <div class="animate-pulse flex flex-col items-center gap-4">
      <div class="w-12 h-12 border-4 border-zinc-700 border-t-zinc-300 rounded-full animate-spin"></div>
      <p class="text-zinc-400">Loading Admin Panel...</p>
    </div>
  </div>

  <div v-else class="max-w-2xl mx-auto space-y-6">
    <div class="text-center space-y-2">
      <h1 class="text-3xl font-bold tracking-tight">Logs</h1>
      <p class="text-zinc-400">Logs of the last 7 days</p>
      <p class="text-sm font-medium text-zinc-500">{{ logs.length }} logs found</p>
    </div>

    <div v-if="logs.length === 0"
      class="flex flex-col items-center justify-center py-12 text-center bg-zinc-900/50 rounded-lg border border-zinc-800">
      <h2 class="text-xl font-semibold">No logs</h2>
      <p class="text-zinc-400 mt-2">No activity recorded.</p>
    </div>

    <div v-else class="space-y-3">
      <Card v-for="(log, index) in logs" :key="index" class="bg-zinc-900 border-zinc-800">
        <CardContent class="p-4 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-lg text-zinc-100">{{ log.action }}</span>
            <span class="text-xs text-zinc-500">{{ log.datetime }}</span>
          </div>
          <p class="text-zinc-300">{{ log.description }}</p>
          <div class="flex gap-4 text-xs text-zinc-500">
            <span>User ID: {{ log.user_id }}</span>
            <span>Chat ID: {{ log.group_id }}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
