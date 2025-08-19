import { test, expect } from '@playwright/test';

test.describe('ホームページ', () => {
  test('ホームページが正しく読み込まれる', async ({ page }) => {
    await page.goto('/');
    
    // ページタイトルが正しいか確認
    await expect(page).toHaveTitle(/Miraikakaku/);
    
    // ヘッダーが表示されているか確認
    const header = page.locator('header');
    await expect(header).toBeVisible();
    
    // ナビゲーションリンクが存在するか確認
    await expect(page.locator('nav')).toBeVisible();
    
    // メインコンテンツが表示されているか確認
    const main = page.locator('main');
    await expect(main).toBeVisible();
  });

  test('ナビゲーションリンクが動作する', async ({ page }) => {
    await page.goto('/');
    
    // 基本的なナビゲーションが存在することを確認
    const navigation = page.locator('nav');
    await expect(navigation).toBeVisible();
    
    // ダッシュボードへの直接ナビゲーション
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/dashboard');
    
    // ウォッチリストへの直接ナビゲーション
    await page.goto('/watchlist');
    await expect(page).toHaveURL('/watchlist');
    
    // 履歴ページへの直接ナビゲーション
    await page.goto('/history');
    await expect(page).toHaveURL('/history');
    
    // ホームページに戻る
    await page.goto('/');
    await expect(page).toHaveURL('/');
  });

  test('レスポンシブデザインが動作する', async ({ page }) => {
    // モバイルサイズでテスト
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // ページが正しく表示されることを確認
    await expect(page.locator('main')).toBeVisible();
    
    // デスクトップサイズでテスト  
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('main')).toBeVisible();
  });
});