<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const isMobileMenuOpen = ref(false);

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

// Chiude il menu mobile quando si fa clic su un link
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

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

interface Language {
  code: string;
  name: string;
  flagSvg: string;
}

const availableLanguages: Language[] = [
  {
    code: 'it',
    name: 'Italiano',
    flagSvg: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="18" viewBox="0 0 640 480">
      <g fill-rule="evenodd" stroke-width="1pt">
        <path fill="#fff" d="M0 0h640v480H0z"/>
        <path fill="#009246" d="M0 0h213.3v480H0z"/>
        <path fill="#ce2b37" d="M426.7 0H640v480H426.7z"/>
      </g>
    </svg>`
  },
  {
    code: 'en',
    name: 'English',
    flagSvg: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="18" viewBox="0 0 640 480">
      <defs>
        <clipPath id="a">
          <path fill-opacity=".7" d="M-85.3 0h682.6v512H-85.3z"/>
        </clipPath>
      </defs>
      <g clip-path="url(#a)" transform="translate(80) scale(.94)">
        <g stroke-width="1pt">
          <path fill="#012169" d="M-256 0H768v512H-256z"/>
          <path fill="#fff" d="M-256 0v57.2L653.5 512H768v-57.2L-141.5 0H-256zM768 0v57.2L-141.5 512H-256v-57.2L653.5 0H768z"/>
          <path fill="#fff" d="M170.7 0v512h170.6V0H170.7zM-256 170.7v170.6H768V170.7H-256z"/>
          <path fill="#c8102e" d="M-256 204.8v102.4H768V204.8H-256zM204.8 0v512h102.4V0H204.8zM-256 512L85.3 341.3h76.4L-179.7 512H-256zm0-512L85.3 170.7H9L-256 38.2V0zm606.4 170.7L691.7 0H768L426.7 170.7h-76.3zM768 512L426.7 341.3h76.3L768 473.8V512z"/>
        </g>
      </g>
    </svg>`
  }
];

// Funzione per cambiare la lingua
const changeLanguage = (lang: string) => {
  locale.value = lang;
  // Chiudi il menu mobile se aperto
  closeMobileMenu();
};

// Gestione del dropdown del language switcher
const isLangDropdownOpen = ref(false);

const toggleLangDropdown = () => {
  isLangDropdownOpen.value = !isLangDropdownOpen.value;
};

const closeLangDropdown = () => {
  isLangDropdownOpen.value = false;
};

// Array dei link di navigazione per evitare duplicazione
const navLinks = [
  { key: 'home', to: '/', isRouter: true },
  { key: 'features', to: '#features', isRouter: false },
  { key: 'pricing', to: '/pricing', isRouter: true },
  { key: 'contact', to: '#contact', isRouter: false }
];
</script>

<template>
  <nav class="bg-gray-900 border-b border-gray-800 p-4 relative z-20">
    <div class="container mx-auto flex justify-between items-center">
      <!-- Logo -->
      <div class="flex items-center space-x-2">
        <img src="../assets/logo.png" alt="Logo" class="h-8 w-8 rounded-full" />
        <router-link to="/" class="text-xl font-bold text-indigo-400">TagEveryone</router-link>
      </div>

      <!-- Links di navigazione - solo desktop -->
      <div class="hidden md:flex items-center space-x-4">
        <template v-for="(link, index) in navLinks" :key="index">
          <router-link v-if="link.isRouter" :to="link.to" class="text-gray-300 hover:text-white transition">
            {{ $t(`navbar.${link.key}`) }}
          </router-link>
          <a v-else :href="link.to" class="text-gray-300 hover:text-white transition">
            {{ $t(`navbar.${link.key}`) }}
          </a>
        </template>

        <!-- Language Switcher - Desktop -->
        <div class="relative ml-2 group">
          <button @click="toggleLangDropdown"
            class="flex items-center space-x-1 py-1 px-2 rounded-md hover:bg-gray-800 text-gray-300 hover:text-white transition"
            :aria-expanded="isLangDropdownOpen" aria-haspopup="true">
            <!-- SVG della bandiera invece dell'emoji -->
            <span class="w-6 h-4 flex items-center justify-center"
              v-html="availableLanguages.find(lang => lang.code === currentLocale)?.flagSvg"></span>
            <span class="hidden lg:inline">{{availableLanguages.find(lang => lang.code === currentLocale)?.name
            }}</span>
            <svg class="h-4 w-4 transform transition-transform duration-200"
              :class="{ 'rotate-180': isLangDropdownOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
              fill="currentColor">
              <path fill-rule="evenodd"
                d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Language Dropdown -->
          <div v-if="isLangDropdownOpen"
            class="absolute right-0 mt-1 py-1 w-32 bg-gray-800 rounded-md shadow-lg z-20 animate-fadeIn">
            <button v-for="lang in availableLanguages" :key="lang.code"
              @click="changeLanguage(lang.code); closeLangDropdown()"
              class="block w-full text-left px-4 py-2 hover:bg-gray-700 text-gray-300 hover:text-white transition"
              :class="{ 'bg-gray-700': currentLocale === lang.code }">
              <div class="flex items-center space-x-2">
                <!-- SVG della bandiera nel dropdown -->
                <span class="w-6 h-4 flex items-center justify-center" v-html="lang.flagSvg"></span>
                <span>{{ lang.name }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- CTA Button - solo desktop -->
      <div class="hidden md:flex items-center space-x-3">
        <button
          class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition hover:cursor-pointer">
          {{ $t('navbar.cta') }}
        </button>
      </div>

      <!-- Hamburger menu - solo mobile -->
      <button @click="toggleMobileMenu" class="md:hidden text-gray-400 hover:text-white focus:outline-none"
        aria-label="Toggle menu">
        <svg class="h-6 w-6" :class="{ 'hidden': isMobileMenuOpen }" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg class="h-6 w-6" :class="{ 'hidden': !isMobileMenuOpen }" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Menu mobile dropdown -->
    <div v-if="isMobileMenuOpen"
      class="md:hidden absolute left-0 right-0 top-full bg-gray-900 border-b border-gray-800 shadow-lg z-10 animate-slideDown">
      <div class="container mx-auto py-3 px-4">
        <div class="flex flex-col space-y-3">
          <template v-for="(link, index) in navLinks" :key="index">
            <router-link v-if="link.isRouter" :to="link.to" @click="closeMobileMenu"
              class="text-gray-300 py-2 px-3 hover:bg-gray-800 rounded-md transition">
              {{ $t(`navbar.${link.key}`) }}
            </router-link>
            <a v-else :href="link.to" @click="closeMobileMenu"
              class="text-gray-300 py-2 px-3 hover:bg-gray-800 rounded-md transition">
              {{ $t(`navbar.${link.key}`) }}
            </a>
          </template>

          <!-- CTA nel menu mobile -->
          <button @click="closeMobileMenu"
            class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition mt-2 hover:cursor-pointer">
            {{ $t('navbar.cta') }}
          </button>

          <!-- Language Switcher - Mobile -->
          <div class="pt-2 pb-1 border-t border-gray-800 mt-2">
            <p class="text-sm text-gray-500 mb-2 px-3">{{ $t('navbar.selectLanguage') }}</p>
            <div class="grid grid-cols-2 gap-2">
              <button v-for="lang in availableLanguages" :key="lang.code" @click="changeLanguage(lang.code)"
                class="flex items-center space-x-2 py-2 px-3 rounded-md transition"
                :class="currentLocale === lang.code ? 'bg-gray-800 text-white' : 'text-gray-300 hover:bg-gray-800 hover:text-white'">
                <!-- SVG della bandiera nel menu mobile -->
                <span class="w-6 h-4 flex items-center justify-center" v-html="lang.flagSvg"></span>
                <span>{{ lang.name }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.animate-slideDown {
  animation: slideDown 0.2s ease-out forwards;
  transform-origin: top center;
}

.animate-fadeIn {
  animation: fadeIn 0.2s ease-out forwards;
}

@keyframes slideDown {
  0% {
    opacity: 0;
    transform: translateY(-10px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: translateY(-5px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Nasconde il dropdown del language switcher quando il mouse esce */
.group:hover .animate-fadeIn {
  display: block;
}

@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>