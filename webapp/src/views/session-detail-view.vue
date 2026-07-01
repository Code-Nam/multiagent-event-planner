<template>
  <div class="mx-auto max-w-4xl px-4 py-8">
    <RouterLink to="/sessions" class="mb-6 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900">
      ← Sessions
    </RouterLink>

    <div v-if="store.loading && !store.session" class="py-16 text-center text-gray-400">Loading…</div>
    <div v-else-if="store.error" class="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">{{ store.error }}</div>

    <template v-else-if="store.session">
      <LiveIndicator v-if="store.isLive" :tokens="store.live?.tokens ?? store.session.tokens" class="mb-4" />

      <SessionSummaryCard :job="store.session" :live-usage="store.live?.usage ?? null" class="mb-6" />

      <h2 class="mb-3 text-lg font-semibold text-gray-800">Sub-agents</h2>
      <AgentBreakdownTable :agents="store.session.agents" :session-usage="store.live?.usage ?? store.session.usage ?? null" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSessionDetailStore } from '../stores/session-detail'
import SessionSummaryCard from '../components/session-summary-card.vue'
import AgentBreakdownTable from '../components/agent-breakdown-table.vue'
import LiveIndicator from '../components/live-indicator.vue'

const props = defineProps<{ sessionId: string }>()

const store = useSessionDetailStore()

const LIVE_STATES = new Set(['working', 'blocked'])

onMounted(async () => {
  await store.fetchSession(props.sessionId)
  if (store.session && LIVE_STATES.has(store.session.state)) {
    store.startLive(props.sessionId)
  }
})

onUnmounted(() => store.stopLive())
</script>
