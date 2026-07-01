import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/use-api'
import type { Job, JobList } from '../types/api'

export const useSessionsStore = defineStore('sessions', () => {
  const list = ref<Job[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const projectFilter = ref<string | null>(import.meta.env.VITE_PROJECT_SLUG ?? null)

  const { get } = useApi()

  async function fetchSessions() {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams({ limit: '50' })
      if (projectFilter.value) params.set('project', projectFilter.value)
      const data = await get<JobList>(`/api/jobs?${params}`)
      list.value = data.jobs
      total.value = data.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'fetch failed'
    } finally {
      loading.value = false
    }
  }

  return { list, total, loading, error, projectFilter, fetchSessions }
})
