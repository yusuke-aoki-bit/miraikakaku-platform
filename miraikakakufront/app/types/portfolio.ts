/**
 * Portfolio Management Types
 * Phase 5-2: Frontend Implementation
 */

export interface PortfolioHolding {
  id: number;
  user_id: string;
  symbol: string;
  company_name: string;
  exchange: string;
  sector: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
  current_price: number;
  cost_basis: number;
  current_value: number;
  unrealized_gain: number;
  unrealized_gain_pct: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PortfolioSummary {
  total_cost: number;
  total_value: number;
  unrealized_gain: number;
  unrealized_gain_pct: number;
}

export interface AddHoldingRequest {
  user_id: string;
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
  notes?: string;
}

export interface PortfolioAPIResponse {
  status: 'success' | 'error';
  holdings?: PortfolioHolding[];
  summary?: PortfolioSummary;
  holding?: Partial<PortfolioHolding>;
  message?: string;
}

export interface SectorAllocation {
  sector: string;
  value: number;
  percentage: number;
  holdings_count: number;
}
