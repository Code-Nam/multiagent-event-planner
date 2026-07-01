<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <nav class="border-b border-gray-200 bg-white shadow-sm">
      <div class="mx-auto flex h-14 max-w-6xl items-center gap-1 px-4">
        <span class="mr-4 text-lg font-bold tracking-tight text-indigo-600">Token Dashboard</span>
        <RouterLink
          to="/sessions"
          class="rounded px-3 py-1.5 text-sm font-medium text-gray-600 transition-colors hover:bg-indigo-50 hover:text-indigo-600"
          active-class="bg-indigo-50 text-indigo-600"
        >
          Sessions
        </RouterLink>
      </div>
    </nav>
    <main class="mx-auto max-w-6xl px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
