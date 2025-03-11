import { createI18n } from 'vue-i18n';
import it from './locales/it.json';
import en from './locales/en.json';

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'it', // Lingua predefinita
  fallbackLocale: 'it', // Lingua di fallback
  messages: {
    it,
    en
  }
});

export default i18n;