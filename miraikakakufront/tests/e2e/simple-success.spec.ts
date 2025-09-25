import { test, expect } from '@playwright/test';

test.describe('Simple Success Tests', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded'
  }
  test('should display homepage title', async ({ page }) => {
    await expect(page).toHaveTitle(/未来価格/
  }
  test('should display main heading', async ({ page }) => {
    const mainHeading = page.locator('h1'
    await expect(mainHeading).toContainText('未来価格'
  }
  test('should display search input', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="検索"]'
    await expect(searchInput).toBeVisible(
  }
  test('should display search button', async ({ page }) => {
    const searchButton = page.locator('button[type="submit"]'
    await expect(searchButton).toBeVisible(
  }
  test('should display AI feature sections', async ({ page }) => {
    // Scroll to ensure content is loaded
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)
    await page.waitForTimeout(1000
    await expect(page.locator('text=AI予測').first()).toBeVisible({ timeout: 10000 }
    await expect(page.locator('text=ビジュアル分析').first()).toBeVisible({ timeout: 5000 }
    await expect(page.locator('text=判断要因').first()).toBeVisible({ timeout: 5000 }
  }
  test('should have interactive elements', async ({ page }) => {
    const buttons = await page.locator('button').count(
    expect(buttons).toBeGreaterThan(0
  }
  test('should display header', async ({ page }) => {
    await expect(page.locator('header, .header, [data-testid="header"]').first()).toBeVisible(
  }
  test('should display footer', async ({ page }) => {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)
    await page.waitForTimeout(500
    await expect(page.locator('footer').first()).toBeVisible(
  }
  test('should have theme classes', async ({ page }) => {
    const themeElements = await page.locator('.theme-page, .theme-container, .theme-card').count(
    expect(themeElements).toBeGreaterThan(0
  }
  test('should load within reasonable time', async ({ page }) => {
    const startTime = Date.now(
    await page.goto('/'
    await page.waitForLoadState('domcontentloaded'
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(10000); // 10 seconds
  }
});