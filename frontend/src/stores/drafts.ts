import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/use-api'
import type { Draft, DraftSummary } from '../types/api'

export const useDraftsStore = defineStore('drafts', () => {
  const list = ref<DraftSummary[]>([])
  const active = ref<Draft | null>(null)
  const loading = ref(false)

  const { get } = useApi()

  async function fetchList() {
    loading.value = true
    try {
      list.value = await get<DraftSummary[]>('/api/drafts')
    } finally {
      loading.value = false
    }
  }

  async function fetchDraft(name: string) {
    loading.value = true
    try {
      active.value = await get<Draft>(`/api/drafts/${encodeURIComponent(name)}`)
    } finally {
      loading.value = false
    }
  }

  return { list, active, loading, fetchList, fetchDraft }
})
