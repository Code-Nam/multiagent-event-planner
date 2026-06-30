interface SseCallbacks {
  onChunk: (chunk: string) => void
  onDone: () => void
  onError: (err: Error) => void
}

interface SseHandle {
  disconnect: () => void
}

export function useSse() {
  function connect(
    path: string,
    body: unknown,
    callbacks: SseCallbacks
  ): SseHandle {
    const base = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
    let aborted = false
    const controller = new AbortController()

    async function run() {
      try {
        const res = await fetch(`${base}${path}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream'
          },
          body: JSON.stringify(body),
          signal: controller.signal
        })

        if (!res.ok || !res.body) {
          callbacks.onError(new Error(`SSE request failed: ${res.status}`))
          return
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let currentEvent = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done || aborted) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() ?? ''

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEvent = line.slice(6).trim()
            } else if (line.startsWith('data:')) {
              const data = line.slice(5).trim()
              if (currentEvent === 'done' || data === '[DONE]') {
                callbacks.onDone()
                return
              }
              callbacks.onChunk(data)
              currentEvent = ''
            }
          }
        }

        if (!aborted) callbacks.onDone()
      } catch (err) {
        if (!aborted) {
          callbacks.onError(err instanceof Error ? err : new Error(String(err)))
        }
      }
    }

    run()

    return {
      disconnect() {
        aborted = true
        controller.abort()
      }
    }
  }

  return { connect }
}
