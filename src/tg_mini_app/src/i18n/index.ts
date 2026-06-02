import { createI18n } from "vue-i18n"
import en from "./locales/en.json"
import it from "./locales/it.json"

export function getDefaultLocale(): string {
    // 1. Check local storage if user explicitly set it
    const saved = localStorage.getItem('user_locale')
    if (saved) return saved

    // 2. Check Telegram initDataUnsafe if available
    const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code
    if (tgLang) {
        // If we only support en and it for now
        if (tgLang.startsWith('it')) return 'it'
        return 'en'
    }

    // 3. Fallback to browser language
    const navLang = navigator.language?.split('-')[0]
    if (navLang === 'it') return 'it'

    return 'en'
}

const i18n = createI18n({
    locale: getDefaultLocale(),
    fallbackLocale: "en",
    legacy: false, // required for Composition API
    globalInjection: true, // allows using $t in templates directly
    messages: {
        en,
        it
    },
})

export function setAppLocale(lang: any) {
    if (!lang) return
    const langStr = String(lang)
    i18n.global.locale.value = langStr as 'en' | 'it'
    localStorage.setItem('user_locale', langStr)
}

export default i18n