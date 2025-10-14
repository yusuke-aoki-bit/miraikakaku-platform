/**
 * WebSocket Client for Real-time Notifications
 * Phase 11: Real-time notification implementation
 */

export interface AlertNotification {
  id: number;
  symbol: string;
  company_name: string;
  alert_type: string;
  current_price: number;
  message: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'connected' | 'alert_triggered' | 'pong' | 'alert_check_result';
  message?: string;
  user_id?: string;
  data?: AlertNotification;
  alerts?: AlertNotification[];
  count?: number;
  timestamp: string;
}

export type MessageHandler = (message: WebSocketMessage) => void;

export class NotificationWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000; // 3 seconds
  private handlers: Set<MessageHandler> = new Set();
  private pingInterval: NodeJS.Timeout | null = null;

  constructor(baseUrl: string, token: string) {
    // HTTPSをWSS、HTTPをWSに変換
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const urlWithoutProtocol = baseUrl.replace(/^https?:\/\//, '');
    this.url = `${wsProtocol}://${urlWithoutProtocol}/api/ws/notifications?token=${token}`;
    this.token = token;
  }

  /**
   * WebSocket接続を開始
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.startPing();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            console.log('📨 WebSocket message:', message);

            // 全てのハンドラーにメッセージを配信
            this.handlers.forEach(handler => {
              try {
                handler(message);
              } catch (err) {
                console.error('❌ Error in message handler:', err);
              }
            });
          } catch (err) {
            console.error('❌ Error parsing WebSocket message:', err);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket disconnected:', event.code, event.reason);
          this.stopPing();

          // 自動再接続（指数バックオフ）
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            console.log(`🔄 Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
              this.connect().catch(err => {
                console.error('❌ Reconnect failed:', err);
              });
            }, delay);
          } else {
            console.error('❌ Max reconnect attempts reached');
          }
        };

      } catch (err) {
        console.error('❌ Error creating WebSocket:', err);
        reject(err);
      }
    });
  }

  /**
   * WebSocket接続を切断
   */
  disconnect() {
    this.stopPing();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.handlers.clear();
    console.log('🔌 WebSocket manually disconnected');
  }

  /**
   * メッセージハンドラーを登録
   */
  onMessage(handler: MessageHandler): () => void {
    this.handlers.add(handler);

    // アンサブスクライブ関数を返す
    return () => {
      this.handlers.delete(handler);
    };
  }

  /**
   * アラートがトリガーされた時のハンドラー
   */
  onAlertTriggered(callback: (alert: AlertNotification) => void): () => void {
    const handler: MessageHandler = (message) => {
      if (message.type === 'alert_triggered' && message.data) {
        callback(message.data);
      }
    };

    return this.onMessage(handler);
  }

  /**
   * 手動でアラートチェックを実行
   */
  checkAlerts() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send('check_alerts');
    } else {
      console.error('❌ WebSocket is not connected');
    }
  }

  /**
   * Ping/Pongでコネクションを維持
   */
  private startPing() {
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send('ping');
      }
    }, 30000); // 30秒ごとにping
  }

  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * 接続状態を取得
   */
  get isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * 接続状態
   */
  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

/**
 * WebSocketフックを使用する React Hook
 */
export function createWebSocketHook() {
  // Next.jsのクライアントサイドでのみ使用可能
  if (typeof window === 'undefined') {
    return null;
  }

  return { NotificationWebSocket };
}
