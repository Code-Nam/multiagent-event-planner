<script setup lang="ts">
import { onMounted } from 'vue'
import { useDraftsStore } from '../stores/drafts'
import { usePipelineStore } from '../stores/pipeline'
import RunAgentButton from '../components/run-agent-button.vue'
import PipelineProgress from '../components/pipeline-progress.vue'

const draftsStore = useDraftsStore()
const pipelineStore = usePipelineStore()

onMounted(() => { draftsStore.fetchList() })

const venuesDrafts = () =>
  draftsStore.list.filter(d => d.name.startsWith('venues-'))
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Venue Search</h1>
    <p class="text-sm text-gray-500 mb-6">Run the venue-scout agent to discover Paris venues.</p>

    <div class="flex items-center gap-4 mb-6">
      <RunAgentButton
        agent="venue-scout"
        label="Search venues"
        message="Find suitable Paris venues for our event"
      />
    </div>

    <PipelineProgress :log="pipelineStore.log" :running="pipelineStore.running" />

    <div v-if="venuesDrafts().length" class="mt-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">Venue drafts</h2>
      <ul class="space-y-2">
        <li
          v-for="draft in venuesDrafts()"
          :key="draft.name"
          class="rounded-md border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 shadow-sm"
        >
          <span class="font-medium">{{ draft.name }}</span>
          <span class="ml-2 text-gray-400">— {{ draft.subject }}</span>
        </li>
      </ul>
    </div>

    <p v-else-if="!pipelineStore.running && !draftsStore.loading" class="mt-6 text-sm text-gray-400 italic">
      No venue drafts found. Run the agent above to start.
    </p>
  </div>
</template>
