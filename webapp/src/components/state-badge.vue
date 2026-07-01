<template>
  <span :class="cls" class="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-semibold uppercase tracking-wide">
    <span v-if="state === 'working'" class="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ state: string }>()

const cfg: Record<string, { label: string; cls: string }> = {
  working: { label: 'running', cls: 'bg-yellow-100 text-yellow-800' },
  blocked: { label: 'blocked', cls: 'bg-orange-100 text-orange-800' },
  done:    { label: 'done',    cls: 'bg-green-100 text-green-800' },
  claude:  { label: 'main',   cls: 'bg-blue-100 text-blue-800' },
  bg:      { label: 'agent',  cls: 'bg-purple-100 text-purple-800' },
}

const resolved = computed(() => cfg[props.state] ?? { label: props.state, cls: 'bg-gray-100 text-gray-700' })
const label = computed(() => resolved.value.label)
const cls = computed(() => resolved.value.cls)
</script>
