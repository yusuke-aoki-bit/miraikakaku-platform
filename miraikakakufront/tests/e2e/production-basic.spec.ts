import { test, expect } from '@playwright/test';

test.describe('Miraikakaku Production Site - Basic Tests', () => {
  test('Homepage loads and displays basic content', async ({ page }) => {
    // Navigate to production site
    await page.goto('https://www.miraikakaku.com');
    
    // Check page loads successfully
    await expect(page).toHaveURL(/miraikakaku/);
    
    // Check for basic page structure
    const body = page.locator('body');
    await expect(body).toBeVisible();
    
    // Check for any visible content
    const mainContent = page.locator('main, .main, [role="main"], .content').first();
    if (await mainContent.count() > 0) {
      await expect(mainContent).toBeVisible();
    }
    
    console.log('Page title:', await page.title());
    console.log('Page URL:', page.url());
  });

  test('Site responds with correct status', async ({ page }) => {
    const response = await page.goto('https://www.miraikakaku.com');
    expect(response?.status()).toBe(200);
  });

  test('Check for market data presence', async ({ page }) => {
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(5000);
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'production-homepage.png', fullPage: true });
    
    // Check page content
    const pageContent = await page.content();
    console.log('Page content length:', pageContent.length);
    
    // Look for any numbers that could be stock prices or market data
    const hasNumbers = /\d+[\.,]\d+/.test(pageContent);
    console.log('Contains numeric data:', hasNumbers);
    
    // Look for common financial terms
    const hasFinancialTerms = /株|price|market|index|株価|市場/i.test(pageContent);
    console.log('Contains financial terms:', hasFinancialTerms);
  });

  test('Navigation links are accessible', async ({ page }) => {
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(3000);
    
    // Find all navigation links
    const navLinks = await page.locator('a[href^="/"], nav a').all();
    console.log(`Found ${navLinks.length} navigation links`);
    
    // Check first few links
    for (let i = 0; i < Math.min(3, navLinks.length); i++) {
      const link = navLinks[i];
      const href = await link.getAttribute('href');
      const text = await link.textContent();
      console.log(`Link ${i + 1}: "${text}" -> ${href}`);
      
      if (href && href.startsWith('/')) {
        await expect(link).toBeVisible();
      }
    }
  });

  test('API endpoints are being called', async ({ page }) => {
    const apiCalls: string[] = [];
    
    // Monitor network requests
    page.on('request', request => {
      const url = request.url();
      if (url.includes('miraikakaku-api') || url.includes('/api/')) {
        apiCalls.push(url);
        console.log('API call detected:', url);
      }
    });
    
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(10000); // Wait longer for API calls
    
    console.log(`Total API calls made: ${apiCalls.length}`);
    apiCalls.forEach((url, index) => {
      console.log(`API ${index + 1}: ${url}`);
    });
    
    // Expect at least some API calls
    expect(apiCalls.length).toBeGreaterThan(0);
  });
});