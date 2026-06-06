<script setup lang="ts">
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useI18n } from 'vue-i18n'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

const { dialogState, closeDialog } = useConfirmDialog()
const { t } = useI18n()

const handleConfirm = () => {
  if (dialogState.value.onConfirm) {
    dialogState.value.onConfirm()
  }
  closeDialog()
}

const handleCancel = () => {
  if (dialogState.value.onCancel) {
    dialogState.value.onCancel()
  }
  closeDialog()
}

// Ensure v-model correctly syncs state updates when clicking outside or using esc key
const updateOpen = (open: boolean) => {
  if (!open) {
    handleCancel()
  }
}
</script>

<template>
  <AlertDialog :open="dialogState.isOpen" @update:open="updateOpen">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>{{ dialogState.title }}</AlertDialogTitle>
        <AlertDialogDescription>
          {{ dialogState.description }}
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="handleCancel">{{ t('actions.cancel') }}</AlertDialogCancel>
        <AlertDialogAction @click="handleConfirm">{{ t('actions.continue') }}</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
