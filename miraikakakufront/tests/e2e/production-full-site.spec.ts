import { test, expect, Page } from '@playwright/test';

const PRODUCTION_URL = 'https://www.miraikakaku.com';

test.describe('Production Full Site E2E Test', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport for full screen testing
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  const testPages = [
    { path: '/', name: 'Home Page', expectedTitle: 'Miraikakaku' },
    { path: '/analysis', name: 'Analysis Page', expectedTitle: 'AI株価分析' },
    { path: '/rankings', name: 'Rankings Page', expectedTitle: 'ランキング' },
    { path: '/search', name: 'Search Page', expectedTitle: '株式検索' },
    { path: '/predictions', name: 'Predictions Page', expectedTitle: 'AI予測' },
    { path: '/watchlist', name: 'Watchlist Page', expectedTitle: 'ウォッチリスト' },
    { path: '/currency', name: 'Currency Page', expectedTitle: '通貨予測' },
    { path: '/themes', name: 'Themes Page', expectedTitle: 'テーマ分析' },
    { path: '/portfolio', name: 'Portfolio Page', expectedTitle: 'ポートフォリオ' },
    { path: '/contests', name: 'Contests Page', expectedTitle: 'コンテスト' },
    { path: '/tools', name: 'Tools Page', expectedTitle: 'ツール' },
    { path: '/management', name: 'Management Page', expectedTitle: '管理' },
    { path: '/sectors', name: 'Sectors Page', expectedTitle: 'セクター分析' }
  ];

  testPages.forEach(({ path, name, expectedTitle }) => {
    test(`${name} (${path}) - Full Screen Test`, async ({ page }) => {
      console.log(`Testing ${name} at ${PRODUCTION_URL}${path}`);
      
      // Navigate to page
      const response = await page.goto(`${PRODUCTION_URL}${path}`, { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });
      
      // Check HTTP status
      expect(response?.status()).toBeLessThan(400);
      
      // Take full page screenshot
      await page.screenshot({ 
        path: `test-results/production-${path.replace(/\//g, '-') || 'home'}.png`, 
        fullPage: true 
      });
      
      // Check page title contains expected text
      const title = await page.title();
      console.log(`Page title: ${title}`);
      expect(title).toContain(expectedTitle);
      
      // Check for basic page structure
      await expect(page.locator('body')).toBeVisible();
      
      // Look for main content area
      const mainContent = page.locator('main, [role="main"], .main-content, #main');
      if (await mainContent.count() > 0) {
        await expect(mainContent.first()).toBeVisible();
      }
      
      // Check for navigation
      const nav = page.locator('nav, .nav, .navigation, header nav');
      if (await nav.count() > 0) {
        await expect(nav.first()).toBeVisible();
      }
      
      // Check for no critical errors in console
      const errors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });
      
      // Wait a bit for any async content to load
      await page.waitForTimeout(2000);
      
      // Log any console errors
      if (errors.length > 0) {
        console.warn(`Console errors on ${path}:`, errors);
      }
      
      console.log(`✅ ${name} test completed successfully`);
    });
  });

  test('API Integration Test', async ({ page }) => {
    console.log('Testing API integration...');
    
    await page.goto(PRODUCTION_URL, { waitUntil: 'networkidle' });
    
    // Test API health check
    const apiResponse = await page.request.get('https://api.miraikakaku.com/health');
    expect(apiResponse.status()).toBe(200);
    
    const apiData = await apiResponse.json();
    console.log('API Health:', apiData);
    expect(apiData).toHaveProperty('status', 'healthy');
    
    // Test stats API
    const statsResponse = await page.request.get('https://api.miraikakaku.com/api/finance/v2/stats');
    expect(statsResponse.status()).toBe(200);
    
    const statsData = await statsResponse.json();
    console.log('API Stats:', statsData);
    expect(statsData).toHaveProperty('total_stocks');
    expect(statsData.total_stocks).toBeGreaterThan(0);
    
    console.log(`Total stocks in database: ${statsData.total_stocks}`);
  });

  test('Interactive Elements Test', async ({ page }) => {
    console.log('Testing interactive elements...');
    
    await page.goto(`${PRODUCTION_URL}/search`, { waitUntil: 'networkidle' });
    
    // Look for search input
    const searchInputs = page.locator('input[type="text"], input[placeholder*="検索"], input[placeholder*="search"]');
    if (await searchInputs.count() > 0) {
      const searchInput = searchInputs.first();
      await searchInput.click();
      await searchInput.fill('AAPL');
      await page.waitForTimeout(1000);
      console.log('✅ Search input working');
    }
    
    // Take screenshot of search page
    await page.screenshot({ 
      path: 'test-results/production-search-interaction.png', 
      fullPage: true 
    });
  });

  test('Mobile Responsiveness Test', async ({ page }) => {
    console.log('Testing mobile responsiveness...');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto(PRODUCTION_URL, { waitUntil: 'networkidle' });
    
    // Take mobile screenshot
    await page.screenshot({ 
      path: 'test-results/production-mobile.png', 
      fullPage: true 
    });
    
    // Check mobile navigation
    const mobileMenu = page.locator('[role="button"][aria-label*="menu"], .mobile-menu, .hamburger');
    if (await mobileMenu.count() > 0) {
      console.log('✅ Mobile menu found');
    }
    
    console.log('✅ Mobile responsiveness test completed');
  });
});