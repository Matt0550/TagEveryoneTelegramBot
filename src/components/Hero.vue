<script setup lang="ts">
// Scroll
const scrollToFeatures = () => {
    document.querySelector('#features')?.scrollIntoView({ behavior: 'smooth' });
};
</script>

<template>
    <section class="bg-gradient-to-r from-purple-700 to-indigo-900 py-16">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row items-center justify-between">
                <div class="md:w-1/2 mb-8 md:mb-0 text-white">
                    <!-- Titolo migliorato con stile accattivante -->
                    <div class="mb-6">
                        <h1 class="text-5xl md:text-6xl font-extrabold leading-tight">
                            <span class="inline-block relative text-white">
                                Tag <span class="text-indigo-300">Everyone</span>
                                <span
                                    class="absolute -bottom-3 left-0 w-full h-1 bg-gradient-to-r from-indigo-400 to-purple-400"></span>
                            </span>
                            <span class="block mt-4 text-3xl md:text-4xl text-indigo-300 font-bold tracking-wide">
                                Premium <span class="relative inline-block">
                                    <span
                                        class="absolute -top-5 -right-8 bg-indigo-500 text-white text-xs px-2 py-0.5 rounded-md font-normal transform rotate-12">{{
                                        $t('hero.badgeNew') }}</span>
                                </span>
                            </span>
                        </h1>
                    </div>

                    <p class="text-xl mb-8 text-gray-300">
                        {{ $t('hero.subtitle') }}
                    </p>

                    <!-- Pulsanti con contrasto migliorato -->
                    <div class="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                        <router-link to="/pricing"> <button
                                class="hover:cursor-pointer bg-white text-indigo-900 px-8 py-3 rounded-lg font-bold shadow-lg hover:bg-gray-100 transition transform hover:-translate-y-1">
                                {{ $t('hero.cta') }}
                            </button>
                        </router-link>

                        <a href="#features"
                            class="hover:cursor-pointer border-2 border-white text-white px-8 py-3 rounded-lg font-bold hover:bg-white/20 transition transform hover:-translate-y-1">
                            {{ $t('hero.secondaryCta') }}
                        </a>

                    </div>
                </div>

                <div class="md:w-1/2 flex justify-center rotate-[-15deg]">
                    <div
                        class="relative mx-auto border-gray-800 dark:border-gray-800 bg-gray-800 border-[14px] rounded-[2.5rem] h-[600px] w-[300px] shadow-2xl">
                        <div
                            class="w-[148px] h-[18px] bg-gray-800 top-0 rounded-b-[1rem] left-1/2 -translate-x-1/2 absolute">
                        </div>
                        <div class="h-[46px] w-[3px] bg-gray-800 absolute -start-[17px] top-[124px] rounded-s-lg"></div>
                        <div class="h-[46px] w-[3px] bg-gray-800 absolute -start-[17px] top-[178px] rounded-s-lg"></div>
                        <div class="h-[64px] w-[3px] bg-gray-800 absolute -end-[17px] top-[142px] rounded-e-lg"></div>
                        <!-- Schermo -->
                        <div class="rounded-[2rem] overflow-hidden w-[272px] h-[572px] bg-gray-900">
                            <!-- Chat Interface -->
                            <div class="flex flex-col h-full mt-4">
                                <!-- Chat Header -->
                                <div class="p-4 bg-gray-900 border-b border-gray-700">
                                    <div class="flex items-center">
                                        <img src="../assets/logo.png" alt="Logo" class="w-8 h-8 rounded-full mr-3" />
                                        <div class="font-medium text-white">TagEveryone Bot</div>
                                    </div>
                                </div>

                                <!-- Chat Messages -->
                                <div class="flex-1 p-4 flex flex-col gap-3 overflow-y-auto">
                                    <!-- User Message -->
                                    <div class="flex flex-col max-w-[80%] self-end">
                                        <div
                                            class="bg-indigo-600 text-white px-3.5 py-2.5 rounded-2xl rounded-br-sm text-sm">
                                            @everyone
                                        </div>
                                        <span class="text-xs text-gray-500 mt-1 self-end mr-1">12:42</span>
                                    </div>

                                    <!-- Bot Message -->
                                    <div class="flex flex-col max-w-[80%] self-start">
                                        <div
                                            class="bg-gray-700 text-white px-3.5 py-2.5 rounded-2xl rounded-bl-sm text-sm">
                                            {{ $t('hero.botMessage') }}
                                            <div class="text-xs mt-1 text-indigo-300">
                                                @NovaByteX @ShadowCircuit7 @EchoVortex99 @GlitchPhantomX
                                                @QuantumNebula_42 @CyberHawkRex @PixelRogue777 @NeonSpecter_21
                                            </div>
                                        </div>
                                        <span class="text-xs text-gray-500 mt-1 self-start ml-1">12:42</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
/* Effetto glow sottile intorno al badge "NEW" */
.rotate-12 {
    filter: drop-shadow(0 0 6px rgba(99, 102, 241, 0.8));
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: rotate(12deg) scale(1);
    }

    50% {
        transform: rotate(12deg) scale(1.1);
    }

    100% {
        transform: rotate(12deg) scale(1);
    }
}

/* Aggiunta di una leggera ombra al testo per migliorare la leggibilità sul gradiente */
h1 {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>