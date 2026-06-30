<script setup lang="ts">
import { ref } from 'vue'
import type { DraftSummary } from '../types/api'

const props = defineProps<{ draft: DraftSummary }>()
const emit = defineEmits<{ (e: 'expand', name: string): void }>()

const expanded = ref(false)

const purposeColour: Record<string, string> = {
  venue: 'bg-blue-100 text-blue-700',
  sponsor: 'bg-purple-100 text-purple-700',
  partner: 'bg-teal-100 text-teal-700',
  followup: 'bg-amber-100 text-amber-700',
  other: 'bg-gray-100 text-gray-600'
}

function badgeClass(purpose: string) {
  return purposeColour[purpose.toLowerCase()] ?? purposeColour['other']
}

function toggle() {
  expanded.value = !expanded.value
  if (expanded.value) emit('expand', props.draft.name)
}
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden">
    <div class="flex items-start justify-between gap-4 px-4 py-3">
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2 flex-wrap">
          <span :class="['inline-block rounded-full px-2 py-0.5 text-xs font-medium', badgeClass(draft.purpose)]">
            {{ draft.purpose }}
          </span>
          <span class="text-xs text-gray-400">{{ draft.name }}</span>
        </div>
        <p class="mt-1 text-sm font-medium text-gray-800 truncate">{{ draft.subject }}</p>
        <p class="text-xs text-gray-500">To: {{ draft.to }}</p>
      </div>
      <button
        class="shrink-0 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
        @click="toggle"
      >
        {{ expanded ? 'Collapse' : 'Expand' }}
      </button>
    </div>
    <slot v-if="expanded" />
  </div>
</template>
