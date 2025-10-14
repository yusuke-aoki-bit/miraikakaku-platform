/**
 * API Client Library
 * 認証ヘッダーの自動付与とエラーハンドリングを提供
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-465603676610.us-central1.run.app';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

interface APIClientOptions extends RequestInit {
  requiresAuth?: boolean;
}

/**
 * APIクライアント - 全てのAPI呼び出しに使用
 *
 * @param endpoint APIエンドポイント（例: "/api/watchlist"）
 * @param options リクエストオプション
 * @returns レスポンスのJSONデータ
 */
export async function apiClient<T = any>(
  endpoint: string,
  options: APIClientOptions = {}
): Promise<T> {
  const { requiresAuth = true, ...fetchOptions } = options;

  // ヘッダーの準備
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  // 認証が必要な場合はトークンを追加
  if (requiresAuth) {
    const token = getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      // トークンがない場合はログインページにリダイレクト
      if (typeof window !== 'undefined') {
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
      }
      throw new APIError('Unauthorized - No access token', 401);
    }
  }

  // リクエストの実行
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    // レスポンスの処理
    if (!response.ok) {
      // エラーレスポンスの詳細を取得
      let errorDetail: any;
      try {
        errorDetail = await response.json();
      } catch {
        errorDetail = await response.text();
      }

      // 401エラーの場合はログインページにリダイレクト
      if (response.status === 401) {
        clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        }
      }

      throw new APIError(
        errorDetail?.detail || errorDetail?.message || `API Error: ${response.status}`,
        response.status,
        errorDetail
      );
    }

    // 204 No Content の場合は null を返す
    if (response.status === 204) {
      return null as T;
    }

    // JSONレスポンスを返す
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // ネットワークエラーなどの場合
    throw new APIError(
      error instanceof Error ? error.message : 'Unknown error occurred',
      0
    );
  }
}

/**
 * GET リクエスト
 */
export async function apiGet<T = any>(
  endpoint: string,
  options: APIClientOptions = {}
): Promise<T> {
  return apiClient<T>(endpoint, {
    ...options,
    method: 'GET',
  });
}

/**
 * POST リクエスト
 */
export async function apiPost<T = any>(
  endpoint: string,
  data?: any,
  options: APIClientOptions = {}
): Promise<T> {
  return apiClient<T>(endpoint, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT リクエスト
 */
export async function apiPut<T = any>(
  endpoint: string,
  data?: any,
  options: APIClientOptions = {}
): Promise<T> {
  return apiClient<T>(endpoint, {
    ...options,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE リクエスト
 */
export async function apiDelete<T = any>(
  endpoint: string,
  options: APIClientOptions = {}
): Promise<T> {
  return apiClient<T>(endpoint, {
    ...options,
    method: 'DELETE',
  });
}

/**
 * トークン管理関数
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

/**
 * トークンのリフレッシュ
 */
export async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      clearTokens();
      return null;
    }

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token || refreshToken);
    return data.access_token;
  } catch (error) {
    clearTokens();
    return null;
  }
}

/**
 * API Hooks（各機能モジュール用）
 */

// Watchlist API
export const watchlistAPI = {
  getAll: () => apiGet('/api/watchlist'),
  getDetails: () => apiGet('/api/watchlist/details'),
  add: (symbol: string, notes?: string) =>
    apiPost('/api/watchlist', { symbol, notes }),
  update: (symbol: string, notes: string) =>
    apiPut(`/api/watchlist/${symbol}`, { notes }),
  remove: (symbol: string) =>
    apiDelete(`/api/watchlist/${symbol}`),
};

// Portfolio API
export const portfolioAPI = {
  getAll: () => apiGet('/api/portfolio'),
  getPerformance: () => apiGet('/api/portfolio/performance'),
  getSummary: () => apiGet('/api/portfolio/summary'),
  add: (data: {
    symbol: string;
    quantity: number;
    average_buy_price: number;
    buy_date: string;
    notes?: string;
  }) => apiPost('/api/portfolio', data),
  update: (id: number, data: {
    quantity?: number;
    average_buy_price?: number;
    notes?: string;
  }) => apiPut(`/api/portfolio/${id}`, data),
  remove: (id: number) => apiDelete(`/api/portfolio/${id}`),
};

// Alerts API
export const alertsAPI = {
  getAll: () => apiGet('/api/alerts'),
  getDetails: () => apiGet('/api/alerts/details'),
  getTriggered: () => apiGet('/api/alerts/triggered'),
  create: (data: {
    symbol: string;
    alert_type: string;
    threshold: number;
    notes?: string;
  }) => apiPost('/api/alerts', data),
  update: (id: number, data: {
    threshold?: number;
    is_active?: boolean;
    notes?: string;
  }) => apiPut(`/api/alerts/${id}`, data),
  remove: (id: number) => apiDelete(`/api/alerts/${id}`),
  checkAlerts: () => apiPost('/api/alerts/check'),
};

// Auth API
export const authAPI = {
  login: (username: string, password: string) =>
    apiPost('/api/auth/login', { username, password }, { requiresAuth: false }),
  register: (username: string, email: string, password: string) =>
    apiPost('/api/auth/register', { username, email, password }, { requiresAuth: false }),
  getMe: () => apiGet('/api/auth/me'),
  refresh: (refreshToken: string) =>
    apiPost('/api/auth/refresh', { refresh_token: refreshToken }, { requiresAuth: false }),
};
