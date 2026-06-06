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
import { ChevronRight } from 'lucide-vue-next'

import { groupService } from '@/services/groupService'
import { useHapticFeedback } from 'vue-tg/latest'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
const { notificationOccurred } = useHapticFeedback()

const groups = ref<any[]>([])

const isLoading = ref(true)
let loadingTimeout: ReturnType<typeof setTimeout> | null = null

const startLoading = () => {
  loadingTimeout = setTimeout(() => {
    isLoading.value = true
  }, 200)
}

const stopLoading = () => {
  if (loadingTimeout) clearTimeout(loadingTimeout)
  isLoading.value = false
}

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
  startLoading()
  try {
    const data = await groupService.getGroups();
    groups.value = data?.items || []
  } catch (e: any) {
    if (e?.status !== 401) {
      notificationOccurred('error')
      toast.error(e.message || t('errors.unknown'))
    }
  } finally {
    stopLoading()
  }
}


const goToGroupDetails = (groupId: string) => {
  router.push(`/groups/${groupId}`)
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <div>
    <div class="max-w-2xl mx-auto space-y-6">
      <div class="text-center space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">{{ t('views.groups.title') }}</h1>
        <p class="text-muted-foreground">{{ t('views.groups.subtitle') }}</p>
      </div>

      <div v-if="isLoading" class="space-y-4">
        <Skeleton class="h-[88px] w-full rounded-xl" />
        <Skeleton class="h-[88px] w-full rounded-xl" />
        <Skeleton class="h-[88px] w-full rounded-xl" />
      </div>

      <div v-else-if="groups.length === 0"
        class="flex flex-col items-center justify-center py-12 text-center bg-muted/50 rounded-lg border border-border">
        <h2 class="text-xl font-semibold">{{ t('errors.noGroups') }}</h2>
        <p class="text-muted-foreground mt-2 max-w-sm">{{ t('errors.noGroupsDesc') }}</p>
      </div>

      <div v-else class="space-y-4">
        <Card v-for="group in paginatedGroups" :key="group.id"
          class="shadow-md cursor-pointer hover:bg-accent/50 transition-colors" @click="goToGroupDetails(group.id)">
          <CardHeader class="flex flex-row items-center justify-between">
            <div>
              <CardTitle class="text-xl">{{ group.group_name }}</CardTitle>
              <CardDescription class="mt-1">{{ t('views.groups.members', { count: group.group_members }) }}
              </CardDescription>
            </div>
            <ChevronRight class="w-6 h-6 text-muted-foreground" />
          </CardHeader>
        </Card>

        <div v-if="groups.length > itemsPerPage" class="flex justify-center mt-6">
          <Pagination v-slot="{ page }" :total="groups.length" :sibling-count="1" show-edges
            :items-per-page="itemsPerPage" v-model:page="currentPage">
            <PaginationContent v-slot="{ items }">
              <PaginationFirst />
              <PaginationPrevious />

              <template v-for="(item, index) in items" :key="index">
                <PaginationItem v-if="item.type === 'page'" :value="item.value" :is-active="item.value === page"
                  @click="currentPage = item.value">
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
