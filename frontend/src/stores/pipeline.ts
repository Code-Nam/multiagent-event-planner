import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useSse } from '../composables/use-sse'

export const usePipelineStore = defineStore('pipeline', () => {
  const running = ref(false)
  const log = ref<string[]>([])
  const currentAgent = ref<string | null>(null)
  const error = ref<string | null>(null)

  let disconnect: (() => void) | null = null

  function run(
    agentName: string,
    message: string,
    context?: Record<string, unknown>
  ) {
    if (running.value) {
      disconnect?.()
    }

    running.value = true
    currentAgent.value = agentName
    error.value = null
    log.value = []

    const { connect } = useSse()
    const handle = connect(
      '/api/run',
      { agent: agentName, message, context: context ?? {} },
      {
        onChunk(chunk) {
          log.value.push(chunk)
        },
        onDone() {
          running.value = false
          currentAgent.value = null
          disconnect = null
        },
        onError(err) {
          running.value = false
          currentAgent.value = null
          error.value = err.message
          disconnect = null
        }
      }
    )

    disconnect = handle.disconnect
  }

  function clear() {
    disconnect?.()
    disconnect = null
    running.value = false
    log.value = []
    currentAgent.value = null
    error.value = null
  }

  return { running, log, currentAgent, error, run, clear }
})
