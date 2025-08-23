'use client';

import { useEffect, useState, useRef } from 'react';
import { WEBSOCKET_CONFIG } from '@/config/constants';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxAttempts = options.maxReconnectAttempts || WEBSOCKET_CONFIG.MAX_RECONNECT_ATTEMPTS;
  const reconnectInterval = options.reconnectInterval || WEBSOCKET_CONFIG.RECONNECT_DELAY;

  const connect = () => {
    try {
      setConnectionStatus('connecting');
      const wsUrl = url.startsWith('ws') ? url : `${process.env.NEXT_PUBLIC_WS_URL || 'wss://miraikakaku-api-465603676610.us-central1.run.app'}${url}`;
      
      // WebSocketサーバーが利用できない場合のフォールバック
      // Cloud Run環境ではWebSocketは部分的なサポートのため、エラーを許容
      if (wsUrl.includes('run.app')) {
        console.info('Cloud Run WebSocket - Limited support, running in degraded mode');
        // WebSocket接続は試みるが、失敗してもアプリケーションは継続
      }
      
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        setError(null);
        reconnectAttempts.current = 0;
        options.onConnect?.();
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          options.onMessage?.(message);
        } catch (err) {
          console.error('WebSocketメッセージ解析エラー:', err);
          setError('メッセージ解析エラー');
        }
      };

      ws.current.onclose = (event) => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        options.onDisconnect?.();
        
        // 正常終了でない場合のみ再接続を試行
        if (event.code !== 1000 && reconnectAttempts.current < maxAttempts) {
          console.log(`WebSocket再接続試行 ${reconnectAttempts.current + 1}/${maxAttempts}`);
          setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, reconnectInterval);
        } else if (reconnectAttempts.current >= maxAttempts) {
          setError(`再接続に失敗しました (${maxAttempts}回試行)`);
          setConnectionStatus('error');
        }
      };

      ws.current.onerror = (event) => {
        // Cloud Run環境でのWebSocketエラーは警告レベルに下げる
        if (wsUrl.includes('run.app')) {
          console.warn('WebSocket connection not available in Cloud Run - continuing without real-time updates');
          setError('リアルタイム更新は利用できません（Cloud Run環境）');
        } else {
          setError('WebSocket接続エラー - サーバーが応答していません');
        }
        setConnectionStatus('error');
        options.onError?.(event);
      };

    } catch (err) {
      setError('WebSocket初期化エラー');
      setConnectionStatus('error');
      console.error('WebSocket初期化エラー:', err);
    }
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  };

  const sendMessage = (message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocketが接続されていません');
    }
  };

  useEffect(() => {
    // クライアントサイドでのみWebSocket接続を実行
    if (typeof window !== 'undefined') {
      // 少し遅延させて、クライアントサイドのハイドレーション後に接続
      const timeout = setTimeout(() => {
        connect();
      }, 100);
      
      return () => {
        clearTimeout(timeout);
        disconnect();
      };
    }
  }, [url]);

  return {
    isConnected,
    lastMessage,
    error,
    connectionStatus,
    reconnectAttempts: reconnectAttempts.current,
    maxAttempts,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}