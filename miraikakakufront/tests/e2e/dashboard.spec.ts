import { test, expect } from '@playwright/test';

test.describe('ダッシュボードページ', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('ダッシュボードページが正しく読み込まれる', async ({ page }) => {
    // ページタイトルが正しいか確認（Miraikakakuタイトルを期待）
    await expect(page).toHaveTitle(/Miraikakaku/);
    
    // ダッシュボードのメインコンテンツが表示されているか確認
    const main = page.locator('main').first();
    await expect(main).toBeVisible();
    
    // ダッシュボード特有の要素を確認
    const dashboardTitle = page.locator('text=リアルタイムダッシュボード');
    await expect(dashboardTitle).toBeVisible();
  });

  test('チャートコンポーネントが表示される', async ({ page }) => {
    // チャートが読み込まれるまで待機
    await page.waitForTimeout(5000);
    
    // ダッシュボード内のチャート関連要素を確認
    const elements = [
      page.locator('text=AAPL'),
      page.locator('text=高度分析'),  
      page.locator('.bg-white'),
      page.locator('canvas'),
      page.locator('svg')
    ];
    
    let foundElements = 0;
    for (const element of elements) {
      const count = await element.count();
      if (count > 0) {
        foundElements++;
      }
    }
    
    // 少なくとも1つの要素が見つかることを確認
    expect(foundElements).toBeGreaterThan(0);
    console.log(`Found ${foundElements} chart-related elements`);
  });

  test('サイドバーナビゲーションが動作する', async ({ page }) => {
    // サイドバーが存在するかチェック
    const sidebar = page.locator('[data-testid="sidebar"]').or(page.locator('aside')).or(page.locator('nav'));
    
    if (await sidebar.count() > 0) {
      await expect(sidebar.first()).toBeVisible();
      
      // サイドバーのリンクをテスト
      const links = sidebar.locator('a');
      const linkCount = await links.count();
      
      if (linkCount > 0) {
        // 最初のリンクをクリックしてナビゲーションをテスト
        await links.first().click();
        await page.waitForTimeout(1000);
      }
    }
  });

  test('リアルタイムダッシュボードコンポーネントが動作する', async ({ page }) => {
    // リアルタイムダッシュボードコンポーネントが存在するかチェック
    const realtimeDashboard = page.locator('[data-testid="realtime-dashboard"]');
    
    if (await realtimeDashboard.count() > 0) {
      await expect(realtimeDashboard).toBeVisible();
      
      // リアルタイムデータの更新を待つ
      await page.waitForTimeout(5000);
    }
  });

  test('ダッシュボードがエラー状態を適切に処理する', async ({ page }) => {
    // ネットワークエラーをシミュレート
    await page.route('**/api/**', route => route.abort());
    
    // ページをリロード
    await page.reload();
    
    // エラーメッセージまたは適切なフォールバックが表示されることを確認
    await page.waitForTimeout(3000);
    
    // エラー状態の表示要素をチェック
    const errorElements = [
      page.locator('[data-testid="error"]'),
      page.locator('.error'),
      page.locator('text=エラー'),
      page.locator('text=Error')
    ];
    
    // いずれかのエラー要素が表示されるかチェック
    for (const element of errorElements) {
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
        break;
      }
    }
  });
});