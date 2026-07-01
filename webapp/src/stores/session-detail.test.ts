import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSessionDetailStore } from './session-detail'

const mockGet = vi.fn()
const mockConnect = vi.fn()

vi.mock('../composables/use-api', () => ({
  useApi: () => ({ get: mockGet, post: vi.fn() }),
}))

vi.mock('../composables/use-ws', () => ({
  useWs: () => ({ connect: mockConnect }),
}))

beforeEach(() => {
  setActivePinia(createPinia())
  mockGet.mockReset()
  mockConnect.mockReset()
})

const SAMPLE_DETAIL = {
  id: 'abc123',
  name: 'test session',
  template: 'claude',
  state: 'done',
  tokens: 5000,
  model: 'claude-sonnet-4-6',
  source: 'job',
  cwd: '/home/user/proj',
  project: 'proj',
  created_at: '2026-06-30T08:00:00.000Z',
  updated_at: '2026-06-30T09:00:00.000Z',
  usage: {
    input_tokens: 100, output_tokens: 50,
    cache_creation_input_tokens: 200, cache_read_input_tokens: 300,
    total_tokens: 350, api_call_count: 2,
  },
  agents: [{ agent_type: 'venue-scout', description: 'find venues', spawn_depth: 1 }],
}

describe('useSessionDetailStore', () => {
  it('fetchSession populates session', async () => {
    mockGet.mockResolvedValueOnce(SAMPLE_DETAIL)
    const store = useSessionDetailStore()
    await store.fetchSession('abc123')
    expect(store.session).toMatchObject({ id: 'abc123', tokens: 5000 })
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('sets error and clears session on fetch failure', async () => {
    mockGet.mockRejectedValueOnce(new Error('not found'))
    const store = useSessionDetailStore()
    await store.fetchSession('abc123')
    expect(store.error).toBe('not found')
    expect(store.session).toBeNull()
  })

  it('startLive connects WebSocket and sets isLive', () => {
    const disconnectFn = vi.fn()
    mockConnect.mockReturnValueOnce({ disconnect: disconnectFn })
    const store = useSessionDetailStore()
    store.startLive('abc123')
    expect(store.isLive).toBe(true)
    expect(mockConnect).toHaveBeenCalledWith(
      '/api/jobs/abc123/ws',
      expect.objectContaining({ onMessage: expect.any(Function), onClose: expect.any(Function) })
    )
  })

  it('onMessage updates live snapshot', () => {
    let capturedCallbacks: { onMessage: (d: string) => void } | null = null
    mockConnect.mockImplementation((_path, callbacks) => {
      capturedCallbacks = callbacks
      return { disconnect: vi.fn() }
    })
    const store = useSessionDetailStore()
    store.startLive('abc123')
    capturedCallbacks!.onMessage(JSON.stringify({ job_id: 'abc123', state: 'working', tokens: 999, updated_at: '2026' }))
    expect(store.live?.tokens).toBe(999)
  })

  it('onClose re-fetches session and sets isLive false', async () => {
    let capturedCallbacks: { onClose: () => void } | null = null
    mockConnect.mockImplementation((_path, callbacks) => {
      capturedCallbacks = callbacks
      return { disconnect: vi.fn() }
    })
    mockGet.mockResolvedValueOnce(SAMPLE_DETAIL)
    const store = useSessionDetailStore()
    store.startLive('abc123')
    capturedCallbacks!.onClose()
    await vi.waitFor(() => expect(mockGet).toHaveBeenCalled())
    expect(store.isLive).toBe(false)
  })

  it('stopLive resets state', () => {
    const disconnectFn = vi.fn()
    mockConnect.mockReturnValueOnce({ disconnect: disconnectFn })
    const store = useSessionDetailStore()
    store.startLive('abc123')
    store.stopLive()
    expect(store.isLive).toBe(false)
    expect(store.live).toBeNull()
    expect(disconnectFn).toHaveBeenCalled()
  })
})
