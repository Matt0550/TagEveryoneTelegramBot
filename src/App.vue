<script setup lang="ts">

import Navbar from './components/NavBar.vue';
import Footer from './components/Footer.vue';

</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-gray-100">
    <Navbar />

    <transition name="fade-slide" mode="out-in">
      <router-view />
    </transition>

    <Footer />
  </div>
</template>

<style>
/* Transizioni di base per tutte le pagine */
.fade-slide-enter-active {
  transition: all 0.3s ease-out;
}

.fade-slide-leave-active {
  transition: all 0.25s ease-in;
}

.fade-slide-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.fade-slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* Transizione alternativa che puoi attivare cambiando il nome della transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Transizione con fade semplice */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>