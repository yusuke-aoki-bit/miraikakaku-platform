/**
 * Portfolio API Client
 * Phase 5-2: Frontend Implementation
 */

import {
  PortfolioHolding,
  PortfolioSummary,
  AddHoldingRequest,
  PortfolioAPIResponse
} from '@/app/types/portfolio';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app';

/**
 * Fetch all holdings for a user
 */
export async function getPortfolioHoldings(userId: string): Promise<PortfolioHolding[]> {
  const response = await fetch(`${API_BASE_URL}/api/portfolio/holdings/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store', // Always fetch fresh data for portfolio
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch holdings: ${response.statusText}`);
  }

  const data: PortfolioAPIResponse = await response.json();

  if (data.status === 'error') {
    throw new Error(data.message || 'Failed to fetch holdings');
  }

  return data.holdings || [];
}

/**
 * Fetch portfolio summary for a user
 */
export async function getPortfolioSummary(userId: string): Promise<PortfolioSummary> {
  const response = await fetch(`${API_BASE_URL}/api/portfolio/summary/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch summary: ${response.statusText}`);
  }

  const data: PortfolioAPIResponse = await response.json();

  if (data.status === 'error') {
    throw new Error(data.message || 'Failed to fetch summary');
  }

  return data.summary || {
    total_cost: 0,
    total_value: 0,
    unrealized_gain: 0,
    unrealized_gain_pct: 0,
  };
}

/**
 * Add a new holding to the portfolio
 */
export async function addPortfolioHolding(request: AddHoldingRequest): Promise<void> {
  const params = new URLSearchParams({
    user_id: request.user_id,
    symbol: request.symbol,
    quantity: request.quantity.toString(),
    purchase_price: request.purchase_price.toString(),
    purchase_date: request.purchase_date,
  });

  if (request.notes) {
    params.append('notes', request.notes);
  }

  const response = await fetch(`${API_BASE_URL}/api/portfolio/holdings?${params}`, {
    method: 'POST',
    headers: {
      'Content-Length': '0',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to add holding: ${response.statusText}`);
  }

  const data: PortfolioAPIResponse = await response.json();

  if (data.status === 'error') {
    throw new Error(data.message || 'Failed to add holding');
  }
}

/**
 * Delete a holding from the portfolio
 */
export async function deletePortfolioHolding(holdingId: number, userId: string): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/portfolio/holdings/${holdingId}?user_id=${userId}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to delete holding: ${response.statusText}`);
  }

  const data: PortfolioAPIResponse = await response.json();

  if (data.status === 'error') {
    throw new Error(data.message || 'Failed to delete holding');
  }
}

/**
 * Format currency for display
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency: 'JPY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format percentage for display
 */
export function formatPercentage(value: number): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

/**
 * Get color class for gain/loss
 */
export function getGainLossColor(value: number): string {
  if (value > 0) return 'text-green-600';
  if (value < 0) return 'text-red-600';
  return 'text-gray-600';
}
