/**
 * ポートフォリオ管理
 * LocalStorageを使用してブラウザ内で保有銘柄を管理
 */

export interface PortfolioPosition {
  id: string;
  symbol: string;
  company_name: string;
  exchange: string;
  quantity: number;
  average_price: number;
  purchase_date: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PortfolioSummary {
  total_positions: number;
  total_value: number;
  total_cost: number;
  total_profit_loss: number;
  total_profit_loss_percent: number;
  positions_with_prices: number;
}

const STORAGE_KEY = 'miraikakaku_portfolio';

export class PortfolioManager {
  /**
   * すべてのポジションを取得
   */
  static getPositions(): PortfolioPosition[] {
    if (typeof window === 'undefined') return [];

    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    try {
      return JSON.parse(stored);
    } catch {
      return [];
    }
  }

  /**
   * ポジションを保存
   */
  static savePositions(positions: PortfolioPosition[]): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(positions));
  }

  /**
   * 新しいポジションを追加
   */
  static addPosition(
    symbol: string,
    company_name: string,
    exchange: string,
    quantity: number,
    average_price: number,
    purchase_date: string,
    notes?: string
  ): PortfolioPosition {
    const position: PortfolioPosition = {
      id: `${symbol}_${Date.now()}`,
      symbol,
      company_name,
      exchange,
      quantity,
      average_price,
      purchase_date,
      notes,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const positions = this.getPositions();
    positions.push(position);
    this.savePositions(positions);

    return position;
  }

  /**
   * ポジションを更新
   */
  static updatePosition(
    id: string,
    updates: Partial<Omit<PortfolioPosition, 'id' | 'symbol' | 'created_at'>>
  ): void {
    const positions = this.getPositions();
    const index = positions.findIndex(p => p.id === id);

    if (index !== -1) {
      positions[index] = {
        ...positions[index],
        ...updates,
        updated_at: new Date().toISOString(),
      };
      this.savePositions(positions);
    }
  }

  /**
   * ポジションを削除
   */
  static removePosition(id: string): void {
    const positions = this.getPositions();
    const filtered = positions.filter(p => p.id !== id);
    this.savePositions(filtered);
  }

  /**
   * 銘柄のポジションを取得
   */
  static getPositionsBySymbol(symbol: string): PortfolioPosition[] {
    return this.getPositions().filter(p => p.symbol === symbol);
  }

  /**
   * ポートフォリオサマリーを計算
   */
  static calculateSummary(
    positions: PortfolioPosition[],
    currentPrices: Map<string, number>
  ): PortfolioSummary {
    let total_cost = 0;
    let total_value = 0;
    let positions_with_prices = 0;

    positions.forEach(position => {
      const cost = position.quantity * position.average_price;
      total_cost += cost;

      const currentPrice = currentPrices.get(position.symbol);
      if (currentPrice !== undefined) {
        total_value += position.quantity * currentPrice;
        positions_with_prices++;
      }
    });

    const total_profit_loss = total_value - total_cost;
    const total_profit_loss_percent = total_cost > 0
      ? (total_profit_loss / total_cost) * 100
      : 0;

    return {
      total_positions: positions.length,
      total_value,
      total_cost,
      total_profit_loss,
      total_profit_loss_percent,
      positions_with_prices,
    };
  }

  /**
   * ポジション別の損益を計算
   */
  static calculatePositionProfitLoss(
    position: PortfolioPosition,
    currentPrice?: number
  ): {
    cost: number;
    current_value: number;
    profit_loss: number;
    profit_loss_percent: number;
  } | null {
    if (currentPrice === undefined) return null;

    const cost = position.quantity * position.average_price;
    const current_value = position.quantity * currentPrice;
    const profit_loss = current_value - cost;
    const profit_loss_percent = cost > 0 ? (profit_loss / cost) * 100 : 0;

    return {
      cost,
      current_value,
      profit_loss,
      profit_loss_percent,
    };
  }

  /**
   * エクスポート（CSV形式）
   */
  static exportToCSV(
    positions: PortfolioPosition[],
    currentPrices: Map<string, number>
  ): string {
    const headers = [
      '銘柄コード',
      '企業名',
      '取引所',
      '保有数',
      '平均取得価格',
      '取得金額',
      '現在価格',
      '評価額',
      '損益',
      '損益率(%)',
      '購入日',
      'メモ',
    ].join(',');

    const rows = positions.map(position => {
      const currentPrice = currentPrices.get(position.symbol);
      const profitLoss = this.calculatePositionProfitLoss(position, currentPrice);

      return [
        position.symbol,
        `"${position.company_name}"`,
        position.exchange,
        position.quantity,
        position.average_price,
        position.quantity * position.average_price,
        currentPrice || '',
        profitLoss?.current_value || '',
        profitLoss?.profit_loss || '',
        profitLoss?.profit_loss_percent.toFixed(2) || '',
        position.purchase_date,
        `"${position.notes || ''}"`,
      ].join(',');
    });

    return [headers, ...rows].join('\n');
  }

  /**
   * インポート（CSV形式）
   */
  static importFromCSV(csvData: string): PortfolioPosition[] {
    const lines = csvData.trim().split('\n');
    if (lines.length < 2) return [];

    const positions: PortfolioPosition[] = [];

    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(',');
      if (parts.length < 6) continue;

      try {
        positions.push({
          id: `${parts[0]}_${Date.now()}_${i}`,
          symbol: parts[0],
          company_name: parts[1].replace(/"/g, ''),
          exchange: parts[2],
          quantity: parseFloat(parts[3]),
          average_price: parseFloat(parts[4]),
          purchase_date: parts[10],
          notes: parts[11]?.replace(/"/g, ''),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      } catch (error) {
        console.error('Error parsing CSV line:', lines[i], error);
      }
    }

    return positions;
  }

  /**
   * すべてのポジションをクリア
   */
  static clearAllPositions(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(STORAGE_KEY);
  }

  /**
   * ポジション数を取得
   */
  static getPositionCount(): number {
    return this.getPositions().length;
  }
}
