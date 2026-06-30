import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/use-api'
import type { OutputFile } from '../types/api'

export const useOutputStore = defineStore('output', () => {
  const files = ref<OutputFile[]>([])
  const loading = ref(false)

  const { get } = useApi()

  async function fetch() {
    loading.value = true
    try {
      files.value = await get<OutputFile[]>('/api/output')
    } finally {
      loading.value = false
    }
  }

  return { files, loading, fetch }
})
