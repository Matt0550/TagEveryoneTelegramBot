<script setup lang="ts">
import Navbar from './components/NavBar.vue';

import Footer from './components/Footer.vue';
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-gray-100">
    <Navbar />

    <router-view />

    <Footer />
  </div>
</template>

<style>

</style>