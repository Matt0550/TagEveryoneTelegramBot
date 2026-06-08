<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { toast } from 'vue-sonner'
import { useI18n } from 'vue-i18n'
import { useHapticFeedback } from 'vue-tg/latest'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  listRuleService,
  type ListTagRuleMode,
  type ListTagRuleItem,
} from '@/services/listRuleService'

const props = defineProps<{
  show: boolean
  groupId: string
  listId: string
  listName: string
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
}>()

const { notificationOccurred } = useHapticFeedback()
const { t } = useI18n()

const MODES: ListTagRuleMode[] = ['EXCLUDE', 'INCLUDE_ONLY', 'AUTO_ADD', 'AUTO_REMOVE']
const modeTitle = (mode: ListTagRuleMode) => t(`views.groupDetails.rules.modes.${mode}.title`)
const modeDesc = (mode: ListTagRuleMode) => t(`views.groupDetails.rules.modes.${mode}.desc`)

const buckets = ref<Record<ListTagRuleMode, string[]>>({
  EXCLUDE: [],
  INCLUDE_ONLY: [],
  AUTO_ADD: [],
  AUTO_REMOVE: [],
})

const knownTags = ref<string[]>([])
const isLoading = ref(false)
const isSaving = ref(false)
const inputs = ref<Record<ListTagRuleMode, string>>({
  EXCLUDE: '',
  INCLUDE_ONLY: '',
  AUTO_ADD: '',
  AUTO_REMOVE: '',
})

const isOpen = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const normalize = (raw: string): string => raw.trim().toLowerCase()

const addTag = (mode: ListTagRuleMode) => {
  const value = normalize(inputs.value[mode])
  if (!value) return
  if (!buckets.value[mode].includes(value)) {
    buckets.value[mode].push(value)
  }
  inputs.value[mode] = ''
}

const removeTag = (mode: ListTagRuleMode, tag: string) => {
  buckets.value[mode] = buckets.value[mode].filter(t => t !== tag)
}

const suggestionsFor = (mode: ListTagRuleMode) => {
  const used = new Set(buckets.value[mode])
  const needle = normalize(inputs.value[mode])
  if (!needle) return []
  return knownTags.value
    .filter(t => !used.has(t) && t.includes(needle))
    .slice(0, 6)
}

const loadAll = async () => {
  isLoading.value = true
  try {
    const [rulesResp, knownResp] = await Promise.all([
      listRuleService.getRules(props.groupId, props.listId),
      listRuleService.getKnownTags(props.groupId).catch(() => ({ tags: [] })),
    ])
    const next: Record<ListTagRuleMode, string[]> = {
      EXCLUDE: [], INCLUDE_ONLY: [], AUTO_ADD: [], AUTO_REMOVE: [],
    }
    for (const r of rulesResp.items) {
      next[r.mode].push(r.tag_value)
    }
    buckets.value = next
    knownTags.value = knownResp.tags || []
  } catch (e: any) {
    toast.error(e?.message || t('messages.loadFailed', { moduleName: t('modules.rules') }))
  } finally {
    isLoading.value = false
  }
}

const save = async () => {
  isSaving.value = true
  try {
    const rules: ListTagRuleItem[] = []
    for (const mode of Object.keys(buckets.value) as ListTagRuleMode[]) {
      for (const tag of buckets.value[mode]) {
        rules.push({ tag_value: tag, mode })
      }
    }
    await listRuleService.putRules(props.groupId, props.listId, rules)
    notificationOccurred('success')
    toast.success(t('messages.saved', { moduleName: t('modules.rules') }))
    emit('update:show', false)
  } catch (e: any) {
    notificationOccurred('error')
    toast.error(e?.message || t('messages.saveFailed', { moduleName: t('modules.rules') }))
  } finally {
    isSaving.value = false
  }
}

watch(() => props.show, (open) => {
  if (open) loadAll()
})
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('views.groupDetails.rules.dialogTitle', { listName }) }}</DialogTitle>
        <DialogDescription>
          {{ t('views.groupDetails.rules.dialogDesc') }}
        </DialogDescription>
      </DialogHeader>

      <div v-if="isLoading" class="space-y-3">
        <Skeleton class="h-16 w-full" />
        <Skeleton class="h-16 w-full" />
      </div>

      <div v-else class="space-y-5 max-h-[60vh] overflow-y-auto pr-1">
        <div v-for="mode in MODES" :key="mode" class="space-y-2">
          <div>
            <p class="font-medium text-sm">{{ modeTitle(mode) }}</p>
            <p class="text-xs text-muted-foreground">{{ modeDesc(mode) }}</p>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="tag in buckets[mode]" :key="tag"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary text-xs">
              {{ tag }}
              <button class="text-muted-foreground hover:text-foreground" @click="removeTag(mode, tag)"
                :aria-label="t('views.groupDetails.rules.removeAria')">×</button>
            </span>
            <span v-if="!buckets[mode].length" class="text-xs text-muted-foreground italic">
              {{ t('views.groupDetails.rules.noTags') }}
            </span>
          </div>
          <div class="flex gap-2">
            <input v-model="inputs[mode]" @keydown.enter.prevent="addTag(mode)" type="text"
              :placeholder="t('views.groupDetails.rules.placeholder')"
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm" />
            <Button size="sm" variant="outline" @click="addTag(mode)">{{ t('actions.add') }}</Button>
          </div>
          <div v-if="suggestionsFor(mode).length" class="flex flex-wrap gap-1">
            <button v-for="s in suggestionsFor(mode)" :key="s"
              class="text-xs px-2 py-0.5 rounded-full bg-muted hover:bg-muted/60"
              @click="inputs[mode] = s; addTag(mode)">
              + {{ s }}
            </button>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-2 border-t mt-2">
        <Button variant="ghost" :disabled="isSaving" @click="emit('update:show', false)">
          {{ t('actions.cancel') }}
        </Button>
        <Button :disabled="isSaving || isLoading" @click="save">
          {{ t('actions.saveChanges') }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
