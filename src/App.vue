<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import Navbar from './components/NavBar.vue';
import Footer from './components/Footer.vue';

const { locale } = useI18n({ useScope: 'global' });
const currentLocale = ref(localStorage.getItem('locale') || 'it');

// Imposta la lingua all'avvio dell'app
locale.value = currentLocale.value;

// Persisti la preferenza della lingua quando cambia
watch(locale, (newLocale) => {
  localStorage.setItem('locale', newLocale);
  currentLocale.value = newLocale;
  document.documentElement.setAttribute('lang', newLocale);
});

// Funzione per cambiare la lingua
const changeLanguage = (lang: string) => {
  locale.value = lang;
};
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-gray-100">
    <div class="language-switcher absolute top-4 right-6 z-50 flex items-center space-x-2">
      <button 
        @click="changeLanguage('it')" 
        :class="{'font-bold text-indigo-400': locale === 'it', 'text-gray-400': locale !== 'it'}" 
        class="transition-colors duration-200 hover:text-white"
      >
        🇮🇹 IT
      </button>
      <span class="text-gray-500">|</span>
      <button 
        @click="changeLanguage('en')" 
        :class="{'font-bold text-indigo-400': locale === 'en', 'text-gray-400': locale !== 'en'}" 
        class="transition-colors duration-200 hover:text-white"
      >
        🇬🇧 EN
      </button>
    </div>

    <Navbar />

    <transition name="fade-slide" mode="out-in">
      <router-view />
    </transition>

    <Footer />
  </div>
</template>

<style>
/* Transizioni di base per tutte le pagine */
.fade-slide-enter-active {
  transition: all 0.3s ease-out;
}

.fade-slide-leave-active {
  transition: all 0.25s ease-in;
}

.fade-slide-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.fade-slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* Transizione alternativa che puoi attivare cambiando il nome della transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Transizione con fade semplice */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>