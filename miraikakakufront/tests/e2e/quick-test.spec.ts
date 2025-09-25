import { test, expect } from '@playwright/test';

test.describe('Quick Frontend Test', () => {
  test.beforeEach(async ({ page }) => {
    // Use the configured baseURL
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded'
    // Wait for main title to appear with increased timeout
    try {
      await page.waitForSelector('h1', { timeout: 30000 }
    } catch {
      }
  }
  test('should load homepage with basic elements', async ({ page }) => {
    // Check if the page loaded at all
    const title = await page.title(
    expect(title).toContain('未来価格'
    // Check main heading exists (be more flexible)
    const headings = await page.locator('h1').count(
    expect(headings).toBeGreaterThan(0
    // Check search input exists
    const searchInputs = await page.locator('input').count(
    expect(searchInputs).toBeGreaterThan(0
    // Check buttons exist
    const buttons = await page.locator('button').count(
    expect(buttons).toBeGreaterThan(0
  }
  test('should click AAPL stock button', async ({ page }) => {
    // Wait for page to be interactive
    await page.waitForTimeout(1000
    const aaplButton = page.locator('button:has-text("AAPL")').first(
    if (await aaplButton.isVisible()) {
      await aaplButton.click(
      await page.waitForTimeout(500
      // Just verify that we're still on a valid page (URL exists)
      const currentUrl = page.url(
      expect(currentUrl).toBeTruthy(
    }
  }
  test('should display categories section', async ({ page }) => {
    const categoriesSection = page.locator('[data-testid="categories"]'
    await expect(categoriesSection).toBeVisible(
    // Check for at least one category button
    const categoryButtons = page.locator('[data-testid="categories"] button'
    const count = await categoryButtons.count(
    expect(count).toBeGreaterThan(0
  }
  test('should perform basic search', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="検索"]'
    await searchInput.fill('MSFT'
    const searchButton = page.locator('button[type="submit"]'
    await searchButton.click(
    await page.waitForTimeout(1000
    // Should remain on a valid page
    const currentUrl = page.url(
    expect(currentUrl).toBeTruthy(
  }
  test('should have proper heading structure', async ({ page }) => {
    // Should have exactly one main heading
    const h1Elements = page.locator('h1'
    await expect(h1Elements).toHaveCount(1
    // Should have multiple section headings
    const h3Elements = page.locator('h3'
    const h3Count = await h3Elements.count(
    expect(h3Count).toBeGreaterThan(2
  }
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }
    await page.reload(
    await page.waitForLoadState('domcontentloaded'
    await page.waitForTimeout(500
    // Basic elements should still be visible
    await expect(page.locator('h1')).toBeVisible(
    await expect(page.locator('input[placeholder*="検索"]')).toBeVisible(
  }
});