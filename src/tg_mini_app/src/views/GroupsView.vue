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
import { listService } from '@/services/listService'

export interface TagListWithSubscription {
  id: number;
  group_id: number;
  name: string;
  trigger_name: string;
  is_system: boolean;
  is_subscribed: boolean;
}

const router = useRouter()
const { t } = useI18n()
const { showConfirmDialog } = useConfirmDialog()
const { notificationOccurred } = useHapticFeedback()

const isLoading = ref(true)
const groups = ref<GroupResponse[]>([])
const newListState = ref<Record<number, { name: string, trigger_name: string, description: string, show: boolean }>>({})
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



const toggleNewListForm = (groupId: number) => {
  if (!newListState.value[groupId]) {
    newListState.value[groupId] = { name: '', trigger_name: '', description: '', show: true };
  } else {
    newListState.value[groupId].show = !newListState.value[groupId].show;
  }
}

const createNewList = async (groupId: number) => {
  const state = newListState.value[groupId];
  if (!state || !state.name || !state.trigger_name) return;
  try {
    await listService.createList(groupId, { group_id: groupId, name: state.name, trigger_name: state.trigger_name, description: state.description });
    toast.success('List created successfully');
    notificationOccurred('success');
    state.show = false;
    state.name = '';
    state.trigger_name = '';
    // Reload groups
    await loadGroups();
  } catch (e: any) {
    notificationOccurred('error');
    toast.error(e.message || t('errors.unknown'));
  }
}

const deleteList = async (groupId: number, listId: number) => {
  showConfirmDialog('Delete List', 'Are you sure you want to delete this list?', async () => {
    try {
      await listService.deleteList(groupId, listId);
      toast.success('List deleted successfully');
      notificationOccurred('success');
      // Reload groups
      await loadGroups();
    } catch (e: any) {
      notificationOccurred('error');
      toast.error(e.message || t('errors.unknown'));
    }
  });
}

const toggleSubscription = async (groupId: number, listId: number, currentlySubscribed: boolean) => {
  try {
    if (currentlySubscribed) {
      await listService.unsubscribe(groupId, listId);
      toast.success('Unsubscribed successfully');
    } else {
      await listService.subscribe(groupId, listId);
      toast.success('Subscribed successfully');
    }
    notificationOccurred('success')
    // Reload groups
    await loadGroups();
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || t('errors.unknown'))
  }
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
      <Card v-for="group in paginatedGroups" :key="group.id" class="shadow-md">
        <CardHeader class="flex flex-row items-start justify-between space-y-0 pb-2">
          <div>
            <CardTitle class="text-xl">{{ group.group_name }}</CardTitle>
            <CardDescription class="mt-1">{{ t('views.groups.members', { count: group.group_members }) }}</CardDescription>
          </div>
        </CardHeader>
        
        <div class="p-6 pt-0">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold">Available Lists:</h3>
            <Button v-if="group.is_admin" variant="outline" size="sm" @click="toggleNewListForm(group.id)">
              {{ newListState[group.id]?.show ? 'Cancel' : 'Create List' }}
            </Button>
          </div>
          
          <div v-if="newListState[group.id]?.show" class="mb-4 p-4 border rounded-lg space-y-3 bg-muted/20">
            <h4 class="text-sm font-medium">Create New List</h4>
            <div class="space-y-2">
              <input v-model="newListState[group.id].name" placeholder="List Name (e.g. Developers)" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
              <input v-model="newListState[group.id].trigger_name" placeholder="Trigger Name (e.g. devs)" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
              <Button class="w-full" size="sm" @click="createNewList(group.id)">Create</Button>
            </div>
          </div>

          <div v-if="(group as any).lists?.length === 0" class="text-sm text-muted-foreground">
            No lists available in this group.
          </div>
          <div class="space-y-3">
            <div v-for="list in (group as any).lists" :key="list.id" class="flex flex-col gap-2 bg-muted/30 p-3 rounded-lg border">
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium">{{ list.name }} <span class="text-xs text-muted-foreground ml-1">/{{ list.trigger_name }}</span></p>
                  <p v-if="list.is_system" class="text-xs text-muted-foreground">System List</p>
                </div>
                <div class="flex items-center gap-2">
                  <Button 
                    :variant="list.is_subscribed ? 'secondary' : 'default'" 
                    size="sm"
                    @click="toggleSubscription(group.id, list.id, list.is_subscribed)"
                  >
                    {{ list.is_subscribed ? 'Unsubscribe' : 'Subscribe' }}
                  </Button>
                  <Button 
                    v-if="group.is_admin && !list.is_system" 
                    variant="destructive" 
                    size="sm"
                    @click="deleteList(group.id, list.id)"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
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
