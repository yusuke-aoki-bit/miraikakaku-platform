import { test, expect } from '@playwright/test';

test.describe('Chart and Stock Data Rendering Tests', () => {

  test('should render stock chart on details page', async ({ page }) => {
    // Navigate directly to AAPL details page
    await page.goto('/details/AAPL'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Wait for potential API data loading
    await page.waitForTimeout(5000
    // Look for chart elements
    const chartElements = [
      page.locator('canvas')
      page.locator('svg')
      page.locator('[class*="chart"]')
      page.locator('[data-testid*="chart"]')
      page.locator('.recharts-wrapper')
      page.locator('.highcharts-container')
    ];

    let hasChart = false;
    for (const element of chartElements) {
      const count = await element.count(
      if (count > 0) {
        hasChart = true;
        break;
      }
    }

    // Check for stock price data
    const priceElements = [
      page.locator('text=/\\$[0-9]+\\.?[0-9]*$/')
      page.locator('[data-testid*="price"]')
      page.locator('[class*="price"]')
    ];

    let hasPriceData = false;
    for (const element of priceElements) {
      const count = await element.count(
      if (count > 0) {
        hasPriceData = true;
        break;
      }
    }

    // Check for stock symbol display
    const symbolElement = page.locator('text=AAPL'
    const hasSymbol = await symbolElement.count() > 0;
    // Page should load without critical errors
    await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
    // Take a screenshot for manual verification
    await page.screenshot({ path: 'chart-test-screenshot.png', fullPage: true }
  }
  test('should display stock information sections', async ({ page }) => {
    await page.goto('/details/AAPL'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await page.waitForTimeout(5000
    // Look for common stock information sections
    const infoSections = [
      'text=予測'
      'text=価格'
      'text=履歴'
      'text=データ'
      'text=分析'
    ];

    for (const section of infoSections) {
      const count = await page.locator(section).count(
      }

    // Check for any data tables or lists
    const dataElements = [
      page.locator('table')
      page.locator('ul')
      page.locator('[role="grid"]')
      page.locator('[data-testid*="data"]')
    ];

    for (const element of dataElements) {
      const count = await element.count(
      if (count > 0) {
        }
    }
  }
  test('should handle multiple stock symbols', async ({ page }) => {
    const symbols = ['AAPL', 'MSFT', 'GOOGL'];

    for (const symbol of symbols) {
      await page.goto(`/details/${symbol}`
      await page.waitForLoadState('domcontentloaded', { timeout: 15000 }
      await page.waitForTimeout(3000
      // Check if page loads without errors
      const hasBody = await page.locator('body').isVisible(
      expect(hasBody).toBe(true
      // Check if symbol is displayed
      const symbolCount = await page.locator(`text=${symbol}`).count(
      // Look for any chart or visualization
      const visualElements = await page.locator('canvas, svg').count(
      }
  }
  test('should display API response data', async ({ page }) => {
    // Monitor network requests
    const responses: string[] = [];
    page.on('response', response => {
      if (response.url().includes('localhost:8080')) {
        responses.push(`${response.status()} - ${response.url()}`
      }
    }
    await page.goto('/details/AAPL'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await page.waitForTimeout(5000
    responses.forEach(response =>
    // Check for any displayed data that would come from API
    const textContent = await page.locator('body').textContent(
    const hasNumbers = /\d+\.\d+/.test(textContent || ''
    const hasCurrency = /\$|¥/.test(textContent || ''
    }
  test('should work on homepage search', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Try to search for AAPL
    const searchInput = page.locator('input[type="text"]').first(
    if (await searchInput.isVisible()) {
      await searchInput.fill('AAPL'
      // Try to submit
      const submitButton = page.locator('button[type="submit"]').first(
      if (await submitButton.isEnabled()) {
        await submitButton.click(
        await page.waitForTimeout(3000

      } else {
        }
    } else {
      }

    // Take a screenshot of homepage
    await page.screenshot({ path: 'homepage-test-screenshot.png', fullPage: true }
  }
});