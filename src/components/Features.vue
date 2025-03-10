<script setup lang="ts">
const featureGroups = {
  free: {
    title: "Funzionalità Free",
    description: "Disponibili per tutti gli utenti",
    features: [
      {
        title: 'Menzione Semplice',
        description: 'Menziona fino a 5 utenti alla volta nei tuoi gruppi Telegram.',
        icon: '👥',
        iconClass: 'text-blue-400'
      },
      {
        title: 'Comandi Base',
        description: 'Accesso ai comandi essenziali per taggare gli utenti nei gruppi.',
        icon: '💬',
        iconClass: 'text-green-400'
      },
      {
        title: 'Statistiche Base',
        description: 'Visualizza semplici statistiche sulle tue menzioni recenti.',
        icon: '📊',
        iconClass: 'text-yellow-400'
      },
      {
        title: 'Supporto Community',
        description: 'Accesso al supporto attraverso la nostra community su Telegram.',
        icon: '🌐',
        iconClass: 'text-purple-400'
      }
    ]
  },
  premium: {
    title: "Funzionalità Premium",
    description: "Esclusivamente per abbonati",
    features: [
      {
        title: 'Menzione Illimitata',
        description: 'Menziona tutti gli utenti del gruppo con un singolo comando, senza limitazioni.',
        icon: '♾️',
        iconClass: 'text-indigo-400'
      },
      {
        title: 'Notifiche Avanzate',
        description: 'Ricevi notifiche personalizzate in tempo reale quando vieni menzionato.',
        icon: '🔔',
        iconClass: 'text-red-400'
      },
      {
        title: 'Analytics Dettagliata',
        description: 'Dashboard completa con grafici interattivi e statistiche approfondite sulle interazioni.',
        icon: '📈',
        iconClass: 'text-emerald-400'
      },
      {
        title: 'Integrazione Multi-Piattaforma',
        description: 'Connetti e gestisci menzioni su più piattaforme oltre a Telegram (Discord, Slack e altro).',
        icon: '🔗',
        iconClass: 'text-amber-400'
      },
      {
        title: 'Gruppi Personalizzati',
        description: 'Crea e gestisci gruppi personalizzati di utenti da menzionare con un comando dedicato.',
        icon: '🗂️',
        iconClass: 'text-fuchsia-400'
      },
      {
        title: 'Supporto Prioritario',
        description: 'Accesso prioritario all\'assistenza tecnica con tempo di risposta garantito entro 24 ore.',
        icon: '🛠️',
        iconClass: 'text-cyan-400'
      }
    ]
  }
};
</script>

<template>
  <section class="py-16 bg-gray-900 border-t border-gray-800" id="features">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <h2 class="text-3xl md:text-4xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Confronta le Funzionalità</h2>
        <p class="max-w-2xl mx-auto text-gray-300">Scopri cosa puoi fare con TagEveryone e quali vantaggi aggiuntivi ottieni con la versione Premium.</p>
      </div>
      
      <div class="space-y-16 max-w-6xl mx-auto">
        <!-- Funzionalità Free -->
        <div>
          <div class="flex items-center mb-8">
            <div class="h-px bg-gray-700 flex-grow"></div>
            <span class="px-4 text-2xl font-bold text-gray-300">{{ featureGroups.free.title }}</span>
            <div class="h-px bg-gray-700 flex-grow"></div>
          </div>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div 
              v-for="(feature, index) in featureGroups.free.features" 
              :key="`free-${index}`"
              class="glass-card backdrop-blur-lg bg-white/5 p-6 rounded-lg border border-gray-700/50 shadow-xl hover:shadow-blue-500/10 transition group"
            >
              <div :class="`text-4xl mb-4 group-hover:scale-110 transition-transform ${feature.iconClass}`">{{ feature.icon }}</div>
              <h3 class="text-xl font-semibold mb-2 text-gray-200">{{ feature.title }}</h3>
              <p class="text-gray-400">{{ feature.description }}</p>
            </div>
          </div>
        </div>
        
        <!-- Funzionalità Premium -->
        <div>
          <div class="flex items-center mb-8">
            <div class="h-px bg-indigo-900/70 flex-grow"></div>
            <div class="px-6 py-2 bg-gradient-to-r from-indigo-800/70 to-purple-800/70 rounded-full">
              <span class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-purple-300">
                {{ featureGroups.premium.title }}
              </span>
            </div>
            <div class="h-px bg-indigo-900/70 flex-grow"></div>
          </div>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="(feature, index) in featureGroups.premium.features" 
              :key="`premium-${index}`"
              class="glass-card-premium backdrop-blur-lg bg-white/10 p-6 rounded-lg border border-indigo-500/30 shadow-xl hover:shadow-indigo-500/30 transition group"
            >
              <div :class="`text-4xl mb-4 group-hover:scale-110 transition-transform ${feature.iconClass}`">{{ feature.icon }}</div>
              <h3 class="text-xl font-semibold mb-2 text-indigo-300">{{ feature.title }}</h3>
              <p class="text-gray-400">{{ feature.description }}</p>
              <div class="absolute top-2 right-2">
                <span class="inline-block px-2 py-1 text-xs font-semibold bg-indigo-900/70 text-indigo-300 rounded-full">Premium</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- CTA -->
      <div class="mt-16 text-center">
        <p class="text-lg text-gray-300 mb-6">Sblocca il pieno potenziale di TagEveryone con il nostro piano Premium.</p>
        <div class="flex items-center justify-center space-x-4">
          <button class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors duration-300">
            Prova Premium
          </button>
          <button class="px-6 py-3 border border-gray-600 text-gray-300 hover:border-gray-400 hover:text-white font-medium rounded-lg transition-colors duration-300">
            Confronta Piani
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.glass-card {
  backdrop-filter: blur(10px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.03));
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
  transition: all 0.3s ease-in-out;
  position: relative;
}

.glass-card:hover {
  transform: translateY(-5px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
}

.glass-card-premium {
  backdrop-filter: blur(10px);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.05));
  box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.2);
  transition: all 0.3s ease-in-out;
  position: relative;
  border-image: linear-gradient(to bottom right, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3)) 1;
}

.glass-card-premium:hover {
  transform: translateY(-5px);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.08));
  box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.25);
}

/* Effetto di glow per le carte premium al passaggio del mouse */
.glass-card-premium:hover::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.4), rgba(168, 85, 247, 0.4));
  border-radius: inherit;
  z-index: -1;
  filter: blur(8px);
  opacity: 0.7;
  pointer-events: none;
  transition: opacity 0.3s ease-in-out;
}
</style>