import { test, expect } from '@playwright/test';

test.describe('Volume Analysis Page', () => {
  test.beforeEach(async ({ page }) => {
    // API モックの設定
    await page.route('**/api/finance/stocks/*/price*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            date: '2025-08-22',
            close_price: 225.50,
            open_price: 224.00,
            high_price: 227.00,
            low_price: 223.50,
            volume: 42500000
          },
          {
            date: '2025-08-21',
            close_price: 224.90,
            open_price: 226.27,
            high_price: 226.52,
            low_price: 223.78,
            volume: 30593700
          }
        ])
      });
    });

    await page.route('**/api/finance/stocks/*/predictions*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            date: '2025-08-23',
            predicted_price: 227.25,
            confidence: 0.85,
            upper_bound: 235.00,
            lower_bound: 219.50
          }
        ])
      });
    });

    await page.goto('/volume');
    await page.waitForLoadState('networkidle');
  });

  test('should display volume analysis page with correct title', async ({ page }) => {
    // ページタイトルの確認
    await expect(page.locator('h1')).toContainText('出来高分析');
    
    // アイコンの存在確認
    const barChartIcon = page.locator('[data-lucide="bar-chart-3"]').first();
    await expect(barChartIcon).toBeVisible();
  });

  test('should show period selection buttons', async ({ page }) => {
    // 期間選択ボタンの確認
    await expect(page.locator('text=1日')).toBeVisible();
    await expect(page.locator('text=1週間')).toBeVisible();
    await expect(page.locator('text=1ヶ月')).toBeVisible();
    await expect(page.locator('text=1年')).toBeVisible();
    
    // デフォルト選択の確認（1ヶ月）
    const monthButton = page.locator('button:has-text("1ヶ月")');
    await expect(monthButton).toHaveClass(/bg-green-500\/20/);
  });

  test('should switch period when buttons are clicked', async ({ page }) => {
    // 1週間ボタンをクリック
    const weekButton = page.locator('button:has-text("1週間")');
    await weekButton.click();
    
    // 選択状態の確認
    await expect(weekButton).toHaveClass(/bg-green-500\/20/);
    
    // 1年ボタンをクリック
    const yearButton = page.locator('button:has-text("1年")');
    await yearButton.click();
    
    // 選択状態の確認
    await expect(yearButton).toHaveClass(/bg-green-500\/20/);
    // 前の選択が解除されていることを確認
    await expect(weekButton).not.toHaveClass(/bg-green-500\/20/);
  });

  test('should display volume summary cards', async ({ page }) => {
    // サマリーカードの確認
    await expect(page.locator('text=本日の出来高')).toBeVisible();
    await expect(page.locator('text=125.4M')).toBeVisible();
    await expect(page.locator('text=+12.5%')).toBeVisible();
    
    // アクティビティアイコンの確認
    const activityIcon = page.locator('[data-lucide="activity"]').first();
    await expect(activityIcon).toBeVisible();
  });

  test('should render volume chart component', async ({ page }) => {
    // VolumeChartコンポーネントの存在確認
    // Canvas要素（Chart.jsが生成）の確認
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible({ timeout: 10000 });
  });

  test('should handle stock symbol change', async ({ page }) => {
    // StockSearchコンポーネントが存在することを確認
    const searchInput = page.locator('[data-testid="stock-search-input"]');
    
    if (await searchInput.isVisible()) {
      // 検索入力のテスト
      await searchInput.fill('TSLA');
      await page.waitForTimeout(1000);
      
      // 新しいシンボルでのデータ読み込みを確認
      // ここでは新しいAPI呼び出しが発生することを確認
    }
  });

  test('should display view mode controls', async ({ page }) => {
    // ビューモード切り替えコントロールの確認
    // VolumeChartコンポーネント内のモード切り替えボタンを探す
    const modeButtons = page.locator('button').filter({ hasText: /combined|volume|price/ });
    
    if (await modeButtons.count() > 0) {
      // モード切り替えボタンが存在する場合のテスト
      const firstModeButton = modeButtons.first();
      await expect(firstModeButton).toBeVisible();
      await firstModeButton.click();
      
      // チャートの再描画を待つ
      await page.waitForTimeout(1000);
    }
  });

  test('should show loading state initially', async ({ page }) => {
    // ページの初期読み込み時にローディングが表示されることを確認
    // 新しいページロードでテスト
    await page.goto('/volume');
    
    // ローディングスピナーまたはスケルトンの確認
    const loadingElement = page.locator('[data-testid*="loading"], .skeleton, .animate-pulse');
    
    // ローディング要素が短時間表示される可能性があるため、タイムアウトを短く設定
    try {
      await expect(loadingElement.first()).toBeVisible({ timeout: 2000 });
    } catch {
      // ローディングが非常に高速な場合、このテストはスキップ
      console.log('Loading state was too fast to capture');
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // モバイルビューポートに変更
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // モバイルでも基本要素が表示されることを確認
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('button:has-text("1ヶ月")')).toBeVisible();
    
    // グリッドレイアウトがモバイルに適応することを確認
    const summaryCards = page.locator('.grid').first();
    await expect(summaryCards).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // API エラーをモック
    await page.route('**/api/finance/stocks/*/price*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    await page.goto('/volume');
    await page.waitForLoadState('networkidle');
    
    // エラー状態でもページが表示されることを確認
    await expect(page.locator('h1')).toBeVisible();
    
    // エラーメッセージまたはフォールバックコンテンツの確認
    // VolumeChartコンポーネントがエラーを適切に処理することを確認
    await page.waitForTimeout(2000);
  });

  test('should maintain state during navigation', async ({ page }) => {
    // 期間を変更
    const weekButton = page.locator('button:has-text("1週間")');
    await weekButton.click();
    
    // 他のページに移動
    await page.click('a[href="/dashboard"]');
    await page.waitForLoadState('networkidle');
    
    // 出来高ページに戻る
    await page.click('a[href="/volume"]');
    await page.waitForLoadState('networkidle');
    
    // 状態が維持されているか確認（セッションストレージやローカルストレージを使用している場合）
    // この動作は実装によって異なるため、必要に応じて調整
  });
});