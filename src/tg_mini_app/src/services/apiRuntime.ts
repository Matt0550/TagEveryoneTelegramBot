import { client } from '@/api/client.gen'

export const setCookie = (name: string, value: string, days = 7) => {
  const expires = new Date(Date.now() + days * 86400000).toUTCString()
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Strict; Secure`
}

export const getCookie = (name: string) => {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=')
    return parts[0] === name ? decodeURIComponent(parts[1]) : r
  }, '')
}

const API_BASE = import.meta.env.VITE_API_URL || ''

export async function authenticateWithTma(initData: string): Promise<{token: string, user: any} | null> {
    try {
        const response = await fetch(`${API_BASE}/api/v1/public/auth/telegram-tma`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ init_data: initData })
        })
        if (!response.ok) return null
        const data = await response.json()
        const token = data?.message?.access_token || data?.access_token
        const user = data?.message?.user || data?.user
        if (token) return { token, user }
        return null
    } catch {
        return null
    }
}

export async function authenticateWithTgl(loginData: any): Promise<{token: string, user: any} | null> {
    try {
        const response = await fetch(`${API_BASE}/api/v1/public/auth/telegram-tgl`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(loginData)
        })
        if (!response.ok) return null
        const data = await response.json()
        const token = data?.message?.access_token || data?.access_token
        const user = data?.message?.user || data?.user
        if (token) return { token, user }
        return null
    } catch {
        return null
    }
}

export function setupApiClient() {
  const token = getCookie('auth_token')

  client.setConfig({
    baseUrl: API_BASE,
    headers: token ? { Authorization: `Bearer ${token}` } : undefined
  })
  
  return token
}

export async function apiData<T>(promise: Promise<{ data?: any; error?: any }>): Promise<T> {
  const { data, error } = await promise;
  if (error) {
    throw error;
  }
  
  if (data && typeof data === 'object' && 'success' in data && 'message' in data) {
    return data.message as T;
  }
  
  return data as T;
}
