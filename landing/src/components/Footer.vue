<script setup lang="ts">
import Navbar from '../components/Navbar.vue';
import Hero from '../components/Hero.vue';
import Features from '../components/Features.vue';

// Anno corrente per il copyright
const currentYear = new Date().getFullYear();

// Social media links
const socialLinks = [
  { name: 'Telegram', url: 'https://t.me/tageveryone', icon: 'telegram' },
  { name: 'Twitter', url: 'https://twitter.com/matt05_dev', icon: 'twitter' },
  { name: 'GitHub', url: 'https://github.com/matt-05/tageveryone', icon: 'github' },
  { name: 'Discord', url: '#', icon: 'discord' }
];

// Icone SVG per i social media
const socialIcons = {
  telegram: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
            </svg>`,
  twitter: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
             <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
           </svg>`,
  github: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
          </svg>`,
  discord: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
             <path d="M13.545 2.907a13.227 13.227 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406.833a12.19 12.19 0 0 0-3.658 0 8.258 8.258 0 0 0-.412-.833.051.051 0 0 0-.052-.025c-1.125.194-2.22.534-3.257 1.011a.041.041 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032c.001.014.01.028.021.037a13.276 13.276 0 0 0 3.995 2.02.05.05 0 0 0 .056-.019c.308-.42.582-.863.818-1.329a.05.05 0 0 0-.01-.059.051.051 0 0 0-.018-.011 8.875 8.875 0 0 1-1.248-.595.05.05 0 0 1-.02-.066.051.051 0 0 1 .015-.019c.084-.063.168-.129.248-.195a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.052.052 0 0 1 .053.007c.08.066.164.132.248.195a.051.051 0 0 1-.004.085 8.254 8.254 0 0 1-1.249.594.05.05 0 0 0-.03.03.052.052 0 0 0 .003.041c.24.465.515.909.817 1.329a.05.05 0 0 0 .056.019 13.235 13.235 0 0 0 4.001-2.02.049.049 0 0 0 .021-.037c.334-3.451-.559-6.449-2.366-9.106a.034.034 0 0 0-.02-.019Zm-8.198 7.307c-.789 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.45.73 1.438 1.613 0 .888-.637 1.612-1.438 1.612Zm5.316 0c-.788 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.451.73 1.438 1.613 0 .888-.631 1.612-1.438 1.612Z"/>
           </svg>`
};
</script>

<template>
    <footer class="bg-gray-800 text-gray-300 pt-12 pb-6 border-t border-gray-700">
      <div class="container mx-auto px-4">
        <!-- Footer Content -->
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8 mb-8">
          <!-- Logo e info -->
          <div class="lg:col-span-1">
            <div class="flex items-center mb-4">
              <img src="../assets/logo.png" alt="Logo" class="h-10 w-10 rounded-full mr-3" />
              <h3 class="text-xl font-bold text-indigo-400">TagEveryone</h3>
            </div>
            <p class="text-gray-400 mb-4">La soluzione completa per gestire facilmente i tuoi tag e menzioni su Telegram e altre piattaforme.</p>
            
            <!-- Social links -->
            <div class="flex space-x-4">
              <a v-for="(social, idx) in socialLinks" :key="idx" 
                 :href="social.url" 
                 :title="social.name"
                 target="_blank" rel="noopener"
                 class="w-10 h-10 flex items-center justify-center rounded-full bg-gray-700 hover:bg-indigo-600 text-gray-300 hover:text-white transition-colors duration-300">
                <span v-html="socialIcons[social.icon]"></span>
              </a>
            </div>
          </div>
          
          <!-- Links colonna 1 -->
          <div class="md:ml-8">
            <h4 class="text-lg font-semibold text-white mb-4">Prodotto</h4>
            <ul class="space-y-2">
              <li><a href="#features" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">Features</a></li>
              <li><router-link to="/pricing" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">Pricing</router-link></li>
              <li><a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">API</a></li>
              <li><a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">Integrazioni</a></li>
            </ul>
          </div>
          
          <!-- Links colonna 2 -->
          <div>
            <h4 class="text-lg font-semibold text-white mb-4">Supporto</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">Documentazione</a></li>
              <li><a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">Guida</a></li>
              <li><a href="#" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">FAQ</a></li>
              <li><a href="#contact" class="text-gray-400 hover:text-indigo-400 transition-colors duration-300">Contatti</a></li>
            </ul>
          </div>
          
          <!-- Newsletter -->
          <div class="lg:col-span-1">
            <h4 class="text-lg font-semibold text-white mb-4">Resta aggiornato</h4>
            <p class="text-gray-400 mb-4">Iscriviti per ricevere aggiornamenti sulle nuove funzionalità e offerte speciali.</p>
            <div class="flex">
              <input type="email" placeholder="La tua email" class="px-4 py-2 rounded-l-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:border-indigo-500 w-full" />
              <button class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-r-md transition-colors duration-300">
                Iscriviti
              </button>
            </div>
          </div>
        </div>
        
        <!-- Divider -->
        <div class="border-t border-gray-700 my-8"></div>
        
        <!-- Bottom bar -->
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-gray-400 text-sm mb-4 md:mb-0">
            &copy; {{ currentYear }} TagEveryone. Tutti i diritti riservati.
          </div>
          <div class="flex space-x-6">
            <a href="#" class="text-gray-400 hover:text-indigo-400 text-sm transition-colors duration-300">Privacy Policy</a>
            <a href="#" class="text-gray-400 hover:text-indigo-400 text-sm transition-colors duration-300">Termini di Servizio</a>
            <a href="#" class="text-gray-400 hover:text-indigo-400 text-sm transition-colors duration-300">Cookie Policy</a>
          </div>
        </div>
      </div>
    </footer>
</template>

<style>
/* Gli stili globali sono in style.css */
body {
  background-color: #111827; /* bg-gray-900 */
  color: #f3f4f6; /* text-gray-100 */
}

/* Stili specifici del footer */
footer a:hover {
  text-decoration: underline;
}
</style>