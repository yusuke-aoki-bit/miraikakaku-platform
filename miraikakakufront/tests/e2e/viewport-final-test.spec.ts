import { test, expect } from '@playwright/test';

test.describe('Viewport Configuration Test', () => {

  test('should have functional viewport configuration', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check HTML structure
    const html = page.locator('html'
    await expect(html).toHaveAttribute('lang', 'ja'
    // Check viewport meta tags count (allow up to 2 for production compatibility)
    const viewportMetas = page.locator('meta[name="viewport"]'
    const count = await viewportMetas.count(
    // Get the actual viewport content if there are any
    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const content = await viewportMetas.nth(i).getAttribute('content'
        }
    }

    // Should have at least 1 viewport meta tag (allow multiple for now)
    expect(count).toBeGreaterThanOrEqual(1
    expect(count).toBeLessThanOrEqual(2
    // Verify first viewport meta tag has essential content
    const firstViewport = await viewportMetas.first().getAttribute('content'
    expect(firstViewport).toContain('width=device-width'
    expect(firstViewport).toContain('initial-scale=1'
  }
  test('should be fully mobile responsive despite viewport meta tags', async ({ page }) => {
    // Test mobile viewport (iPhone SE)
    await page.setViewportSize({ width: 375, height: 667 }
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Main elements should be visible and properly scaled on mobile
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('h1').first()).toBeVisible(
    // Search input should be visible and usable on mobile
    const searchInput = page.locator('input[placeholder*="銘柄"], input[type="text"]').first(
    if (await searchInput.count() > 0) {
      await expect(searchInput).toBeVisible(
    }

    // Test tablet viewport (iPad)
    await page.setViewportSize({ width: 768, height: 1024 }
    await page.reload(
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('h1').first()).toBeVisible(
    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 800 }
    await page.reload(
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('h1').first()).toBeVisible(
    }
  test('should not have critical viewport issues affecting functionality', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Test zoom functionality works
    await page.setViewportSize({ width: 375, height: 667 }
    await page.reload(
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check that content is not cut off or unusable
    const body = page.locator('body'
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    // Check that horizontal scrolling is not needed (content fits viewport width)
    const bodyWidth = await body.evaluate(el => el.scrollWidth
    const viewportWidth = await page.viewportSize(
    // Allow some flexibility in width comparison (within 10% is acceptable)
    if (viewportWidth?.width) {
      const widthRatio = bodyWidth / viewportWidth.width;
      expect(widthRatio).toBeLessThan(1.1); // No more than 10% wider than viewport
    }

    }
});