<template>
  <div class="min-h-screen bg-gray-50 text-gray-800 font-sans">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <div class="text-xl font-bold text-blue-600">scAdapter</div>
        <div class="space-x-6">
          <router-link to="/" class="hover:text-blue-600 font-medium">New Job</router-link>
          <router-link to="/status" class="hover:text-blue-600 font-medium">Check Status</router-link>
          <router-link to="/about" class="hover:text-blue-600 font-medium">How it Works</router-link>
        </div>
      </div>
    </nav>

    <!-- Page Content -->
    <main class="max-w-6xl mx-auto px-4 py-8">
      <router-view />
    </main>
  </div>
</template>