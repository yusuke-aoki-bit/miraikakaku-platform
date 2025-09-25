import { test, expect } from '@playwright/test';

test.describe('Simple Debug Test', () => {
  test('should load 1802.T page and capture status', async ({ page }) => {
    const consoleMessages: string[] = [];
    const errors: string[] = [];

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
    try {
      // Navigate to 1802.T page
      await page.goto('http://localhost:3003/details/1802.T', {
        timeout: 60000
        waitUntil: 'domcontentloaded'
      }
      await page.waitForLoadState('networkidle', { timeout: 30000 }
      await page.waitForTimeout(10000
      // Take screenshot for debugging
      await page.screenshot({
        path: 'debug-simple.png'
        fullPage: true
      }
      // Check page state
      const pageContent = await page.textContent('body'
      // Check for loading state
      const loadingElements = await page.locator('text=株式データを読み込み中').count(
      // Check if content is rendered
      const hasCharts = await page.locator('[data-testid="stock-chart"]').count(
      consoleMessages.forEach((msg, i) =>
      errors.forEach((err, i) =>
      } catch (error) {
      await page.screenshot({
        path: 'debug-simple-error.png'
        fullPage: true
      }
    }
  }
});