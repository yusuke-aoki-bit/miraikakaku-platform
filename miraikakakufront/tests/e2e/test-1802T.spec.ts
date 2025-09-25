import { test, expect } from '@playwright/test';

test.describe('1802.T Specific Test', () => {
  test('should test 1802.T page specifically for investment analysis features', async ({ page }) => {
    const consoleMessages: string[] = [];
    const errors: string[] = [];
    const failedRequests: {url: string, status: number}[] = [];

    // Capture network requests
    page.on('response', response => {
      if (response.status() >= 400) {
        const failedRequest = { url: response.url(), status: response.status() };
        failedRequests.push(failedRequest
        } ${response.url()}`
      } else if (response.url().includes('/api/')) {
        } ${response.url()}`
      }
    }
    // Capture console messages
    page.on('console', msg => {
      const message = `${msg.type()}: ${msg.text()}`;
      consoleMessages.push(message
      if (msg.type() === 'error') {
        }
    }
    // Capture JavaScript errors
    page.on('pageerror', error => {
      const errorMessage = `Runtime Error: ${error.message}`;
      errors.push(errorMessage
      }
    // Set long timeout
    test.setTimeout(120000
    try {
      // Navigate to 1802.T page
      await page.goto('http://localhost:3003/details/1802.T', {
        timeout: 60000
        waitUntil: 'domcontentloaded'
      }
      await page.waitForLoadState('networkidle', { timeout: 30000 }
      await page.waitForTimeout(20000
      // Take screenshot for debugging
      await page.screenshot({
        path: '1802T-debug.png'
        fullPage: true
      }
      // Check page content
      const pageContent = await page.textContent('body'
      // Check if still loading
      const loadingElements = await page.locator('text=株式データを読み込み中').count(
      // Check for specific investment analysis content
      const searchTerms = [
        'テクニカル分析'
        '財務分析'
        'リスク分析'
        'AI予測'
        '過去の予測'
        'P/E Ratio'
        'RSI'
        '価格アラート'
        '1802'
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
      failedRequests.forEach((req, i) =>
      consoleMessages.filter(msg => msg.includes('error')).forEach((msg, i) =>
      errors.forEach((err, i) =>
      // Basic assertion
      expect(foundTerms).toBeGreaterThan(2
    } catch (error) {
      // Take error screenshot
      await page.screenshot({
        path: '1802T-debug-error.png'
        fullPage: true
      }
      throw error;
    }
  }
});