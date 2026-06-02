<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, CardContent } from '@/components/ui/card'

import { toast } from 'vue-sonner'
import { adminService } from '@/services/adminService'
import { useHapticFeedback } from 'vue-tg/latest'
import { useI18n } from 'vue-i18n'

const { notificationOccurred } = useHapticFeedback()
const { t } = useI18n()

const logs = ref<any[]>([])
const isLoading = ref(true)

const loadAdminPanel = async () => {
  isLoading.value = true
  try {
    const data = await adminService.getWeeklyLogs()
    logs.value = data?.items || []
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || t('errors.unknown'))
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadAdminPanel()
})
</script>

<template>
  <div>
    <div v-if="isLoading" class="flex items-center justify-center h-64">
    <div class="animate-pulse flex flex-col items-center gap-4">
      <div class="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
      <p class="text-muted-foreground">{{ t('views.admin.loading') }}</p>
    </div>
  </div>

  <div v-else class="max-w-2xl mx-auto space-y-6">
    <div class="text-center space-y-2">
      <h1 class="text-3xl font-bold tracking-tight">{{ t('views.admin.title') }}</h1>
      <p class="text-muted-foreground">{{ t('views.admin.subtitle') }}</p>
      <p class="text-sm font-medium text-muted-foreground">{{ t('views.admin.logsFound', { count: logs.length }) }}</p>
    </div>

    <div v-if="logs.length === 0"
      class="flex flex-col items-center justify-center py-12 text-center bg-muted/50 rounded-lg border border-border">
      <h2 class="text-xl font-semibold">{{ t('errors.noLogs') }}</h2>
      <p class="text-muted-foreground mt-2">{{ t('errors.noLogsDesc') }}</p>
    </div>

    <div v-else class="space-y-3">
      <Card v-for="(log, index) in logs" :key="index" class="shadow-sm">
        <CardContent class="p-4 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-lg text-foreground">{{ log.action }}</span>
            <span class="text-xs text-muted-foreground">{{ log.datetime }}</span>
          </div>
          <p class="text-muted-foreground">{{ log.description }}</p>
          <div class="flex gap-4 text-xs text-muted-foreground">
            <span>{{ t('views.admin.userId') }}: {{ log.user_id }}</span>
            <span>{{ t('views.admin.chatId') }}: {{ log.group_id }}</span>
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  </div>
</template>
