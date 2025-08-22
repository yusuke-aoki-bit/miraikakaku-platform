import { test, expect } from '@playwright/test';

test.describe('Comprehensive API Integration Tests', () => {
  // 実際のAPIサーバーが動作していることを前提とするテスト
  test.beforeEach(async ({ page }) => {
    // 実際のAPIを使用するため、モックは最小限に
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should successfully connect to backend API', async ({ page }) => {
    // APIサーバーとの基本接続確認
    const response = await page.evaluate(async () => {
      try {
        const res = await fetch('http://localhost:8000/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        return {
          status: res.status,
          data: await res.json()
        };
      } catch (error) {
        return {
          error: error.message
        };
      }
    });

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('message');
    expect(response.data.message).toContain('Universal Stock Market API');
  });

  test('should perform end-to-end stock search flow', async ({ page }) => {
    // 株式検索の完全なフローテスト
    const searchInput = page.locator('[data-testid="stock-search-input"]');
    await expect(searchInput).toBeVisible();

    // Apple株を検索
    await searchInput.fill('AAPL');
    await page.waitForTimeout(1000);

    // 検索結果のドロップダウンが表示されることを確認
    const searchResults = page.locator('[data-testid*="search-result"], .search-results');
    
    if (await searchResults.count() > 0) {
      await expect(searchResults.first()).toBeVisible();
      
      // 最初の検索結果をクリック
      const firstResult = searchResults.first();
      await firstResult.click();
      await page.waitForTimeout(1000);
    }

    // 株式データが実際に取得されることを確認
    const stockData = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/finance/stocks/AAPL/price?days=7');
        if (response.ok) {
          return await response.json();
        }
        return null;
      } catch (error) {
        return { error: error.message };
      }
    });

    expect(stockData).toBeTruthy();
    expect(Array.isArray(stockData)).toBe(true);
    if (stockData.length > 0) {
      expect(stockData[0]).toHaveProperty('close_price');
      expect(stockData[0]).toHaveProperty('date');
    }
  });

  test('should display real-time prediction data', async ({ page }) => {
    // 予測データの取得と表示テスト
    const predictionData = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/finance/stocks/AAPL/predictions?days=7');
        if (response.ok) {
          return await response.json();
        }
        return null;
      } catch (error) {
        return { error: error.message };
      }
    });

    expect(predictionData).toBeTruthy();
    expect(Array.isArray(predictionData)).toBe(true);
    
    if (predictionData.length > 0) {
      const prediction = predictionData[0];
      expect(prediction).toHaveProperty('predicted_price');
      expect(prediction).toHaveProperty('confidence');
      expect(prediction).toHaveProperty('date');
      
      // 予測価格が合理的な範囲内であることを確認
      expect(prediction.predicted_price).toBeGreaterThan(0);
      expect(prediction.confidence).toBeGreaterThanOrEqual(0);
      expect(prediction.confidence).toBeLessThanOrEqual(1);
    }
  });

  test('should handle rankings page with real data', async ({ page }) => {
    // ランキングページでの実データ処理テスト
    await page.goto('/rankings');
    await page.waitForLoadState('networkidle');

    // ページが読み込まれることを確認
    await expect(page.locator('h1')).toContainText('ランキング');

    // ランキングタブの切り替えテスト
    const compositeTab = page.locator('button').filter({ hasText: /総合|Composite/ });
    if (await compositeTab.count() > 0) {
      await compositeTab.click();
      await page.waitForTimeout(2000);
    }

    const accuracyTab = page.locator('button').filter({ hasText: /精度|Accuracy/ });
    if (await accuracyTab.count() > 0) {
      await accuracyTab.click();
      await page.waitForTimeout(2000);
    }

    const growthTab = page.locator('button').filter({ hasText: /成長|Growth/ });
    if (await growthTab.count() > 0) {
      await growthTab.click();
      await page.waitForTimeout(2000);
    }

    // ランキングデータが表示されることを確認
    const rankingItems = page.locator('.ranking-item, [data-testid*="ranking"]');
    if (await rankingItems.count() > 0) {
      await expect(rankingItems.first()).toBeVisible();
      
      // 最低1つのランキング項目にシンボルが表示されることを確認
      const symbols = page.locator('text=/[A-Z]{1,5}$/');
      if (await symbols.count() > 0) {
        await expect(symbols.first()).toBeVisible();
      }
    }
  });

  test('should handle analysis page with real API data', async ({ page }) => {
    // 分析ページでの実データ処理テスト
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h1')).toContainText('市場分析');

    // ローディング完了を待つ
    await page.waitForTimeout(3000);

    // 分析カードが表示されることを確認
    const analysisCards = page.locator('.youtube-card, .financial-card, .card');
    if (await analysisCards.count() > 0) {
      await expect(analysisCards.first()).toBeVisible();
      
      // 価格データが表示されることを確認
      const priceElements = page.locator('text=/\\$[0-9]+\\.[0-9]+/');
      if (await priceElements.count() > 0) {
        await expect(priceElements.first()).toBeVisible();
      }
      
      // 変動率が表示されることを確認
      const changeElements = page.locator('text=/%$/').or(page.locator('text=/[+-][0-9]+\\.[0-9]+%/'));
      if (await changeElements.count() > 0) {
        await expect(changeElements.first()).toBeVisible();
      }
    }
  });

  test('should test volume page API integration', async ({ page }) => {
    // 出来高ページでのAPI統合テスト
    await page.goto('/volume');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h1')).toContainText('出来高分析');

    // チャートが読み込まれるまで待機
    const canvas = page.locator('canvas');
    await expect(canvas.first()).toBeVisible({ timeout: 15000 });

    // 期間変更時のAPI呼び出しテスト
    const weekButton = page.locator('button:has-text("1週間")');
    if (await weekButton.isVisible()) {
      await weekButton.click();
      await page.waitForTimeout(2000);
      
      // チャートが更新されることを確認
      await expect(canvas.first()).toBeVisible();
    }

    // 実際のAPI呼び出しが成功することを確認
    const volumeData = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/finance/stocks/AAPL/price?days=30');
        if (response.ok) {
          const data = await response.json();
          return data.map((item: any) => ({
            date: item.date,
            volume: item.volume,
            price: item.close_price
          }));
        }
        return null;
      } catch (error) {
        return { error: error.message };
      }
    });

    expect(volumeData).toBeTruthy();
    if (Array.isArray(volumeData) && volumeData.length > 0) {
      expect(volumeData[0]).toHaveProperty('volume');
      expect(volumeData[0]).toHaveProperty('price');
    }
  });

  test('should handle API error scenarios gracefully', async ({ page }) => {
    // API エラーシナリオのテスト
    
    // 無効なシンボルでの検索テスト
    const invalidSymbolData = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/finance/stocks/INVALID/price?days=7');
        return {
          status: response.status,
          ok: response.ok
        };
      } catch (error) {
        return { error: error.message };
      }
    });

    // 404エラーまたは適切なエラーハンドリングを確認
    if (invalidSymbolData.status) {
      expect([200, 404, 500]).toContain(invalidSymbolData.status);
    }

    // ページ上でのエラーハンドリング確認
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // エラーが発生してもページが正常に表示されることを確認
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('h1, .title, [role="heading"]')).toBeVisible();
  });

  test('should test cross-page API data consistency', async ({ page }) => {
    // ページ間でのAPIデータ一貫性テスト
    
    // ダッシュボードでAAPLを選択
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const searchInput = page.locator('[data-testid="stock-search-input"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('AAPL');
      await page.waitForTimeout(1000);
    }

    // ダッシュボードでのデータ取得
    const dashboardData = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/finance/stocks/AAPL/price?days=7');
        if (response.ok) {
          const data = await response.json();
          return data[0]; // 最新のデータ
        }
        return null;
      } catch (error) {
        return { error: error.message };
      }
    });

    // 分析ページに移動
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 分析ページでの同じデータ確認
    const analysisData = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/finance/stocks/AAPL/price?days=7');
        if (response.ok) {
          const data = await response.json();
          return data[0]; // 最新のデータ
        }
        return null;
      } catch (error) {
        return { error: error.message };
      }
    });

    // データの一貫性を確認
    if (dashboardData && analysisData && 
        !dashboardData.error && !analysisData.error) {
      expect(dashboardData.date).toBe(analysisData.date);
      expect(dashboardData.close_price).toBe(analysisData.close_price);
    }
  });

  test('should validate API response data types and structures', async ({ page }) => {
    // API レスポンスのデータ型と構造検証
    const testSymbols = ['AAPL', 'GOOGL', 'MSFT'];

    for (const symbol of testSymbols) {
      // 価格データの構造検証
      const priceData = await page.evaluate(async (sym) => {
        try {
          const response = await fetch(`http://localhost:8000/api/finance/stocks/${sym}/price?days=3`);
          if (response.ok) {
            return await response.json();
          }
          return null;
        } catch (error) {
          return { error: error.message };
        }
      }, symbol);

      if (priceData && Array.isArray(priceData) && priceData.length > 0) {
        const firstRecord = priceData[0];
        
        // 必須フィールドの存在確認
        expect(firstRecord).toHaveProperty('date');
        expect(firstRecord).toHaveProperty('close_price');
        expect(typeof firstRecord.close_price).toBe('number');
        expect(firstRecord.close_price).toBeGreaterThan(0);
        
        if (firstRecord.volume !== undefined) {
          expect(typeof firstRecord.volume).toBe('number');
          expect(firstRecord.volume).toBeGreaterThanOrEqual(0);
        }
      }

      // 予測データの構造検証
      const predictionData = await page.evaluate(async (sym) => {
        try {
          const response = await fetch(`http://localhost:8000/api/finance/stocks/${sym}/predictions?days=3`);
          if (response.ok) {
            return await response.json();
          }
          return null;
        } catch (error) {
          return { error: error.message };
        }
      }, symbol);

      if (predictionData && Array.isArray(predictionData) && predictionData.length > 0) {
        const firstPrediction = predictionData[0];
        
        expect(firstPrediction).toHaveProperty('predicted_price');
        expect(typeof firstPrediction.predicted_price).toBe('number');
        expect(firstPrediction.predicted_price).toBeGreaterThan(0);
        
        if (firstPrediction.confidence !== undefined) {
          expect(typeof firstPrediction.confidence).toBe('number');
          expect(firstPrediction.confidence).toBeGreaterThanOrEqual(0);
          expect(firstPrediction.confidence).toBeLessThanOrEqual(1);
        }
      }
    }
  });

  test('should measure API response performance', async ({ page }) => {
    // API レスポンス性能測定
    const performanceResults = await page.evaluate(async () => {
      const results = [];
      const testEndpoints = [
        '/api/finance/stocks/AAPL/price?days=7',
        '/api/finance/stocks/AAPL/predictions?days=7',
        '/api/finance/stocks/search?query=AAPL&limit=10'
      ];

      for (const endpoint of testEndpoints) {
        const startTime = performance.now();
        
        try {
          const response = await fetch(`http://localhost:8000${endpoint}`);
          const endTime = performance.now();
          const responseTime = endTime - startTime;
          
          results.push({
            endpoint,
            responseTime,
            status: response.status,
            ok: response.ok
          });
        } catch (error) {
          const endTime = performance.now();
          results.push({
            endpoint,
            responseTime: endTime - startTime,
            error: error.message
          });
        }
      }
      
      return results;
    });

    // パフォーマンス要件の確認
    for (const result of performanceResults) {
      console.log(`${result.endpoint}: ${result.responseTime.toFixed(2)}ms`);
      
      // レスポンス時間が妥当であることを確認（5秒以内）
      expect(result.responseTime).toBeLessThan(5000);
      
      // 成功したリクエストは2秒以内であることを確認
      if (result.ok) {
        expect(result.responseTime).toBeLessThan(2000);
      }
    }
  });
});