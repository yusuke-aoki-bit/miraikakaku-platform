import { test, expect } from '@playwright/test';

test.describe('銘柄詳細ページ E2Eテスト', () => {
  const testSymbol = '6758.T'; // Sony Group Corporation (有効な銘柄)

  test.beforeEach(async ({ page }) => {
    // テストのタイムアウトを60秒に延長
    page.setDefaultTimeout(60000);
  });

  test('銘柄詳細ページが正しく表示される', async ({ page }) => {
    // 銘柄詳細ページに遷移
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // タイトルが表示されている
    await expect(page.locator('h1')).toBeVisible({ timeout: 10000 });

    // 銘柄コードが表示されている
    await expect(page.getByText(testSymbol)).toBeVisible();
  });

  test('価格情報セクションが表示される', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // 価格情報セクション
    await expect(page.getByText('価格情報')).toBeVisible();
    await expect(page.getByText('最新価格')).toBeVisible();
    await expect(page.getByText('変動率')).toBeVisible();
    await expect(page.getByText('出来高')).toBeVisible();
  });

  test('グラフが表示される', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // グラフのタイトル
    await expect(page.getByText('株価チャート（過去1年 + 予測）')).toBeVisible();

    // 凡例が表示されている
    await expect(page.getByText('実際の価格')).toBeVisible();
    await expect(page.getByText('過去予測')).toBeVisible();
    await expect(page.getByText('未来予測')).toBeVisible();

    // Rechartsのチャートが描画されている
    const chart = page.locator('.recharts-wrapper');
    await expect(chart).toBeVisible();
  });

  test('予測テーブルが表示される', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // テーブルヘッダー
    await expect(page.getByText('LSTM AI予測')).toBeVisible();

    // テーブルカラム
    await expect(page.getByRole('columnheader', { name: '予測日' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '予測価格' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '予測時点価格' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '実際の価格' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '変動予測' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '精度' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '予測期間' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '信頼度' })).toBeVisible();
  });

  test('予測データが表示される', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // テーブルに少なくとも1行のデータがある
    const rows = page.locator('tbody tr');
    await expect(rows.first()).toBeVisible();

    // 予測価格の値が表示されている
    const predictionCell = rows.first().locator('td').nth(1);
    await expect(predictionCell).toBeVisible();
    const predictionText = await predictionCell.textContent();
    expect(predictionText).toMatch(/[\d,]+\.\d{2}/); // 数値フォーマットを確認
  });

  test('ウォッチリストボタンが表示される', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // ウォッチリストボタン
    const watchlistButton = page.getByRole('button', { name: /ウォッチリスト/ });
    await expect(watchlistButton).toBeVisible();
  });

  test('ホームに戻るボタンが動作する', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // ホームに戻るボタンをクリック
    await page.getByRole('button', { name: /ホームに戻る/ }).click();

    // ホームページに遷移していることを確認
    await expect(page).toHaveURL('/');
  });

  test('ページネーションが動作する', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // ページネーション情報が表示されている
    const paginationInfo = page.getByText(/ページ \d+ \/ \d+/);
    if (await paginationInfo.isVisible()) {
      // 次のページボタン（exactマッチで>のみ取得）
      const nextButton = page.getByRole('button', { name: '>', exact: true });
      if (await nextButton.isEnabled()) {
        await nextButton.click();
        await page.waitForLoadState('domcontentloaded');

        // ページ番号が変わっていることを確認
        await expect(page.getByText(/ページ 2 \//)).toBeVisible();
      }
    }
  });

  test('予測精度評価セクションが表示される（データがある場合）', async ({ page }) => {
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // 予測精度評価セクションが存在する場合
    const accuracySection = page.getByText('予測精度評価');
    if (await accuracySection.isVisible()) {
      await expect(page.getByText('信頼性')).toBeVisible();
      await expect(page.getByText('平均誤差率 (MAPE)')).toBeVisible();
      await expect(page.getByText('方向精度')).toBeVisible();
    }
  });

  test('レスポンシブデザインが動作する', async ({ page }) => {
    // モバイルサイズ
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`/stock/${testSymbol}`);
    await page.waitForLoadState('domcontentloaded');

    // グラフが表示される
    await expect(page.locator('.recharts-wrapper')).toBeVisible();

    // テーブルがスクロール可能
    const tableContainer = page.locator('.overflow-x-auto');
    await expect(tableContainer).toBeVisible();
  });
});
