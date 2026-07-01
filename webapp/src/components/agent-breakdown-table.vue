<template>
  <div class="overflow-x-auto rounded-lg border border-gray-200">
    <table class="w-full text-left text-sm">
      <thead class="bg-gray-50 text-xs uppercase text-gray-500">
        <tr>
          <th class="px-4 py-3">Agent</th>
          <th class="px-4 py-3">Description</th>
          <th class="px-4 py-3 text-right">Tokens</th>
          <th class="px-4 py-3 text-right">Cost</th>
          <th v-if="sessionUsage" class="px-4 py-3 text-right">% Session</th>
          <th class="px-4 py-3 text-right">Depth</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-if="agents.length === 0">
          <td :colspan="sessionUsage ? 6 : 5" class="px-4 py-6 text-center text-gray-400">
            No sub-agents recorded for this session.
          </td>
        </tr>
        <template v-for="(a, i) in sortedAgents" :key="i">
          <tr class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono font-medium text-gray-900">{{ a.agent_type }}</td>
            <td class="max-w-xs truncate px-4 py-3 text-gray-600">{{ a.description }}</td>
            <td class="px-4 py-3 text-right font-mono text-gray-700">
              <span v-if="a.usage !== null">{{ a.usage.total_tokens.toLocaleString() }}</span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td class="px-4 py-3 text-right font-mono text-gray-700">
              <span v-if="a.usage !== null">${{ agentCost(a).toFixed(4) }}</span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td v-if="sessionUsage" class="px-4 py-3 text-right font-mono text-gray-500">
              <span v-if="a.usage !== null && sessionCost > 0">
                {{ ((agentCost(a) / sessionCost) * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td class="px-4 py-3 text-right">
              <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-gray-100 text-xs text-gray-500">
                {{ a.spawn_depth }}
              </span>
            </td>
          </tr>
          <tr v-if="a.usage !== null" class="bg-gray-50">
            <td :colspan="sessionUsage ? 6 : 5" class="px-4 pb-2 pt-0">
              <TokenBar :usage="a.usage" class="h-1" />
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <!-- Legend -->
    <div v-if="agents.some(a => a.usage !== null)" class="flex flex-wrap gap-3 border-t border-gray-100 px-4 py-2 text-xs text-gray-500">
      <span class="flex items-center gap-1"><span class="inline-block h-2 w-3 rounded-sm bg-blue-500"></span> Input</span>
      <span class="flex items-center gap-1"><span class="inline-block h-2 w-3 rounded-sm bg-green-500"></span> Output</span>
      <span class="flex items-center gap-1"><span class="inline-block h-2 w-3 rounded-sm bg-yellow-400"></span> Cache write</span>
      <span class="flex items-center gap-1"><span class="inline-block h-2 w-3 rounded-sm bg-purple-400"></span> Cache read</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentMeta, TokenUsage } from '../types/api'
import TokenBar from './token-bar.vue'

const props = defineProps<{ agents: AgentMeta[]; sessionUsage?: TokenUsage | null }>()

interface PricingTier {
  input: number
  output: number
  cacheCreate: number
  cacheRead: number
}

const PRICING: { prefix: string; rates: PricingTier }[] = [
  { prefix: 'claude-opus-4',   rates: { input: 15,   output: 75,  cacheCreate: 18.75, cacheRead: 1.50 } },
  { prefix: 'claude-sonnet-4', rates: { input: 3,    output: 15,  cacheCreate: 3.75,  cacheRead: 0.30 } },
  { prefix: 'claude-haiku-4',  rates: { input: 0.80, output: 4,   cacheCreate: 1.00,  cacheRead: 0.08 } },
]

const DEFAULT_RATES: PricingTier = { input: 3, output: 15, cacheCreate: 3.75, cacheRead: 0.30 }

function getRates(model: string | null): PricingTier {
  if (model) {
    for (const entry of PRICING) {
      if (model.includes(entry.prefix)) return entry.rates
    }
  }
  return DEFAULT_RATES
}

function agentCost(agent: AgentMeta): number {
  if (agent.usage === null) return 0
  const p = getRates(agent.model)
  return (
    agent.usage.input_tokens * p.input +
    agent.usage.output_tokens * p.output +
    agent.usage.cache_creation_input_tokens * p.cacheCreate +
    agent.usage.cache_read_input_tokens * p.cacheRead
  ) / 1_000_000
}

function usageCost(usage: TokenUsage): number {
  const p = DEFAULT_RATES
  return (
    usage.input_tokens * p.input +
    usage.output_tokens * p.output +
    usage.cache_creation_input_tokens * p.cacheCreate +
    usage.cache_read_input_tokens * p.cacheRead
  ) / 1_000_000
}

const sessionCost = computed<number>(() =>
  props.sessionUsage != null ? usageCost(props.sessionUsage) : 0
)

const sortedAgents = computed<AgentMeta[]>(() =>
  [...props.agents].sort((a, b) => agentCost(b) - agentCost(a))
)
</script>
