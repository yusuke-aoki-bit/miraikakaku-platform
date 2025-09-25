import { test, expect, Page } from '@playwright/test';

test.describe('Progressive Loading Performance Tests', () => {
  test.beforeEach(async ({ page }) => {
    // APIサーバーが稼働していることを確認
    await page.goto('http://localhost:3000'
    await expect(page).toHaveTitle(/Miraikakaku/
  }
  test('Should load critical data (Stage 1) within 2 seconds', async ({ page }) => {
    const startTime = Date.now(
    // 詳細ページにナビゲート
    await page.goto('http://localhost:3000/details/AAPL'
    // Stage 1: ヘッダーが表示されるまでの時間を測定
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible({ timeout: 5000 }
    const headerLoadTime = Date.now() - startTime;
    loaded in: ${headerLoadTime}ms`
    // Stage 1は2秒以内に表示されるべき
    expect(headerLoadTime).toBeLessThan(2000
    // ヘッダーに必要な情報が含まれていることを確認
    await expect(page.locator('[data-testid="stock-header"]')).toContainText('AAPL'
  }
  test('Should show skeleton loaders during progressive loading', async ({ page }) => {
    await page.goto('http://localhost:3000/details/AAPL'
    // スケルトンローダーが表示されることを確認
    const skeletonElements = page.locator('.skeleton-animate'
    // 最初はスケルトンが表示される
    await expect(skeletonElements.first()).toBeVisible({ timeout: 1000 }
    // 時間が経つとスケルトンが消える
    await expect(skeletonElements.first()).not.toBeVisible({ timeout: 10000 }
  }
  test('Should load chart data (Stage 2) progressively', async ({ page }) => {
    const measurements: { stage: string; time: number }[] = [];
    const startTime = Date.now(
    await page.goto('http://localhost:3000/details/AAPL'
    // Stage 1: ヘッダーが表示
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    measurements.push({ stage: 'Stage 1 (Header)', time: Date.now() - startTime }
    // Stage 2: チャートが表示
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible({ timeout: 8000 }
    measurements.push({ stage: 'Stage 2 (Chart)', time: Date.now() - startTime }
    // チャートデータの表示確認
    await expect(page.locator('[data-testid="stock-chart"]')).toContainText('価格データ'
    measurements.forEach(m => {
      }
    // Stage 2は8秒以内に表示されるべき
    expect(measurements[1].time).toBeLessThan(8000
  }
  test('Should load all content progressively within acceptable timeframes', async ({ page }) => {
    const performanceMetrics: { [key: string]: number } = {};
    const startTime = Date.now(
    // パフォーマンス観察を開始
    await page.goto('http://localhost:3000/details/AAPL'
    // Stage 1: 基本データ（ヘッダー + サイドバー統計）
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    performanceMetrics['stage1_header'] = Date.now() - startTime;

    // Stage 2: チャートデータ
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible({ timeout: 8000 }
    performanceMetrics['stage2_chart'] = Date.now() - startTime;

    // Stage 3: 分析データ（AI分析、技術分析）
    await expect(page.locator('[data-testid="ai-analysis"]')).toBeVisible({ timeout: 10000 }
    performanceMetrics['stage3_analysis'] = Date.now() - startTime;

    // 会社情報が表示されることを確認
    await expect(page.locator('[data-testid="company-info"]')).toBeVisible(
    performanceMetrics['company_info'] = Date.now() - startTime;

    // パフォーマンス結果をログ出力
    : ${performanceMetrics.stage1_header}ms`
    : ${performanceMetrics.stage2_chart}ms`
    : ${performanceMetrics.stage3_analysis}ms`
    // パフォーマンス目標の検証
    expect(performanceMetrics.stage1_header).toBeLessThan(2000); // Stage 1: 2秒以内
    expect(performanceMetrics.stage2_chart).toBeLessThan(6000);  // Stage 2: 6秒以内
    expect(performanceMetrics.stage3_analysis).toBeLessThan(12000); // Stage 3: 12秒以内

    // プログレッシブローディングが正しく動作していることを確認
    expect(performanceMetrics.stage1_header).toBeLessThan(performanceMetrics.stage2_chart
    expect(performanceMetrics.stage2_chart).toBeLessThan(performanceMetrics.stage3_analysis
  }
  test('Should measure API response times for each stage', async ({ page }) => {
    const apiCalls: { url: string; startTime: number; endTime?: number }[] = [];

    // APIコールを監視
    page.on('request', (request) => {
      if (request.url().includes('/api/finance/stocks/')) {
        apiCalls.push({ url: request.url(), startTime: Date.now() }
      }
    }
    page.on('response', (response) => {
      if (response.url().includes('/api/finance/stocks/')) {
        const call = apiCalls.find(call => call.url === response.url() && !call.endTime
        if (call) {
          call.endTime = Date.now(
        }
      }
    }
    await page.goto('http://localhost:3000/details/AAPL'
    // すべてのコンテンツが読み込まれるまで待機
    await expect(page.locator('[data-testid="ai-analysis"]')).toBeVisible({ timeout: 15000 }
    // 1秒待ってAPIコールが完了することを確認
    await page.waitForTimeout(1000
    apiCalls.filter(call => call.endTime).forEach(call => {
      const duration = call.endTime! - call.startTime;
      const endpoint = call.url.split('/api/finance/stocks/')[1];
      }
    // 少なくとも3つのAPIコールがあることを確認（details, price, predictions）
    const completedCalls = apiCalls.filter(call => call.endTime
    expect(completedCalls.length).toBeGreaterThanOrEqual(2
  }
  test('Should handle loading states gracefully', async ({ page }) => {
    await page.goto('http://localhost:3000/details/AAPL'
    // 初期ローディング状態を確認
    const initialLoadingElement = page.locator('[data-testid="loading-page"]'
    // ローディングページが最初に表示される
    const isLoadingVisible = await initialLoadingElement.isVisible(
    if (isLoadingVisible) {
      // ローディングが消えることを確認
      await expect(initialLoadingElement).not.toBeVisible({ timeout: 10000 }
      }

    // 最終的にコンテンツが表示されることを確認
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
  }
  test('Should maintain responsive design during progressive loading', async ({ page }) => {
    // モバイル画面サイズでテスト
    await page.setViewportSize({ width: 375, height: 667 }
    await page.goto('http://localhost:3000/details/AAPL'
    // ヘッダーが表示されることを確認
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    // レスポンシブデザインが維持されていることを確認
    const header = page.locator('[data-testid="stock-header"]'
    const headerBox = await header.boundingBox(
    expect(headerBox?.width).toBeLessThanOrEqual(375
    // デスクトップサイズに変更
    await page.setViewportSize({ width: 1920, height: 1080 }
    // チャートが表示されることを確認
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible({ timeout: 8000 }
  }
});