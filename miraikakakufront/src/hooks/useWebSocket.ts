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
      const wsUrl = url.startsWith('ws') ? url : `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001'}${url}`;
      
      // WebSocketサーバーが存在しない場合のフォールバック
      if (!process.env.NEXT_PUBLIC_WS_URL && typeof window !== 'undefined') {
        console.warn('WebSocket URL not configured. Simulating offline mode.');
        setConnectionStatus('error');
        setError('WebSocketサーバーが設定されていません');
        return;
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
        setError('WebSocket接続エラー - サーバーが応答していません');
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
    connect();
    
    return () => {
      disconnect();
    };
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