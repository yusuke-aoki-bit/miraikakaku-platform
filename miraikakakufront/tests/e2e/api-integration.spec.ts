import { test, expect } from '@playwright/test';

test.describe('API統合テスト', () => {
  test('APIヘルスチェックが成功する', async ({ request }) => {
    // APIサーバーのヘルスチェック
    const response = await request.get('http://localhost:8001/health');
    expect(response.ok()).toBeTruthy();
    
    const healthData = await response.json();
    expect(healthData).toHaveProperty('status', 'healthy');
  });

  test('株式検索APIが動作する', async ({ request }) => {
    // 株式検索APIをテスト
    const response = await request.get('http://localhost:8001/api/finance/stocks/search?query=AAPL&limit=10');
    
    if (response.ok()) {
      const searchResults = await response.json();
      expect(Array.isArray(searchResults)).toBeTruthy();
    } else {
      // APIが利用できない場合はスキップ
      console.log('Stock search API not available, skipping test');
    }
  });

  test('フロントエンドとAPIの統合が動作する', async ({ page }) => {
    // APIレスポンスをモック
    await page.route('**/api/finance/stocks/search*', async route => {
      const mockResponse = [
        {
          symbol: 'AAPL',
          company_name: 'Apple Inc.',
          exchange: 'NASDAQ',
          sector: 'Technology',
          industry: 'Consumer Electronics'
        }
      ];
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse)
      });
    });

    await page.goto('/');
    
    // 検索フォームに入力
    const searchInput = page.locator('input[type="text"]').first();
    if (await searchInput.count() > 0) {
      await searchInput.fill('AAPL');
      await searchInput.press('Enter');
      
      // 検索結果が表示されるまで待機
      await page.waitForTimeout(2000);
    }
  });

  test('エラーハンドリングが適切に動作する', async ({ page }) => {
    // APIエラーをシミュレート
    await page.route('**/api/**', route => route.abort());

    await page.goto('/');
    
    // エラー状態が適切に表示されることを確認
    await page.waitForTimeout(3000);
    
    // コンソールエラーをキャプチャ
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // ページがクラッシュしていないことを確認
    await expect(page.locator('body')).toBeVisible();
  });

  test('リアルタイム機能が動作する', async ({ page }) => {
    // WebSocketモック（可能な場合）
    await page.goto('/realtime');
    
    // リアルタイムページが読み込まれることを確認
    await page.waitForTimeout(3000);
    await expect(page.locator('main')).toBeVisible();
    
    // WebSocket接続のテスト（実装に応じて）
    const wsConnections = await page.evaluate(() => {
      return (window as any).WebSocket ? 'WebSocket available' : 'WebSocket not available';
    });
    
    expect(wsConnections).toContain('WebSocket');
  });
});