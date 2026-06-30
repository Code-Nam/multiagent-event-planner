<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const navLinks = [
  { to: '/setup', label: 'Setup' },
  { to: '/venues', label: 'Venues' },
  { to: '/budget', label: 'Budget' },
  { to: '/plan', label: 'Plan' },
  { to: '/emails', label: 'Emails' },
  { to: '/export', label: 'Export' },
  { to: '/pipeline', label: 'Pipeline' }
]
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <nav class="bg-white border-b border-gray-200 shadow-sm">
      <div class="max-w-6xl mx-auto px-4 flex items-center gap-1 h-14">
        <span class="font-bold text-indigo-600 mr-4 text-lg tracking-tight">AGEVP</span>
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="px-3 py-1.5 rounded text-sm font-medium text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
          active-class="text-indigo-600 bg-indigo-50"
        >
          {{ link.label }}
        </RouterLink>
      </div>
    </nav>
    <main class="max-w-6xl mx-auto px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
