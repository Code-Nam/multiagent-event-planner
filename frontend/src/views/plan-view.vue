<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDraftsStore } from '../stores/drafts'
import { usePipelineStore } from '../stores/pipeline'
import RunAgentButton from '../components/run-agent-button.vue'
import PipelineProgress from '../components/pipeline-progress.vue'

const draftsStore = useDraftsStore()
const pipelineStore = usePipelineStore()

onMounted(async () => {
  await draftsStore.fetchList()
  const latest = draftsStore.list.find(d => d.name.startsWith('planning-'))
  if (latest) draftsStore.fetchDraft(latest.name)
})

const planningDraft = computed(() =>
  draftsStore.active?.name?.startsWith('planning-') ? draftsStore.active : null
)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Event Planning</h1>
    <p class="text-sm text-gray-500 mb-6">Generate task list, materials checklist, and day-of timeline.</p>

    <div class="flex items-center gap-4 mb-6">
      <RunAgentButton
        agent="event-planner"
        label="Generate plan"
        message="Create task list, assign roles, and build timeline for the event"
      />
    </div>

    <PipelineProgress :log="pipelineStore.log" :running="pipelineStore.running" />

    <div v-if="planningDraft" class="mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">{{ planningDraft.subject }}</h2>
      <pre class="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{{ planningDraft.body }}</pre>
    </div>

    <p v-else-if="!pipelineStore.running && !draftsStore.loading" class="mt-6 text-sm text-gray-400 italic">
      No planning draft yet. Run the agent above.
    </p>
  </div>
</template>
