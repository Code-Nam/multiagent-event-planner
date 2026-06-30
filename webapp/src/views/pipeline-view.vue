<script setup lang="ts">
import { usePipelineStore } from '../stores/pipeline'
import PipelineProgress from '../components/pipeline-progress.vue'

const store = usePipelineStore()
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">Pipeline</h1>
        <p class="text-sm text-gray-500">Live agent output stream.</p>
      </div>
      <div class="flex items-center gap-3">
        <span
          v-if="store.currentAgent"
          class="rounded-full bg-indigo-100 text-indigo-700 px-3 py-1 text-xs font-medium"
        >
          {{ store.currentAgent }}
        </span>
        <button
          class="rounded-md border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition-colors"
          @click="store.clear()"
        >
          Clear
        </button>
      </div>
    </div>

    <div
      v-if="store.error"
      class="mb-4 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700"
    >
      {{ store.error }}
    </div>

    <PipelineProgress :log="store.log" :running="store.running" />

    <p class="mt-4 text-xs text-gray-400">
      Run an agent from any view (Venues, Budget, Plan, Export) to see live output here.
    </p>
  </div>
</template>
