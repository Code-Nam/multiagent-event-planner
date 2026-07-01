<template>
  <div class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0 flex-1">
        <p class="truncate font-semibold text-gray-900">{{ job.name || job.id }}</p>
        <p class="mt-0.5 text-xs text-gray-500">{{ job.project }} · {{ job.id }}</p>
      </div>
      <div class="flex shrink-0 gap-2">
        <StateBadge :state="job.template" />
        <StateBadge :state="job.state" />
      </div>
    </div>

    <div class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div>
        <p class="text-xs text-gray-500">Total tokens</p>
        <p class="mt-0.5 truncate font-mono text-sm font-medium text-gray-900">{{ (liveUsage?.total_tokens ?? job.tokens).toLocaleString() }}</p>
      </div>
      <div v-if="liveUsage ?? job.usage">
        <p class="text-xs text-gray-500">API calls</p>
        <p class="mt-0.5 font-mono text-sm font-medium text-gray-900">{{ (liveUsage ?? job.usage)!.api_call_count }}</p>
      </div>
      <div v-if="job.model">
        <p class="text-xs text-gray-500">Model</p>
        <p class="mt-0.5 truncate font-mono text-sm font-medium text-gray-900">{{ job.model }}</p>
      </div>
      <div v-if="totalCost !== null">
        <p class="text-xs text-gray-500">Total cost</p>
        <p class="mt-0.5 font-mono text-sm font-medium text-gray-900">${{ totalCost.toFixed(4) }}</p>
      </div>
      <div>
        <p class="text-xs text-gray-500">Agents spawned</p>
        <p class="mt-0.5 font-mono text-sm font-medium text-gray-900">{{ job.agents.length }}</p>
      </div>
    </div>

    <div v-if="liveUsage ?? job.usage" class="mt-4">
      <TokenBar :usage="(liveUsage ?? job.usage)!" />
      <div class="mt-1 flex gap-4 text-xs text-gray-500">
        <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-blue-500" />input</span>
        <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-green-500" />output</span>
        <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-yellow-400" />cache create</span>
        <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-purple-400" />cache read</span>
      </div>
    </div>

    <p class="mt-3 text-xs text-gray-400">
      {{ fmtDate(job.created_at) }}
      <span v-if="job.updated_at !== job.created_at"> → {{ fmtDate(job.updated_at) }}</span>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StateBadge from './state-badge.vue'
import TokenBar from './token-bar.vue'
import type { JobDetail, TokenUsage } from '../types/api'

const props = withDefaults(defineProps<{ job: JobDetail; liveUsage?: TokenUsage | null }>(), {
  liveUsage: null,
})

const PRICING: { prefix: string; input: number; output: number; cacheCreate: number; cacheRead: number }[] = [
  { prefix: 'claude-opus-4',   input: 15,   output: 75,  cacheCreate: 18.75, cacheRead: 1.50 },
  { prefix: 'claude-sonnet-4', input: 3,    output: 15,  cacheCreate: 3.75,  cacheRead: 0.30 },
  { prefix: 'claude-haiku-4',  input: 0.80, output: 4,   cacheCreate: 1.00,  cacheRead: 0.08 },
]
const DEFAULT_RATES = { input: 3, output: 15, cacheCreate: 3.75, cacheRead: 0.30 }

const totalCost = computed<number | null>(() => {
  const usage = props.liveUsage ?? props.job.usage
  if (!usage) return null
  const model = props.job.model
  const p = PRICING.find(e => model?.includes(e.prefix)) ?? DEFAULT_RATES
  return (
    usage.input_tokens * p.input +
    usage.output_tokens * p.output +
    usage.cache_creation_input_tokens * p.cacheCreate +
    usage.cache_read_input_tokens * p.cacheRead
  ) / 1_000_000
})

function fmtDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}
</script>
