<script setup lang="ts">
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import { useHapticFeedback } from 'vue-tg/latest'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { listService } from '@/services/listService'
import { Skeleton } from '@/components/ui/skeleton'

const props = defineProps<{
  show: boolean
  groupId: string
  listId: string
  listName: string
}>()

const emit = defineEmits(['update:show'])

const { notificationOccurred } = useHapticFeedback()

const members = ref<Array<{ user_id: number, first_name: string | null, last_name: string | null, username: string | null }>>([])
const isLoading = ref(false)
const isAdding = ref(false)
const newMemberIdentifier = ref('')

const loadMembers = async () => {
  if (!props.listId || !props.groupId) return
  isLoading.value = true
  try {
    members.value = await listService.getMembers(props.groupId, props.listId)
  } catch (e: any) {
    toast.error(e.message || 'Failed to load members')
  } finally {
    isLoading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadMembers()
  } else {
    members.value = []
    newMemberIdentifier.value = ''
  }
})

const handleAddMember = async () => {
  if (!newMemberIdentifier.value.trim()) return
  isAdding.value = true
  try {
    await listService.addMember(props.groupId, props.listId, newMemberIdentifier.value.trim())
    toast.success('Member added successfully')
    notificationOccurred('success')
    newMemberIdentifier.value = ''
    await loadMembers()
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || 'Failed to add member')
  } finally {
    isAdding.value = false
  }
}

const handleRemoveMember = async (userId: number) => {
  try {
    await listService.removeMember(props.groupId, props.listId, userId)
    toast.success('Member removed successfully')
    notificationOccurred('success')
    await loadMembers()
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || 'Failed to remove member')
  }
}

const handleTriggerMention = async () => {
  try {
    await listService.triggerMention(props.groupId, props.listId)
    toast.success('Mention triggered successfully')
    notificationOccurred('success')
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || 'Failed to trigger mention')
  }
}
</script>

<template>
  <Dialog :open="show" @update:open="(val) => emit('update:show', val)">
    <DialogContent class="sm:max-w-[425px] max-h-[80vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>Members of {{ listName }}</DialogTitle>
      </DialogHeader>

      <div class="flex flex-col flex-1 overflow-hidden gap-4 mt-2">
        <div class="flex flex-col gap-2">
          <p class="text-sm text-muted-foreground">Add user by Telegram ID or @username</p>
          <div class="flex items-center gap-2">
            <input 
              v-model="newMemberIdentifier" 
              placeholder="@username or 123456789"
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
            <Button size="sm" @click="handleAddMember" :disabled="isAdding || !newMemberIdentifier.trim()">
              Add
            </Button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto space-y-2 border rounded-md p-2 bg-muted/20">
          <div v-if="isLoading" class="space-y-2">
             <Skeleton class="h-[40px] w-full" />
             <Skeleton class="h-[40px] w-full" />
             <Skeleton class="h-[40px] w-full" />
          </div>
          <div v-else-if="members.length === 0" class="text-center py-4 text-sm text-muted-foreground">
            No members in this list.
          </div>
          <div v-else v-for="user in members" :key="user.user_id" class="flex items-center justify-between p-2 rounded-md hover:bg-muted/50 border bg-background">
            <div class="flex flex-col overflow-hidden">
              <span class="text-sm font-medium truncate">
                {{ user.first_name }} {{ user.last_name || '' }}
              </span>
              <span class="text-xs text-muted-foreground truncate" v-if="user.username">
                @{{ user.username }}
              </span>
              <span class="text-xs text-muted-foreground truncate" v-else>
                ID: {{ user.user_id }}
              </span>
            </div>
            <Button variant="destructive" size="sm" class="h-7 px-2 text-xs" @click="handleRemoveMember(user.user_id)">
              Remove
            </Button>
          </div>
        </div>
        
        <div class="pt-2">
            <Button variant="secondary" class="w-full" @click="handleTriggerMention" :disabled="members.length === 0">
              Trigger Mention (@everyone)
            </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
