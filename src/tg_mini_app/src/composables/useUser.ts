import { ref, readonly } from 'vue'

export interface UserProfile {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  language_code?: string
}

const currentUser = ref<UserProfile | null>(null)

export function useUser() {
  const setUser = (user: UserProfile) => {
    currentUser.value = user
  }

  const clearUser = () => {
    currentUser.value = null
  }

  return {
    user: readonly(currentUser),
    setUser,
    clearUser
  }
}
