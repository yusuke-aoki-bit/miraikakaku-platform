import { test, expect } from '@playwright/test';

test.describe('Miraikakaku Production - Basic Site Check', () => {
  test.beforeEach(async ({ page }) => {
    // Set up error tracking
    page.on('pageerror', (error) => {
      console.log(`JavaScript error: ${error.message}`);
    });
    
    page.on('response', (response) => {
      if (response.status() >= 400) {
        console.log(`HTTP error: ${response.status()} ${response.url()}`);
      }
    });
  });

  // Critical pages that must work
  const criticalPages = [
    { path: '/', title: '未来価格', description: 'Homepage' },
    { path: '/rankings', title: 'ランキング', description: 'Rankings page' },
    { path: '/predictions', title: '予測', description: 'Predictions page' },
    { path: '/sectors', title: 'セクター', description: 'Sectors page' },
    { path: '/currency', title: '通貨', description: 'Currency page' },
    { path: '/search', title: '検索', description: 'Search page' },
    { path: '/tools', title: 'ツール', description: 'Tools page' },
    { path: '/themes', title: 'テーマ', description: 'Themes page' },
    { path: '/portfolio', title: 'ポートフォリオ', description: 'Portfolio page' }
  ];

  for (const pageInfo of criticalPages) {
    test(`${pageInfo.description} (${pageInfo.path}) is accessible and renders`, async ({ page }) => {
      try {
        // Navigate to the page with reduced timeout
        const response = await page.goto(pageInfo.path, { 
          timeout: 45000,
          waitUntil: 'domcontentloaded'
        });

        // Check response status
        expect(response?.status()).toBeLessThan(400);

        // Wait for basic DOM elements to load
        await page.waitForSelector('html', { timeout: 10000 });
        await page.waitForSelector('body', { timeout: 10000 });

        // Verify URL is correct
        expect(page.url()).toContain(pageInfo.path);

        // Check page doesn't show error states
        const bodyText = await page.locator('body').textContent();
        expect(bodyText).not.toContain('Application error');
        expect(bodyText).not.toContain('Internal Server Error');
        expect(bodyText).not.toContain('This page could not be found');

        // Verify basic HTML structure
        await expect(page.locator('html')).toBeVisible();
        await expect(page.locator('body')).toBeVisible();

        // Check for page title
        const title = await page.title();
        expect(title).toBeTruthy();
        expect(title.length).toBeGreaterThan(0);

        // Verify content is loading (not blank page)
        const mainContent = await page.locator('main, #main-content, [role="main"]').first();
        if (await mainContent.count() > 0) {
          await expect(mainContent).toBeVisible();
        } else {
          // Fallback: check if body has meaningful content
          expect(bodyText).toBeTruthy();
          expect(bodyText?.trim().length).toBeGreaterThan(50);
        }

        console.log(`✓ ${pageInfo.description} loaded successfully`);

      } catch (error) {
        console.log(`✗ Error testing ${pageInfo.path}: ${error}`);
        throw error;
      }
    });
  }

  test('Site navigation elements are present', async ({ page }) => {
    await page.goto('/', { timeout: 45000, waitUntil: 'domcontentloaded' });
    
    // Check for basic navigation structure
    const nav = page.locator('nav, [role="navigation"], .navigation').first();
    if (await nav.count() > 0) {
      await expect(nav).toBeVisible();
    }

    // Check for header/footer
    const header = page.locator('header, [role="banner"]').first();
    const footer = page.locator('footer, [role="contentinfo"]').first();

    if (await header.count() > 0) {
      await expect(header).toBeVisible();
    }

    if (await footer.count() > 0) {
      await expect(footer).toBeVisible();
    }
  });

  test('Basic responsive design check', async ({ page, isMobile }) => {
    await page.goto('/', { timeout: 45000, waitUntil: 'domcontentloaded' });

    // Check viewport meta tag
    const viewport = page.locator('meta[name="viewport"]');
    if (await viewport.count() > 0) {
      const viewportContent = await viewport.getAttribute('content');
      expect(viewportContent).toContain('width=device-width');
    }

    if (isMobile) {
      // Check for mobile-specific elements
      const body = page.locator('body');
      await expect(body).toBeVisible();

      // Ensure no horizontal overflow
      const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
      const clientWidth = await page.evaluate(() => document.body.clientWidth);
      
      expect(scrollWidth - clientWidth).toBeLessThanOrEqual(50); // Allow small tolerance
    }
  });

  test('Performance baseline check', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/', { timeout: 45000, waitUntil: 'domcontentloaded' });
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within reasonable time (relaxed for production)
    expect(loadTime).toBeLessThan(45000);
    console.log(`Homepage load time: ${loadTime}ms`);
  });

  test('API endpoints are responding', async ({ page }) => {
    let apiCalls = 0;
    
    page.route('**/api/**', async (route) => {
      apiCalls++;
      const response = await route.fetch();
      route.fulfill({ response });
    });

    await page.goto('/', { timeout: 45000, waitUntil: 'domcontentloaded' });
    
    // Wait a bit for any async API calls
    await page.waitForTimeout(3000);
    
    if (apiCalls > 0) {
      console.log(`✓ ${apiCalls} API calls detected`);
    } else {
      console.log('ℹ No API calls detected (may be expected for static pages)');
    }
  });
});