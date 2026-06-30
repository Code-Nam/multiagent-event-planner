import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/use-api'
import type { EventContext } from '../types/api'

export const useEventStore = defineStore('event', () => {
  const context = ref<EventContext | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { get, post } = useApi()

  async function fetch() {
    loading.value = true
    error.value = null
    try {
      context.value = await get<EventContext>('/api/event')
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
    } finally {
      loading.value = false
    }
  }

  async function save(data: EventContext) {
    loading.value = true
    error.value = null
    try {
      context.value = await post<EventContext>('/api/event', data)
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
    } finally {
      loading.value = false
    }
  }

  return { context, loading, error, fetch, save }
})
