<script setup lang="ts">
import { computed } from 'vue'
import ApiMultiSelect from '@/components/ApiMultiSelect.vue'
import { listService } from '@/services/listService'

interface Props {
  modelValue: string[];
  groupId: string;
  preloadedItems?: Array<{ id: string, name: string }>;
  placeholder?: string;
  label?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  preloadedItems: () => [],
  placeholder: 'Select lists...',
  label: 'Available Lists'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const internalValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const fetchLists = async () => {
  const response = await listService.getLists(props.groupId)
  if (response?.items) {
    return response.items.map((i: any) => ({
      id: i.id.toString(),
      name: i.name
    }))
  }
  return []
}
</script>

<template>
  <ApiMultiSelect v-model="internalValue" :fetch-data="fetchLists" :preloaded-items="preloadedItems"
    :placeholder="placeholder" :label="label" />
</template>
