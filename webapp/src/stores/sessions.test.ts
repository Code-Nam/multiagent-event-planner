import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSessionsStore } from './sessions'

vi.mock('../composables/use-api', () => ({
  useApi: () => ({ get: mockGet, post: vi.fn() }),
}))

const mockGet = vi.fn()

beforeEach(() => {
  setActivePinia(createPinia())
  mockGet.mockReset()
})

const SAMPLE_LIST = {
  jobs: [
    {
      id: 'abc123',
      name: 'test run',
      template: 'claude',
      state: 'done',
      tokens: 5000,
      model: null,
      cwd: '/home/user/proj',
      project: 'proj',
      created_at: '2026-06-30T08:00:00.000Z',
      updated_at: '2026-06-30T09:00:00.000Z',
    }
  ],
  total: 1,
}

describe('useSessionsStore', () => {
  it('fetchSessions populates list and total', async () => {
    mockGet.mockResolvedValueOnce(SAMPLE_LIST)
    const store = useSessionsStore()
    await store.fetchSessions()
    expect(store.list).toHaveLength(1)
    expect(store.list[0].id).toBe('abc123')
    expect(store.total).toBe(1)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('sets loading during fetch', async () => {
    let resolve!: (v: typeof SAMPLE_LIST) => void
    mockGet.mockReturnValueOnce(new Promise(r => { resolve = r }))
    const store = useSessionsStore()
    const p = store.fetchSessions()
    expect(store.loading).toBe(true)
    resolve(SAMPLE_LIST)
    await p
    expect(store.loading).toBe(false)
  })

  it('sets error on fetch failure', async () => {
    mockGet.mockRejectedValueOnce(new Error('network error'))
    const store = useSessionsStore()
    await store.fetchSessions()
    expect(store.error).toBe('network error')
    expect(store.loading).toBe(false)
  })

  it('clears error on subsequent successful fetch', async () => {
    mockGet.mockRejectedValueOnce(new Error('oops'))
    const store = useSessionsStore()
    await store.fetchSessions()
    expect(store.error).toBeTruthy()

    mockGet.mockResolvedValueOnce(SAMPLE_LIST)
    await store.fetchSessions()
    expect(store.error).toBeNull()
  })
})
