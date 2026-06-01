<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

import { groupService } from '@/services/groupService'
import { useMainButton, usePopup, useHapticFeedback } from 'vue-tg/latest'
import type { GroupResponse } from '@/api'

const router = useRouter()
const { showAlert, showConfirm } = usePopup()
const { notificationOccurred } = useHapticFeedback()
const mainButton = useMainButton()

const isLoading = ref(true)
const groups = ref<GroupResponse[]>([])
const isOwner = ref(false)

const loadGroups = async () => {
  isLoading.value = true
  try {
    const data = await groupService.getUserGroups();
    groups.value = data?.items || []
    isOwner.value = data?.isOwner || false

    if (isOwner.value) {
      mainButton.setParams({ text: 'Admin Panel' })
      mainButton.show()
    }
  } catch (e: any) {
    if (e?.status !== 401) {
      notificationOccurred('error')
      showAlert(`Error: ${e.message || 'Unknown error'}`)
    }
  } finally {
    isLoading.value = false
  }
}

const leaveGroup = (groupId: Number) => {
  showConfirm("Are you sure you want to leave this list? You can rejoin at any time with /in command.", async (result: boolean) => {
    if (result) {
      try {
        const data = await groupService.leaveGroup(groupId)
        notificationOccurred('success')
        toast({ title: 'Success', description: (data as any)?.message || 'Successfully left group' })
        await loadGroups() // reload groups
      } catch (e: any) {
        notificationOccurred('error')
        showAlert(`Error: ${e.message || 'Unknown error'}`)
      }
    }
  })
}

const goToAdmin = () => {
  router.push('/admin')
}

let offClick: { off: () => void }

onMounted(() => {
  offClick = mainButton.onClick(goToAdmin)
  loadGroups()
})

onUnmounted(() => {
  if (offClick) offClick.off()
  mainButton.hide()
})
</script>

<template>
  <div v-if="isLoading" class="flex items-center justify-center h-64">
    <div class="animate-pulse flex flex-col items-center gap-4">
      <div class="w-12 h-12 border-4 border-zinc-700 border-t-zinc-300 rounded-full animate-spin"></div>
      <p class="text-zinc-400">Loading...</p>
    </div>
  </div>

  <div v-else class="max-w-2xl mx-auto space-y-6">
    <div class="text-center space-y-2">
      <h1 class="text-3xl font-bold tracking-tight">Groups</h1>
      <p class="text-zinc-400">Groups you are part of in the tag list</p>
    </div>

    <div v-if="groups.length === 0"
      class="flex flex-col items-center justify-center py-12 text-center bg-zinc-900/50 rounded-lg border border-zinc-800">
      <h2 class="text-xl font-semibold">No groups</h2>
      <p class="text-zinc-400 mt-2 max-w-sm">You are not included in any tag list. To join a group, use the <span
          class="font-bold text-white">/in</span> command.</p>
    </div>

    <div v-else class="space-y-4">
      <Card v-for="group in groups" :key="group.group_id" class="bg-zinc-900 border-zinc-800">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle class="text-xl">{{ group.group_name }}</CardTitle>
            <CardDescription class="text-zinc-400 mt-1">{{ group.group_members }} members</CardDescription>
          </div>
          <Button variant="destructive" @click="leaveGroup(group.group_id)">
            Leave list
          </Button>
        </CardHeader>
      </Card>
    </div>
  </div>
</template>
