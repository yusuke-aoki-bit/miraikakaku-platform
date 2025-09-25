import { test, expect } from '@playwright/test';

test.describe('Viewport Meta Tag Fix Verification', () => {

  test('should have single viewport meta tag', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check HTML structure
    const html = page.locator('html'
    await expect(html).toHaveAttribute('lang', 'ja'
    // Check viewport meta tags count
    const viewportMetas = page.locator('meta[name="viewport"]'
    const count = await viewportMetas.count(
    // Get the actual viewport content if there are any
    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const content = await viewportMetas.nth(i).getAttribute('content'
        }
    }

    // Should have exactly 1 viewport meta tag
    expect(count).toBe(1
  }
  test('should have proper viewport configuration', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check that the viewport meta tag exists and has proper content
    const viewportMeta = page.locator('meta[name="viewport"]'
    await expect(viewportMeta).toHaveCount(1
    const content = await viewportMeta.getAttribute('content'
    // Should contain essential viewport settings
    expect(content).toContain('width=device-width'
    expect(content).toContain('initial-scale=1'
  }
  test('should be mobile responsive', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Main elements should be visible on mobile
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('h1').first()).toBeVisible(
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 }
    await page.reload(
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('h1').first()).toBeVisible(
    }
});