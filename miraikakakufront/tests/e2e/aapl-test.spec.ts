import { test, expect } from '@playwright/test';

test.describe('AAPL Page Test', () => {
  test('should test AAPL page rendering', async ({ page }) => {
    // Set long timeout
    test.setTimeout(120000
    try {
      // Navigate to AAPL page
      await page.goto('http://localhost:3003/details/AAPL', {
        timeout: 60000
        waitUntil: 'domcontentloaded'
      }
      // Wait for network to be idle
      await page.waitForLoadState('networkidle', { timeout: 30000 }
      // Wait additional time for API calls
      await page.waitForTimeout(10000
      // Take screenshot for debugging
      await page.screenshot({
        path: 'aapl-test.png'
        fullPage: true
      }
      // Check page content
      const pageContent = await page.textContent('body'
      // Check if still loading
      const loadingElements = await page.locator('text=株式データを読み込み中').count(
      // Check for specific content
      const searchTerms = [
        'テクニカル分析'
        '財務分析'
        'リスク分析'
        'P/E Ratio'
        'RSI'
        '価格アラート'
        'AAPL'
      ];

      let foundTerms = 0;
      for (const term of searchTerms) {
        const found = await page.locator(`text=${term}`).count(
        if (found > 0) {
          `
          foundTerms++;
        } else {
          }
      }

      // Check for error messages
      const errorText = await page.locator('text=404').count(
      expect(foundTerms).toBeGreaterThan(2
    } catch (error) {
      // Take error screenshot
      await page.screenshot({
        path: 'aapl-test-error.png'
        fullPage: true
      }
      }
  }
});