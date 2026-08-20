import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketHookProps {
  sessionId: string;
  serverUrl?: string;
  onMessage?: (data: any) => void;
}

export function useWebSocket({ sessionId, serverUrl = 'ws://localhost:8005', onMessage }: WebSocketHookProps) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    try {
      const url = `${serverUrl}/ws/${sessionId}`;
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('[WebSocket] Connected to Central Server:', url);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (onMessage) {
            onMessage(data);
          }
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('[WebSocket] Disconnected. Reconnecting in 3s...');
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.warn('[WebSocket] Error:', err);
        ws.close();
      };

      wsRef.current = ws;
    } catch (e) {
      console.warn('[WebSocket] Connection creation error:', e);
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [sessionId, serverUrl, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  const sendMessage = useCallback((msg: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return { isConnected, sendMessage };
}
