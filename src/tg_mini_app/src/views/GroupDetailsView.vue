<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useI18n } from 'vue-i18n'
import { useHapticFeedback } from 'vue-tg/latest'
import { BackButton } from 'vue-tg'
import { Skeleton } from '@/components/ui/skeleton'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ListMultiSelect from '@/components/ListMultiSelect.vue'
import ListMembersDialog from '@/components/ListMembersDialog.vue'
import ListRulesDialog from '@/components/ListRulesDialog.vue'

import { groupService } from '@/services/groupService'
import { listService } from '@/services/listService'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useAuth, GlobalRole } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { notificationOccurred } = useHapticFeedback()
const { showConfirmDialog } = useConfirmDialog()
const { hasRole } = useAuth()

const groupId = route.params.id as string
const group = ref<any>(null)

const canManage = computed(() => {
  return group.value?.is_group_admin || hasRole(GlobalRole.SUPER_ADMIN)
})

const isLoading = ref(true)
let loadingTimeout: ReturnType<typeof setTimeout> | null = null

const startLoading = () => {
  loadingTimeout = setTimeout(() => { isLoading.value = true }, 200)
}
const stopLoading = () => {
  if (loadingTimeout) clearTimeout(loadingTimeout)
  isLoading.value = false
}

const loadGroup = async () => {
  startLoading()
  try {
    group.value = await groupService.getGroup(groupId)
  } catch (e: any) {
    if (e?.status !== 401) {
      notificationOccurred('error')
      toast.error(e.message || t('errors.unknown'))
    }
  } finally {
    stopLoading()
  }
}

const newListState = ref({ name: '', trigger_name: '', description: '', show: false })
const groupSettingsState = ref({ auto_add_new_members: false, auto_add_list_ids: [] as string[], preloadedItems: [] as Array<{id: string, name: string}>, show: false, isLoading: false })
const membersDialogState = ref({ show: false, listId: '', listName: '' })
const rulesDialogState = ref({ show: false, listId: '', listName: '' })

const openMembersDialog = (listId: string, listName: string) => {
  membersDialogState.value.listId = listId
  membersDialogState.value.listName = listName
  membersDialogState.value.show = true
}

const openRulesDialog = (listId: string, listName: string) => {
  rulesDialogState.value.listId = listId
  rulesDialogState.value.listName = listName
  rulesDialogState.value.show = true
}

const toggleNewListForm = () => {
  newListState.value.show = !newListState.value.show
}

const loadSettings = async () => {
  if (!groupSettingsState.value.isLoading) {
    groupSettingsState.value.isLoading = true
    try {
      const settings = await groupService.getGroupSettings(groupId) as any
      groupSettingsState.value.auto_add_new_members = settings.auto_add_new_members
      groupSettingsState.value.auto_add_list_ids = settings.auto_add_lists?.map((l: any) => l.id) || []
      groupSettingsState.value.preloadedItems = settings.auto_add_lists?.map((l: any) => ({ id: l.id, name: l.name })) || []
    } catch (e: any) {
      toast.error(t('messages.loadFailed', { moduleName: t('modules.settings') }))
    } finally {
      groupSettingsState.value.isLoading = false
    }
  }
}

const saveSettings = async () => {
  try {
    groupSettingsState.value.isLoading = true
    await groupService.updateGroupSettings(groupId, {
      auto_add_new_members: groupSettingsState.value.auto_add_new_members,
      auto_add_list_ids: groupSettingsState.value.auto_add_list_ids
    })
    toast.success(t('messages.saved', { moduleName: t('modules.settings') }))
    notificationOccurred('success')
  } catch (e: any) {
    toast.error(t('messages.saveFailed', { moduleName: t('modules.settings') }))
  } finally {
    groupSettingsState.value.isLoading = false
  }
}

const createNewList = async () => {
  if (!newListState.value.name || !newListState.value.trigger_name) return
  startLoading()
  try {
    await listService.createList(groupId, { group_id: groupId, name: newListState.value.name, trigger_name: newListState.value.trigger_name, description: newListState.value.description })
    toast.success(t('messages.created', { moduleName: t('modules.list') }))
    notificationOccurred('success')
    newListState.value.show = false
    newListState.value.name = ''
    newListState.value.trigger_name = ''
    await loadGroup()
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || t('errors.unknown'))
    stopLoading()
  }
}

const deleteList = async (listId: string) => {
  showConfirmDialog(t('dialogs.deleteTitle', { moduleName: t('modules.list') }), t('dialogs.deleteDesc', { moduleName: t('modules.list') }), async () => {
    startLoading()
    try {
      await listService.deleteList(groupId, listId)
      toast.success(t('messages.deleted', { moduleName: t('modules.list') }))
      notificationOccurred('success')
      await loadGroup()
    } catch (e: any) {
      notificationOccurred('error')
      toast.error(e.message || t('errors.unknown'))
      stopLoading()
    }
  })
}

const clearList = (listId: string, listName: string) => {
  showConfirmDialog(t('dialogs.clearTitle', { moduleName: t('modules.list') }), t('dialogs.clearDesc', { moduleName: t('modules.list'), name: listName }), async () => {
    startLoading()
    try {
      await listService.clear(groupId, listId)
      toast.success(t('messages.cleared', { moduleName: t('modules.list') }))
      notificationOccurred('success')
      await loadGroup()
    } catch (e: any) {
      notificationOccurred('error')
      toast.error(e.message || t('errors.unknown'))
      stopLoading()
    }
  })
}

const toggleSubscription = async (listId: string, currentlySubscribed: boolean) => {
  startLoading()
  try {
    if (currentlySubscribed) {
      await listService.unsubscribe(groupId, listId)
      toast.success(t('messages.unsubscribed'))
    } else {
      await listService.subscribe(groupId, listId)
      toast.success(t('messages.subscribed'))
    }
    notificationOccurred('success')
    await loadGroup()
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e.message || t('errors.unknown'))
    stopLoading()
  }
}

onMounted(() => {
  loadGroup()
})
</script>

<template>
  <div>
    <BackButton @click="router.back()" />

    <div v-if="!group && isLoading" class="max-w-2xl mx-auto space-y-4">
      <Skeleton class="h-40 w-full rounded-xl" />
    </div>

    <div v-else-if="!group" class="max-w-2xl mx-auto py-12 text-center bg-muted/50 rounded-lg border">
      <h2 class="text-xl font-semibold">{{ t('views.groupDetails.notFound') }}</h2>
    </div>

    <div v-else class="max-w-2xl mx-auto space-y-6">
      <div class="text-center space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">{{ group.group_name }}</h1>
        <p class="text-muted-foreground">{{ t('views.groups.members', { count: group.group_members }) }}</p>
      </div>

      <Tabs default-value="lists" class="w-full" @update:model-value="(val) => val === 'settings' && loadSettings()">
        <TabsList :class="['grid w-full', canManage ? 'grid-cols-2' : 'grid-cols-1']">
          <TabsTrigger value="lists">{{ t('views.groupDetails.tabs.lists') }}</TabsTrigger>
          <TabsTrigger v-if="canManage" value="settings">{{ t('views.groupDetails.tabs.settings') }}</TabsTrigger>
        </TabsList>

        <TabsContent value="lists" class="mt-4">
          <Card class="shadow-md p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-semibold">{{ t('views.groupDetails.lists.available') }}</h3>
              <Button v-if="canManage" variant="outline" size="sm" @click="toggleNewListForm">
                {{ newListState.show ? t('actions.cancel') : t('actions.create') }}
              </Button>
            </div>

            <div v-if="newListState.show" class="mb-4 p-4 border rounded-lg space-y-3 bg-muted/20">
              <h4 class="text-sm font-medium">{{ t('views.groupDetails.lists.createNew') }}</h4>
              <div class="space-y-2">
                <input v-model="newListState.name" :placeholder="t('views.groupDetails.lists.namePlaceholder')"
                  class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
                <input v-model="newListState.trigger_name" :placeholder="t('views.groupDetails.lists.triggerPlaceholder')"
                  class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
                <Button class="w-full" size="sm" @click="createNewList">{{ t('actions.create') }}</Button>
              </div>
            </div>

            <div v-if="isLoading && !newListState.show" class="space-y-3">
               <Skeleton class="h-[74px] w-full rounded-xl" />
               <Skeleton class="h-[74px] w-full rounded-xl" />
            </div>

            <div v-else>
              <div v-if="group.lists?.length === 0" class="text-sm text-muted-foreground">
                {{ t('views.groupDetails.lists.noLists') }}
              </div>
              <div class="space-y-3">
                <div v-for="list in group.lists" :key="list.id"
                  class="flex flex-col gap-2 bg-muted/30 p-3 rounded-lg border">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="font-medium">{{ list.name }} <span class="text-xs text-muted-foreground ml-1">/{{
                        list.trigger_name }}</span></p>
                      <p v-if="list.is_system" class="text-xs text-muted-foreground">{{ t('views.groupDetails.lists.systemList') }}</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                      <Button :variant="list.is_subscribed ? 'secondary' : 'default'" size="sm"
                        @click="toggleSubscription(list.id, list.is_subscribed)">
                        {{ list.is_subscribed ? t('actions.unsubscribe') : t('actions.subscribe') }}
                      </Button>
                      <Button v-if="canManage" variant="outline" size="sm" @click="openMembersDialog(list.id, list.name)">
                        Members
                      </Button>
                      <Button v-if="canManage" variant="outline" size="sm" @click="openRulesDialog(list.id, list.name)">
                        {{ t('views.groupDetails.rules.buttonLabel') }}
                      </Button>
                      <Button v-if="canManage" variant="outline" size="sm"
                        @click="clearList(list.id, list.name)">
                        {{ t('actions.clear') }}
                      </Button>
                      <Button v-if="canManage && !list.is_system" variant="destructive" size="sm"
                        @click="deleteList(list.id)">
                        {{ t('actions.delete') }}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="settings" class="mt-4" v-if="canManage">
          <Card class="shadow-md p-6">
            <h3 class="font-semibold mb-4">{{ t('views.groupDetails.settings.title') }}</h3>
            <div v-if="groupSettingsState.isLoading" class="text-sm text-muted-foreground">{{ t('views.groupDetails.settings.loading') }}</div>
            <div v-else class="space-y-4">
              <Label :for="`toggle-${group.id}`"
                class="hover:bg-accent/50 flex items-start gap-3 rounded-lg border p-4 cursor-pointer has-[[aria-checked=true]]:border-blue-600 has-[[aria-checked=true]]:bg-blue-50 dark:has-[[aria-checked=true]]:border-blue-900 dark:has-[[aria-checked=true]]:bg-blue-950 transition-colors">
                <Checkbox :id="`toggle-${group.id}`"
                  :default-value="groupSettingsState.auto_add_new_members"
                  @update:model-value="(val) => { groupSettingsState.auto_add_new_members = (val === true); }"
                  class="data-[state=checked]:border-blue-600 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white dark:data-[state=checked]:border-blue-700 dark:data-[state=checked]:bg-blue-700 mt-0.5" />
                <div class="grid gap-1.5 font-normal">
                  <p class="text-sm leading-none font-medium">
                    {{ t('views.groupDetails.settings.autoAdd') }}
                  </p>
                  <p class="text-muted-foreground text-sm">
                    {{ t('views.groupDetails.settings.autoAddDesc') }}
                  </p>
                </div>
              </Label>

              <div class="pt-2">
                <ListMultiSelect v-if="groupSettingsState.auto_add_new_members"
                  v-model="groupSettingsState.auto_add_list_ids" :group-id="group.id"
                  :preloaded-items="groupSettingsState.preloadedItems" :placeholder="t('views.groupDetails.settings.selectLists')"
                  :label="t('views.groupDetails.lists.available')" />
              </div>
              <Button class="w-full mt-2" @click="saveSettings"
                :disabled="groupSettingsState.isLoading">{{ t('actions.save') }}</Button>

              <div class="mt-4 rounded-lg border border-blue-200 bg-blue-50/60 dark:border-blue-900 dark:bg-blue-950/40 p-4 space-y-2">
                <p class="text-sm font-medium">
                  {{ t('views.groupDetails.settings.precedence.title') }}
                </p>
                <p class="text-xs text-muted-foreground">
                  {{ t('views.groupDetails.settings.precedence.intro') }}
                </p>
                <ol class="text-xs text-muted-foreground list-decimal pl-4 space-y-0.5">
                  <li>{{ t('views.groupDetails.settings.precedence.step1') }}</li>
                  <li>{{ t('views.groupDetails.settings.precedence.step2') }}</li>
                </ol>
                <p class="text-xs text-muted-foreground italic">
                  {{ t('views.groupDetails.settings.precedence.hint') }}
                </p>
                <details class="text-xs">
                  <summary class="cursor-pointer text-muted-foreground hover:text-foreground">
                    {{ t('views.groupDetails.settings.precedence.examplesLabel') }}
                  </summary>
                  <ul class="mt-2 space-y-2 pl-1">
                    <li>
                      <p class="font-medium">{{ t('views.groupDetails.settings.precedence.examples.ex1.title') }}</p>
                      <p class="text-muted-foreground">{{ t('views.groupDetails.settings.precedence.examples.ex1.body') }}</p>
                    </li>
                    <li>
                      <p class="font-medium">{{ t('views.groupDetails.settings.precedence.examples.ex2.title') }}</p>
                      <p class="text-muted-foreground">{{ t('views.groupDetails.settings.precedence.examples.ex2.body') }}</p>
                    </li>
                    <li>
                      <p class="font-medium">{{ t('views.groupDetails.settings.precedence.examples.ex3.title') }}</p>
                      <p class="text-muted-foreground">{{ t('views.groupDetails.settings.precedence.examples.ex3.body') }}</p>
                    </li>
                  </ul>
                </details>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>

    <ListMembersDialog
      v-model:show="membersDialogState.show"
      :group-id="groupId"
      :list-id="membersDialogState.listId"
      :list-name="membersDialogState.listName"
    />

    <ListRulesDialog
      v-model:show="rulesDialogState.show"
      :group-id="groupId"
      :list-id="rulesDialogState.listId"
      :list-name="rulesDialogState.listName"
    />
  </div>
</template>
