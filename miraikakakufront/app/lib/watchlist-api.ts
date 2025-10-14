const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface WatchlistItem {
  id: number;
  symbol: string;
  company_name: string;
  exchange: string;
  sector?: string;
  current_price: number;
  price_change: number;
  price_change_pct: number;
  ensemble_prediction?: number;
  ensemble_confidence?: number;
  predicted_change_pct?: number;
  alert_price_high?: number;
  alert_price_low?: number;
  alert_enabled: boolean;
  alert_triggered: boolean;
  notes?: string;
  created_at: string;
}

export async function getWatchlist(userId: string): Promise<WatchlistItem[]> {
  const response = await fetch(`${API_BASE}/api/watchlist?user_id=${userId}`);
  if (!response.ok) throw new Error('Failed to fetch watchlist');
  const data = await response.json();
  return data.items || [];
}

export async function addToWatchlist(params: {
  user_id: string;
  symbol: string;
  notes?: string;
  alert_price_high?: number;
  alert_price_low?: number;
  alert_enabled?: boolean;
}) {
  const response = await fetch(`${API_BASE}/api/watchlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to add to watchlist');
  }
  return response.json();
}

export async function removeFromWatchlist(id: number, userId: string) {
  const response = await fetch(
    `${API_BASE}/api/watchlist/${id}?user_id=${userId}`,
    { method: 'DELETE' }
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to remove from watchlist');
  }
  return response.json();
}

export async function updateWatchlistItem(id: number, params: {
  user_id: string;
  notes?: string;
  alert_price_high?: number;
  alert_price_low?: number;
  alert_enabled?: boolean;
}) {
  const response = await fetch(`${API_BASE}/api/watchlist/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to update watchlist item');
  }
  return response.json();
}
