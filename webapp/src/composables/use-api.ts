export class ApiError extends Error {
  constructor(
    public message: string,
    public code: number
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function useApi() {
  const base = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

  async function get<T>(path: string): Promise<T> {
    const res = await fetch(`${base}${path}`)
    if (!res.ok) {
      const body = await res.json().catch(() => ({ message: res.statusText }))
      throw new ApiError(body.message || res.statusText, res.status)
    }
    return res.json().catch((e: Error) => { throw new ApiError(e.message, res.status) }) as Promise<T>
  }

  async function post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({ message: res.statusText }))
      throw new ApiError(errBody.message || res.statusText, res.status)
    }
    return res.json().catch((e: Error) => { throw new ApiError(e.message, res.status) }) as Promise<T>
  }

  return { get, post }
}
