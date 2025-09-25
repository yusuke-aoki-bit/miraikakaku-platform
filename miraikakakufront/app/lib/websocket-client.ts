/**
 * WebSocket Real-time AI Client
 * Phase 3.1 - リアルタイムAI推論エンジン
 */

import React from 'react';
import { EventEmitter } from 'events';

export interface RealtimePrediction {
  symbol: string;
  prediction: number;
  confidence: number;
  timestamp: string;
  model_version: string;
  factors: Array<{
    name: string;
    impact: number;
    confidence: number;
  }>;
}

export interface RealtimeAlert {
  id: string;
  user_id: string;
  symbol: string;
  alert_type: 'price_threshold' | 'volume_spike' | 'volatility_change' | 'prediction_update';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  latency_ms: number;
  active_connections: number;
  predictions_per_second: number;
  timestamp: string;
}

export class RealtimeAIClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private subscriptions = new Set<string>();
  private connectionId: string | null = null;

  constructor(
    private apiUrl: string = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8080/ws',
    private token?: string
  ) {
    super();
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = this.token ? `${this.apiUrl}?token=${this.token}` : this.apiUrl;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = (event) => {
          console.log('🔗 WebSocket connected');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.emit('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket disconnected:', event.code, event.reason);
          this.cleanup();
          this.emit('disconnected', { code: event.code, reason: event.reason });

          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.emit('error', error);
          reject(error);
        };

      } catch (error) {
        console.error('❌ Failed to create WebSocket connection:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
    }
  }

  /**
   * Subscribe to real-time predictions for a symbol
   */
  subscribeToSymbol(symbol: string): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    const subscription = `predictions:${symbol}`;
    this.subscriptions.add(subscription);

    this.send({
      type: 'subscribe',
      channel: 'predictions',
      symbol: symbol,
      timestamp: new Date().toISOString()
    });

    console.log(`📈 Subscribed to predictions for ${symbol}`);
  }

  /**
   * Unsubscribe from symbol predictions
   */
  unsubscribeFromSymbol(symbol: string): void {
    if (!this.isConnected()) {
      return;
    }

    const subscription = `predictions:${symbol}`;
    this.subscriptions.delete(subscription);

    this.send({
      type: 'unsubscribe',
      channel: 'predictions',
      symbol: symbol,
      timestamp: new Date().toISOString()
    });

    console.log(`📉 Unsubscribed from predictions for ${symbol}`);
  }

  /**
   * Subscribe to real-time market data
   */
  subscribeToMarketData(symbols: string[]): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    symbols.forEach(symbol => {
      const subscription = `market_data:${symbol}`;
      this.subscriptions.add(subscription);
    });

    this.send({
      type: 'subscribe',
      channel: 'market_data',
      symbols: symbols,
      timestamp: new Date().toISOString()
    });

    console.log(`📊 Subscribed to market data for ${symbols.join(', ')}`);
  }

  /**
   * Subscribe to user alerts
   */
  subscribeToAlerts(userId: string): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    const subscription = `alerts:${userId}`;
    this.subscriptions.add(subscription);

    this.send({
      type: 'subscribe',
      channel: 'alerts',
      user_id: userId,
      timestamp: new Date().toISOString()
    });

    console.log(`🚨 Subscribed to alerts for user ${userId}`);
  }

  /**
   * Subscribe to system health updates
   */
  subscribeToSystemHealth(): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    this.subscriptions.add('system_health');

    this.send({
      type: 'subscribe',
      channel: 'system_health',
      timestamp: new Date().toISOString()
    });

    console.log('🏥 Subscribed to system health updates');
  }

  /**
   * Request immediate prediction for a symbol
   */
  requestPrediction(symbol: string, options: {
    horizon?: string;
    confidence?: number;
    model?: string;
  } = {}): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    this.send({
      type: 'request_prediction',
      symbol: symbol,
      options: {
        horizon: options.horizon || '1d',
        confidence: options.confidence || 0.95,
        model: options.model || 'ensemble',
      },
      timestamp: new Date().toISOString()
    });

    console.log(`🤖 Requested prediction for ${symbol}`);
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection info
   */
  getConnectionInfo(): {
    connected: boolean;
    connectionId: string | null;
    subscriptions: string[];
    reconnectAttempts: number;
  } {
    return {
      connected: this.isConnected(),
      connectionId: this.connectionId,
      subscriptions: Array.from(this.subscriptions),
      reconnectAttempts: this.reconnectAttempts
    };
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);

      switch (message.type) {
        case 'connection_established':
          this.connectionId = message.connection_id;
          this.emit('connection_established', message);
          break;

        case 'prediction':
          this.emit('prediction', message.data as RealtimePrediction);
          break;

        case 'market_data':
          this.emit('market_data', message.data as MarketData);
          break;

        case 'alert':
          this.emit('alert', message.data as RealtimeAlert);
          break;

        case 'system_health':
          this.emit('system_health', message.data as SystemHealth);
          break;

        case 'error':
          console.error('🚨 Server error:', message.error);
          this.emit('server_error', message.error);
          break;

        case 'pong':
          // Heartbeat response - connection is alive
          break;

        default:
          console.warn('🤔 Unknown message type:', message.type);
          this.emit('unknown_message', message);
      }
    } catch (error) {
      console.error('❌ Failed to parse WebSocket message:', error);
      this.emit('parse_error', { error, data });
    }
  }

  /**
   * Send message to WebSocket server
   */
  private send(message: any): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    try {
      this.ws!.send(JSON.stringify(message));
    } catch (error) {
      console.error('❌ Failed to send WebSocket message:', error);
      this.emit('send_error', error);
    }
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);

    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect().catch(error => {
          console.error('❌ Reconnect failed:', error);
        });
      } else {
        console.error('❌ Max reconnect attempts reached. Giving up.');
        this.emit('max_reconnects_reached');
      }
    }, delay);
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    this.ws = null;
    this.connectionId = null;
  }
}

/**
 * React Hook for WebSocket connection
 */
export function useRealtimeAI(token?: string) {
  const [client, setClient] = React.useState<RealtimeAIClient | null>(null);
  const [connected, setConnected] = React.useState(false);
  const [connectionInfo, setConnectionInfo] = React.useState<any>(null);

  React.useEffect(() => {
    const wsClient = new RealtimeAIClient(undefined, token);

    wsClient.on('connected', () => {
      setConnected(true);
      setConnectionInfo(wsClient.getConnectionInfo());
    });

    wsClient.on('disconnected', () => {
      setConnected(false);
      setConnectionInfo(wsClient.getConnectionInfo());
    });

    wsClient.connect().catch(error => {
      console.error('Failed to connect:', error);
    });

    setClient(wsClient);

    return () => {
      wsClient.disconnect();
    };
  }, [token]);

  return {
    client,
    connected,
    connectionInfo,
    connect: () => client?.connect(),
    disconnect: () => client?.disconnect(),
    subscribeToSymbol: (symbol: string) => client?.subscribeToSymbol(symbol),
    unsubscribeFromSymbol: (symbol: string) => client?.unsubscribeFromSymbol(symbol),
    subscribeToMarketData: (symbols: string[]) => client?.subscribeToMarketData(symbols),
    subscribeToAlerts: (userId: string) => client?.subscribeToAlerts(userId),
    subscribeToSystemHealth: () => client?.subscribeToSystemHealth(),
    requestPrediction: (symbol: string, options?: any) => client?.requestPrediction(symbol, options)
  };
}