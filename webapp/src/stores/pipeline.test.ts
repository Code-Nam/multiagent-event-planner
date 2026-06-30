import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePipelineStore } from './pipeline'

vi.mock('../composables/use-sse', () => ({
  useSse: vi.fn(),
}))

import { useSse } from '../composables/use-sse'

type SseCallbacks = {
  onChunk: (chunk: string) => void
  onDone: () => void
  onError: (err: Error) => void
}

function makeSseMock(handler: (callbacks: SseCallbacks) => void) {
  const disconnectFn = vi.fn()
  vi.mocked(useSse).mockReturnValue({
    connect: vi.fn((_path: string, _body: unknown, callbacks: SseCallbacks) => {
      handler(callbacks)
      return { disconnect: disconnectFn }
    }),
  })
  return disconnectFn
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.mocked(useSse).mockReset()
})

describe('pipelineStore — run()', () => {
  it('sets running = true and currentAgent = agentName', () => {
    makeSseMock(() => {
      // do not call any callback — leave running
    })

    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})

    expect(store.running).toBe(true)
    expect(store.currentAgent).toBe('venue-scout')
  })

  it('appends chunks to log as SSE streams', () => {
    makeSseMock((cbs) => {
      cbs.onChunk('chunk one')
      cbs.onChunk('chunk two')
    })

    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})

    expect(store.log).toEqual(['chunk one', 'chunk two'])
  })

  it('sets running = false on done event', () => {
    makeSseMock((cbs) => {
      cbs.onDone()
    })

    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})

    expect(store.running).toBe(false)
    expect(store.currentAgent).toBeNull()
  })

  it('sets error on error event', () => {
    makeSseMock((cbs) => {
      cbs.onError(new Error('SSE failed'))
    })

    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})

    expect(store.running).toBe(false)
    expect(store.error).toBe('SSE failed')
    expect(store.currentAgent).toBeNull()
  })

  it('resets log to empty before each run', () => {
    makeSseMock((cbs) => {
      cbs.onChunk('first run chunk')
      cbs.onDone()
    })

    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})

    makeSseMock((cbs) => {
      cbs.onChunk('second run chunk')
      cbs.onDone()
    })
    store.run('venue-scout', 'find venues again', {})

    expect(store.log).toEqual(['second run chunk'])
  })
})

describe('pipelineStore — clear()', () => {
  it('resets running to false', () => {
    makeSseMock(() => {})
    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})
    store.clear()

    expect(store.running).toBe(false)
  })

  it('resets log to empty array', () => {
    makeSseMock((cbs) => {
      cbs.onChunk('a chunk')
    })
    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})
    store.clear()

    expect(store.log).toEqual([])
  })

  it('resets currentAgent to null', () => {
    makeSseMock(() => {})
    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})
    store.clear()

    expect(store.currentAgent).toBeNull()
  })

  it('resets error to null', () => {
    makeSseMock((cbs) => {
      cbs.onError(new Error('boom'))
    })
    const store = usePipelineStore()
    store.run('venue-scout', 'find venues', {})
    store.clear()

    expect(store.error).toBeNull()
  })
})
