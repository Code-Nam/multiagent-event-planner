import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useApi, ApiError } from './use-api'

const mockFetch = vi.fn()

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch)
})

afterEach(() => {
  vi.restoreAllMocks()
})

function makeResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    json: vi.fn().mockResolvedValue(body),
  } as unknown as Response
}

describe('useApi — get()', () => {
  it('resolves with parsed JSON on 200', async () => {
    const payload = { name: 'Summer Gala' }
    mockFetch.mockResolvedValueOnce(makeResponse(200, payload))

    const { get } = useApi()
    const result = await get<typeof payload>('/api/event')

    expect(result).toEqual(payload)
  })

  it('throws ApiError on non-2xx with correct message', async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(404, { message: 'Not found' }))

    const { get } = useApi()
    await expect(get('/api/event')).rejects.toThrow(ApiError)
    await expect(get('/api/event')).rejects.toMatchObject({
      message: 'Not found',
      code: 404,
    })
  })

  it('throws ApiError on non-2xx with statusText when body has no message', async () => {
    const res: Response = {
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: vi.fn().mockRejectedValue(new Error('parse error')),
    } as unknown as Response
    mockFetch.mockResolvedValueOnce(res)

    const { get } = useApi()
    await expect(get('/api/event')).rejects.toMatchObject({
      code: 500,
      message: 'Internal Server Error',
    })
  })

  it('uses VITE_API_BASE as base URL', async () => {
    vi.stubGlobal('import', { meta: { env: { VITE_API_BASE: 'http://api.test' } } })
    mockFetch.mockResolvedValueOnce(makeResponse(200, {}))

    const { get } = useApi()
    await get('/api/event')

    const calledUrl = mockFetch.mock.calls[0][0] as string
    expect(calledUrl).toMatch(/^http:\/\//)
  })
})

describe('useApi — post()', () => {
  it('sends correct Content-Type header', async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(200, {}))

    const { post } = useApi()
    await post('/api/event', { name: 'Test' })

    const [, init] = mockFetch.mock.calls[0] as [string, RequestInit]
    expect((init.headers as Record<string, string>)['Content-Type']).toBe(
      'application/json'
    )
  })

  it('sends body as JSON string', async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(200, {}))

    const { post } = useApi()
    const data = { name: 'Test', date: '2026-07-01' }
    await post('/api/event', data)

    const [, init] = mockFetch.mock.calls[0] as [string, RequestInit]
    expect(init.body).toBe(JSON.stringify(data))
  })

  it('resolves with parsed JSON on 200', async () => {
    const payload = { name: 'Saved' }
    mockFetch.mockResolvedValueOnce(makeResponse(200, payload))

    const { post } = useApi()
    const result = await post<typeof payload>('/api/event', {})

    expect(result).toEqual(payload)
  })

  it('throws ApiError on non-2xx', async () => {
    mockFetch.mockResolvedValueOnce(makeResponse(422, { message: 'Validation error' }))

    const { post } = useApi()
    await expect(post('/api/event', {})).rejects.toMatchObject({
      code: 422,
      message: 'Validation error',
    })
  })
})
