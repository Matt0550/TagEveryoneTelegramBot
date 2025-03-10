<script setup lang="ts">
const statistics = [
    {
        value: '10k+',
        label: 'Utenti menzionati',
        icon: 'users'
    },
    {
        value: '680+',
        label: 'Gruppi attivi',
        icon: 'groups'
    },
    {
        value: '3k+',
        label: 'Utenti attivi',
        icon: 'chart'
    },
    {
        value: '24/7',
        label: 'Supporto disponibile',
        icon: 'support'
    }
];

// Icone SVG inline per le statistiche
const icons = {
    users: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
         </svg>`,
    groups: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>`,
    chart: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
         </svg>`,
    support: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
           </svg>`
};
</script>

<template>
    <section class="py-16 relative my-16">
        <div class="container mx-auto px-4">
            <div class="stats-container glass shadow-2xl rounded-2xl mx-auto max-w-5xl">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-4 p-6 md:p-8">
                    <div v-for="(stat, index) in statistics" :key="index"
                        class="flex flex-col items-center text-center p-5 transition-transform duration-300 hover:transform hover:scale-105">
                        <!-- Icon with glowing background -->
                        <div class="mb-4 rounded-full p-3 bg-indigo-900/30 stat-icon-glow">
                            <div v-html="icons[stat.icon as keyof typeof icons]" class="text-indigo-400"></div>
                        </div>

                        <!-- Value with highlight -->
                        <div
                            class="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
                            {{ stat.value }}
                        </div>

                        <!-- Label -->
                        <p class="text-gray-300">{{ stat.label }}</p>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.stats-container {
    backdrop-filter: blur(10px);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(17, 24, 39, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-icon-glow {
    position: relative;
}

.stat-icon-glow:after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    padding: 2px;
    background: linear-gradient(135deg, rgba(130, 90, 235, 0.5), rgba(80, 70, 230, 0.5));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
}

@media (max-width: 768px) {
    .stats-container {
        margin-top: 2rem;
    }
}
</style>