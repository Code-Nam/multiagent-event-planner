import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useEventStore } from './event'
import type { EventContext } from '../types/api'

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
const mockPost = vi.fn()

beforeEach(() => {
  setActivePinia(createPinia())
  vi.mocked(useApi).mockReturnValue({ get: mockGet, post: mockPost })
  mockGet.mockReset()
  mockPost.mockReset()
})

const sampleContext: EventContext = {
  name: 'Summer Gala',
  date: '2026-07-01',
  type: 'gala',
  expected_attendance: '200',
  fixed_budget: '15000',
  event_lead: 'Alice',
  preferred_area: '11e',
  constraints: 'none',
}

describe('eventStore — fetch()', () => {
  it('sets context from API response', async () => {
    mockGet.mockResolvedValueOnce(sampleContext)

    const store = useEventStore()
    await store.fetch()

    expect(store.context).toEqual(sampleContext)
  })

  it('sets loading true during request, false after', async () => {
    let capturedLoading: boolean | undefined
    mockGet.mockImplementationOnce(async () => {
      capturedLoading = useEventStore().loading
      return sampleContext
    })

    const store = useEventStore()
    await store.fetch()

    expect(capturedLoading).toBe(true)
    expect(store.loading).toBe(false)
  })

  it('sets error on failure', async () => {
    mockGet.mockRejectedValueOnce(new Error('Network error'))

    const store = useEventStore()
    await store.fetch()

    expect(store.error).toBe('Network error')
    expect(store.loading).toBe(false)
  })

  it('clears error before fetching', async () => {
    mockGet.mockResolvedValueOnce(sampleContext)
    const store = useEventStore()
    store.$patch({ error: 'old error' })

    await store.fetch()

    expect(store.error).toBeNull()
  })
})

describe('eventStore — save()', () => {
  it('calls post with event data and updates context', async () => {
    const updated = { ...sampleContext, name: 'Updated Gala' }
    mockPost.mockResolvedValueOnce(updated)

    const store = useEventStore()
    await store.save(sampleContext)

    expect(mockPost).toHaveBeenCalledWith('/api/event', sampleContext)
    expect(store.context).toEqual(updated)
  })

  it('sets error on failure', async () => {
    mockPost.mockRejectedValueOnce(new Error('Save failed'))

    const store = useEventStore()
    await store.save(sampleContext)

    expect(store.error).toBe('Save failed')
    expect(store.loading).toBe(false)
  })

  it('sets loading true during request, false after', async () => {
    let capturedLoading: boolean | undefined
    mockPost.mockImplementationOnce(async () => {
      capturedLoading = useEventStore().loading
      return sampleContext
    })

    const store = useEventStore()
    await store.save(sampleContext)

    expect(capturedLoading).toBe(true)
    expect(store.loading).toBe(false)
  })
})
