import { test, expect } from '@playwright/test';

test.describe('Runtime Error Debug', () => {
  test('should capture browser console errors and runtime issues', async ({ page }) => {
    const consoleMessages: string[] = [];
    const errors: string[] = [];
    const failedRequests: {url: string, status: number}[] = [];

    // Capture network requests
    page.on('response', response => {
      if (response.status() >= 400) {
        const failedRequest = { url: response.url(), status: response.status() };
        failedRequests.push(failedRequest
        } ${response.url()}`
      } else {
        } ${response.url()}`
      }
    }
    // Capture console messages
    page.on('console', msg => {
      const message = `${msg.type()}: ${msg.text()}`;
      consoleMessages.push(message
      }
    // Capture JavaScript errors
    page.on('pageerror', error => {
      const errorMessage = `Runtime Error: ${error.message}`;
      errors.push(errorMessage
      }
    // Set long timeout
    test.setTimeout(120000
    try {
      // Navigate to details page
      await page.goto('http://localhost:3003/details/1605.T', {
        timeout: 60000
        waitUntil: 'domcontentloaded'
      }
      await page.waitForLoadState('networkidle', { timeout: 30000 }
      await page.waitForTimeout(15000
      // Take screenshot for debugging
      await page.screenshot({
        path: 'runtime-error-debug.png'
        fullPage: true
      }
      // Check for error indicators
      const errorElements = await page.locator('[data-testid*="error"]').count(
      const loadingElements = await page.locator('text=株式データを読み込み中').count(
      // Check for specific content
      const pageContent = await page.textContent('body'
      // Look for analysis sections
      const sections = [
        'テクニカル分析'
        '財務分析'
        'リスク分析'
        'AI予測'
        '過去の予測'
      ];

      for (const section of sections) {
        const found = await page.locator(`text=${section}`).count(
        }

      // Check network requests
      const requests = await page.evaluate(() => {
        return performance.getEntriesByType('resource').map(entry => ({
          name: entry.name
          transferSize: (entry as any).transferSize || 0
        })
      }
      requests.forEach(req => {
        if (req.name.includes('api/finance')) {
          `
        }
      }
      failedRequests.forEach((req, i) =>
      consoleMessages.forEach((msg, i) =>
      errors.forEach((err, i) =>
      } catch (error) {
      // Take error screenshot
      await page.screenshot({
        path: 'runtime-error-debug-error.png'
        fullPage: true
      }
      failedRequests.forEach((req, i) =>
      consoleMessages.forEach((msg, i) =>
      errors.forEach((err, i) =>
    }
  }
});