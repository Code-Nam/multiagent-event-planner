<template>
  <div class="mx-auto max-w-4xl px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">Claude Code Sessions</h1>
      <span class="text-sm text-gray-500">{{ store.total }} total</span>
    </div>

    <!-- Search -->
    <div class="mb-4 relative">
      <input
        v-model="search"
        type="text"
        placeholder="Search sessions…"
        class="w-full rounded-lg border border-gray-200 bg-white py-2 pl-9 pr-4 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <button v-if="search" @click="search = ''" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs">✕</button>
    </div>

    <!-- Row 1: State filter -->
    <div class="mb-3 flex flex-wrap gap-2">
      <button
        v-for="s in ['all', 'working', 'done', 'error']"
        :key="s"
        :class="activeState === s
          ? 'rounded-full px-3 py-1 text-xs font-medium bg-indigo-600 text-white'
          : 'rounded-full px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200'"
        @click="activeState = s"
      >
        {{ s === 'all' ? 'All' : s.charAt(0).toUpperCase() + s.slice(1) }}
      </button>
    </div>

    <!-- Row 2: Model filter (only when ≥2 distinct models) -->
    <div v-if="uniqueModels.length >= 2" class="mb-5 flex flex-wrap gap-2">
      <button
        :class="activeModel === 'all'
          ? 'rounded-full px-3 py-1 text-xs font-medium bg-indigo-600 text-white'
          : 'rounded-full px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200'"
        @click="activeModel = 'all'"
      >
        All
      </button>
      <button
        v-for="m in uniqueModels"
        :key="m"
        :class="activeModel === m
          ? 'rounded-full px-3 py-1 text-xs font-medium bg-indigo-600 text-white'
          : 'rounded-full px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200'"
        @click="activeModel = m"
      >
        {{ m.replace(/^claude-/, '') }}
      </button>
    </div>

    <!-- Row 3: Cost range filter + sort -->
    <div class="mb-3 flex items-center gap-2 text-xs text-gray-500">
      <span class="w-12 shrink-0">Cost</span>
      <input
        type="number"
        min="0"
        step="0.0001"
        placeholder="min $"
        class="w-24 rounded-md border border-gray-200 bg-white px-2 py-1 text-xs font-mono text-gray-700 focus:outline-none focus:ring-1 focus:ring-indigo-400"
        :value="costMin ?? ''"
        @input="costMin = ($event.target as HTMLInputElement).value === '' ? null : Number(($event.target as HTMLInputElement).value)"
      />
      <span>—</span>
      <input
        type="number"
        min="0"
        step="0.0001"
        placeholder="max $"
        class="w-24 rounded-md border border-gray-200 bg-white px-2 py-1 text-xs font-mono text-gray-700 focus:outline-none focus:ring-1 focus:ring-indigo-400"
        :value="costMax ?? ''"
        @input="costMax = ($event.target as HTMLInputElement).value === '' ? null : Number(($event.target as HTMLInputElement).value)"
      />
      <button
        @click="costSort = costSort === null ? 'desc' : costSort === 'desc' ? 'asc' : null"
        :class="costSort !== null ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        class="ml-2 rounded-full px-3 py-1 font-medium transition-colors"
      >
        {{ costSort === 'asc' ? '↑ Cost' : costSort === 'desc' ? '↓ Cost' : 'Sort cost' }}
      </button>
    </div>

    <!-- Row 4: Token range filter -->
    <div class="mb-5 flex items-center gap-2 text-xs text-gray-500">
      <span class="w-12 shrink-0">Tokens</span>
      <input
        type="number"
        min="0"
        step="1"
        placeholder="min"
        class="w-24 rounded-md border border-gray-200 bg-white px-2 py-1 text-xs font-mono text-gray-700 focus:outline-none focus:ring-1 focus:ring-indigo-400"
        :value="tokenMin ?? ''"
        @input="tokenMin = ($event.target as HTMLInputElement).value === '' ? null : Number(($event.target as HTMLInputElement).value)"
      />
      <span>—</span>
      <input
        type="number"
        min="0"
        step="1"
        placeholder="max"
        class="w-24 rounded-md border border-gray-200 bg-white px-2 py-1 text-xs font-mono text-gray-700 focus:outline-none focus:ring-1 focus:ring-indigo-400"
        :value="tokenMax ?? ''"
        @input="tokenMax = ($event.target as HTMLInputElement).value === '' ? null : Number(($event.target as HTMLInputElement).value)"
      />
    </div>

    <!-- Total usage banner -->
    <div
      :class="bannerFlash ? 'bg-green-50 border-green-200' : 'bg-indigo-50 border-indigo-100'"
      class="mb-6 rounded-xl border px-6 py-4 flex flex-wrap gap-6 transition-colors duration-500"
    >
      <div>
        <p class="text-xs text-indigo-400 uppercase tracking-wide">Total tokens</p>
        <p class="text-3xl font-bold text-indigo-700 font-mono tabular-nums">{{ totalTokens.toLocaleString() }}</p>
      </div>
      <div>
        <p class="text-xs text-indigo-400 uppercase tracking-wide">Total cost</p>
        <p class="text-3xl font-bold text-indigo-700 font-mono tabular-nums">${{ totalCost.toFixed(4) }}</p>
      </div>
      <div v-if="hasWorking" class="flex items-center gap-1.5 self-end pb-1">
        <span class="inline-block h-2 w-2 animate-ping rounded-full bg-yellow-400" />
        <span class="text-xs text-yellow-600">live</span>
      </div>
      <div v-else-if="filtered.length !== store.list.length" class="self-end pb-1 text-xs text-indigo-400">
        {{ filtered.length }} / {{ store.list.length }} sessions
      </div>
    </div>

    <div v-if="store.loading && store.list.length === 0" class="py-16 text-center text-gray-400">Loading…</div>
    <div v-else-if="store.error" class="rounded-lg bg-red-50 p-4 text-sm text-red-700">{{ store.error }}</div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="job in filtered"
        :key="job.id"
        :to="`/sessions/${job.id}`"
        class="block rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="truncate font-medium text-gray-900">{{ job.name || job.id }}</p>
            <p class="mt-0.5 text-xs text-gray-500">{{ job.project }}</p>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <StateBadge :state="job.template" />
            <StateBadge :state="job.state" />
          </div>
        </div>
        <div class="mt-3 flex items-center gap-4 text-sm">
          <span
            :class="job.state === 'working' ? 'animate-pulse' : ''"
            class="font-mono text-gray-700 tabular-nums"
          >{{ job.tokens.toLocaleString() }} <span class="font-sans text-gray-400">tokens</span></span>
          <span class="font-mono text-gray-500 text-xs tabular-nums">${{ costUsd(job).toFixed(4) }}</span>
          <span v-if="job.model" class="text-gray-400">{{ job.model }}</span>
        </div>
        <div class="mt-1.5 h-1.5 w-full rounded-full bg-gray-100">
          <div
            class="h-1.5 rounded-full bg-indigo-500 transition-all duration-700 ease-out"
            :style="{ width: `${(costUsd(job) / maxCost) * 100}%` }"
          />
        </div>
        <p class="mt-1 text-xs text-gray-400">{{ fmtDate(job.created_at) }}</p>
      </RouterLink>

      <div v-if="filtered.length === 0" class="py-16 text-center text-gray-400">
        No sessions found in <code class="text-xs">~/.claude/jobs/</code>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useSessionsStore } from '../stores/sessions'
import StateBadge from '../components/state-badge.vue'
import type { Job } from '../types/api'

const store = useSessionsStore()

const activeState = ref<string>('all')
const activeModel = ref<string>('all')

const costMin = ref<number | null>(null)
const costMax = ref<number | null>(null)
const tokenMin = ref<number | null>(null)
const tokenMax = ref<number | null>(null)

const search = ref('')
const costSort = ref<'asc' | 'desc' | null>(null)
const bannerFlash = ref(false)

const uniqueModels = computed<string[]>(() =>
  [...new Set(store.list.map(j => j.model).filter((m): m is string => m !== null))]
)

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const result = store.list.filter(job => {
    const stateOk = activeState.value === 'all' || job.state === activeState.value
    const modelOk = activeModel.value === 'all' || job.model === activeModel.value
    const cost = costUsd(job)
    const costOk = (costMin.value === null || cost >= costMin.value) &&
                   (costMax.value === null || cost <= costMax.value)
    const tokOk  = (tokenMin.value === null || job.tokens >= tokenMin.value) &&
                   (tokenMax.value === null || job.tokens <= tokenMax.value)
    const searchOk = !q || (job.name || job.id).toLowerCase().includes(q) || job.project.toLowerCase().includes(q)
    return stateOk && modelOk && costOk && tokOk && searchOk
  })
  if (!costSort.value) return result
  return result.sort((a, b) => {
    const diff = costUsd(a) - costUsd(b)
    return costSort.value === 'asc' ? diff : -diff
  })
})

const hasWorking = computed(() => store.list.some(j => j.state === 'working'))

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

function costUsd(job: Job): number {
  const p = getRates(job.model)
  if (job.usage !== null) {
    return (
      job.usage.input_tokens * p.input +
      job.usage.output_tokens * p.output +
      job.usage.cache_creation_input_tokens * p.cacheCreate +
      job.usage.cache_read_input_tokens * p.cacheRead
    ) / 1_000_000
  }
  const inputEst = Math.round(job.tokens / 6)
  const outputEst = job.tokens - inputEst
  return (inputEst * p.input + outputEst * p.output) / 1_000_000
}

const maxCost = computed<number>(() =>
  Math.max(...filtered.value.map((j) => costUsd(j)), 0.000001)
)

const totalTokens = computed<number>(() =>
  filtered.value.reduce((sum, j) => sum + j.tokens, 0)
)

const totalCost = computed<number>(() =>
  filtered.value.reduce((sum, j) => sum + costUsd(j), 0)
)

let flashTimer: ReturnType<typeof setTimeout> | null = null
watch(totalTokens, (next, prev) => {
  if (next <= prev) return
  if (flashTimer) clearTimeout(flashTimer)
  bannerFlash.value = true
  flashTimer = setTimeout(() => { bannerFlash.value = false }, 600)
})

function fmtDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}

let interval: ReturnType<typeof setInterval>

function restartInterval() {
  clearInterval(interval)
  interval = setInterval(() => store.fetchSessions(), hasWorking.value ? 1000 : 5000)
}

watch(hasWorking, restartInterval)

onMounted(() => {
  store.fetchSessions()
  restartInterval()
})

onUnmounted(() => {
  clearInterval(interval)
  if (flashTimer) clearTimeout(flashTimer)
})
</script>
