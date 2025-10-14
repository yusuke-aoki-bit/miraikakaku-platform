/**
 * 価格アラート管理
 * LocalStorageを使用してブラウザ内でアラートを管理
 */

export interface PriceAlert {
  id: string;
  symbol: string;
  company_name: string;
  target_price: number;
  condition: 'above' | 'below';
  created_at: string;
  triggered: boolean;
  triggered_at?: string;
}

const STORAGE_KEY = 'miraikakaku_price_alerts';

export class PriceAlertManager {
  /**
   * すべてのアラートを取得
   */
  static getAlerts(): PriceAlert[] {
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
   * アラートを保存
   */
  static saveAlerts(alerts: PriceAlert[]): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(alerts));
  }

  /**
   * 新しいアラートを追加
   */
  static addAlert(
    symbol: string,
    company_name: string,
    target_price: number,
    condition: 'above' | 'below'
  ): PriceAlert {
    const alert: PriceAlert = {
      id: `${symbol}_${Date.now()}`,
      symbol,
      company_name,
      target_price,
      condition,
      created_at: new Date().toISOString(),
      triggered: false,
    };

    const alerts = this.getAlerts();
    alerts.push(alert);
    this.saveAlerts(alerts);

    return alert;
  }

  /**
   * アラートを削除
   */
  static removeAlert(alertId: string): void {
    const alerts = this.getAlerts();
    const filtered = alerts.filter(a => a.id !== alertId);
    this.saveAlerts(filtered);
  }

  /**
   * 銘柄のアラートを取得
   */
  static getAlertsForSymbol(symbol: string): PriceAlert[] {
    return this.getAlerts().filter(a => a.symbol === symbol);
  }

  /**
   * アラートチェック
   */
  static checkAlerts(symbol: string, current_price: number): PriceAlert[] {
    const alerts = this.getAlerts();
    const triggeredAlerts: PriceAlert[] = [];

    const updatedAlerts = alerts.map(alert => {
      if (alert.symbol === symbol && !alert.triggered) {
        const shouldTrigger =
          (alert.condition === 'above' && current_price >= alert.target_price) ||
          (alert.condition === 'below' && current_price <= alert.target_price);

        if (shouldTrigger) {
          const triggered = {
            ...alert,
            triggered: true,
            triggered_at: new Date().toISOString(),
          };
          triggeredAlerts.push(triggered);
          return triggered;
        }
      }
      return alert;
    });

    if (triggeredAlerts.length > 0) {
      this.saveAlerts(updatedAlerts);
    }

    return triggeredAlerts;
  }

  /**
   * トリガー済みアラートをクリア
   */
  static clearTriggeredAlerts(): void {
    const alerts = this.getAlerts();
    const active = alerts.filter(a => !a.triggered);
    this.saveAlerts(active);
  }

  /**
   * アラート数を取得
   */
  static getAlertCount(): number {
    return this.getAlerts().filter(a => !a.triggered).length;
  }

  /**
   * トリガー済みアラート数を取得
   */
  static getTriggeredAlertCount(): number {
    return this.getAlerts().filter(a => a.triggered).length;
  }

  /**
   * すべてのアラートをクリア
   */
  static clearAllAlerts(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(STORAGE_KEY);
  }

  /**
   * アラートの通知を送信（ブラウザ通知API）
   */
  static async notify(alert: PriceAlert, current_price: number): Promise<void> {
    if (typeof window === 'undefined') return;

    // 通知権限をリクエスト
    if ('Notification' in window && Notification.permission === 'granted') {
      const message = alert.condition === 'above'
        ? `${alert.company_name} (${alert.symbol}) が目標価格 ¥${alert.target_price.toLocaleString()} を上回りました！現在価格: ¥${current_price.toLocaleString()}`
        : `${alert.company_name} (${alert.symbol}) が目標価格 ¥${alert.target_price.toLocaleString()} を下回りました！現在価格: ¥${current_price.toLocaleString()}`;

      new Notification('価格アラート', {
        body: message,
        icon: '/favicon.ico',
        tag: alert.id,
      });
    }
  }

  /**
   * 通知権限をリクエスト
   */
  static async requestNotificationPermission(): Promise<NotificationPermission> {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      return 'denied';
    }

    if (Notification.permission === 'default') {
      return await Notification.requestPermission();
    }

    return Notification.permission;
  }
}
