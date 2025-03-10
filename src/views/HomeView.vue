<script setup lang="ts">
import Hero from '../components/Hero.vue';
import Features from '../components/Features.vue';
import Statistics from '../components/Statistics.vue';

</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-gray-100">
    <Hero />
    <Statistics />
    <Features />

  </div>
</template>

<style>
/* Gli stili globali sono in style.css */
body {
  background-color: #111827; /* bg-gray-900 */
  color: #f3f4f6; /* text-gray-100 */
}
</style>