<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDraftsStore } from '../stores/drafts'
import { usePipelineStore } from '../stores/pipeline'
import RunAgentButton from '../components/run-agent-button.vue'
import PipelineProgress from '../components/pipeline-progress.vue'

const draftsStore = useDraftsStore()
const pipelineStore = usePipelineStore()

onMounted(() => { draftsStore.fetchList() })

const budgetDraft = computed(() =>
  draftsStore.list.find(d => d.name.startsWith('budget-'))
)

const statusBadge = computed(() => {
  if (!budgetDraft.value) return null
  const s = budgetDraft.value.status?.toUpperCase()
  if (s === 'APPROVED') return { label: 'APPROVED', cls: 'bg-green-100 text-green-700 border-green-200' }
  if (s === 'REJECTED') return { label: 'REJECTED', cls: 'bg-red-100 text-red-700 border-red-200' }
  return { label: s ?? 'PENDING', cls: 'bg-yellow-100 text-yellow-700 border-yellow-200' }
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Budget Validation</h1>
    <p class="text-sm text-gray-500 mb-6">Validate expenses against the fixed event budget.</p>

    <div class="flex items-center gap-4 mb-6">
      <RunAgentButton
        agent="budget-validator"
        label="Validate budget"
        message="Check expenses against the fixed budget"
      />
    </div>

    <div v-if="statusBadge" class="mb-6">
      <span :class="['inline-flex items-center rounded-full border px-4 py-1.5 text-sm font-bold tracking-wide', statusBadge.cls]">
        {{ statusBadge.label }}
      </span>
    </div>

    <PipelineProgress :log="pipelineStore.log" :running="pipelineStore.running" />

    <p v-if="!budgetDraft && !pipelineStore.running && !draftsStore.loading" class="mt-6 text-sm text-gray-400 italic">
      No budget validation yet. Run the agent above.
    </p>
  </div>
</template>
