<template>
  <div class="flex h-3 w-full overflow-hidden rounded-full bg-gray-200" :title="tooltip">
    <div class="bg-blue-500"   :style="{ width: pct(usage.input_tokens) }" />
    <div class="bg-green-500"  :style="{ width: pct(usage.output_tokens) }" />
    <div class="bg-yellow-400" :style="{ width: pct(usage.cache_creation_input_tokens) }" />
    <div class="bg-purple-400" :style="{ width: pct(usage.cache_read_input_tokens) }" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TokenUsage } from '../types/api'

const props = defineProps<{ usage: TokenUsage }>()

const total = computed(() =>
  props.usage.input_tokens +
  props.usage.output_tokens +
  props.usage.cache_creation_input_tokens +
  props.usage.cache_read_input_tokens
)

function pct(n: number): string {
  if (total.value === 0) return '0%'
  return `${((n / total.value) * 100).toFixed(1)}%`
}

const tooltip = computed(() =>
  `input: ${props.usage.input_tokens} | output: ${props.usage.output_tokens} | cache_create: ${props.usage.cache_creation_input_tokens} | cache_read: ${props.usage.cache_read_input_tokens}`
)
</script>
