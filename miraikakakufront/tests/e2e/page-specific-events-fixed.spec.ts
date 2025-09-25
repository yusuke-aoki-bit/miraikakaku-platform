import { test, expect, devices } from '@playwright/test';

test.describe('Page-Specific Events E2E Testing (Fixed)', () => {

  test.describe('Stock Details Page Events', () => {
    test('should handle stock symbol search and details page navigation', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Search for a stock symbol
      const searchInput = page.locator('input[type="text"]').first(
      if (await searchInput.count() > 0) {
        await searchInput.fill('AAPL'
        await page.locator('button[type="submit"]').first().click(
        await page.waitForTimeout(3000
        // Check if we navigated to details page or got results
        const currentUrl = page.url(
        // If we're on a details page, test its functionality
        if (currentUrl.includes('/details/') || currentUrl.includes('AAPL')) {
          // Test page-specific events on details page
          await page.waitForTimeout(2000
          // Test back navigation
          if (await page.locator('button').filter({ hasText: /戻る|Back/ }).count() > 0) {
            await page.locator('button').filter({ hasText: /戻る|Back/ }).first().click(
            await page.waitForTimeout(2000
            }
        }
      }
    }
  }
  test.describe('Legal Pages Events', () => {
    const legalPages = [
      { path: '/privacy', name: 'Privacy Policy' }
      { path: '/terms', name: 'Terms of Service' }
      { path: '/about', name: 'About Page' }
      { path: '/contact', name: 'Contact Page' }
      { path: '/disclaimer', name: 'Disclaimer Page' }
    ];

    for (const legalPage of legalPages) {
      test(`should handle ${legalPage.name} page events`, async ({ page }) => {
        // Try to navigate to the page directly
        await page.goto(legalPage.path
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
        // Check if page loads successfully
        const body = page.locator('body'
        await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
        // Test scroll events on content pages
        await page.evaluate(() => window.scrollTo(0, 500)
        await page.waitForTimeout(500
        await page.evaluate(() => window.scrollTo(0, 0)
        await page.waitForTimeout(500
        // Test navigation back to home
        if (await page.locator('a[href="/"]').count() > 0) {
          await page.locator('a[href="/"]').first().click(
          await page.waitForTimeout(2000
        } else if (await page.locator('button').filter({ hasText: /ホーム|Home/ }).count() > 0) {
          await page.locator('button').filter({ hasText: /ホーム|Home/ }).first().click(
          await page.waitForTimeout(2000
        }

        }
    }
  }
  test.describe('Dynamic Content Events', () => {
    test('should handle dynamic loading events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Wait for any dynamic content to load
      await page.waitForTimeout(3000
      // Test interactions with dynamically loaded elements
      const dynamicElements = page.locator('[data-testid*="dynamic"], .loading, .skeleton'
      const count = await dynamicElements.count(
      if (count > 0) {
        // Wait for loading to complete
        await page.waitForTimeout(2000
        // Test interaction with loaded content
        const loadedContent = page.locator('h1, h2, h3, button, a').first(
        if (await loadedContent.count() > 0 && await loadedContent.isVisible()) {
          await loadedContent.hover(
          await page.waitForTimeout(300
        }
      }

      }
    test('should handle async data loading events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Monitor network requests for data loading
      const apiRequests: string[] = [];
      page.on('request', request => {
        if (request.url().includes('api')) {
          apiRequests.push(request.url()
        }
      }
      // Trigger actions that might load data
      const searchInput = page.locator('input[type="text"]').first(
      if (await searchInput.count() > 0) {
        await searchInput.fill('AAPL'
        await page.waitForTimeout(1000
        // Submit to trigger API calls
        await page.locator('button[type="submit"]').first().click(
        await page.waitForTimeout(3000
      }

      }
  }
  test.describe('Error State Events', () => {
    test('should handle 404 error page events', async ({ page }) => {
      // Navigate to a non-existent page
      await page.goto('/non-existent-page'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Check if we get a proper error page or redirect
      const currentUrl = page.url(
      const pageTitle = await page.title(
      // Page should still be functional
      await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
      // Test navigation from error page
      if (await page.locator('a[href="/"]').count() > 0) {
        await page.locator('a[href="/"]').first().click(
        await page.waitForTimeout(2000
        }
    }
    test('should handle search result error states', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test with invalid search queries
      const invalidQueries = ['@#$%^&*()', '12345678901234567890', '', '   '];

      for (const query of invalidQueries) {
        const searchInput = page.locator('input[type="text"]').first(
        if (await searchInput.count() > 0) {
          await searchInput.fill(query
          await page.locator('button[type="submit"]').first().click(
          await page.waitForTimeout(2000
          // Page should still be functional after error
          await expect(page.locator("main, .theme-container, h1, h2").first()).toBeVisible({ timeout: 10000 }
        }
      }

      }
  }
  test.describe('Mobile-Specific Events (Fixed)', () => {
    test('should handle mobile interactions without touch API', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 }
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test click interactions (which work on mobile too)
      const clickTargets = page.locator('button, a, input'
      const count = await clickTargets.count(
      if (count > 0) {
        // Test click events (equivalent to tap on mobile)
        for (let i = 0; i < Math.min(3, count); i++) {
          const element = clickTargets.nth(i
          if (await element.isVisible()) {
            await element.click(
            await page.waitForTimeout(300
          }
        }
      }

      // Test scroll on mobile (swipe simulation)
      await page.evaluate(() => {
        window.scrollTo(0, 300
      }
      await page.waitForTimeout(300
      await page.evaluate(() => {
        window.scrollTo(0, 0
      }
      await page.waitForTimeout(300
      }
    test('should handle mobile menu events', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Look for mobile menu button
      const menuButtons = page.locator('button').filter({
        hasText: /menu|メニュー|☰|≡/
      }).or(page.locator('button[aria-label*="menu"]')
      const menuCount = await menuButtons.count(
      if (menuCount > 0) {
        // Test menu toggle
        await menuButtons.first().click(
        await page.waitForTimeout(500
        // Test menu close (if menu opened)
        await menuButtons.first().click(
        await page.waitForTimeout(500
        } else {
        }
    }
  }
  test.describe('Mobile Touch Events with Proper Context', () => {
    test('should handle touch events on mobile device', async ({ page, context }) => {
      // Set up mobile device context with touch support
      const mobileContext = await context.browser()?.newContext({
        ...devices['iPhone 12']
        hasTouch: true
      }
      const mobilePage = mobileContext ? await mobileContext.newPage() : page;
      await mobilePage.goto('/'
      await mobilePage.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test touch interactions
      const touchTargets = mobilePage.locator('button, a, input'
      const count = await touchTargets.count(
      if (count > 0) {
        // Test tap events
        for (let i = 0; i < Math.min(3, count); i++) {
          const element = touchTargets.nth(i
          if (await element.isVisible()) {
            await element.tap(
            await mobilePage.waitForTimeout(300
          }
        }
      }

      // Test touch screen tap if context supports it
      if (mobileContext) {
        await mobilePage.touchscreen.tap(200, 300
        await mobilePage.waitForTimeout(300
      }

      // Cleanup mobile context if created
      if (mobileContext) {
        await mobileContext.close(
      }
    }
  }
  test.describe('Accessibility Events', () => {
    test('should handle keyboard navigation events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test Tab navigation
      await page.keyboard.press('Tab'
      await page.waitForTimeout(200
      await page.keyboard.press('Tab'
      await page.waitForTimeout(200
      await page.keyboard.press('Tab'
      await page.waitForTimeout(200
      // Test Shift+Tab navigation
      await page.keyboard.press('Shift+Tab'
      await page.waitForTimeout(200
      // Test Enter key activation
      await page.keyboard.press('Enter'
      await page.waitForTimeout(1000
      }
    test('should handle screen reader friendly events', async ({ page }) => {
      await page.goto('/'
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
      // Test focus management
      const focusableElements = page.locator('button, input, a, [tabindex]'
      const count = await focusableElements.count(
      if (count > 0) {
        // Test focus events
        for (let i = 0; i < Math.min(3, count); i++) {
          const element = focusableElements.nth(i
          if (await element.isVisible()) {
            await element.focus(
            await page.waitForTimeout(200
            // Check if element has proper ARIA attributes
            const ariaLabel = await element.getAttribute('aria-label'
            const ariaDescribedBy = await element.getAttribute('aria-describedby'
            const role = await element.getAttribute('role'
            if (ariaLabel || ariaDescribedBy || role) {
              }
          }
        }
      }

      }
  }
});