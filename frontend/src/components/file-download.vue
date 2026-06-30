<script setup lang="ts">
import type { OutputFile } from '../types/api'

const props = defineProps<{ file: OutputFile }>()

const base = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const typeIcon: Record<string, string> = {
  xlsx: '📊',
  docx: '📄',
  pptx: '📑',
  pdf: '📋'
}

function icon(type: string) {
  return typeIcon[type.toLowerCase()] ?? '📁'
}
</script>

<template>
  <div class="flex items-center justify-between rounded-md border border-gray-200 bg-white px-4 py-3 shadow-sm">
    <div class="flex items-center gap-3">
      <span class="text-2xl" aria-hidden="true">{{ icon(file.type) }}</span>
      <div>
        <p class="text-sm font-medium text-gray-800">{{ file.name }}</p>
        <p class="text-xs text-gray-400 uppercase">{{ file.type }}</p>
      </div>
    </div>
    <a
      :href="`${base}/api/output/${encodeURIComponent(file.name)}`"
      download
      class="rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200 transition-colors"
    >
      Download
    </a>
  </div>
</template>
