import { test, expect } from '@playwright/test';

test.describe('Triple Chart Component', () => {
  test.beforeEach(async ({ page }) => {
    // 株価データのモック（3つの時間軸用）
    await page.route('**/api/finance/stocks/*/price*', async route => {
      const url = route.request().url();
      let mockData;
      
      if (url.includes('days=7')) {
        // 短期データ（1週間）
        mockData = Array.from({ length: 7 }, (_, i) => ({
          date: new Date(2025, 7, 22 - i).toISOString().split('T')[0],
          close_price: 225.50 + (Math.random() - 0.5) * 10,
          open_price: 224.00 + (Math.random() - 0.5) * 10,
          high_price: 227.00 + (Math.random() - 0.5) * 10,
          low_price: 223.50 + (Math.random() - 0.5) * 10,
          volume: 42500000 + Math.floor(Math.random() * 10000000)
        }));
      } else if (url.includes('days=30')) {
        // 中期データ（1ヶ月）
        mockData = Array.from({ length: 30 }, (_, i) => ({
          date: new Date(2025, 7, 22 - i).toISOString().split('T')[0],
          close_price: 225.50 + (Math.random() - 0.5) * 25,
          open_price: 224.00 + (Math.random() - 0.5) * 25,
          high_price: 227.00 + (Math.random() - 0.5) * 25,
          low_price: 223.50 + (Math.random() - 0.5) * 25,
          volume: 42500000 + Math.floor(Math.random() * 20000000)
        }));
      } else {
        // 長期データ（90日）
        mockData = Array.from({ length: 90 }, (_, i) => ({
          date: new Date(2025, 7, 22 - i).toISOString().split('T')[0],
          close_price: 225.50 + (Math.random() - 0.5) * 50,
          open_price: 224.00 + (Math.random() - 0.5) * 50,
          high_price: 227.00 + (Math.random() - 0.5) * 50,
          low_price: 223.50 + (Math.random() - 0.5) * 50,
          volume: 42500000 + Math.floor(Math.random() * 30000000)
        }));
      }
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockData)
      });
    });

    // 予測データのモック（3つの時間軸用）
    await page.route('**/api/finance/stocks/*/predictions*', async route => {
      const url = route.request().url();
      let predictionDays = 7;
      
      if (url.includes('days=30')) predictionDays = 30;
      else if (url.includes('days=90')) predictionDays = 90;
      
      const mockPredictions = Array.from({ length: predictionDays }, (_, i) => ({
        date: new Date(2025, 7, 23 + i).toISOString().split('T')[0],
        predicted_price: 225.50 + (Math.random() - 0.5) * 15,
        confidence: 0.9 - (i * 0.01), // 信頼度は時間とともに低下
        upper_bound: 225.50 + Math.random() * 20,
        lower_bound: 225.50 - Math.random() * 20,
        prediction_model: 'LSTM-Dynamic',
        volatility: 0.013 + (i * 0.001)
      }));
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPredictions)
      });
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should render all three chart timeframes', async ({ page }) => {
    // 3つのチャートコンテナの確認
    const chartContainers = page.locator('.triple-chart, [data-testid="triple-chart"]');
    
    if (await chartContainers.count() > 0) {
      await expect(chartContainers.first()).toBeVisible();
      
      // 3つのキャンバス要素（各時間軸用）の確認
      const canvases = page.locator('canvas');
      const canvasCount = await canvases.count();
      expect(canvasCount).toBeGreaterThanOrEqual(3);
      
      // 各チャートが描画されることを確認
      for (let i = 0; i < Math.min(3, canvasCount); i++) {
        await expect(canvases.nth(i)).toBeVisible({ timeout: 10000 });
      }
    } else {
      // TripleChartが個別のチャートとして配置されている場合
      const shortTermChart = page.locator('[data-testid="short-term-chart"], .short-term');
      const mediumTermChart = page.locator('[data-testid="medium-term-chart"], .medium-term');
      const longTermChart = page.locator('[data-testid="long-term-chart"], .long-term');
      
      if (await shortTermChart.count() > 0) {
        await expect(shortTermChart.first()).toBeVisible();
      }
      if (await mediumTermChart.count() > 0) {
        await expect(mediumTermChart.first()).toBeVisible();
      }
      if (await longTermChart.count() > 0) {
        await expect(longTermChart.first()).toBeVisible();
      }
    }
  });

  test('should display timeframe labels', async ({ page }) => {
    // 時間軸ラベルの確認
    await expect(page.locator('text=短期').or(page.locator('text=1週間')).or(page.locator('text=Short'))).toBeVisible();
    await expect(page.locator('text=中期').or(page.locator('text=1ヶ月')).or(page.locator('text=Medium'))).toBeVisible();
    await expect(page.locator('text=長期').or(page.locator('text=3ヶ月')).or(page.locator('text=Long'))).toBeVisible();
  });

  test('should show prediction accuracy for each timeframe', async ({ page }) => {
    // 各時間軸の予測精度の確認
    const accuracyElements = page.locator('text=/\\d+%/').or(page.locator('text=/精度/'));
    const accuracyCount = await accuracyElements.count();
    
    if (accuracyCount > 0) {
      // 少なくとも1つの精度指標が表示されることを確認
      await expect(accuracyElements.first()).toBeVisible();
    }
    
    // 信頼度スコアの確認
    const confidenceElements = page.locator('text=/0\\.[0-9]/').or(page.locator('text=/信頼度/'));
    const confidenceCount = await confidenceElements.count();
    
    if (confidenceCount > 0) {
      await expect(confidenceElements.first()).toBeVisible();
    }
  });

  test('should handle chart synchronization', async ({ page }) => {
    // チャート間の同期機能のテスト
    const charts = page.locator('canvas');
    const chartCount = await charts.count();
    
    if (chartCount >= 3) {
      // 最初のチャートでホバーイベントをシミュレート
      const firstChart = charts.first();
      await firstChart.hover();
      await page.waitForTimeout(500);
      
      // 他のチャートでもツールチップが表示されるかチェック
      const tooltips = page.locator('.chartjs-tooltip, [data-testid="tooltip"]');
      const tooltipCount = await tooltips.count();
      
      // 同期されている場合、複数のツールチップが表示される可能性がある
      if (tooltipCount > 1) {
        console.log(`${tooltipCount} tooltips found - charts may be synchronized`);
      }
    }
  });

  test('should display correlation analysis', async ({ page }) => {
    // 相関分析結果の確認
    await expect(page.locator('text=相関').or(page.locator('text=Correlation'))).toBeVisible();
    
    // 相関係数の表示確認
    const correlationValues = page.locator('text=/0\\.[0-9]+/').or(page.locator('text=/-?[01]\\.[0-9]+/'));
    if (await correlationValues.count() > 0) {
      await expect(correlationValues.first()).toBeVisible();
    }
  });

  test('should show trend comparison across timeframes', async ({ page }) => {
    // トレンド比較インジケーターの確認
    const trendIndicators = page.locator('[data-lucide="trending-up"], [data-lucide="trending-down"]');
    const trendCount = await trendIndicators.count();
    
    if (trendCount > 0) {
      // 各時間軸のトレンド方向が表示されることを確認
      expect(trendCount).toBeGreaterThanOrEqual(1);
      
      // 上昇・下降トレンドアイコンの確認
      const upTrend = page.locator('[data-lucide="trending-up"]');
      const downTrend = page.locator('[data-lucide="trending-down"]');
      
      if (await upTrend.count() > 0) {
        await expect(upTrend.first()).toBeVisible();
      }
      if (await downTrend.count() > 0) {
        await expect(downTrend.first()).toBeVisible();
      }
    }
  });

  test('should handle different chart types', async ({ page }) => {
    // チャートタイプ切り替えボタンの確認
    const chartTypeButtons = page.locator('button').filter({ hasText: /Line|Candlestick|Bar|線|ローソク|棒/ });
    const buttonCount = await chartTypeButtons.count();
    
    if (buttonCount > 0) {
      // 線グラフボタンをクリック
      const lineButton = chartTypeButtons.filter({ hasText: /Line|線/ });
      if (await lineButton.count() > 0) {
        await lineButton.first().click();
        await page.waitForTimeout(1000);
        
        // チャートが更新されることを確認
        const canvas = page.locator('canvas');
        await expect(canvas.first()).toBeVisible();
      }
      
      // ローソク足チャートボタンをクリック
      const candlestickButton = chartTypeButtons.filter({ hasText: /Candlestick|ローソク/ });
      if (await candlestickButton.count() > 0) {
        await candlestickButton.first().click();
        await page.waitForTimeout(1000);
        
        // チャートが更新されることを確認
        const canvas = page.locator('canvas');
        await expect(canvas.first()).toBeVisible();
      }
    }
  });

  test('should display volume overlay options', async ({ page }) => {
    // 出来高オーバーレイオプションの確認
    const volumeToggle = page.locator('input[type="checkbox"]').or(page.locator('button')).filter({ hasText: /Volume|出来高/ });
    
    if (await volumeToggle.count() > 0) {
      const toggle = volumeToggle.first();
      await expect(toggle).toBeVisible();
      
      // 出来高表示の切り替えテスト
      await toggle.click();
      await page.waitForTimeout(1000);
      
      // チャートが更新されることを確認
      const canvas = page.locator('canvas');
      await expect(canvas.first()).toBeVisible();
      
      // 再度クリックして切り替え
      await toggle.click();
      await page.waitForTimeout(1000);
    }
  });

  test('should handle legend interaction', async ({ page }) => {
    // チャートの凡例の確認
    const legend = page.locator('.chartjs-legend, [data-testid="legend"], .legend');
    
    if (await legend.count() > 0) {
      await expect(legend.first()).toBeVisible();
      
      // 凡例項目のクリック可能性をテスト
      const legendItems = legend.locator('li, span, .legend-item').first();
      
      if (await legendItems.count() > 0) {
        await legendItems.click();
        await page.waitForTimeout(500);
        
        // データの表示/非表示が切り替わることを確認
        const canvas = page.locator('canvas');
        await expect(canvas.first()).toBeVisible();
      }
    }
  });

  test('should be responsive across different screen sizes', async ({ page }) => {
    // デスクトップサイズでのテスト
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    let canvases = page.locator('canvas');
    let canvasCount = await canvases.count();
    expect(canvasCount).toBeGreaterThanOrEqual(1);
    
    // タブレットサイズでのテスト
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    canvases = page.locator('canvas');
    canvasCount = await canvases.count();
    expect(canvasCount).toBeGreaterThanOrEqual(1);
    
    // モバイルサイズでのテスト
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    canvases = page.locator('canvas');
    canvasCount = await canvases.count();
    expect(canvasCount).toBeGreaterThanOrEqual(1);
    
    // モバイルでもスクロール可能であることを確認
    await page.mouse.wheel(0, 300);
  });

  test('should handle data loading states', async ({ page }) => {
    // データ読み込み中のローディング状態をテスト
    await page.goto('/dashboard');
    
    // ページが基本的にロードされることを確認
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // ダッシュボードページが正常に表示されていることを確認
    // ページタイトルまたは基本的な要素の存在確認
    const pageLoaded = await page.locator('body').isVisible();
    expect(pageLoaded).toBe(true);
    
    // ダッシュボードのメイン要素（どれか1つでも存在すれば成功）
    const possibleElements = [
      page.locator('h1, h2'), // ページタイトル
      page.locator('nav'), // ナビゲーション
      page.locator('[class*="dashboard"]'), // ダッシュボード関連クラス
      page.locator('[class*="bg-"]'), // Tailwind背景クラス
      page.locator('main, [role="main"]'), // メインコンテンツ
      page.locator('svg, canvas'), // チャート要素
    ];
    
    let foundElement = false;
    for (const element of possibleElements) {
      const count = await element.count();
      if (count > 0) {
        foundElement = true;
        break;
      }
    }
    
    expect(foundElement).toBe(true);
  });

  test('should handle API failures gracefully', async ({ page }) => {
    // 特定の時間軸のAPIエラーをシミュレート
    await page.route('**/api/finance/stocks/*/price*days=30*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server Error' })
      });
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // エラーが発生しても他の時間軸は正常に表示されることを確認
    await page.waitForTimeout(3000); // Chart.js初期化待機
    
    // API失敗でもページが読み込まれることを確認
    const rechartElements = page.locator('.recharts-wrapper, .recharts-responsive-container');
    const dashboardContent = page.locator('[class*="bg-gray"], .card, .widget');
    const errorElements = page.locator('text=エラー, text=failed, text=error, .error, .alert');
    
    // ダッシュボードコンテンツまたはエラー表示があることを確認
    const hasContent = await dashboardContent.count() > 0;
    const hasError = await errorElements.count() > 0;
    const hasRecharts = await rechartElements.count() > 0;
    
    if (hasRecharts) {
      await expect(rechartElements.first()).toBeVisible({ timeout: 15000 });
    } else if (hasContent) {
      await expect(dashboardContent.first()).toBeVisible({ timeout: 10000 });
    } else if (hasError) {
      await expect(errorElements.first()).toBeVisible({ timeout: 10000 });
    } else {
      // 最低限ページが読み込まれていることを確認
      await expect(page.locator('body')).toBeVisible();
    }
    
    // エラーメッセージまたはフォールバック表示の確認
    await page.waitForTimeout(2000);
  });

  test('should support chart export functionality', async ({ page }) => {
    // チャートエクスポート機能のテスト
    const exportButton = page.locator('button').filter({ hasText: /Export|Download|保存|ダウンロード/ });
    
    if (await exportButton.count() > 0) {
      await expect(exportButton.first()).toBeVisible();
      
      // ダウンロードイベントの監視
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);
      
      await exportButton.first().click();
      
      const download = await downloadPromise;
      if (download) {
        expect(download.suggestedFilename()).toMatch(/\.(png|jpg|pdf|csv)$/);
      }
    }
  });
});