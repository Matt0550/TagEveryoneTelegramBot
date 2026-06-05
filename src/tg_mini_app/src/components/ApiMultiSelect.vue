<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
interface Props {
  modelValue: string[];
  fetchData: () => Promise<Array<{ id: string, name: string }>>;
  preloadedItems?: Array<{ id: string, name: string }>;
  placeholder?: string;
  label?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  preloadedItems: () => [],
  placeholder: 'Select options...',
  label: 'Available Lists'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const items = ref<Array<{ id: string, name: string }>>([...props.preloadedItems])
const isLoading = ref(false)

const internalValue = ref<string[]>([])

watch(() => props.modelValue, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(internalValue.value)) {
    internalValue.value = [...newVal]
  }
}, { immediate: true })

const updateValue = (val: any) => {
  const arr = Array.isArray(val) ? val : (val ? [val.toString()] : [])
  internalValue.value = arr
  emit('update:modelValue', arr)
}



const fetchItems = async () => {
  isLoading.value = true
  try {
    const fetchedItems = await props.fetchData()
    if (fetchedItems) {

      // Merge with preloaded items avoiding duplicates
      const mergedMap = new Map<string, { id: string, name: string }>()
      props.preloadedItems.forEach(item => mergedMap.set(item.id, item))
      fetchedItems.forEach(item => mergedMap.set(item.id, item))

      items.value = Array.from(mergedMap.values())
    }
  } catch (error) {
    console.error('Failed to fetch lists:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchItems()
})
</script>

<template>
  <Select multiple :model-value="internalValue" @update:model-value="updateValue">
    <SelectTrigger class="w-full">
      <SelectValue :placeholder="placeholder" />
    </SelectTrigger>
    <SelectContent>
      <SelectGroup>
        <SelectLabel v-if="label">{{ label }}</SelectLabel>
        <SelectItem v-for="item in items" :key="item.id" :value="item.id">
          {{ item.name }}
        </SelectItem>
        <SelectItem v-if="items.length === 0 && !isLoading" value="empty" disabled>
          No options available
        </SelectItem>
        <SelectItem v-if="isLoading" value="loading" disabled>
          Loading...
        </SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
</template>
