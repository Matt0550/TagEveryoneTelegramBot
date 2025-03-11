<script setup lang="ts">

// Definizione dell'interfaccia per le funzionalità
interface Feature {
  icon: string;
  iconClass: string;
  isSoon?: boolean;
  isPremium?: boolean;
  key: string; // Chiave per le traduzioni
}

// Funzionalità Free
const freeFeatures: Feature[] = [
  {
    icon: '👥',
    iconClass: 'text-blue-400',
    isPremium: false,
    key: 'limited_mention'
  },
  {
    icon: '💬',
    iconClass: 'text-green-400',
    isPremium: false,
    key: 'basic_commands'
  },
  {
    icon: '🌐',
    iconClass: 'text-purple-400',
    isPremium: false,
    key: 'basic_webapp'
  },
  {
    icon: '🔗',
    iconClass: 'text-yellow-400',
    isPremium: false,
    key: 'community_support'
  },
 
];

// Funzionalità Premium
const premiumFeatures: Feature[] = [
  {
    icon: '♾️',
    iconClass: 'text-indigo-400',
    isPremium: true,
    key: 'unlimited_mention'
  },
  {
    icon: '🗂️',
    iconClass: 'text-fuchsia-400',
    isPremium: true,
    isSoon: true,
    key: 'custom_lists'
  },
  {
    icon: '🔄',
    iconClass: 'text-red-400',
    isPremium: true,
    isSoon: true,
    key: 'reduced_cooldown'
  },
  {
    icon: '📊',
    iconClass: 'text-emerald-400',
    isPremium: true,
    isSoon: true,
    key: 'no_activity_logs'
  },
  {
    icon: '🚫',
    iconClass: 'text-amber-400',
    isPremium: true,
    key: 'ad_free_experience'
  },
  {
    icon: '🛠️',
    iconClass: 'text-cyan-400',
    isPremium: true,
    key: 'dedicated_instance'
  }
];
</script>

<template>
  <section class="py-16 bg-gray-900 border-t border-gray-800" id="features">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <h2 class="text-3xl md:text-4xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
          {{ $t('features.title') }}
        </h2>
        <p class="max-w-2xl mx-auto text-gray-300">
          {{ $t('features.subtitle') }}
        </p>
      </div>
      
      <div class="space-y-16 max-w-6xl mx-auto">
        <!-- Funzionalità Free -->
        <div>
          <div class="flex items-center mb-8">
            <div class="h-px bg-gray-700 flex-grow"></div>
            <span class="px-4 text-2xl font-bold text-gray-300">{{ $t('features.free.title') }}</span>
            <div class="h-px bg-gray-700 flex-grow"></div>
          </div>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div 
              v-for="(feature, index) in freeFeatures" 
              :key="`free-${index}`"
              class="feature-card p-6 rounded-lg shadow-xl transition-all duration-300 relative border border-gray-700/50"
            >
              <div :class="`text-4xl mb-4 group-hover:scale-110 transition-transform ${feature.iconClass}`">{{ feature.icon }}</div>
              <h3 class="text-xl font-semibold mb-2 text-gray-200">
                {{ $t(`features.free.items.${feature.key}.title`) }}
              </h3>
              <p class="text-gray-400">
                {{ $t(`features.free.items.${feature.key}.description`) }}
              </p>
              
              <!-- Badge "Soon" -->
              <div v-if="feature.isSoon" class="absolute top-2 right-2">
                <span class="inline-block px-2 py-1 text-xs font-semibold bg-amber-500/60 text-white rounded-full">
                  {{ $t('features.badges.soon') }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Funzionalità Premium -->
        <div>
          <div class="flex items-center mb-8">
            <div class="h-px bg-indigo-900/70 flex-grow"></div>
            <div class="px-6 py-2 bg-gradient-to-r from-indigo-800/70 to-purple-800/70 rounded-full">
              <span class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-purple-300">
                {{ $t('features.premium.title') }}
              </span>
            </div>
            <div class="h-px bg-indigo-900/70 flex-grow"></div>
          </div>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="(feature, index) in premiumFeatures" 
              :key="`premium-${index}`"
              class="feature-card feature-card-premium p-6 rounded-lg shadow-xl transition-all duration-300 relative border border-indigo-500/50"
            >
              <div :class="`text-4xl mb-4 group-hover:scale-110 transition-transform ${feature.iconClass}`">{{ feature.icon }}</div>
              <h3 class="text-xl font-semibold mb-2 text-indigo-300">
                {{ $t(`features.premium.items.${feature.key}.title`) }}
              </h3>
              <p class="text-gray-400">
                {{ $t(`features.premium.items.${feature.key}.description`) }}
              </p>
              
              <!-- Badge Premium -->
              <div class="absolute top-2 right-2" v-if="feature.isPremium && !feature.isSoon">
                <span class="inline-block px-2 py-1 text-xs font-semibold bg-indigo-900/70 text-indigo-300 rounded-full">
                  {{ $t('features.badges.premium') }}
                </span>
              </div>
              
              <!-- Badge "Soon" se la funzione è in arrivo -->
              <div v-if="feature.isSoon" class="absolute top-2 right-2">
                <span class="inline-block px-2 py-1 text-xs font-semibold bg-amber-500/60 text-white rounded-full">
                  {{ $t('features.badges.soon') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- CTA -->
      <div class="mt-16 text-center">
        <p class="text-lg text-gray-300 mb-6">{{ $t('features.cta.title') }}</p>
        <div class="flex items-center justify-center space-x-4">
          <button class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors duration-300 hover:cursor-pointer">
            {{ $t('features.cta.primary') }}
          </button>
          <button
           class="px-6 py-3 border border-gray-600 text-gray-300 hover:border-gray-400 hover:text-white font-medium rounded-lg transition-colors duration-300 hover:cursor-pointer">
            {{ $t('features.cta.secondary') }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Base card style */
.feature-card {
  backdrop-filter: blur(10px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.03));
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
  transition: all 0.3s ease-in-out;
  position: relative;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  border-color: rgba(255, 255, 255, 0.2);
}

/* Premium card style */
.feature-card-premium {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.05));
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
}

.feature-card-premium:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.08));
  box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.3);
  border-color: rgba(99, 102, 241, 0.4);
}

/* Soft glow effect on hover for all cards */
.feature-card:hover {
  box-shadow: 0 10px 40px -10px rgba(78, 78, 211, 0.4);
}

.feature-card-premium:hover {
  box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.5);
}

/* Icon animation */
.feature-card:hover .text-4xl {
  transform: scale(1.1);
}
</style>