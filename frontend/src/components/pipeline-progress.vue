<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  log: string[]
  running: boolean
}>()

const container = ref<HTMLElement | null>(null)

watch(
  () => props.log.length,
  async () => {
    await nextTick()
    if (container.value) {
      container.value.scrollTop = container.value.scrollHeight
    }
  }
)
</script>

<template>
  <div class="rounded-md border border-gray-200 bg-gray-900 text-green-300 font-mono text-xs">
    <div class="flex items-center justify-between px-3 py-2 border-b border-gray-700">
      <span class="text-gray-400 text-xs uppercase tracking-wider">Agent output</span>
      <span v-if="running" class="flex items-center gap-1.5 text-yellow-400">
        <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Running…
      </span>
      <span v-else-if="log.length" class="text-green-400 text-xs">Done</span>
    </div>
    <div ref="container" class="h-64 overflow-y-auto p-3 space-y-0.5">
      <p v-for="(line, i) in log" :key="i" class="whitespace-pre-wrap break-all leading-5">{{ line }}</p>
      <p v-if="!log.length && !running" class="text-gray-600 italic">No output yet.</p>
    </div>
  </div>
</template>
