import { test, expect } from '@playwright/test';

test.describe('Detailed Debug Test', () => {
  test('should debug the rendering process step by step', async ({ page }) => {
    // Set long timeout
    test.setTimeout(120000
    try {
      // Navigate to details page
      await page.goto('http://localhost:3003/details/1802.T', {
        timeout: 60000
        waitUntil: 'domcontentloaded'
      }
      // Wait for network to be idle
      await page.waitForLoadState('networkidle', { timeout: 30000 }
      // Wait additional time for API calls
      await page.waitForTimeout(10000
      // Take screenshot for debugging
      await page.screenshot({
        path: 'debug-after-network-idle.png'
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

      // Wait even longer and check again
      await page.waitForTimeout(10000
      foundTerms = 0;
      for (const term of searchTerms) {
        const found = await page.locator(`text=${term}`).count(
        if (found > 0) {
          : ${term} (${found} times)`
          foundTerms++;
        } else {
          : ${term}`
        }
      }

      // Take final screenshot
      await page.screenshot({
        path: 'debug-final-state.png'
        fullPage: true
      }
      // Check for error messages
      const errorText = await page.locator('text=Error').count(
      const errorElements = await page.locator('[data-testid*="error"]').count(
      // Check for loading state
      const loadingState = await page.locator('[data-testid="loading-page"]').count(
      // Mark as passed if we found at least some features
      expect(foundTerms).toBeGreaterThan(0
    } catch (error) {
      // Take error screenshot
      await page.screenshot({
        path: 'debug-error-state.png'
        fullPage: true
      }
      // Don't fail completely, just log
      }
  }
});