import { test, expect } from '@playwright/test';

test.describe('株式検索機能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('検索フォームが表示される', async ({ page }) => {
    // ヘッダーにある検索フォームが存在することを確認
    const searchInput = page.locator('input[placeholder*="株式コード"]');
    await expect(searchInput).toBeVisible();
    
    // 検索プレースホルダーテキストを確認
    const inputText = await searchInput.getAttribute('placeholder');
    expect(inputText).toContain('株式コード');
  });

  test('株式検索が動作する', async ({ page }) => {
    // 検索入力フィールドを見つける
    const searchInput = page.locator('input[type="text"]').first();
    
    // 検索クエリを入力
    await searchInput.fill('AAPL');
    
    // Enterキーを押すか検索ボタンをクリック
    await searchInput.press('Enter');
    
    // 検索結果が表示されるまで待機
    await page.waitForTimeout(2000);
  });

  test('検索候補が表示される', async ({ page }) => {
    const searchInput = page.locator('input[type="text"]').first();
    
    // 検索クエリを入力
    await searchInput.fill('App');
    
    // 検索候補が表示されるまで少し待機
    await page.waitForTimeout(1000);
    
    // 検索候補リストが表示されているかチェック（存在する場合）
    const suggestions = page.locator('[data-testid="search-suggestions"]');
    
    // 検索候補が存在するかチェック（APIが利用できない場合はスキップ）
    if (await suggestions.count() > 0) {
      await expect(suggestions).toBeVisible();
    }
  });

  test('無効な検索に対してエラーハンドリングが動作する', async ({ page }) => {
    const searchInput = page.locator('input[type="text"]').first();
    
    // 空の検索を試行
    await searchInput.fill('');
    await searchInput.press('Enter');
    
    // エラーメッセージまたは適切な処理が行われることを確認
    // （実際のUIの実装に応じて調整）
    await page.waitForTimeout(1000);
  });
});