<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

// Stato del form
const email = ref('');
const telegramUsername = ref('');
const subscribed = ref(false);
const hasParticipated = ref(false);
const submitting = ref(false);
const error = ref(false);
const submitted = ref(false);
const touchedFields = ref({ email: false, telegramUsername: false });

// Data di fine del giveaway (fissa per un mese da ora)
const endDate = new Date();
endDate.setMonth(endDate.getMonth() + 1);

// Countdown state
const remainingTime = ref({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
});

// Timer reference
let countdownTimer: number | null = null;

// Computed per il conteggio dei partecipanti (simulato)
const participantsCount = computed(() => {
    return Math.floor(Math.random() * 500) + 750; // Tra 750 e 1250
});

// Validazione email
const isValidEmail = (email: string): boolean => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

// Validazione username Telegram
const isValidTelegramUsername = (username: string): boolean => {
    // Accetta username con o senza @ iniziale, almeno 5 caratteri totali
    return /^@?[a-zA-Z0-9_]{4,}$/.test(username);
};

const isEmailValid = computed(() => {
    return email.value.trim() === '' || isValidEmail(email.value);
});

const isTelegramValid = computed(() => {
    return telegramUsername.value.trim() === '' || isValidTelegramUsername(telegramUsername.value);
});

const isFormValid = computed(() => {
    return isValidEmail(email.value) && isValidTelegramUsername(telegramUsername.value);
});

// Funzione per aggiornare il countdown
const updateCountdown = () => {
    const now = new Date();
    const timeLeft = endDate.getTime() - now.getTime();

    if (timeLeft <= 0) {
        // Il giveaway è terminato
        remainingTime.value = {
            days: 0,
            hours: 0,
            minutes: 0,
            seconds: 0
        };

        if (countdownTimer) {
            clearInterval(countdownTimer);
            countdownTimer = null;
        }
        return;
    }

    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    remainingTime.value = {
        days,
        hours,
        minutes,
        seconds
    };
};

// Segna un campo come "toccato" quando l'utente modifica il valore
const markAsTouched = (field: keyof typeof touchedFields.value) => {
    touchedFields.value[field] = true;
};

// Assicura che l'username Telegram abbia @
const formatTelegramUsername = () => {
    if (telegramUsername.value.trim() !== '' && !telegramUsername.value.startsWith('@')) {
        telegramUsername.value = '@' + telegramUsername.value;
    }
};

// Invio del form
const submitForm = async () => {
    // Segna tutti i campi come toccati in caso di tentativo di invio
    Object.keys(touchedFields.value).forEach(field => {
        touchedFields.value[field as keyof typeof touchedFields.value] = true;
    });

    if (!isFormValid.value) return;

    // Formatta l'username di telegram
    formatTelegramUsername();

    submitting.value = true;

    try {
        // Simuliamo una chiamata API
        await new Promise(resolve => setTimeout(resolve, 1500));

        submitted.value = true;
        error.value = false;

        // Reset del form
        email.value = '';
        telegramUsername.value = '';
        Object.keys(touchedFields.value).forEach(field => {
            touchedFields.value[field as keyof typeof touchedFields.value] = false;
        });
    } catch (e) {
        error.value = true;
    } finally {
        submitting.value = false;
    }
};

// Hook del ciclo di vita
onMounted(() => {
    updateCountdown();
    countdownTimer = window.setInterval(updateCountdown, 1000);
});

onUnmounted(() => {
    if (countdownTimer) {
        clearInterval(countdownTimer);
        countdownTimer = null;
    }
});

// Elementi del giveaway - regole e premi
const giveawayRules = [
    { id: 1, key: 'follow' },
    { id: 2, key: 'subscribe' },
    { id: 3, key: 'share' }
];

const prizeLevels = [
    { level: 1, key: 'first', winners: 3, prize: 'premium_year' },
    { level: 2, key: 'second', winners: 7, prize: 'premium_month' }
];
</script>

<template>
    <div class="min-h-screen flex flex-col bg-gray-900">

        <main class="flex-grow">
            <!-- Hero Section -->
            <section class="bg-gradient-to-r from-purple-900 to-indigo-800 py-12 md:py-20">
                <div class="container mx-auto px-4 text-center">
                    <div
                        class="inline-block px-3 py-1 bg-indigo-500 bg-opacity-30 rounded-full text-white text-sm font-semibold mb-4">
                        {{ $t('giveaway.limited') }}
                    </div>
                    <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                        {{ $t('giveaway.title') }}
                    </h1>
                    <p class="text-xl text-indigo-200 max-w-2xl mx-auto mb-8">
                        {{ $t('giveaway.subtitle') }}
                    </p>

                    <!-- Countdown Timer -->
                    <div
                        class="max-w-2xl mx-auto bg-gray-800 rounded-xl p-6 mb-8 backdrop-blur-sm bg-opacity-80 border border-gray-700 shadow-lg">
                        <h2 class="text-lg text-indigo-300 mb-4">{{ $t('giveaway.endsIn') }}</h2>
                        <div class="grid grid-cols-4 gap-4">
                            <div class="flex flex-col">
                                <div
                                    class="bg-indigo-800 text-white text-3xl md:text-4xl font-bold rounded-lg p-3 shadow-inner">
                                    {{ remainingTime.days }}
                                </div>
                                <span class="text-gray-300 mt-2">{{ $t('giveaway.days') }}</span>
                            </div>
                            <div class="flex flex-col">
                                <div
                                    class="bg-indigo-800 text-white text-3xl md:text-4xl font-bold rounded-lg p-3 shadow-inner">
                                    {{ remainingTime.hours }}
                                </div>
                                <span class="text-gray-300 mt-2">{{ $t('giveaway.hours') }}</span>
                            </div>
                            <div class="flex flex-col">
                                <div
                                    class="bg-indigo-800 text-white text-3xl md:text-4xl font-bold rounded-lg p-3 shadow-inner">
                                    {{ remainingTime.minutes }}
                                </div>
                                <span class="text-gray-300 mt-2">{{ $t('giveaway.minutes') }}</span>
                            </div>
                            <div class="flex flex-col">
                                <div
                                    class="bg-indigo-800 text-white text-3xl md:text-4xl font-bold rounded-lg p-3 shadow-inner">
                                    {{ remainingTime.seconds }}
                                </div>
                                <span class="text-gray-300 mt-2">{{ $t('giveaway.seconds') }}</span>
                            </div>
                        </div>

                        <div class="mt-6 text-center">
                            <div class="text-indigo-300 font-semibold">{{ $t('giveaway.participants') }}</div>
                            <div class="text-2xl font-bold text-white">{{ participantsCount }}</div>
                        </div>
                    </div>

                    <a href="#participate"
                        class="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg px-8 py-3 transition-colors duration-300 hover:shadow-lg">
                        {{ $t('giveaway.participateNow') }}
                    </a>
                </div>
            </section>

            <!-- About section -->
            <section class="py-16 bg-gray-850">
                <div class="container mx-auto px-4">
                    <div class="max-w-3xl mx-auto text-center mb-12">
                        <h2 class="text-3xl font-bold text-white mb-6">{{ $t('giveaway.about.title') }}</h2>
                        <p class="text-gray-300 mb-6">{{ $t('giveaway.about.description') }}</p>

                        <div class="grid md:grid-cols-2 gap-6 mt-10">
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 text-left">
                                <h3 class="text-xl font-semibold text-white mb-4">{{ $t('giveaway.about.prizes') }}</h3>
                                <ul class="space-y-3">
                                    <li v-for="prize in prizeLevels" :key="prize.level" class="flex items-start">
                                        <div
                                            class="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5 mr-3">
                                            <span class="text-white text-sm font-bold">{{ prize.level }}</span>
                                        </div>
                                        <div>
                                            <div class="font-medium text-white">{{
                                                $t(`giveaway.prizes.${prize.level}.title`) }}</div>
                                            <div class="text-gray-400">{{
                                                $t(`giveaway.prizes.${prize.level}.description`, {
                                                    count: prize.winners
                                                }) }}</div>
                                        </div>
                                    </li>
                                </ul>
                            </div>

                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 text-left">
                                <h3 class="text-xl font-semibold text-white mb-4">{{ $t('giveaway.about.howToEnter') }}
                                </h3>
                                <ul class="space-y-3">
                                    <li v-for="rule in giveawayRules" :key="rule.id" class="flex items-start">
                                        <div
                                            class="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5 mr-3">
                                            <span class="text-white text-sm font-bold">{{ rule.id }}</span>
                                        </div>
                                        <div class="text-gray-300">
                                            {{ $t(`giveaway.rules.${rule.key}`) }}
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Entry Form -->
            <section id="participate" class="">
                <div class="container mx-auto px-4">
                    <div class="max-w-xl mx-auto">
                        <h2 class="text-3xl font-bold text-white text-center mb-8">{{ $t('giveaway.participate.title')
                            }}</h2>

                        <div v-if="submitted"
                            class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded mb-8">
                            <div class="font-medium">{{ $t('giveaway.participate.success.title') }}</div>
                            <p>{{ $t('giveaway.participate.success.message') }}</p>
                        </div>

                        <div v-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded mb-8">
                            <div class="font-medium">{{ $t('giveaway.participate.error.title') }}</div>
                            <p>{{ $t('giveaway.participate.error.message') }}</p>
                        </div>

                        <form v-if="!submitted" @submit.prevent="submitForm"
                            class="bg-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg giveaway-form">
                            <!-- Email -->
                            <div class="mb-6">
                                <label for="email" class="block text-sm font-medium text-gray-300 mb-1">
                                    {{ $t('giveaway.participate.email') }} *
                                </label>
                                <input type="email" id="email" v-model="email" @blur="markAsTouched('email')"
                                    @input="markAsTouched('email')"
                                    class="w-full px-4 py-2 rounded-md bg-gray-700 border text-white focus:outline-none focus:ring-2"
                                    :class="[
                                        touchedFields.email && !isEmailValid ?
                                            'border-red-500 focus:ring-red-500' :
                                            'border-gray-600 focus:ring-indigo-500'
                                    ]" :placeholder="$t('giveaway.participate.emailPlaceholder')" required />
                                <p v-if="touchedFields.email && !isEmailValid" class="mt-1 text-sm text-red-500">
                                    {{ $t('giveaway.participate.emailInvalid') }}
                                </p>
                            </div>

                            <!-- Telegram Username -->
                            <div class="mb-6">
                                <label for="telegramUsername" class="block text-sm font-medium text-gray-300 mb-1">
                                    {{ $t('giveaway.participate.telegram') }} *
                                </label>
                                <input type="text" id="telegramUsername" v-model="telegramUsername"
                                    @blur="markAsTouched('telegramUsername'); formatTelegramUsername();"
                                    @input="markAsTouched('telegramUsername')"
                                    class="w-full px-4 py-2 rounded-md bg-gray-700 border text-white focus:outline-none focus:ring-2"
                                    :class="[
                                        touchedFields.telegramUsername && !isTelegramValid ?
                                            'border-red-500 focus:ring-red-500' :
                                            'border-gray-600 focus:ring-indigo-500'
                                    ]" :placeholder="$t('giveaway.participate.telegramPlaceholder')" required />
                                <p v-if="touchedFields.telegramUsername && !isTelegramValid"
                                    class="mt-1 text-sm text-red-500">
                                    {{ $t('giveaway.participate.telegramInvalid') }}
                                </p>
                            </div>

                            <!-- Newsletter Subscription -->
                            <div class="flex items-start mb-6">
                                <div class="flex items-center h-5">
                                    <input id="newsletter" type="checkbox" v-model="subscribed"
                                        class="w-4 h-4 rounded bg-gray-700 border-gray-600 focus:ring-indigo-600 focus:ring-offset-gray-800" />
                                </div>
                                <label for="newsletter" class="ml-2 text-sm font-medium text-gray-300">
                                    {{ $t('giveaway.participate.newsletter') }}
                                </label>
                            </div>

                            <!-- Terms and conditions -->
                            <div class="flex items-start mb-6">
                                <div class="flex items-center h-5">
                                    <input id="terms" type="checkbox" v-model="hasParticipated"
                                        class="w-4 h-4 rounded bg-gray-700 border-gray-600 focus:ring-indigo-600 focus:ring-offset-gray-800"
                                        required />
                                </div>
                                <label for="terms" class="ml-2 text-sm font-medium text-gray-300">
                                    {{ $t('giveaway.participate.termsAgreement') }}
                                    <a href="#" class="text-indigo-400 hover:text-indigo-300">{{
                                        $t('giveaway.participate.termsLink') }}</a>
                                </label>
                            </div>

                            <!-- Submit Button -->
                            <button type="submit"
                                class="w-full py-3 bg-indigo-600 text-white font-medium rounded-lg transition-colors duration-300 flex items-center justify-center"
                                :class="{
                                    'hover:bg-indigo-700 hover:cursor-pointer': isFormValid && !submitting,
                                    'opacity-60 cursor-not-allowed': !isFormValid || submitting
                                }" :disabled="!isFormValid || submitting">
                                <svg v-if="submitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                    </path>
                                </svg>
                                {{ submitting ? $t('giveaway.participate.submitting') :
                                    $t('giveaway.participate.submit') }}
                            </button>
                        </form>

                        <div v-else class="text-center mt-8">
                            <button @click="submitted = false"
                                class="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors">
                                {{ $t('giveaway.participate.enterAgain') }}
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- FAQ -->
            <section class="py-16 bg-gray-850">
                <div class="container mx-auto px-4">
                    <div class="max-w-3xl mx-auto">
                        <h2 class="text-3xl font-bold text-white text-center mb-8">{{ $t('giveaway.faq.title') }}</h2>

                        <div class="space-y-4">
                            <div class="border border-gray-700 rounded-lg overflow-hidden bg-gray-800">
                                <details class="group">
                                    <summary class="flex justify-between items-center p-5 cursor-pointer">
                                        <h3 class="text-lg font-medium text-white">{{ $t('giveaway.faq.q1') }}</h3>
                                        <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform"
                                            fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </summary>
                                    <div class="p-5 border-t border-gray-700 text-gray-300">
                                        <p>{{ $t('giveaway.faq.a1') }}</p>
                                    </div>
                                </details>
                            </div>

                            <div class="border border-gray-700 rounded-lg overflow-hidden bg-gray-800">
                                <details class="group">
                                    <summary class="flex justify-between items-center p-5 cursor-pointer">
                                        <h3 class="text-lg font-medium text-white">{{ $t('giveaway.faq.q2') }}</h3>
                                        <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform"
                                            fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </summary>
                                    <div class="p-5 border-t border-gray-700 text-gray-300">
                                        <p>{{ $t('giveaway.faq.a2') }}</p>
                                    </div>
                                </details>
                            </div>

                            <div class="border border-gray-700 rounded-lg overflow-hidden bg-gray-800">
                                <details class="group">
                                    <summary class="flex justify-between items-center p-5 cursor-pointer">
                                        <h3 class="text-lg font-medium text-white">{{ $t('giveaway.faq.q3') }}</h3>
                                        <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform"
                                            fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </summary>
                                    <div class="p-5 border-t border-gray-700 text-gray-300">
                                        <p>{{ $t('giveaway.faq.a3') }}</p>
                                    </div>
                                </details>
                            </div>

                            <div class="border border-gray-700 rounded-lg overflow-hidden bg-gray-800">
                                <details class="group">
                                    <summary class="flex justify-between items-center p-5 cursor-pointer">
                                        <h3 class="text-lg font-medium text-white">{{ $t('giveaway.faq.q4') }}</h3>
                                        <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform"
                                            fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </summary>
                                    <div class="p-5 border-t border-gray-700 text-gray-300">
                                        <p>{{ $t('giveaway.faq.a4') }}</p>
                                    </div>
                                </details>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>
