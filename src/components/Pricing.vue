<script setup lang="ts">
import { ref, computed } from 'vue';

const billingCycle = ref('monthly');

interface Plan {
  id: string;
  price?: string;
  monthlyPrice?: string;
  yearlyPrice?: string;
  featuresCount: number; // Numero di funzionalità per questo piano
  buttonClass: string;
  highlight: boolean;
}

// Piani ottimizzati: separiamo la struttura dalle traduzioni
const plans: Plan[] = [
  {
    id: "free",
    price: "Free",
    featuresCount: 5, // Questo piano ha 5 funzionalità
    buttonClass: "bg-gray-700 hover:bg-gray-600",
    highlight: false
  },
  {
    id: "premium",
    monthlyPrice: "€14.99",
    yearlyPrice: "€143.99", // Prezzo annuale (risparmio di circa 2 mesi)
    featuresCount: 7, // Questo piano ha 7 funzionalità
    buttonClass: "bg-indigo-600 hover:bg-indigo-700",
    highlight: true
  },
  {
    id: "unlimited",
    monthlyPrice: "€24.99",
    yearlyPrice: "€239.99", // Prezzo annuale (risparmio di circa 2 mesi)
    featuresCount: 3, // Questo piano ha 3 funzionalità
    buttonClass: "bg-gray-700 hover:bg-gray-600",
    highlight: false
  }
];

// Calcola il risparmio annuale
const calculateSaving = (monthlyPrice: string, yearlyPrice: string) => {
  if (!monthlyPrice.startsWith('€') || !yearlyPrice.startsWith('€')) return null;

  const monthly = parseFloat(monthlyPrice.replace('€', ''));
  const yearly = parseFloat(yearlyPrice.replace('€', ''));
  const monthlyCost = monthly * 12;
  const saving = monthlyCost - yearly;

  return Math.round(saving);
};

// Calcola la percentuale di sconto per il piano annuale
const calculateDiscountPercentage = (plan: Plan) => {
  if (!plan.monthlyPrice || !plan.yearlyPrice) return null;

  const monthly = parseFloat(plan.monthlyPrice.replace('€', ''));
  const yearly = parseFloat(plan.yearlyPrice.replace('€', ''));

  const monthlyCost = monthly * 12;
  const discount = monthlyCost - yearly;
  const discountPercentage = Math.round((discount / monthlyCost) * 100);

  return discountPercentage;
};

// Calcola la percentuale di sconto media tra tutti i piani
const averageDiscountPercentage = computed(() => {
  const discounts = plans
    .filter(plan => plan.monthlyPrice && plan.yearlyPrice)
    .map(plan => calculateDiscountPercentage(plan))
    .filter(percentage => percentage !== null) as number[];

  if (discounts.length === 0) return 0;

  const sum = discounts.reduce((total, current) => total + current, 0);
  return Math.round(sum / discounts.length);
});
</script>

<template>
  <section class="py-20 bg-gray-900">
    <div class="container mx-auto px-4">
      <!-- Intestazione -->
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-3xl md:text-4xl font-bold mb-4 text-white">{{ $t('pricing.title') }}</h2>
        <p class="text-xl text-gray-300">{{ $t('pricing.subtitle') }}</p>
      </div>

      <!-- Selettore Mensile/Annuale -->
      <div class="flex justify-center items-center mb-12">
        <div class="inline-flex items-center p-1 rounded-full bg-gray-800 border border-gray-700">
          <button @click="billingCycle = 'monthly'" :class="[
            'py-2 px-6 rounded-full transition-all duration-200 font-medium text-sm hover:cursor-pointer',
            billingCycle === 'monthly' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:text-white'
          ]">
            {{ $t('pricing.monthly') }}
          </button>
          <button @click="billingCycle = 'yearly'" :class="[
            'py-2 px-6 rounded-full transition-all duration-200 font-medium text-sm relative hover:cursor-pointer',
            billingCycle === 'yearly' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:text-white'
          ]">
            {{ $t('pricing.yearly') }}
            <span class="absolute -top-3 -right-2 bg-green-500 text-xs py-0.5 px-1.5 rounded-full text-white">
              {{ $t('pricing.savingBadge', { discount: averageDiscountPercentage }) }}
            </span>
          </button>
        </div>
      </div>

      <!-- Piani di prezzo (un'unica griglia) -->
      <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <div v-for="(plan, index) in plans" :key="index" :class="[
          'glass rounded-xl overflow-hidden transition-all duration-300 transform hover:-translate-y-2',
          plan.highlight ? 'border-2 border-indigo-500 scale-105' : 'border border-gray-700'
        ]">
          <div :class="[
            'p-6 text-center',
            plan.highlight ? 'bg-gradient-to-br from-indigo-900/70 to-purple-900/70' : 'bg-gray-800/50'
          ]">
            <!-- Nome del piano -->
            <h3 class="text-xl font-bold text-white mb-2">{{ $t(`pricing.plans.${plan.id}.name`) }}</h3>

            <!-- Prezzo del piano -->
            <div class="flex items-center justify-center">
              <span class="text-3xl md:text-4xl font-extrabold text-white">
                {{ plan.price || (billingCycle === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice) }}
              </span>
              <span v-if="plan.monthlyPrice && plan.yearlyPrice" class="text-gray-400 ml-1">
                {{ $t(`pricing.plans.${plan.id}.period.${billingCycle}`) }}
              </span>
            </div>

            <!-- Descrizione del piano -->
            <p class="text-gray-400 mt-2">{{ $t(`pricing.plans.${plan.id}.description`) }}</p>

            <!-- Badge risparmio per piani annuali -->
            <div v-if="plan.monthlyPrice && plan.yearlyPrice && billingCycle === 'yearly'"
              class="mt-2 text-sm text-green-400 font-medium">
              {{ $t('pricing.saving', { amount: calculateSaving(plan.monthlyPrice, plan.yearlyPrice) }) }}
            </div>
            <div v-if="plan.monthlyPrice && plan.yearlyPrice && billingCycle === 'yearly'"
              class="mt-1 inline-block px-2 py-0.5 bg-green-500/20 text-green-400 rounded text-xs font-medium">
              {{ $t('pricing.discountPercentage', { discount: calculateDiscountPercentage(plan) }) }}
            </div>
          </div>

          <div class="p-6">
            <!-- Lista funzionalità -->
            <ul class="space-y-3 mb-6">
              <li v-for="i in plan.featuresCount" :key="i" class="flex items-start">
                <svg class="w-5 h-5 text-indigo-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-gray-300">{{ $t(`pricing.plans.${plan.id}.features.${i-1}`) }}</span>
              </li>
            </ul>

            <!-- Pulsante d'azione -->
            <button :class="[
              'w-full py-3 px-4 rounded-lg font-medium text-white transition-colors duration-300 hover:cursor-pointer',
              plan.buttonClass
            ]">
              {{ $t(`pricing.plans.${plan.id}.button`) }}
            </button>
          </div>

          <!-- Badge piano consigliato -->
          <div v-if="plan.highlight" class="bg-indigo-600 py-2 text-center text-sm font-medium text-white">
            {{ $t('pricing.plans.premium.recommended') }}
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="mt-24 max-w-3xl mx-auto">
        <h3 class="text-2xl font-bold mb-8 text-center text-white">{{ $t('faq.title') }}</h3>

        <div class="space-y-4">
          <div v-for="(question, index) in $tm('faq.questions')" :key="index"
            class="border border-gray-700 rounded-lg overflow-hidden">
            <details class="group">
              <summary class="flex justify-between items-center p-5 bg-gray-800/50 cursor-pointer">
                <h4 class="text-lg font-medium text-white">{{ question.question }}</h4>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none"
                  stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </summary>
              <div class="p-5 border-t border-gray-700">
                <p class="text-gray-300">{{ question.answer }}</p>
              </div>
            </details>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="mt-16 text-center">
        <div class="max-w-3xl mx-auto p-8 rounded-xl glass bg-gradient-to-r from-purple-900/30 to-indigo-900/30">
          <h3 class="text-2xl font-bold mb-4 text-white">{{ $t('pricing.cta.title') }}</h3>
          <p class="text-gray-300 mb-6">{{ $t('pricing.cta.subtitle') }}</p>
          <div class="flex flex-col md:flex-row gap-4 justify-center">
            <button
              class=" hover:cursor-pointer px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors duration-300">
              {{ $t('pricing.cta.primary') }}
            </button>
            <button
              class="hover:cursor-pointer px-6 py-3 border border-indigo-500 text-indigo-400 hover:bg-indigo-900/30 font-medium rounded-lg transition-colors duration-300">
              {{ $t('pricing.cta.secondary') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>