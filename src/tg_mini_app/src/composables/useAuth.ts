import { ref } from 'vue'
import { setupApiClient, setCookie, getCookie, authenticateWithTma, authenticateWithTgl } from '@/services/apiRuntime'
import type { LoginWidgetUser } from 'vue-tg'
import { useMiniApp } from 'vue-tg'
import { useUser } from './useUser'

export const GlobalRole = {
  SUPER_ADMIN: 'super_admin',
  USER: 'user'
} as const;

export type GlobalRole = typeof GlobalRole[keyof typeof GlobalRole];

const isAuthenticated = ref(false)
const isLoading = ref(true)
const userRole = ref<GlobalRole>(GlobalRole.USER)

export function useAuth() {
  const { setUser, clearUser } = useUser()
  const miniApp = useMiniApp()

  const initAuth = async () => {
    isLoading.value = true

    // Check if we already have a JWT
    const existingToken = getCookie('auth_token')
    if (existingToken) {
      isAuthenticated.value = true
      setupApiClient()

      try {
        const base64Url = existingToken.split('.')[1]
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        }).join(''))
        const payload = JSON.parse(jsonPayload)

        setUser({
          id: payload.id,
          first_name: payload.first_name,
          last_name: payload.last_name,
          username: payload.username,
          photo_url: payload.photo_url
        })
        userRole.value = payload.role as GlobalRole || GlobalRole.USER
      } catch (e) {
        console.error("Failed to parse JWT payload:", e)
      }
    } else {
      if (miniApp.initData) {
        const authData = await authenticateWithTma(miniApp.initData)
        if (authData) {
          setCookie('auth_token', authData.token, 7)
          setupApiClient()
          isAuthenticated.value = true
          userRole.value = authData.role as GlobalRole
          if (authData.user) {
            setUser(authData.user)
          }
        }
      }
    }

    isLoading.value = false
  }

  const loginWithWidget = async (user: LoginWidgetUser) => {
    isLoading.value = true
    const authData = await authenticateWithTgl(user)
    if (authData) {
      setCookie('auth_token', authData.token, 7)
      setupApiClient()
      isAuthenticated.value = true
      userRole.value = authData.role as GlobalRole
      setUser(authData.user || {
        id: user.id,
        first_name: user.first_name,
        last_name: user.last_name,
        username: user.username,
        photo_url: user.photo_url
      })
    } else {
      console.error("Authentication failed")
    }
    isLoading.value = false
    return authData?.token || null
  }

  const logout = () => {
    setCookie('auth_token', '', -1)
    isAuthenticated.value = false
    userRole.value = GlobalRole.USER
    clearUser()
  }
  
  const hasRole = (role: GlobalRole): boolean => {
    return userRole.value === role
  }

  return {
    isAuthenticated,
    isLoading,
    userRole,
    initAuth,
    loginWithWidget,
    logout,
    hasRole
  }
}
