import { test, expect } from '@playwright/test';

test.describe('Miraikakaku E2E Tests - Detailed API to Frontend Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Set up any necessary test data or state
    await page.goto('http://localhost:3000'
  }
  test('Complete data flow: API → Frontend rendering', async ({ page }) => {
    // Step 1: Wait for page to load
    await page.waitForLoadState('networkidle'
    // Step 2: Check if the main elements are present
    await expect(page).toHaveTitle(/未来価格|Miraikakaku/
    // Step 3: Wait for the app to fully load (look for main content)
    try {
      // Wait for any loading spinner to disappear
      await page.waitForSelector('.animate-spin', { state: 'detached', timeout: 30000 }
      } catch (e) {
      }

    // Step 4: Look for main navigation or search elements
    const searchSelectors = [
      'input[type="search"]'
      'input[placeholder*="検索"]'
      'input[placeholder*="search"]'
      '[data-testid="search"]'
      '.search-input'
      'input[type="text"]'
    ];

    let searchInput = null;
    for (const selector of searchSelectors) {
      try {
        searchInput = await page.waitForSelector(selector, { timeout: 5000 }
        if (searchInput) {
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (searchInput) {
      // Step 5: Test search functionality
      await searchInput.fill('AAPL'
      // Look for search button or trigger search
      const searchTriggers = [
        'button[type="submit"]'
        '.search-button'
        '[data-testid="search-button"]'
        'button:has-text("検索")'
        'button:has-text("Search")'
      ];

      let searchTriggered = false;
      for (const trigger of searchTriggers) {
        try {
          const button = await page.waitForSelector(trigger, { timeout: 2000 }
          if (button) {
            await button.click(
            searchTriggered = true;
            break;
          }
        } catch (e) {
          // Continue
        }
      }

      if (!searchTriggered) {
        // Try pressing Enter
        await searchInput.press('Enter'
        }

      // Step 6: Wait for API call and results
      try {
        await page.waitForResponse(response =>
          response.url().includes('/api/') && response.status() === 200
          { timeout: 15000 }
        } catch (e) {
        }
    }

    // Step 7: Check for any stock data display
    const dataSelectors = [
      '.stock-card'
      '.stock-item'
      '[data-testid="stock"]'
      '.price'
      '.chart'
      '.prediction'
    ];

    let dataFound = false;
    for (const selector of dataSelectors) {
      try {
        const element = await page.waitForSelector(selector, { timeout: 5000 }
        if (element) {
          dataFound = true;
          break;
        }
      } catch (e) {
        // Continue
      }
    }

    // Step 8: Test direct API endpoints
    const apiTests = [
      { url: 'http://localhost:8000/health', name: 'Health Check' }
      { url: 'http://localhost:8000/api/symbols', name: 'Symbols List' }
      { url: 'http://localhost:8000/api/stocks/AAPL', name: 'AAPL Stock Data' }
      { url: 'http://localhost:8000/api/market/summary', name: 'Market Summary' }
    ];

    for (const apiTest of apiTests) {
      try {
        const response = await page.request.get(apiTest.url
        if (response.ok()) {
          const data = await response.json(
          }, Data keys: ${Object.keys(data).length}`
        } else {
          }`
        }
      } catch (e) {
        }
    }

    // Step 9: Check frontend responsiveness
    await page.setViewportSize({ width: 1200, height: 800 }
    await page.waitForTimeout(1000
    await page.setViewportSize({ width: 375, height: 667 }
    await page.waitForTimeout(1000
    // Step 10: Take screenshot for verification
    await page.screenshot({ path: 'e2e-test-result.png', fullPage: true }
    // Final validation
    const pageContent = await page.content(
    const hasNextJS = pageContent.includes('_next') || pageContent.includes('__next'
    const hasTitle = pageContent.includes('未来価格') || pageContent.includes('Miraikakaku'
    expect(hasNextJS, 'Next.js framework should be detected').toBe(true
    expect(hasTitle, 'Page should have correct title/branding').toBe(true
    }
  test('API data consistency validation', async ({ page }) => {
    // Test API endpoints directly
    const apiEndpoints = [
      '/health'
      '/api/symbols?limit=10'
      '/api/stocks/AAPL'
      '/api/stocks/AAPL/predictions'
      '/api/market/summary'
    ];

    const results = [];

    for (const endpoint of apiEndpoints) {
      try {
        const response = await page.request.get(`http://localhost:8000${endpoint}`
        const responseTime = Date.now(
        if (response.ok()) {
          const data = await response.json(
          const result = {
            endpoint
            status: response.status()
            responseTime: responseTime
            dataSize: JSON.stringify(data).length
            hasTimestamp: 'timestamp' in data
            success: true
          };
          results.push(result
          }, ${result.dataSize} bytes`
        } else {
          results.push({
            endpoint
            status: response.status()
            success: false
            error
          }
          }`
        }
      } catch (error) {
        results.push({
          endpoint
          success: false
          error: error.message
        }
        }
    }

    // Validate that at least 70% of API calls are successful
    const successRate = results.filter(r => r.success).length / results.length;
    expect(successRate, 'API success rate should be at least 70%').toBeGreaterThanOrEqual(0.7
    .toFixed(1)}%`
  }
  test('Frontend loading and error handling', async ({ page }) => {
    // Test page load performance
    const startTime = Date.now(
    await page.goto('http://localhost:3000'
    await page.waitForLoadState('networkidle'
    const loadTime = Date.now() - startTime;

    expect(loadTime, 'Page should load within 10 seconds').toBeLessThan(10000
    // Test navigation
    try {
      // Look for any navigation links
      const navLinks = await page.locator('a, button').all(
      // Test error scenarios
      await page.goto('http://localhost:3000/nonexistent-page'
      await page.waitForLoadState('networkidle'
      // Should show 404 or handle gracefully
      const pageContent = await page.content(
      const has404 = pageContent.includes('404') || pageContent.includes('Not Found') || pageContent.includes('見つかりません'
      if (has404) {
        } else {
        }

    } catch (error) {
      }

    // Test going back to home
    await page.goto('http://localhost:3000'
    await page.waitForLoadState('networkidle'
    }
  test('Real-time data flow simulation', async ({ page }) => {
    await page.goto('http://localhost:3000'
    await page.waitForLoadState('networkidle'
    // Monitor network requests
    const apiCalls = [];
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        apiCalls.push({
          url: response.url()
          status: response.status()
          timestamp: new Date()
        }
      }
    }
    // Simulate user interactions
    try {
      // Try to interact with any search or input elements
      const interactiveElements = await page.locator('input, button, select').all(
      for (let i = 0; i < Math.min(3, interactiveElements.length); i++) {
        try {
          const element = interactiveElements[i];
          const tagName = await element.evaluate(el => el.tagName.toLowerCase()
          if (tagName === 'input') {
            await element.fill('TEST'
            await page.waitForTimeout(500
          } else if (tagName === 'button') {
            await element.click(
            await page.waitForTimeout(1000
          }

          } catch (e) {
          }
      }
    } catch (error) {
      }

    // Wait a bit more for any delayed API calls
    await page.waitForTimeout(2000
    // Log API calls for debugging
    apiCalls.forEach((call, index) => {
      }
    // Take final screenshot
    await page.screenshot({ path: 'real-time-test-result.png', fullPage: true }
    }
});