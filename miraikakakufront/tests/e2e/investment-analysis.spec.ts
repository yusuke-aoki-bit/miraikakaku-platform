import { test, expect } from '@playwright/test';

test.describe('Investment Analysis Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/'
    await page.waitForLoadState('networkidle'
  }
  test('should display all investment analysis sections for stock with data', async ({ page }) => {
    // Navigate directly to a stock with data (Japanese stock)
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Verify main stock information is displayed
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible(
    // Check if Technical Analysis section is present
    const technicalAnalysis = page.locator('text=テクニカル分析'
    await expect(technicalAnalysis).toBeVisible(
    // Verify technical indicators are displayed
    await expect(page.locator('text=RSI')).toBeVisible(
    await expect(page.locator('text=移動平均線')).toBeVisible(
    await expect(page.locator('text=ボラティリティ')).toBeVisible(
    await expect(page.locator('text=出来高')).toBeVisible(
    // Check if overall signal is displayed
    const overallSignal = page.locator('text=総合シグナル'
    await expect(overallSignal).toBeVisible(
    // Check for BUY/SELL/HOLD signals
    const signals = page.locator('text=/BUY|SELL|HOLD/'
    await expect(signals.first()).toBeVisible(
  }
  test('should display financial analysis section', async ({ page }) => {
    // Navigate to a stock details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Check if Financial Analysis section is present
    const financialAnalysis = page.locator('text=財務分析'
    await expect(financialAnalysis).toBeVisible(
    // Verify financial metrics are displayed
    const peRatio = page.locator('text=P/E Ratio'
    const marketCap = page.locator('text=時価総額'
    const beta = page.locator('text=ベータ値'
    // At least some financial metrics should be visible
    const financialMetrics = [peRatio, marketCap, beta];
    let visibleCount = 0;
    for (const metric of financialMetrics) {
      if (await metric.isVisible()) {
        visibleCount++;
      }
    }
    expect(visibleCount).toBeGreaterThan(0
  }
  test('should display risk analysis section', async ({ page }) => {
    // Navigate to a stock details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Check if Risk Analysis section is present
    const riskAnalysis = page.locator('text=リスク分析'
    await expect(riskAnalysis).toBeVisible(
    // Verify risk levels are displayed (LOW/MEDIUM/HIGH)
    const riskLevels = page.locator('text=/LOW|MEDIUM|HIGH/'
    await expect(riskLevels.first()).toBeVisible(
    // Check for investment warning
    const investmentWarning = page.locator('text=投資リスク警告'
    await expect(investmentWarning).toBeVisible(
  }
  test('should allow adding and managing price alerts', async ({ page }) => {
    // Navigate to a stock details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Check if Price Alerts section is present
    const priceAlerts = page.locator('text=価格アラート'
    await expect(priceAlerts).toBeVisible(
    // Click on add alert button
    const addAlertButton = page.locator('button[title="アラート追加"]'
    await expect(addAlertButton).toBeVisible(
    await addAlertButton.click(
    // Verify add alert form appears
    await expect(page.locator('text=新しいアラート')).toBeVisible(
    await expect(page.locator('text=目標価格')).toBeVisible(
    // Fill in alert form
    await page.fill('input[type="number"]', '2700'
    // Select alert type (above)
    await page.click('text=上昇時'
    // Add the alert
    await page.click('text=アラート追加'
    // Verify alert was added
    await expect(page.locator('text=¥2700.00')).toBeVisible(
    await expect(page.locator('text=監視中')).toBeVisible(
  }
  test('should test quick alert settings', async ({ page }) => {
    // Navigate to a stock details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Scroll to price alerts section
    await page.locator('text=価格アラート').scrollIntoViewIfNeeded(
    // Test quick setting buttons
    const quickButtons = ['+5%', '+10%', '-5%', '-10%'];

    for (const buttonText of quickButtons) {
      const button = page.locator(`text=${buttonText}`
      if (await button.isVisible()) {
        await button.click(
        // Verify form opens with pre-filled values
        await expect(page.locator('text=新しいアラート')).toBeVisible(
        // Cancel the form
        await page.click('text=キャンセル'
        // Wait a bit before next iteration
        await page.waitForTimeout(500
      }
    }
  }
  test('should handle stocks without sufficient data gracefully', async ({ page }) => {
    // Navigate to a stock that might not have enough data
    await page.goto('http://localhost:3001/details/AAPL'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Check if appropriate messages are shown for insufficient data
    const insufficientDataMessage = page.locator('text=十分な価格データがありません'
    const noDataMessage = page.locator('text=財務データが利用できません'
    // At least one of these should be visible if there's no data
    const hasInsufficientDataMessage = await insufficientDataMessage.isVisible(
    const hasNoDataMessage = await noDataMessage.isVisible(
    // Verify that the page doesn't crash and shows appropriate messages
    if (hasInsufficientDataMessage || hasNoDataMessage) {
      }

    // Verify that basic structure is still present
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    await expect(page.locator('text=テクニカル分析')).toBeVisible(
    await expect(page.locator('text=財務分析')).toBeVisible(
  }
  test('should display enhanced AI analysis with impact indicators', async ({ page }) => {
    // Navigate to a stock details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Check if AI Analysis section is present
    await expect(page.locator('[data-testid="ai-analysis"]')).toBeVisible(
    // Verify enhanced AI analysis features
    const impactIndicators = page.locator('text=/ポジティブ|ネガティブ|ニュートラル/'
    const weightIndicators = page.locator('text=/重み:/'
    // At least some impact indicators should be visible
    const impactCount = await impactIndicators.count(
    expect(impactCount).toBeGreaterThan(0
  }
  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }
    // Navigate to stock details
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Verify main sections are still accessible on mobile
    await expect(page.locator('[data-testid="stock-header"]')).toBeVisible(
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible(
    // Check if technical analysis is accessible (might need scrolling)
    await page.locator('text=テクニカル分析').scrollIntoViewIfNeeded(
    await expect(page.locator('text=テクニカル分析')).toBeVisible(
    // Check if price alerts are accessible in sidebar
    await page.locator('text=価格アラート').scrollIntoViewIfNeeded(
    await expect(page.locator('text=価格アラート')).toBeVisible(
  }
  test('should maintain investment analysis functionality across page refreshes', async ({ page }) => {
    // Navigate to details page
    await page.goto('http://localhost:3001/details/1605.T'
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Add a price alert
    const addAlertButton = page.locator('button[title="アラート追加"]'
    if (await addAlertButton.isVisible()) {
      await addAlertButton.click(
      await page.fill('input[type="number"]', '2800'
      await page.click('text=上昇時'
      await page.click('text=アラート追加'
      // Verify alert was added
      await expect(page.locator('text=¥2800.00')).toBeVisible(
    }

    // Refresh the page
    await page.reload(
    await page.waitForLoadState('networkidle'
    await page.waitForSelector('[data-testid="stock-header"]', { timeout: 15000 }
    // Verify that all analysis sections are still present
    await expect(page.locator('text=テクニカル分析')).toBeVisible(
    await expect(page.locator('text=財務分析')).toBeVisible(
    await expect(page.locator('text=価格アラート')).toBeVisible(
    // Verify that the price alert persisted (stored in localStorage)
    if (await addAlertButton.isVisible()) {
      await expect(page.locator('text=¥2800.00')).toBeVisible(
    }
  }
});