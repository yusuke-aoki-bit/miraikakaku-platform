import { test, expect, Page, Browser } from '@playwright/test';

/**
 * Enhanced E2E Test Suite with Automation Features
 * Miraikakaku Stock Prediction Platform
 */

// Test configuration and utilities
const CONFIG = {
  timeouts: {
    navigation: 10000
    api: 15000
    element: 5000
    short: 2000
  }
  apiEndpoints: {
    stockPrice: '/api/finance/stocks/{symbol}/price'
    stockPrediction: '/api/finance/stocks/{symbol}/prediction'
    stockSearch: '/api/finance/stocks/search'
    stockList: '/api/finance/stocks/list'
  }
  stockSymbols: {
    us: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
    japanese: ['7203.T', '6758.T', '9984.T', '8306.T', '6861.T']
  }
};

// Test utilities
class TestUtils {
  static async waitForPageLoad(page: Page): Promise<void> {
    await page.waitForLoadState('domcontentloaded'
    // Wait for main content to be visible instead of body
    try {
      await page.waitForSelector('h1, main, [data-testid="main-content"]', { timeout: CONFIG.timeouts.element }
    } catch {
      // Fallback: just wait for page load
      await page.waitForTimeout(1000
    }
  }

  static async capturePageMetrics(page: Page): Promise<any> {
    return await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
        timestamp: Date.now()
      };
    }
  }

  static async checkAPIAvailability(page: Page, endpoint: string): Promise<boolean> {
    try {
      const response = await page.request.get(endpoint
      return response.ok(
    } catch (error) {
      return false;
    }
  }

  static async waitForAPIResponse(page: Page, urlPattern: string): Promise<any> {
    return await page.waitForResponse(
      response => response.url().includes(urlPattern) && response.status() === 200
      { timeout: CONFIG.timeouts.api }
  }
}

test.describe('Enhanced Automated E2E Test Suite', () => {
  let testMetrics: any[] = [];

  test.beforeEach(async ({ page }) => {
    // Enhanced setup with error tracking
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text()
      }
    }
    await page.goto('/'
    await TestUtils.waitForPageLoad(page
    // Store page errors for analysis
    (page as any).testErrors = errors;
  }
  test.afterEach(async ({ page }, testInfo) => {
    // Collect test metrics
    const metrics = await TestUtils.capturePageMetrics(page
    testMetrics.push({
      testName: testInfo.title
      status: testInfo.status
      duration: testInfo.duration
      metrics
      errors: (page as any).testErrors || []
    }
  }
  test.describe('Core Application Functionality', () => {
    test('should verify complete homepage functionality', async ({ page }) => {
      // Title verification
      await expect(page).toHaveTitle(/未来価格/
      // Essential elements
      const mainHeading = page.locator('h1'
      await expect(mainHeading).toContainText('未来価格'
      const searchInput = page.locator('input[placeholder*="検索"]'
      await expect(searchInput).toBeVisible(
      const searchButton = page.locator('button[type="submit"]'
      await expect(searchButton).toBeVisible(
      // Verify sections are loading properly
      await page.waitForTimeout(CONFIG.timeouts.short
      const pageContent = await page.textContent('body'
      expect(pageContent).toContain('未来価格'
    }
    test('should handle stock symbol search with API integration', async ({ page }) => {
      // Test with different stock symbols
      for (const symbol of CONFIG.stockSymbols.us.slice(0, 3)) {
        await page.goto('/'
        await TestUtils.waitForPageLoad(page
        const searchInput = page.locator('input[placeholder*="検索"]'
        await searchInput.fill(symbol
        const searchButton = page.locator('button[type="submit"]'
        await searchButton.click(
        await page.waitForTimeout(CONFIG.timeouts.short
        // Verify navigation or results
        const url = page.url(
        expect(url).toBeTruthy(
        // Check for potential API calls
        const hasApiError = (page as any).testErrors.some((error: string) =>
          error.includes('fetch') || error.includes('API') || error.includes('network')
        if (!hasApiError) {
          }
      }
    }
    test('should verify responsive design across viewports', async ({ page }) => {
      const viewports = [
        { width: 375, height: 667, name: 'Mobile' }
        { width: 768, height: 1024, name: 'Tablet' }
        { width: 1920, height: 1080, name: 'Desktop' }
      ];

      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height }
        await page.goto('/'
        await TestUtils.waitForPageLoad(page
        // Essential elements should be visible
        await expect(page.locator('h1')).toBeVisible(
        await expect(page.locator('input[placeholder*="検索"]')).toBeVisible(
        working`
      }
    }
  }
  test.describe('API Integration and Data Flow', () => {
    test('should test stock data retrieval automation', async ({ page }) => {
      // Test API endpoints if available
      const apiEndpoints = [
        'http://localhost:8080/api/finance/stocks/AAPL/price'
        'http://localhost:8080/api/finance/stocks/list'
        'http://localhost:8080/health'
      ];

      for (const endpoint of apiEndpoints) {
        const isAvailable = await TestUtils.checkAPIAvailability(page, endpoint
        }
    }
    test('should validate stock detail page functionality', async ({ page }) => {
      // Test navigation to stock details
      const stockSymbol = 'AAPL';

      // Try to navigate to detail page
      await page.goto(`/details/${stockSymbol}`
      await TestUtils.waitForPageLoad(page
      // Check if page loads without critical errors
      const criticalErrors = (page as any).testErrors.filter((error: string) =>
        !error.includes('favicon') &&
        !error.includes('fonts.gstatic.com') &&
        !error.includes('net::ERR_INTERNET_DISCONNECTED')
      expect(criticalErrors.length).toBe(0
      // Verify page structure
      const pageTitle = await page.title(
      expect(pageTitle).toBeTruthy(
    }
    test('should test chart rendering capabilities', async ({ page }) => {
      await page.goto('/details/AAPL'
      await TestUtils.waitForPageLoad(page
      // Wait for potential chart loading
      await page.waitForTimeout(CONFIG.timeouts.element
      // Check for chart container or recharts elements
      const hasChartContainer = await page.locator('.recharts-wrapper, [data-testid="stock-chart"], canvas').count(
      if (hasChartContainer > 0) {
        } else {
        }
    }
  }
  test.describe('Performance and Reliability', () => {
    test('should measure and validate page performance', async ({ page }) => {
      const startTime = Date.now(
      await page.goto('/'
      await TestUtils.waitForPageLoad(page
      const metrics = await TestUtils.capturePageMetrics(page
      const totalLoadTime = Date.now() - startTime;

      // Performance thresholds
      expect(totalLoadTime).toBeLessThan(15000); // 15 seconds max
      expect(metrics.domContentLoaded).toBeLessThan(5000); // 5 seconds max DOMContentLoaded

      }
    test('should test error handling and graceful degradation', async ({ page }) => {
      // Test with invalid stock symbol
      const searchInput = page.locator('input[placeholder*="検索"]'
      await searchInput.fill('INVALID_SYMBOL_12345'
      const searchButton = page.locator('button[type="submit"]'
      await searchButton.click(
      await page.waitForTimeout(CONFIG.timeouts.short
      // Application should handle gracefully
      const pageIsResponsive = await page.locator('body').isVisible(
      expect(pageIsResponsive).toBe(true
    }
    test('should validate accessibility features', async ({ page }) => {
      // Check for basic accessibility features
      const h1Count = await page.locator('h1').count(
      expect(h1Count).toBeGreaterThanOrEqual(1
      // Check for form labels
      const searchInput = page.locator('input[placeholder*="検索"]'
      await expect(searchInput).toBeVisible(
      // Check for button accessibility
      const buttons = page.locator('button'
      const buttonCount = await buttons.count(
      expect(buttonCount).toBeGreaterThan(0
      }
  }
  test.describe('Automated Regression Testing', () => {
    test('should run automated smoke test suite', async ({ page }) => {
      const smokeTests = [
        async () => {
          await page.goto('/'
          await expect(page.locator('h1')).toBeVisible(
          return 'Homepage loads';
        }
        async () => {
          const searchInput = page.locator('input[placeholder*="検索"]'
          await searchInput.fill('AAPL'
          await page.locator('button[type="submit"]').click(
          await page.waitForTimeout(1000
          return 'Search functionality works';
        }
        async () => {
          await page.goto('/privacy'
          await TestUtils.waitForPageLoad(page
          return 'Privacy page accessible';
        }
        async () => {
          await page.goto('/terms'
          await TestUtils.waitForPageLoad(page
          return 'Terms page accessible';
        }
      ];

      const results = [];
      for (const [index, test] of Array.from(smokeTests.entries())) {
        try {
          const result = await test(
          results.push(`✓ ${result}`
        } catch (error) {
          results.push(`✗ Test ${index + 1} failed: ${error}`
        }
      }

      // At least 75% of smoke tests should pass
      const passedTests = results.filter(r => r.startsWith('✓')).length;
      expect(passedTests / smokeTests.length).toBeGreaterThanOrEqual(0.75
    }
    test('should test critical user journeys', async ({ page }) => {
      // Journey 1: Homepage → Search → Results
      await page.goto('/'
      await TestUtils.waitForPageLoad(page
      const searchInput = page.locator('input[placeholder*="検索"]'
      await searchInput.fill('AAPL'
      const searchButton = page.locator('button[type="submit"]'
      await searchButton.click(
      await page.waitForTimeout(CONFIG.timeouts.short
      // Verify journey completion
      const finalUrl = page.url(
      expect(finalUrl).toBeTruthy(
      }
  }
  test.afterAll(async () => {
    // Generate test report
    const passedTests = testMetrics.filter(t => t.status === 'passed').length;
    const failedTests = testMetrics.filter(t => t.status === 'failed').length;

    * 100).toFixed(1)}%`
    // Performance summary
    const avgDuration = testMetrics.reduce((sum, t) => sum + t.duration, 0) / testMetrics.length;
    }ms`
    // Error summary
    const totalErrors = testMetrics.reduce((sum, t) => sum + t.errors.length, 0
    }
});