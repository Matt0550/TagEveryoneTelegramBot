<script setup lang="ts">
const plans = [
  {
    name: "Base",
    price: "Gratis",
    description: "Perfetto per piccoli gruppi",
    features: [
      "Prestazioni limitate",
      "Menzioni illimitate",
      "Gruppi illimitati",
      "Log di attività",
      "Annunci pubblicitari"
    ],
    button: {
      text: "Inizia Gratis",
      class: "bg-gray-700 hover:bg-gray-600"
    },
    highlight: false
  },
  {
    name: "Premium",
    price: "€14.99",
    period: "/ mese / gruppo",
    description: "Per gruppi di medie dimensioni",
    features: [
      "Tutto del piano Base",
      "Istanza dedicata",
      "Funzioni aggiuntive (es. liste)",
      "Cooldown ridotto",
      "Nessun log di attività",
      "Supporto prioritario",
      "Nessuna pubblicità"
    ],
    button: {
      text: "Inizia ora",
      class: "bg-indigo-600 hover:bg-indigo-700"
    },
    highlight: true
  },
  {
    name: "Unlimited",
    price: "€24.99",
    period: "/ mese",
    description: "Per ∞ gruppi e utenti",
    features: [
      "Tutto del piano Premium",
      "Gruppi illimitati",
      "Utenti illimitati",
      
      
    ],
    button: {
      text: "Contattaci",
      class: "bg-gray-700 hover:bg-gray-600"
    },
    highlight: false
  }
];
</script>

<template>
  <section class="py-20 bg-gray-900">
    <div class="container mx-auto px-4">
      <!-- Intestazione -->
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-3xl md:text-4xl font-bold mb-4 text-white">Scegli il piano più adatto a te</h2>
        <p class="text-xl text-gray-300">Piani flessibili per ogni esigenza. Ottieni di più con TagEveryone Premium.</p>
      </div>

      <!-- Piani di prezzo -->
      <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <div v-for="(plan, index) in plans" :key="index" 
             :class="[
               'glass rounded-xl overflow-hidden transition-all duration-300 transform hover:-translate-y-2',
               plan.highlight ? 'border-2 border-indigo-500 scale-105' : 'border border-gray-700'
             ]">
          <div :class="[
                 'p-6 text-center',
                 plan.highlight ? 'bg-gradient-to-br from-indigo-900/70 to-purple-900/70' : 'bg-gray-800/50'
               ]">
            <h3 class="text-xl font-bold text-white mb-2">{{ plan.name }}</h3>
            <div class="flex items-center justify-center">
              <span class="text-3xl md:text-4xl font-extrabold text-white">{{ plan.price }}</span>
              <span v-if="plan.period" class="text-gray-400 ml-1">{{ plan.period }}</span>
            </div>
            <p class="text-gray-400 mt-2">{{ plan.description }}</p>
          </div>
          
          <div class="p-6">
            <ul class="space-y-3 mb-6">
              <li v-for="(feature, featureIndex) in plan.features" :key="featureIndex" class="flex items-start">
                <svg class="w-5 h-5 text-indigo-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                     xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-gray-300">{{ feature }}</span>
              </li>
            </ul>
            <button :class="[
                      'w-full py-3 px-4 rounded-lg font-medium text-white transition-colors duration-300 hover:cursor-pointer',
                      plan.button.class
                    ]">
              {{ plan.button.text }}
            </button>
          </div>
          
          <div v-if="plan.highlight" class="bg-indigo-600 py-2 text-center text-sm font-medium text-white">
            Piano consigliato
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="mt-24 max-w-3xl mx-auto">
        <h3 class="text-2xl font-bold mb-8 text-center text-white">Domande frequenti</h3>
        
        <div class="space-y-4">
          <div class="border border-gray-700 rounded-lg overflow-hidden">
            <details class="group">
              <summary class="flex justify-between items-center p-5 bg-gray-800/50 cursor-pointer">
                <h4 class="text-lg font-medium text-white">Posso cambiare piano in qualsiasi momento?</h4>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </summary>
              <div class="p-5 border-t border-gray-700">
                <p class="text-gray-300">Sì, puoi facilmente passare da un piano all'altro in qualsiasi momento. Se effettui l'upgrade, la differenza sarà calcolata proporzionalmente al tempo rimanente dell'abbonamento corrente.</p>
              </div>
            </details>
          </div>
          
          <div class="border border-gray-700 rounded-lg overflow-hidden">
            <details class="group">
              <summary class="flex justify-between items-center p-5 bg-gray-800/50 cursor-pointer">
                <h4 class="text-lg font-medium text-white">Quali metodi di pagamento accettate?</h4>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </summary>
              <div class="p-5 border-t border-gray-700">
                <p class="text-gray-300">Accettiamo tutte le principali carte di credito (Visa, Mastercard, American Express), PayPal, e bonifici bancari per le aziende.</p>
              </div>
            </details>
          </div>
          
          <div class="border border-gray-700 rounded-lg overflow-hidden">
            <details class="group">
              <summary class="flex justify-between items-center p-5 bg-gray-800/50 cursor-pointer">
                <h4 class="text-lg font-medium text-white">Posso annullare il mio abbonamento?</h4>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </summary>
              <div class="p-5 border-t border-gray-700">
                <p class="text-gray-300">Puoi annullare il tuo abbonamento in qualsiasi momento. L'accesso ai servizi premium rimarrà attivo fino alla fine del periodo di fatturazione corrente.</p>
              </div>
            </details>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="mt-16 text-center">
        <div class="max-w-3xl mx-auto p-8 rounded-xl glass bg-gradient-to-r from-purple-900/30 to-indigo-900/30">
          <h3 class="text-2xl font-bold mb-4 text-white">Hai ancora domande?</h3>
          <p class="text-gray-300 mb-6">Il nostro team è pronto ad aiutarti a scegliere il piano più adatto alle tue esigenze.</p>
          <div class="flex flex-col md:flex-row gap-4 justify-center">
            <button class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors duration-300">
              Contattaci
            </button>
            <button class="px-6 py-3 border border-indigo-500 text-indigo-400 hover:bg-indigo-900/30 font-medium rounded-lg transition-colors duration-300">
              FAQ
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
