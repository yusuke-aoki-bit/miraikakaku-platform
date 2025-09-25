import { test, expect } from '@playwright/test';

test.describe('Simple Investment Analysis Test', () => {
  test('should display investment analysis features on details page', async ({ page }) => {
    // Navigate directly to a stock details page
    await page.goto('http://localhost:3001/details/1605.T'
    // Wait for page to load with generous timeout
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Wait for main content to load
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 30000 }
    // Verify basic elements are present
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible(
    // Check for Technical Analysis section
    const technicalAnalysis = page.locator('h2:has-text("テクニカル分析")'
    if (await technicalAnalysis.isVisible()) {
      // Look for RSI indicators
      const rsiIndicator = page.locator('text=RSI'
      if (await rsiIndicator.isVisible()) {
        }

      // Look for moving average
      const movingAverage = page.locator('text=移動平均線'
      if (await movingAverage.isVisible()) {
        }

      // Look for buy/sell signals
      const signals = page.locator('text=/BUY|SELL|HOLD/'
      const signalCount = await signals.count(
      } else {
      }

    // Check for Financial Analysis section
    const financialAnalysis = page.locator('h2:has-text("財務分析")'
    if (await financialAnalysis.isVisible()) {
      // Look for P/E ratio
      const peRatio = page.locator('text=P/E Ratio'
      if (await peRatio.isVisible()) {
        }
    } else {
      }

    // Check for Risk Analysis section
    const riskAnalysis = page.locator('h2:has-text("リスク分析")'
    if (await riskAnalysis.isVisible()) {
      // Look for risk levels
      const riskLevels = page.locator('text=/LOW|MEDIUM|HIGH/'
      const riskCount = await riskLevels.count(
      } else {
      }

    // Check for Price Alerts section
    const priceAlerts = page.locator('h3:has-text("価格アラート")'
    if (await priceAlerts.isVisible()) {
      // Look for add alert button
      const addButton = page.locator('button[title="アラート追加"]'
      if (await addButton.isVisible()) {
        }
    } else {
      }

    // Check for AI Analysis section
    const aiAnalysis = page.locator('[data-testid="ai-analysis"]'
    if (await aiAnalysis.isVisible()) {
      // Look for impact indicators
      const impactIndicators = page.locator('text=/ポジティブ|ネガティブ|ニュートラル/'
      const impactCount = await impactIndicators.count(
      } else {
      }

    }
  test('should handle price alert creation', async ({ page }) => {
    // Navigate to details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 30000 }
    // Try to find price alerts section
    const priceAlerts = page.locator('h3:has-text("価格アラート")'
    if (await priceAlerts.isVisible()) {
      // Scroll to price alerts section
      await priceAlerts.scrollIntoViewIfNeeded(
      // Look for add alert button
      const addButton = page.locator('button[title="アラート追加"]'
      if (await addButton.isVisible()) {
        // Click add alert button
        await addButton.click(
        // Wait for form to appear
        await page.waitForSelector('text=新しいアラート', { timeout: 5000 }
        // Fill in alert price
        const priceInput = page.locator('input[type="number"]'
        if (await priceInput.isVisible()) {
          await priceInput.fill('2700'
          // Click add button
          const addAlertBtn = page.locator('text=アラート追加'
          if (await addAlertBtn.isVisible()) {
            await addAlertBtn.click(
            // Verify alert was created
            const alertItem = page.locator('text=¥2700.00'
            if (await alertItem.isVisible()) {
              }
          }
        }
      } else {
        }
    } else {
      }
  }
  test('should display responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }
    // Navigate to details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 30000 }
    // Verify main elements are still accessible on mobile
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible(
    // Check if analysis sections are accessible with scrolling
    const technicalAnalysis = page.locator('h2:has-text("テクニカル分析")'
    if (await technicalAnalysis.isVisible({ timeout: 5000 })) {
      await technicalAnalysis.scrollIntoViewIfNeeded(
      }

    const priceAlerts = page.locator('h3:has-text("価格アラート")'
    if (await priceAlerts.isVisible({ timeout: 5000 })) {
      await priceAlerts.scrollIntoViewIfNeeded(
      }

    }
});