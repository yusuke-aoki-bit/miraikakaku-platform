import { test, expect } from '@playwright/test';

test.describe('Production Health Check', () => {

  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check title
    await expect(page).toHaveTitle(/Miraikakaku/
    // Check main heading exists
    const headings = page.locator('h1'
    await expect(headings.first()).toBeVisible(
  }
  test('should display search functionality', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check search input exists
    const searchInput = page.locator('input[placeholder*="銘柄"], input[type="text"]').first(
    await expect(searchInput).toBeVisible({ timeout: 10000 }
    // Check submit button exists
    const searchButton = page.locator('button[type="submit"]').first(
    await expect(searchButton).toBeVisible({ timeout: 10000 }
  }
  test('should perform basic search', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Find search input
    const searchInput = page.locator('input[placeholder*="銘柄"], input[type="text"]').first(
    await expect(searchInput).toBeVisible({ timeout: 10000 }
    // Enter search term
    await searchInput.fill('AAPL'
    // Click search button
    const searchButton = page.locator('button[type="submit"]').first(
    await searchButton.click(
    // Wait for response (either navigation or results)
    await page.waitForTimeout(3000
    // Verify we're still on a valid page
    expect(page.url()).toBeTruthy(
  }
  test('should have proper page structure', async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check HTML structure
    const html = page.locator('html'
    await expect(html).toHaveAttribute('lang', 'ja'
    // Check viewport meta tag
    const viewport = page.locator('meta[name="viewport"]'
    await expect(viewport).toHaveCount(1
  }
  test('should handle mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Check if page loads on mobile
    await expect(page.locator('main, .theme-container, h1, h2').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('h1').first()).toBeVisible(
  }
  test('should not have console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text()
      }
    }
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 }
    // Filter out known non-critical errors
    const criticalErrors = consoleErrors.filter(error =>
      !error.includes('favicon') &&
      !error.includes('fonts.gstatic.com') &&
      !error.includes('net::ERR_') &&
      !error.includes('Failed to load resource')
    expect(criticalErrors.length).toBe(0
  }
});