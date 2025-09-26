/**
 * 監視API クライアント
 * Monitoring API Client
 */

export interface SystemHealth {
  status: string;
  connection_status: boolean;
  issues: string[];
  recommendations: string[];
  metrics?: {
    active_connections: number;
    total_connections: number;
    avg_query_duration: number;
    cpu_usage: number;
    memory_usage: number;
    timestamp: string;
  };
}

export interface PerformanceMetrics {
  timestamp: string;
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
  };
  api: {
    response_time: number;
    active_requests: number;
    total_requests: number;
    error_rate: number;
  };
  database: {
    connections: number;
  };
  cache: {
    hit_rate: number;
  };
}

export interface PerformanceAnalytics {
  period_hours: number;
  data_points: number;
  system: {
    cpu: { avg: number; max: number; min: number };
    memory: { avg: number; max: number; min: number };
  };
  api: {
    total_requests: number;
    total_errors: number;
    error_rate: number;
    response_time: { avg: number; max: number; min: number };
  };
  period: {
    start: string;
    end: string;
  };
}

export interface EndpointAnalytics {
  period_hours: number;
  total_endpoints: number;
  endpoints: Record<string, {
    requests: number;
    avg_response_time: number;
    max_response_time: number;
    error_rate: number;
    requests_per_hour: number;
  }>;
}

class MonitoringAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
  }

  private async fetchAPI<T>(endpoint: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  /**
   * データベース健全性を取得
   */
  async getDatabaseHealth(): Promise<SystemHealth> {
    return this.fetchAPI<SystemHealth>('/api/database/health');
  }

  /**
   * データベース監視サマリーを取得
   */
  async getDatabaseMonitoringSummary(hours: number = 24): Promise<any> {
    return this.fetchAPI(`/api/database/monitoring/summary?hours=${hours}`);
  }

  /**
   * 現在のパフォーマンス状況を取得
   */
  async getCurrentPerformance(): Promise<PerformanceMetrics | { status: string; message: string }> {
    return this.fetchAPI<PerformanceMetrics | { status: string; message: string }>('/api/performance/current');
  }

  /**
   * パフォーマンス分析を取得
   */
  async getPerformanceAnalytics(hours: number = 24): Promise<PerformanceAnalytics> {
    return this.fetchAPI<PerformanceAnalytics>(`/api/performance/analytics?hours=${hours}`);
  }

  /**
   * エンドポイント別パフォーマンス分析を取得
   */
  async getEndpointAnalytics(hours: number = 24): Promise<EndpointAnalytics> {
    return this.fetchAPI<EndpointAnalytics>(`/api/performance/endpoints?hours=${hours}`);
  }

  /**
   * システム状態を取得
   */
  async getSystemStatus(): Promise<any> {
    return this.fetchAPI('/api/system/status');
  }

  /**
   * ヘルスチェックを実行
   */
  async getHealthCheck(): Promise<any> {
    return this.fetchAPI('/api/health');
  }

  /**
   * パフォーマンスデータをエクスポート
   */
  async exportPerformanceData(): Promise<{ status: string; filename?: string; message: string }> {
    return this.fetchAPI('/api/performance/export');
  }
}

export const monitoringAPI = new MonitoringAPI();