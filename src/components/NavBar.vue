<template>
    <nav class="bg-gray-900 border-b border-gray-800 p-4">
      <div class="container mx-auto flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <img src="../assets/logo.png" alt="Logo" class="h-8 w-8 rounded-full" />
          <span class="text-xl font-bold text-indigo-400">TagEveryone_TheBot</span>
        </div>
          <div class="space-x-4">
              <router-link to="/" class="text-gray-300 hover:text-white transition">Home</router-link>
              <a href="#features" class="text-gray-300 hover:text-white transition">Features</a>
              <router-link to="/pricing" class="text-gray-300 hover:text-white transition">Pricing</router-link>
              <a href="#contact" class="text-gray-300 hover:text-white transition">Contact</a>
          </div>
          
        <button class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition hover:cursor-pointer">
          Get Started
        </button>
      </div>
    </nav>
  </template>