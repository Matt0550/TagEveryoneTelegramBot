<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationFirst,
  PaginationItem,
  PaginationLast,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

import { groupService } from '@/services/groupService'
import { useHapticFeedback } from 'vue-tg/latest'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { MainButton } from 'vue-tg'
import { useI18n } from 'vue-i18n'
import type { GroupResponse } from '@/api'

const router = useRouter()
const { t } = useI18n()
const { showConfirmDialog } = useConfirmDialog()
const { notificationOccurred } = useHapticFeedback()

const isLoading = ref(true)
const groups = ref<GroupResponse[]>([])
const isOwner = ref(false)

const currentPage = ref(1)
const itemsPerPage = 5

const paginatedGroups = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return groups.value.slice(start, end)
})

watch(() => groups.value.length, () => {
  currentPage.value = 1
})

const loadGroups = async () => {
  isLoading.value = true
  try {
    const data = await groupService.getUserGroups();
    groups.value = data?.items || []
    isOwner.value = data?.isOwner || false
  } catch (e: any) {
    if (e?.status !== 401) {
      notificationOccurred('error')
      toast.error(e.message || t('errors.unknown'))
    }
  } finally {
    isLoading.value = false
  }
}

const leaveGroup = (groupId: Number) => {
  showConfirmDialog(
    t('views.groups.leaveGroupTitle'),
    t('views.groups.leaveGroupDesc'),
    async () => {
      try {
        const data = await groupService.leaveGroup(groupId)
        notificationOccurred('success')
        toast({ title: 'Success', description: (data as any)?.message || t('views.groups.leaveGroupSuccess') })
        await loadGroups() // reload groups
      } catch (e: any) {
        notificationOccurred('error')
        toast.error(e.message || t('errors.unknown'))
      }
    }
  )
}

const goToAdmin = () => {
  router.push('/admin')
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <div>
    <MainButton v-if="isOwner" :text="t('actions.adminPanel')" @click="goToAdmin" />

    <div v-if="isLoading" class="max-w-2xl mx-auto space-y-4">
      <Skeleton class="h-28 w-full rounded-xl" />
      <Skeleton class="h-28 w-full rounded-xl" />
      <Skeleton class="h-28 w-full rounded-xl" />
    </div>

  <div v-else class="max-w-2xl mx-auto space-y-6">
    <div class="text-center space-y-2">
      <h1 class="text-3xl font-bold tracking-tight">{{ t('views.groups.title') }}</h1>
      <p class="text-muted-foreground">{{ t('views.groups.subtitle') }}</p>
    </div>

    <div v-if="groups.length === 0"
      class="flex flex-col items-center justify-center py-12 text-center bg-muted/50 rounded-lg border border-border">
      <h2 class="text-xl font-semibold">{{ t('errors.noGroups') }}</h2>
      <p class="text-muted-foreground mt-2 max-w-sm">{{ t('errors.noGroupsDesc') }}</p>
    </div>

    <div v-else class="space-y-4">
      <Card v-for="group in paginatedGroups" :key="group.group_id" class="shadow-md">
        <CardHeader class="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle class="text-xl">{{ group.group_name }}</CardTitle>
            <CardDescription class="mt-1">{{ t('views.groups.members', { count: group.group_members }) }}</CardDescription>
          </div>
          <Button variant="destructive" @click="leaveGroup(group.group_id)">
            {{ t('actions.leaveList') }}
          </Button>
        </CardHeader>
      </Card>
      
      <div v-if="groups.length > itemsPerPage" class="flex justify-center mt-6">
        <Pagination v-slot="{ page }" :total="groups.length" :sibling-count="1" show-edges :items-per-page="itemsPerPage" v-model:page="currentPage">
          <PaginationContent v-slot="{ items }">
            <PaginationFirst />
            <PaginationPrevious />

            <template v-for="(item, index) in items" :key="index">
              <PaginationItem v-if="item.type === 'page'" :value="item.value" :is-active="item.value === page" @click="currentPage = item.value">
                {{ item.value }}
              </PaginationItem>
              <PaginationEllipsis v-else />
            </template>

            <PaginationNext />
            <PaginationLast />
          </PaginationContent>
        </Pagination>
      </div>
      </div>
    </div>
  </div>
</template>
