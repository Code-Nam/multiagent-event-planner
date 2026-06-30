<script setup lang="ts">
import { useRouter } from 'vue-router'
import { usePipelineStore } from '../stores/pipeline'

const props = defineProps<{
  agent: string
  label: string
  message: string
  context?: Record<string, unknown>
}>()

const router = useRouter()
const pipelineStore = usePipelineStore()

function handleClick() {
  pipelineStore.run(props.agent, props.message, props.context)
  router.push('/pipeline')
}
</script>

<template>
  <button
    :disabled="pipelineStore.running"
    class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
    @click="handleClick"
  >
    <svg
      v-if="pipelineStore.running && pipelineStore.currentAgent === agent"
      class="animate-spin h-4 w-4"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
    {{ label }}
  </button>
</template>
