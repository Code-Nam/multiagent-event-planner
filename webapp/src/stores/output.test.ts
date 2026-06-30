import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useOutputStore } from './output'
import type { OutputFile } from '../types/api'

vi.mock('../composables/use-api', () => ({
  useApi: vi.fn(),
  ApiError: class ApiError extends Error {
    code: number
    constructor(message: string, code: number) {
      super(message)
      this.code = code
      this.name = 'ApiError'
    }
  },
}))

import { useApi } from '../composables/use-api'

const mockGet = vi.fn()

beforeEach(() => {
  setActivePinia(createPinia())
  vi.mocked(useApi).mockReturnValue({ get: mockGet, post: vi.fn() })
  mockGet.mockReset()
})

const sampleFiles: OutputFile[] = [
  { name: 'recap.xlsx', type: 'xlsx', path: 'output/recap.xlsx' },
  { name: 'report.docx', type: 'docx', path: 'output/report.docx' },
]

describe('outputStore — fetch()', () => {
  it('calls GET /api/output and populates files', async () => {
    mockGet.mockResolvedValueOnce(sampleFiles)

    const store = useOutputStore()
    await store.fetch()

    expect(mockGet).toHaveBeenCalledWith('/api/output')
    expect(store.files).toEqual(sampleFiles)
  })

  it('sets loading true during request', async () => {
    let capturedLoading: boolean | undefined
    mockGet.mockImplementationOnce(async () => {
      capturedLoading = useOutputStore().loading
      return sampleFiles
    })

    const store = useOutputStore()
    await store.fetch()

    expect(capturedLoading).toBe(true)
  })

  it('sets loading false after request completes', async () => {
    mockGet.mockResolvedValueOnce(sampleFiles)

    const store = useOutputStore()
    await store.fetch()

    expect(store.loading).toBe(false)
  })

  it('sets loading false even when fetch throws', async () => {
    mockGet.mockRejectedValueOnce(new Error('Network error'))

    const store = useOutputStore()
    try {
      await store.fetch()
    } catch {
      // expected
    }

    expect(store.loading).toBe(false)
  })
})
