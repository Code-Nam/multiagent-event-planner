import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/use-api'
import { useWs } from '../composables/use-ws'
import type { JobDetail, LiveSnapshot } from '../types/api'

export const useSessionDetailStore = defineStore('sessionDetail', () => {
  const session = ref<JobDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const live = ref<LiveSnapshot | null>(null)
  const isLive = ref(false)

  const { get } = useApi()
  const { connect } = useWs()

  let disconnect: (() => void) | null = null

  async function fetchSession(jobId: string) {
    loading.value = true
    error.value = null
    try {
      session.value = await get<JobDetail>(`/api/jobs/${jobId}`)
    } catch (e) {
      session.value = null
      error.value = e instanceof Error ? e.message : 'fetch failed'
    } finally {
      loading.value = false
    }
  }

  function startLive(jobId: string) {
    stopLive()
    isLive.value = true
    const handle = connect(`/api/jobs/${jobId}/ws`, {
      onMessage(data) {
        try {
          live.value = JSON.parse(data) as LiveSnapshot
        } catch {
          // ignore malformed snapshots
        }
      },
      onClose() {
        isLive.value = false
        fetchSession(jobId)
      },
      onError() {
        isLive.value = false
        error.value = 'websocket error'
      },
    })
    disconnect = handle.disconnect
  }

  function stopLive() {
    disconnect?.()
    disconnect = null
    isLive.value = false
    live.value = null
  }

  return { session, loading, error, live, isLive, fetchSession, startLive, stopLive }
})
