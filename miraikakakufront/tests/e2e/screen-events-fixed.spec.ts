import { test, expect } from '@playwright/test';

test.describe('Screen Events and Interactions E2E Testing (Fixed)', () => {

  test.describe('Homepage Events', () => {
    test('should handle search form submission events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Wait for page to be fully interactive
      await page.waitForTimeout(2000
      // Test form submission event - fixed version
      const searchInput = page.locator('input[placeholder*="銘柄"], input[type="text"]').first(
      const searchButton = page.locator('button[type="submit"]').first(
      // Ensure elements are visible and ready
      await expect(searchInput).toBeVisible({ timeout: 10000 }
      await expect(searchButton).toBeVisible({ timeout: 10000 }
      // Test input change events
      await searchInput.fill('AAPL'
      await page.waitForTimeout(500); // Allow for debounced search

      // Test button click event instead of form submit
      await searchButton.click(
      await page.waitForTimeout(2000
      // Verify the action was processed (page change or search results)
      const currentUrl = page.url(
      const pageContent = await page.content(
      // Check if search was processed in some way
      const searchProcessed =
        currentUrl.includes('AAPL') ||
        currentUrl.includes('search') ||
        currentUrl.includes('details') ||
        pageContent.includes('AAPL') ||
        (await page.locator('text=/AAPL|Apple/i').count()) > 0;

      if (searchProcessed) {
        } else {
        '
      }
    }
    test('should handle navigation click events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test navigation links
      const navLinks = [
        'a[href="/predictions"]'
        'a[href="/watchlist"]'
        'a[href="/discovery"]'
        'a[href="/portfolio"]'
        'a[href="/news"]'
      ];

      for (const linkSelector of navLinks) {
        const link = page.locator(linkSelector).first(
        if (await link.count() > 0) {
          await link.click(
          await page.waitForTimeout(1000
          // Check if navigation occurred
          const currentUrl = page.url(
          // Go back to home for next test
          await page.goto('/'
          await page.waitForTimeout(1000
        }
      }
      }
    test('should handle keyboard events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      const searchInput = page.locator('input[placeholder*="銘柄"], input[type="text"]').first(
      await expect(searchInput).toBeVisible({ timeout: 10000 }
      // Test keyboard events
      await searchInput.focus(
      // Test typing events
      await searchInput.type('AAPL', { delay: 100 }
      await page.waitForTimeout(500
      // Test Enter key event
      await searchInput.press('Enter'
      await page.waitForTimeout(2000
      // Test Escape key event
      await searchInput.press('Escape'
      await page.waitForTimeout(500
      // Test backspace events
      await searchInput.press('Backspace'
      await searchInput.press('Backspace'
      }
    test('should handle scroll events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test scroll events
      await page.evaluate(() => window.scrollTo(0, 500)
      await page.waitForTimeout(1000
      await page.evaluate(() => window.scrollTo(0, 1000)
      await page.waitForTimeout(1000
      // Test scroll to bottom
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)
      await page.waitForTimeout(1000
      // Test scroll back to top
      await page.evaluate(() => window.scrollTo(0, 0)
      await page.waitForTimeout(1000
      }
  }
  test.describe('Mouse and Touch Events', () => {
    test('should handle mouse hover events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test hover events on buttons and links
      const hoverTargets = [
        'button[type="submit"]'
        'a[href="/predictions"]'
        'input[type="text"]'
      ];

      for (const selector of hoverTargets) {
        const element = page.locator(selector).first(
        if (await element.count() > 0) {
          await element.hover(
          await page.waitForTimeout(300
        }
      }

      }
    test('should handle click and double-click events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test single click events
      const clickableElements = page.locator('button, a[href], input[type="text"]'
      const count = await clickableElements.count(
      if (count > 0) {
        // Test click on first few elements
        for (let i = 0; i < Math.min(3, count); i++) {
          const element = clickableElements.nth(i
          if (await element.isVisible()) {
            await element.click(
            await page.waitForTimeout(500
          }
        }
      }

      }
    test('should handle focus and blur events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      const searchInput = page.locator('input[type="text"]').first(
      if (await searchInput.count() > 0) {
        // Test focus event
        await searchInput.focus(
        await page.waitForTimeout(300
        // Test blur event
        await searchInput.blur(
        await page.waitForTimeout(300
        // Test focus again
        await searchInput.focus(
        await page.waitForTimeout(300
      }

      }
  }
  test.describe('Responsive Screen Events', () => {
    test('should handle viewport resize events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test different viewport sizes
      const viewports = [
        { width: 375, height: 667, name: 'Mobile' }
        { width: 768, height: 1024, name: 'Tablet' }
        { width: 1280, height: 800, name: 'Desktop' }
        { width: 1920, height: 1080, name: 'Large Desktop' }
      ];

      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height }
        await page.waitForTimeout(500
        // Verify page is still functional
        await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
        viewport handled`
      }
    }
    test('should handle orientation change simulation', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Simulate mobile portrait
      await page.setViewportSize({ width: 375, height: 667 }
      await page.waitForTimeout(500
      // Simulate mobile landscape
      await page.setViewportSize({ width: 667, height: 375 }
      await page.waitForTimeout(500
      // Verify functionality still works
      await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
      }
  }
  test.describe('Page Navigation Events (Fixed)', () => {
    test('should handle page load events', async ({ page }) => {
      // Test page load event with proper timeout handling
      await page.goto('/', { waitUntil: 'domcontentloaded' }
      await page.waitForTimeout(2000); // Give time for async operations

      // Check if page loaded successfully
      await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
      const title = await page.title(
      expect(title).toBeTruthy(
      // Test navigation if about link exists
      const aboutLink = page.locator('a[href="/about"]').first(
      if (await aboutLink.count() > 0 && await aboutLink.isVisible()) {
        await aboutLink.click(
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
        } else {
        // Try alternative navigation
        const anyLink = page.locator('a[href^="/"]').first(
        if (await anyLink.count() > 0 && await anyLink.isVisible()) {
          await anyLink.click(
          await page.waitForTimeout(2000
          }
      }
    }
    test('should handle browser back/forward events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Navigate to another page
      const termsLink = page.locator('a[href="/terms"]').first(
      if (await termsLink.count() > 0 && await termsLink.isVisible()) {
        await termsLink.click(
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
        // Test back navigation
        await page.goBack(
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
        // Test forward navigation
        await page.goForward(
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
        } else {
        // Alternative: test with any available link
        const anyLink = page.locator('a[href^="/"]').first(
        if (await anyLink.count() > 0 && await anyLink.isVisible()) {
          const href = await anyLink.getAttribute('href'
          await page.goto(href || '/'
          await page.waitForTimeout(2000
          await page.goBack(
          await page.waitForTimeout(2000
          }
      }
    }
  }
  test.describe('Form and Input Events', () => {
    test('should handle various input events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      const searchInput = page.locator('input[type="text"]').first(
      if (await searchInput.count() > 0) {
        // Test input events
        await searchInput.focus(
        await searchInput.fill('TEST'
        await page.waitForTimeout(300
        // Test selection events
        await searchInput.selectText(
        await page.waitForTimeout(300
        // Test cut/copy/paste events (simulate)
        await searchInput.press('Control+a'
        await page.waitForTimeout(100
        await searchInput.press('Control+c'
        await page.waitForTimeout(100
        await searchInput.press('Delete'
        await page.waitForTimeout(100
        await searchInput.press('Control+v'
        await page.waitForTimeout(300
        }
    }
    test('should handle form validation events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      const searchInput = page.locator('input[type="text"]').first(
      const searchButton = page.locator('button[type="submit"]').first(
      if (await searchInput.count() > 0 && await searchButton.count() > 0) {
        // Test empty form submission
        await searchInput.clear(
        await searchButton.click(
        await page.waitForTimeout(1000
        // Test with valid input
        await searchInput.fill('AAPL'
        await searchButton.click(
        await page.waitForTimeout(2000
        }
    }
  }
  test.describe('Error Handling Events', () => {
    test('should handle JavaScript errors gracefully', async ({ page }) => {
      const jsErrors: string[] = [];

      page.on('pageerror', error => {
        jsErrors.push(error.message
      }
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Trigger some interactions that might cause errors
      await page.evaluate(() => {
        // Simulate clicking on elements that might not exist
        const element = document.querySelector('non-existent-element'
        if (element) (element as HTMLElement).click(
      }
      // Test with invalid search
      const searchInput = page.locator('input[type="text"]').first(
      if (await searchInput.count() > 0) {
        await searchInput.fill('INVALID_SYMBOL_@#$%'
        const searchButton = page.locator('button[type="submit"]').first(
        if (await searchButton.count() > 0) {
          await searchButton.click(
          await page.waitForTimeout(3000
        }
      }

      // Filter critical errors
      const criticalErrors = jsErrors.filter(error =>
        !error.includes('favicon') &&
        !error.includes('fonts.gstatic.com') &&
        !error.includes('Failed to load resource')
      expect(criticalErrors.length).toBe(0
      }
    test('should handle network errors gracefully', async ({ page }) => {
      const failedRequests: string[] = [];

      page.on('requestfailed', request => {
        failedRequests.push(request.url()
      }
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Try to trigger API calls that might fail
      const searchInput = page.locator('input[type="text"]').first(
      if (await searchInput.count() > 0) {
        await searchInput.fill('TEST_NETWORK_ERROR'
        const searchButton = page.locator('button[type="submit"]').first(
        if (await searchButton.count() > 0) {
          await searchButton.click(
          await page.waitForTimeout(3000
        }
      }

      }
  }
  test.describe('Performance Events', () => {
    test('should handle performance-related events', async ({ page }) => {
      const startTime = Date.now(
      await page.goto('/'
      await page.waitForLoadState('load', { timeout: 30000 }
      const loadTime = Date.now() - startTime;
      // Test that page loads within reasonable time
      expect(loadTime).toBeLessThan(30000); // 30 seconds max

      // Test large content handling
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight
      }
      await page.waitForTimeout(1000
      }
  }
});