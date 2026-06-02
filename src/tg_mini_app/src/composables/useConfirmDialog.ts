import { ref } from 'vue'
import { usePopup } from 'vue-tg'

interface ConfirmDialogState {
  isOpen: boolean
  title: string
  description: string
  onConfirm: () => void
  onCancel?: () => void
}

const dialogState = ref<ConfirmDialogState>({
  isOpen: false,
  title: '',
  description: '',
  onConfirm: () => { }
})

export function useConfirmDialog() {
  const popup = usePopup()

  const showConfirmDialog = (title: string, description: string, onConfirm: () => void, onCancel?: () => void) => {
    // Check if we are running inside Telegram Native environment
    const isTelegramEnv = window.Telegram?.WebApp?.platform && window.Telegram.WebApp.platform !== 'unknown'

    if (isTelegramEnv) {
      // Use native Telegram confirm popup
      if (popup.showConfirm) {
        popup.showConfirm(description, (result: boolean) => {
          if (result) {
            onConfirm()
          } else if (onCancel) {
            onCancel()
          }
        })
      } else {
        // Fallback to Shadcn AlertDialog if native method is missing despite platform check
        dialogState.value = {
          isOpen: true,
          title,
          description,
          onConfirm,
          onCancel
        }
      }
    } else {
      // Fallback to Shadcn AlertDialog
      dialogState.value = {
        isOpen: true,
        title,
        description,
        onConfirm,
        onCancel
      }
    }
  }

  const closeDialog = () => {
    dialogState.value.isOpen = false
  }

  return {
    dialogState,
    showConfirmDialog,
    closeDialog
  }
}
