import { test, expect } from '@playwright/test';

test('should display enhanced adjustable chart with all features', async ({ page }) => {
    // Navigate to stock details page
    await page.goto('http://localhost:3001/details/AAPL'
    // Wait for the page to load
    await page.waitForSelector('[data-testid="stock-chart"]', { timeout: 60000 }
    // Take a screenshot of the enhanced chart
    await page.screenshot({
      path: 'enhanced-chart-screenshot.png'
      fullPage: true
    }
    // Verify chart control elements are present
    await expect(page.locator('text=1W')).toBeVisible(
    await expect(page.locator('text=1M')).toBeVisible(
    await expect(page.locator('text=3M')).toBeVisible(
    // Check for zoom controls
    await expect(page.locator('[title="ズームイン"]')).toBeVisible(
    await expect(page.locator('[title="ズームアウト"]')).toBeVisible(
    await expect(page.locator('[title="ズームリセット"]')).toBeVisible(
    // Check for export functionality
    await expect(page.locator('[title="CSVエクスポート"]')).toBeVisible(
    // Check for settings panel
    await expect(page.locator('[title="設定"]')).toBeVisible(
    // Open settings panel
    await page.click('[title="設定"]'
    // Verify chart type options
    await expect(page.locator('text=ライン')).toBeVisible(
    await expect(page.locator('text=エリア')).toBeVisible(
    await expect(page.locator('text=バー')).toBeVisible(
    await expect(page.locator('text=ローソク足')).toBeVisible(
    // Verify indicator toggles
    await expect(page.locator('text=AI予測')).toBeVisible(
    await expect(page.locator('text=過去の予測')).toBeVisible(
    await expect(page.locator('text=移動平均線')).toBeVisible(
    // Test chart type switching
    await page.click('text=エリア'
    await page.waitForTimeout(1000
    // Test period switching
    await page.click('text=1M'
    await page.waitForTimeout(1000
    // Check for stock comparison section
    await expect(page.locator('text=銘柄比較')).toBeVisible(
    await expect(page.locator('text=比較銘柄を追加')).toBeVisible(
    // Take final screenshot
    await page.screenshot({
      path: 'enhanced-chart-final.png'
      fullPage: true
    }
  }
test('should test stock comparison functionality', async ({ page }) => {
  await page.goto('http://localhost:3001/details/AAPL'
  // Wait for page load
  await page.waitForSelector('[data-testid="stock-chart"]', { timeout: 60000 }
  // Scroll to comparison section
  await page.locator('text=銘柄比較').scrollIntoViewIfNeeded(
  // Click add comparison stock
  await page.click('text=比較銘柄を追加'
  // Type in search box
  await page.fill('input[placeholder*="銘柄コード"]', 'MSFT'
  // Wait for search results
  await page.waitForTimeout(1000
  // Click on search result if available
  const searchResult = page.locator('text=MSFT').first(
  if (await searchResult.isVisible()) {
    await searchResult.click(
  }

  // Take screenshot of comparison
  await page.screenshot({
    path: 'stock-comparison-test.png'
    fullPage: true
  }
});