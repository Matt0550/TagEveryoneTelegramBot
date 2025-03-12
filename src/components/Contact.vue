<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// Stati del form
const name = ref('');
const email = ref('');
const subject = ref('');
const message = ref('');
const submitted = ref(false);
const submitting = ref(false);
const error = ref(false);

// Stato per tenere traccia dei campi toccati (per mostrare errori solo dopo interazione)
const touchedFields = ref({
  name: false,
  email: false,
  subject: false,
  message: false
});

// Segna un campo come "toccato" quando l'utente modifica il valore
const markAsTouched = (field: keyof typeof touchedFields.value) => {
  touchedFields.value[field] = true;
};

// Definizione delle interfacce
interface ContactSubject {
    value: string;
    key: string; // Chiave per le traduzioni
}

interface ContactMethod {
    icon: string;
    key: string; // Chiave per le traduzioni
    link: string;
}

// Categorie di contatto - solo valori e chiavi, senza hardcoding delle traduzioni
const contactSubjectsList: ContactSubject[] = [
    { value: 'general', key: 'general' },
    { value: 'support', key: 'support' },
    { value: 'billing', key: 'billing' },
    { value: 'partnership', key: 'partnership' },
    { value: 'other', key: 'other' }
];

// Computed property per accedere alle traduzioni
const contactSubjects = computed(() => {
    return contactSubjectsList.map(subject => ({
        value: subject.value,
        label: t(`contact.form.subjects.${subject.key}`)
    }));
});

// Metodi di contatto secondari - solo struttura e chiavi
const contactMethodsList: ContactMethod[] = [
    {
        icon: 'telegram',
        key: 'telegram',
        link: 'https://t.me/TagEveryoneSupport'
    },
    {
        icon: 'email',
        key: 'email',
        link: 'mailto:support@tageveryone.xyz'
    }
];

// Computed property per i metodi di contatto con le traduzioni
const contactMethods = computed(() => {
    return contactMethodsList.map(method => ({
        icon: method.icon,
        title: t(`contact.methods.${method.key}.title`),
        description: t(`contact.methods.${method.key}.description`),
        action: t(`contact.methods.${method.key}.action`),
        link: method.link
    }));
});

// Validazione del form
const isValidEmail = (email: string): boolean => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

// Computed property per verificare la validità dell'email
const isEmailValid = computed(() => {
    return email.value.trim() === '' || isValidEmail(email.value);
});

// Computed property per verificare la lunghezza del messaggio
const isMessageValid = computed(() => {
    return message.value.trim() === '' || message.value.trim().length >= 10;
});

// Computed property per validare tutto il form
const isFormValid = computed(() => {
    return name.value.trim() !== '' &&
        isValidEmail(email.value) &&
        subject.value !== '' &&
        message.value.trim().length >= 10;
});

// Invio del form
const submitForm = async () => {
    // Segna tutti i campi come toccati in caso di tentativo di invio
    Object.keys(touchedFields.value).forEach(field => {
        touchedFields.value[field as keyof typeof touchedFields.value] = true;
    });
    
    if (!isFormValid.value) return;

    submitting.value = true;

    try {
        // Simuliamo una chiamata API
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Resetta il form dopo l'invio
        name.value = '';
        email.value = '';
        subject.value = '';
        message.value = '';
        
        // Resetta anche lo stato dei campi toccati
        Object.keys(touchedFields.value).forEach(field => {
            touchedFields.value[field as keyof typeof touchedFields.value] = false;
        });

        submitted.value = true;
        error.value = false;
    } catch (e) {
        error.value = true;
    } finally {
        submitting.value = false;
    }
};

// Icone SVG per i metodi di contatto
const iconSvgs: { [key: string]: string } = {
    telegram: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm5.894 8.221-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295l.213-3.053 5.56-5.023c.24-.213-.054-.334-.373-.121l-6.87 4.326-2.962-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.831.941z"/>
            </svg>`,
    email: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
           <path d="M0 3v18h24v-18h-24zm21.518 2l-9.518 7.713-9.518-7.713h19.036zm-19.518 14v-11.817l10 8.104 10-8.104v11.817h-20z"/>
         </svg>`
};
</script>

<template>
    <div class="min-h-screen flex flex-col bg-gray-900">
        <main class="flex-grow">
            <!-- Hero Section -->
            <section class="bg-gradient-to-r from-purple-900 to-indigo-800 py-16">
                <div class="container mx-auto px-4 text-center">
                    <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">{{ $t('contact.title') }}</h1>
                    <p class="text-xl text-indigo-200 max-w-xl mx-auto">{{ $t('contact.subtitle') }}</p>
                </div>
            </section>

            <!-- Contact Form Section -->
            <section class="py-16">
                <div class="container mx-auto px-4">
                    <div class="max-w-5xl mx-auto">
                        <div class="grid md:grid-cols-2 gap-12">
                            <!-- Form -->
                            <div class="bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-700 contact-form">
                                <h2 class="text-2xl font-bold text-white mb-6">{{ $t('contact.form.title') }}</h2>

                                <div v-if="submitted"
                                    class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded mb-6">
                                    <p>{{ $t('contact.form.success') }}</p>
                                </div>

                                <div v-if="error"
                                    class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded mb-6">
                                    <p>{{ $t('contact.form.error') }}</p>
                                </div>

                                <form @submit.prevent="submitForm" class="space-y-4">
                                    <!-- Nome -->
                                    <div>
                                        <label for="name" class="block text-sm font-medium text-gray-300 mb-1">
                                            {{ $t('contact.form.name') }}
                                        </label>
                                        <input type="text" id="name" v-model="name"
                                            @blur="markAsTouched('name')"
                                            class="w-full px-4 py-2 rounded-md bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                            :placeholder="$t('contact.form.namePlaceholder')" required />
                                    </div>

                                    <!-- Email -->
                                    <div>
                                        <label for="email" class="block text-sm font-medium text-gray-300 mb-1">
                                            {{ $t('contact.form.email') }}
                                        </label>
                                        <input type="email" id="email" v-model="email"
                                            @blur="markAsTouched('email')"
                                            @input="markAsTouched('email')"
                                            class="w-full px-4 py-2 rounded-md bg-gray-700 border text-white focus:outline-none focus:ring-2"
                                            :class="[
                                                touchedFields.email && !isEmailValid ? 
                                                'border-red-500 focus:ring-red-500' : 
                                                'border-gray-600 focus:ring-indigo-500'
                                            ]"
                                            :placeholder="$t('contact.form.emailPlaceholder')" required />
                                        <p v-if="touchedFields.email && !isEmailValid" class="mt-1 text-sm text-red-500">
                                            {{ $t('contact.form.emailInvalid') }}
                                        </p>
                                    </div>

                                    <!-- Oggetto -->
                                    <div>
                                        <label for="subject" class="block text-sm font-medium text-gray-300 mb-1">
                                            {{ $t('contact.form.subject') }}
                                        </label>
                                        <select id="subject" v-model="subject"
                                            @blur="markAsTouched('subject')"
                                            class="w-full px-4 py-2 rounded-md bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                            required>
                                            <option value="" disabled selected>{{ $t('contact.form.subjectPlaceholder') }}</option>
                                            <option v-for="option in contactSubjects" :key="option.value" :value="option.value">
                                                {{ option.label }}
                                            </option>
                                        </select>
                                    </div>

                                    <!-- Messaggio -->
                                    <div>
                                        <label for="message" class="block text-sm font-medium text-gray-300 mb-1">
                                            {{ $t('contact.form.message') }}
                                        </label>
                                        <textarea id="message" v-model="message" rows="5"
                                            @blur="markAsTouched('message')"
                                            @input="markAsTouched('message')"
                                            class="w-full px-4 py-2 rounded-md bg-gray-700 border text-white focus:outline-none focus:ring-2"
                                            :class="[
                                                touchedFields.message && !isMessageValid ? 
                                                'border-red-500 focus:ring-red-500' : 
                                                'border-gray-600 focus:ring-indigo-500'
                                            ]"
                                            :placeholder="$t('contact.form.messagePlaceholder')" required></textarea>
                                        <p v-if="touchedFields.message && !isMessageValid" class="mt-1 text-sm text-red-500">
                                            {{ $t('contact.form.messageInvalid') }}
                                        </p>
                                    </div>

                                    <!-- Pulsante invio -->
                                    <div>
                                        <button type="submit"
                                            class="w-full py-3 bg-indigo-600 text-white font-medium rounded-lg transition-colors duration-300 flex items-center justify-center"
                                            :class="{
                                                'hover:bg-indigo-700 hover:cursor-pointer': isFormValid && !submitting,
                                                'opacity-60 cursor-not-allowed': !isFormValid || submitting
                                            }"
                                            :disabled="!isFormValid || submitting">
                                            <svg v-if="submitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                                xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                                    stroke-width="4"></circle>
                                                <path class="opacity-75" fill="currentColor"
                                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                                </path>
                                            </svg>
                                            {{ submitting ? $t('contact.form.sending') : $t('contact.form.send') }}
                                        </button>
                                    </div>
                                </form>
                            </div>

                            <!-- Alternative contact methods -->
                            <div>
                                <h2 class="text-2xl font-bold text-white mb-6">{{ $t('contact.alternativesTitle') }}</h2>

                                <div class="space-y-6">
                                    <div v-for="(method, index) in contactMethods" :key="index"
                                        class="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-indigo-500 transition-colors duration-300 contact-method">
                                        <div class="flex items-start">
                                            <div class="flex-shrink-0 bg-indigo-900/50 p-3 rounded-lg mr-4">
                                                <div class="text-indigo-400" v-html="iconSvgs[method.icon]"></div>
                                            </div>
                                            <div>
                                                <h3 class="text-lg font-medium text-white">{{ method.title }}</h3>
                                                <p class="text-gray-400 mt-1">{{ method.description }}</p>
                                                <a :href="method.link" target="_blank" rel="noopener noreferrer"
                                                    class="inline-block mt-3 text-indigo-400 hover:text-indigo-300 transition-colors duration-300">
                                                    {{ method.action }} →
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<style scoped>
/* Animazione per le cards dei metodi di contatto */
.contact-method:hover,
.contact-form:hover {
    box-shadow: 0 0 25px rgba(99, 102, 241, 0.2);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>