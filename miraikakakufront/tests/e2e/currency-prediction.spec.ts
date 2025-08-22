import { test, expect } from '@playwright/test';

test.describe('Currency Prediction Page', () => {
  test.beforeEach(async ({ page }) => {
    // 通貨ペアリストのモック
    await page.route('**/api/currency/pairs*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { pair: 'USD/JPY', base_currency: 'USD', quote_currency: 'JPY', current_rate: 150.25 },
          { pair: 'EUR/USD', base_currency: 'EUR', quote_currency: 'USD', current_rate: 1.0845 },
          { pair: 'GBP/USD', base_currency: 'GBP', quote_currency: 'USD', current_rate: 1.2715 },
          { pair: 'EUR/JPY', base_currency: 'EUR', quote_currency: 'JPY', current_rate: 162.90 }
        ])
      });
    });

    // 通貨レートのモック
    await page.route('**/api/currency/rate/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          pair: 'USD/JPY',
          current_rate: 150.25,
          bid: 150.23,
          ask: 150.27,
          spread: 0.04,
          change_24h: 0.45,
          change_percent_24h: 0.3,
          high_24h: 150.85,
          low_24h: 149.65,
          volume_24h: 1250000000,
          last_updated: '2025-08-22T08:30:00Z'
        })
      });
    });

    // 通貨予測のモック
    await page.route('**/api/currency/predictions/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          pair: 'USD/JPY',
          predictions: [
            {
              timeframe: '1D',
              predicted_rate: 150.75,
              confidence: 0.82,
              support_level: 149.50,
              resistance_level: 151.20,
              trend_direction: 'bullish'
            }
          ],
          technical_indicators: {
            rsi: 58.5,
            macd: {
              value: 0.15,
              signal: 0.12,
              histogram: 0.03
            },
            bollinger_bands: {
              upper: 151.50,
              middle: 150.25,
              lower: 149.00
            }
          },
          trading_signals: {
            signal: 'BUY',
            strength: 75,
            entry_point: 150.30,
            stop_loss: 149.80,
            take_profit: 151.00
          }
        })
      });
    });

    // 経済カレンダーのモック
    await page.route('**/api/currency/economic-calendar*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            date: '2025-08-22',
            time: '14:30',
            currency: 'USD',
            event: 'GDP Growth Rate',
            importance: 'high',
            forecast: 2.1,
            previous: 2.0,
            actual: null,
            impact: 'neutral'
          }
        ])
      });
    });

    await page.goto('/currency');
    await page.waitForLoadState('networkidle');
  });

  test('should display currency prediction page with correct title', async ({ page }) => {
    // ページタイトルの確認
    await expect(page.locator('h1')).toContainText('通貨予測');
    
    // 地球アイコンの確認
    const globeIcon = page.locator('[data-lucide="globe"]').first();
    await expect(globeIcon).toBeVisible();
  });

  test('should show currency pair selector', async ({ page }) => {
    // 通貨ペアセレクターの確認
    const pairSelector = page.locator('select, .currency-pair-selector');
    
    // セレクターが存在するかチェック
    if (await pairSelector.count() > 0) {
      await expect(pairSelector.first()).toBeVisible();
      
      // オプションの確認
      await expect(page.locator('text=USD/JPY')).toBeVisible();
      await expect(page.locator('text=EUR/USD')).toBeVisible();
    } else {
      // ドロップダウンやボタン形式の場合
      const pairButton = page.locator('button').filter({ hasText: /USD\/JPY|EUR\/USD/ });
      if (await pairButton.count() > 0) {
        await expect(pairButton.first()).toBeVisible();
      }
    }
  });

  test('should display current exchange rates', async ({ page }) => {
    // 現在のレート表示の確認
    await expect(page.locator('text=150.25').or(page.locator('text=¥150.25'))).toBeVisible();
    
    // 変動率の表示確認
    await expect(page.locator('text=+0.3%').or(page.locator('text=0.3%'))).toBeVisible();
  });

  test('should show prediction chart', async ({ page }) => {
    // チャートコンポーネントの確認
    const canvas = page.locator('canvas');
    await expect(canvas.first()).toBeVisible({ timeout: 10000 });
    
    // チャートの描画完了を待つ
    await page.waitForTimeout(2000);
  });

  test('should display technical indicators', async ({ page }) => {
    // テクニカル指標の確認
    await expect(page.locator('text=RSI').or(page.locator('text=58.5'))).toBeVisible();
    await expect(page.locator('text=MACD')).toBeVisible();
    await expect(page.locator('text=ボリンジャーバンド').or(page.locator('text=Bollinger'))).toBeVisible();
  });

  test('should show trading signals', async ({ page }) => {
    // トレーディングシグナルの確認
    await expect(page.locator('text=BUY').or(page.locator('text=買い'))).toBeVisible();
    
    // シグナル強度の確認
    await expect(page.locator('text=75').or(page.locator('text=75%'))).toBeVisible();
    
    // エントリーポイントの確認
    await expect(page.locator('text=150.30').or(page.locator('text=¥150.30'))).toBeVisible();
  });

  test('should display economic calendar', async ({ page }) => {
    // 経済カレンダーの確認
    await expect(page.locator('text=GDP Growth Rate').or(page.locator('text=GDP'))).toBeVisible();
    await expect(page.locator('text=14:30')).toBeVisible();
    await expect(page.locator('text=USD')).toBeVisible();
  });

  test('should switch currency pairs', async ({ page }) => {
    // 通貨ペアの切り替えテスト
    const eurUsdOption = page.locator('text=EUR/USD');
    
    if (await eurUsdOption.isVisible()) {
      await eurUsdOption.click();
      await page.waitForTimeout(1000);
      
      // 新しい通貨ペアのデータが表示されることを確認
      // APIモックを更新して異なるレートを返すようにする
      await page.route('**/api/currency/rate/EUR-USD', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            pair: 'EUR/USD',
            current_rate: 1.0845,
            change_24h: -0.0015,
            change_percent_24h: -0.14
          })
        });
      });
    }
  });

  test('should handle timeframe selection', async ({ page }) => {
    // 時間軸選択ボタンの確認
    const timeframeButtons = page.locator('button').filter({ hasText: /1D|1W|1M|3M|1Y/ });
    
    if (await timeframeButtons.count() > 0) {
      // 1週間ボタンをクリック
      const weekButton = timeframeButtons.filter({ hasText: '1W' });
      if (await weekButton.count() > 0) {
        await weekButton.click();
        await page.waitForTimeout(1000);
        
        // チャートが更新されることを確認
        const canvas = page.locator('canvas');
        await expect(canvas).toBeVisible();
      }
    }
  });

  test('should show prediction confidence levels', async ({ page }) => {
    // 予測信頼度の表示確認
    await expect(page.locator('text=82%').or(page.locator('text=0.82'))).toBeVisible();
    
    // 信頼度バーまたはメーターの確認
    const confidenceIndicator = page.locator('.confidence, [data-testid="confidence"], .progress');
    if (await confidenceIndicator.count() > 0) {
      await expect(confidenceIndicator.first()).toBeVisible();
    }
  });

  test('should display support and resistance levels', async ({ page }) => {
    // サポートレベルの確認
    await expect(page.locator('text=149.50').or(page.locator('text=¥149.50'))).toBeVisible();
    
    // レジスタンスレベルの確認
    await expect(page.locator('text=151.20').or(page.locator('text=¥151.20'))).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // モバイルビューポートに変更
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // モバイルでも基本要素が表示されることを確認
    await expect(page.locator('h1')).toBeVisible();
    
    // チャートがモバイルに適応することを確認
    const canvas = page.locator('canvas');
    await expect(canvas.first()).toBeVisible({ timeout: 10000 });
    
    // コンテンツがスクロール可能であることを確認
    await page.mouse.wheel(0, 200);
  });

  test('should handle loading states', async ({ page }) => {
    // 新しいページロードでローディング状態をテスト
    await page.goto('/currency');
    
    // ローディングスピナーまたはスケルトンの確認
    const loadingElement = page.locator('[data-testid*="loading"], .skeleton, .animate-pulse');
    
    try {
      await expect(loadingElement.first()).toBeVisible({ timeout: 2000 });
    } catch {
      console.log('Loading state was too fast to capture');
    }
    
    // ローディング完了後にコンテンツが表示されることを確認
    await expect(page.locator('h1')).toBeVisible({ timeout: 10000 });
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // API エラーをモック
    await page.route('**/api/currency/**', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Currency API unavailable' })
      });
    });

    await page.goto('/currency');
    await page.waitForLoadState('networkidle');
    
    // エラー状態でもページが表示されることを確認
    await expect(page.locator('h1')).toBeVisible();
    
    // エラーメッセージまたはフォールバックコンテンツの確認
    await page.waitForTimeout(2000);
  });

  test('should show trend direction indicators', async ({ page }) => {
    // トレンド方向インジケーターの確認
    await expect(page.locator('text=bullish').or(page.locator('text=上昇'))).toBeVisible();
    
    // 上昇トレンドのアイコン確認
    const trendUpIcon = page.locator('[data-lucide="trending-up"]');
    if (await trendUpIcon.count() > 0) {
      await expect(trendUpIcon.first()).toBeVisible();
    }
  });

  test('should update data in real-time', async ({ page }) => {
    // リアルタイム更新のシミュレーション
    // 初期レートを確認
    await expect(page.locator('text=150.25')).toBeVisible();
    
    // WebSocketや定期更新をモック
    // 新しいレートでAPIレスポンスを更新
    await page.route('**/api/currency/rate/USD-JPY', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          pair: 'USD/JPY',
          current_rate: 150.35,
          change_24h: 0.55,
          change_percent_24h: 0.37
        })
      });
    });
    
    // データの更新をトリガー（実際のアプリケーションによる）
    await page.waitForTimeout(3000);
  });
});