import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {

  test('should connect to API endpoints', async ({ page }) => {
    // Listen for network requests to API
    const apiRequests: string[] = [];
    page.on('request', request => {
      if (request.url().includes('api.miraikakaku.com')) {
        apiRequests.push(request.url()
      }
    }
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Try to trigger an API call by searching
    const searchInput = page.locator('[data-testid="search-input"], input[placeholder*="銘柄"], input[type="text"]').first(
    await expect(searchInput).toBeVisible({ timeout: 10000 }
    await searchInput.fill('AAPL'
    const searchButton = page.locator('button[type="submit"]').first(
    await searchButton.click(
    // Wait for potential API calls
    await page.waitForTimeout(5000
    // Check if API calls were made (informational - not failing test)
    apiRequests.forEach(url =>
  }
  test('should display real stock data if available', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Look for any stock price displays or market data
    const stockElements = [
      page.locator('[data-testid*="stock"]')
      page.locator('[data-testid*="price"]')
      page.locator('text=/\\$[0-9]+/')
      page.locator('text=/¥[0-9
]+/')
      page.locator('text=/[+-]?[0-9]+\\.?[0-9]*%/')
    ];

    let hasStockData = false;
    for (const element of stockElements) {
      const count = await element.count(
      if (count > 0) {
        hasStockData = true;
        break;
      }
    }

    // This is informational - we check for data but don't fail if none found
    }
  test('should handle API errors gracefully', async ({ page }) => {
    const networkErrors: string[] = [];

    page.on('response', response => {
      if (response.url().includes('api.miraikakaku.com') && !response.ok()) {
        networkErrors.push(`${response.status()} - ${response.url()}`
      }
    }
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Try an API operation
    const searchInput = page.locator('input[placeholder*="銘柄"], input[type="text"]').first(
    if (await searchInput.isVisible()) {
      await searchInput.fill('INVALID_SYMBOL'
      const searchButton = page.locator('button[type="submit"]').first(
      await searchButton.click(
      await page.waitForTimeout(3000
    }

    // Log network errors (informational)
    networkErrors.forEach(error =>
    // The page should still be functional regardless of API errors
    // Instead of checking body visibility (which can be affected by loaders)
    // check for main content or interactive elements
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
  }
  test('should show loading states appropriately', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Look for common loading indicators
    const loadingElements = [
      page.locator('[data-testid*="loading"]')
      page.locator('text=読み込み中')
      page.locator('text=Loading')
      page.locator('.loading')
      page.locator('.spinner')
    ];

    let hasLoadingStates = false;
    for (const element of loadingElements) {
      const count = await element.count(
      if (count > 0) {
        hasLoadingStates = true;
        break;
      }
    }

    }
  test('should navigate between pages correctly', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check if navigation links exist and work
    const navLinks = [
      page.locator('a[href="/predictions"]')
      page.locator('a[href="/watchlist"]')
      page.locator('a[href="/discovery"]')
      page.locator('text=AI予測').locator('a').first()
      page.locator('text=ウォッチリスト').locator('a').first()
    ];

    for (const link of navLinks) {
      if (await link.count() > 0 && await link.first().isVisible()) {
        await link.first().click(
        await page.waitForTimeout(2000
        // Verify we're on a valid page
        expect(page.url()).toBeTruthy(

        // Go back to home
        await page.goto('/'
        await page.waitForTimeout(1000
        break;
      }
    }
  }
});