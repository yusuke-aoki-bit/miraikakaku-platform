import { test, expect } from '@playwright/test';

test.describe('Ranking Data Validation E2E', () => {
  test('Verify API returns correct ranking data', async ({ page }) => {
    // Test the API directly first
    const apiResponse = await page.request.get('http://localhost:8086/api/finance/rankings/accurate'
    expect(apiResponse.ok()).toBeTruthy(
    const apiData = await apiResponse.json(

    // Verify API returns actual data with non-zero values
    expect(apiData.success).toBe(true
    expect(apiData.data).toBeDefined(
    expect(Array.isArray(apiData.data)).toBe(true
    expect(apiData.data.length).toBeGreaterThan(0
    // Check first ranking item has non-zero values
    const firstItem = apiData.data[0];
    expect(firstItem.symbol).toBeDefined(
    expect(firstItem.company_name).toBeDefined(
    expect(firstItem.avg_confidence_score).toBeGreaterThan(0
    expect(firstItem.avg_current_price).toBeGreaterThan(0
    }
  test('Verify frontend displays correct ranking data', async ({ page }) => {
    // Navigate to the main page
    await page.goto('http://localhost:3002/'
    // Wait for the page to load and rankings to appear
    await page.waitForLoadState('networkidle'
    await page.waitForTimeout(3000); // Give time for API calls

    // Take a screenshot for debugging
    await page.screenshot({ path: '/tmp/frontend-ranking-test.png', fullPage: true }
    // Check if ranking cards are present
    const rankingCards = await page.locator('[data-testid="ranking-card"]').count(
    if (rankingCards === 0) {
      // Try alternative selectors
      const altCards = await page.locator('.bg-white.rounded-lg.shadow').count(
      // Log the entire page content for debugging
      const pageContent = await page.content(
      // Check for error messages
      const errorMessages = await page.locator('text=エラー').count(
      }

    // Intercept API calls to see what the frontend is requesting
    page.on('request', request => {
      if (request.url().includes('/api/finance/rankings')) {
      }
    }
    page.on('response', response => {
      if (response.url().includes('/api/finance/rankings')) {
        , response.url()
      }
    }
    // Wait for any API calls to complete
    await page.waitForTimeout(2000
    // Check if ranking data is displayed with actual values
    const confidenceElements = await page.locator('text=/信頼度.*%/').count(
    const priceElements = await page.locator('text=/\\$\\d+/').count(
    // Get specific text content to verify values
    const allText = await page.textContent('body'
    const hasZeroValues = allText?.includes('0.00%') || allText?.includes('$0.00'
    const hasActualValues = /\d+\.\d+%/.test(allText || '') && /\$\d+\.\d+/.test(allText || ''
    if (hasZeroValues) {
      // Extract specific ranking data from the page
      const rankingTexts = await page.locator('.bg-white.rounded-lg.shadow').allTextContents(
      rankingTexts.forEach((text, index) => {
      }
    }
  }
  test('Check frontend API configuration and network calls', async ({ page }) => {
    // Monitor all network requests
    const apiCalls: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiCalls.push({
          url: request.url()
          method: request.method()
        }
      }
    }
    page.on('response', async response => {
      if (response.url().includes('/api/finance/rankings')) {
        const responseBody = await response.text(

      }
    }
    // Go to homepage
    await page.goto('http://localhost:3002/'
    await page.waitForLoadState('networkidle'
    await page.waitForTimeout(3000
    apiCalls.forEach(call => {
      }
    // Check if the correct API endpoint is being called
    const correctEndpointCalled = apiCalls.some(call =>
      call.url.includes('localhost:8086') && call.url.includes('/api/finance/rankings')
    if (!correctEndpointCalled) {
      }
  }
});