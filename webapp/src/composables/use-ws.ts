interface WsCallbacks {
  onMessage: (data: string) => void
  onClose: () => void
  onError: (err: Event) => void
}

interface WsHandle {
  disconnect: () => void
}

export function useWs() {
  function connect(path: string, callbacks: WsCallbacks): WsHandle {
    const base = (import.meta.env.VITE_API_BASE ?? 'http://localhost:8000').replace(/^http/, 'ws')
    const socket = new WebSocket(`${base}${path}`)
    socket.onmessage = (e) => callbacks.onMessage(e.data as string)
    socket.onclose = () => callbacks.onClose()
    socket.onerror = (e) => callbacks.onError(e)
    return {
      disconnect() {
        socket.close()
      },
    }
  }

  return { connect }
}
