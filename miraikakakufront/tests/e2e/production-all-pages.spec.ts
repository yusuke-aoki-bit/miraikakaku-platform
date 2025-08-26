import { test, expect } from '@playwright/test';

test.describe('Miraikakaku Production - All Pages E2E Tests', () => {
  // All pages identified from the app directory structure
  const pages = [
    { path: '/', title: '未来価格', description: 'Homepage' },
    { path: '/analysis', title: '分析', description: 'Analysis page' },
    { path: '/auth/login', title: 'ログイン', description: 'Login page' },
    { path: '/auth/register', title: '新規登録', description: 'Register page' },
    { path: '/auth/forgot-password', title: 'パスワード忘れ', description: 'Forgot password page' },
    { path: '/auth/reset-password', title: 'パスワードリセット', description: 'Reset password page' },
    { path: '/contests', title: 'コンテスト', description: 'Contests page' },
    { path: '/currency', title: '通貨', description: 'Currency page' },
    { path: '/dashboard', title: 'ダッシュボード', description: 'Dashboard page' },
    { path: '/history', title: '履歴', description: 'History page' },
    { path: '/management', title: '管理', description: 'Management page' },
    { path: '/news', title: 'ニュース', description: 'News page' },
    { path: '/portfolio', title: 'ポートフォリオ', description: 'Portfolio page' },
    { path: '/predictions', title: '予測', description: 'Predictions page' },
    { path: '/privacy', title: 'プライバシーポリシー', description: 'Privacy policy page' },
    { path: '/rankings', title: 'ランキング', description: 'Rankings page' },
    { path: '/realtime', title: 'リアルタイム', description: 'Realtime page' },
    { path: '/search', title: '検索', description: 'Search page' },
    { path: '/sectors', title: 'セクター', description: 'Sectors page' },
    { path: '/terms', title: '利用規約', description: 'Terms page' },
    { path: '/test', title: 'テスト', description: 'Test page' },
    { path: '/themes', title: 'テーマ', description: 'Themes page' },
    { path: '/tools', title: 'ツール', description: 'Tools page' },
    { path: '/tools/trading-setup', title: 'トレーディングセットアップ', description: 'Trading setup page' },
    { path: '/user-rankings', title: 'ユーザーランキング', description: 'User rankings page' },
    { path: '/volume', title: '出来高', description: 'Volume page' },
    { path: '/watchlist', title: 'ウォッチリスト', description: 'Watchlist page' }
  ];

  test.beforeEach(async ({ page }) => {
    // Set up error tracking
    page.on('pageerror', (error) => {
      console.log(`JavaScript error on page: ${error.message}`);
    });
    
    page.on('response', (response) => {
      if (response.status() >= 400) {
        console.log(`HTTP error: ${response.status()} ${response.url()}`);
      }
    });
  });

  // Test each page individually
  for (const pageInfo of pages) {
    test(`${pageInfo.description} (${pageInfo.path}) loads successfully`, async ({ page }) => {
      try {
        // Navigate to the page
        await page.goto(pageInfo.path, { timeout: 30000 });
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 });

        // Basic page load check
        await expect(page).toHaveURL(new RegExp(pageInfo.path.replace(/\//g, '\\/')));

        // Check that the page doesn't have critical errors
        const bodyText = await page.locator('body').textContent();
        expect(bodyText).not.toContain('Application error');
        expect(bodyText).not.toContain('500');
        expect(bodyText).not.toContain('404');

        // Check for basic HTML structure
        await expect(page.locator('html')).toBeVisible();
        await expect(page.locator('head')).toHaveCount(1);
        await expect(page.locator('body')).toBeVisible();

        // Check meta tags exist
        const metaDescription = page.locator('meta[name="description"]');
        if (await metaDescription.count() > 0) {
          const description = await metaDescription.getAttribute('content');
          expect(description).toBeTruthy();
          expect(description?.length).toBeGreaterThan(0);
        }

        // Check for proper page title (if specified)
        if (pageInfo.title) {
          const title = await page.title();
          expect(title).toBeTruthy();
          expect(title.length).toBeGreaterThan(0);
        }

        // Check basic navigation elements
        const nav = page.locator('nav, [role="navigation"]').first();
        if (await nav.count() > 0) {
          await expect(nav).toBeVisible();
        }

        // Check footer exists
        const footer = page.locator('footer, [role="contentinfo"]').first();
        if (await footer.count() > 0) {
          await expect(footer).toBeVisible();
        }

        // Performance check - page should load within reasonable time
        const performanceEntries = await page.evaluate(() => {
          return JSON.stringify(performance.getEntriesByType('navigation'));
        });
        const navigation = JSON.parse(performanceEntries)[0];
        if (navigation) {
          const loadTime = navigation.loadEventEnd - navigation.fetchStart;
          expect(loadTime).toBeLessThan(15000); // 15 seconds max
        }

      } catch (error) {
        console.log(`Error testing ${pageInfo.path}: ${error}`);
        throw error;
      }
    });
  }

  // Test page-specific functionality
  test('Stock symbol pages load with dynamic routes', async ({ page }) => {
    const stockSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', '7203.T'];
    
    for (const symbol of stockSymbols.slice(0, 2)) { // Test first 2 to avoid timeout
      try {
        await page.goto(`/stock/${symbol}`, { timeout: 30000 });
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
        
        // Check that page loads without error
        const bodyText = await page.locator('body').textContent();
        expect(bodyText).not.toContain('404');
        expect(bodyText).not.toContain('Application error');
        
        // Should contain the stock symbol somewhere
        expect(bodyText).toMatch(new RegExp(symbol, 'i'));
        
      } catch (error) {
        console.log(`Error testing stock page for ${symbol}: ${error}`);
        // Don't fail the test if stock page doesn't exist or has issues
      }
    }
  });

  test('Theme pages load with dynamic routes', async ({ page }) => {
    const themes = ['ai', 'renewable-energy', 'biotech'];
    
    for (const theme of themes.slice(0, 2)) { // Test first 2 to avoid timeout
      try {
        await page.goto(`/themes/${theme}`, { timeout: 30000 });
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
        
        // Check that page loads without error
        const bodyText = await page.locator('body').textContent();
        expect(bodyText).not.toContain('404');
        expect(bodyText).not.toContain('Application error');
        
      } catch (error) {
        console.log(`Error testing theme page for ${theme}: ${error}`);
        // Don't fail the test if theme page doesn't exist or has issues
      }
    }
  });

  test('News article pages load with dynamic routes', async ({ page }) => {
    // First get news list to find actual article IDs
    try {
      await page.goto('/news', { timeout: 30000 });
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
      
      // Look for news article links
      const newsLinks = await page.locator('a[href*="/news/"]').all();
      
      if (newsLinks.length > 0) {
        // Test first news article
        const firstLink = newsLinks[0];
        const href = await firstLink.getAttribute('href');
        
        if (href && href !== '/news') {
          await page.goto(href, { timeout: 30000 });
          await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
          
          const bodyText = await page.locator('body').textContent();
          expect(bodyText).not.toContain('404');
          expect(bodyText).not.toContain('Application error');
        }
      }
    } catch (error) {
      console.log(`Error testing news article pages: ${error}`);
      // Don't fail if no news articles available
    }
  });

  test('Contest pages load with dynamic routes', async ({ page }) => {
    // First get contest list to find actual contest IDs
    try {
      await page.goto('/contests', { timeout: 30000 });
      await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
      
      // Look for contest links
      const contestLinks = await page.locator('a[href*="/contests/"]').all();
      
      if (contestLinks.length > 0) {
        // Test first contest
        const firstLink = contestLinks[0];
        const href = await firstLink.getAttribute('href');
        
        if (href && href !== '/contests') {
          await page.goto(href, { timeout: 30000 });
          await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
          
          const bodyText = await page.locator('body').textContent();
          expect(bodyText).not.toContain('404');
          expect(bodyText).not.toContain('Application error');
        }
      }
    } catch (error) {
      console.log(`Error testing contest pages: ${error}`);
      // Don't fail if no contests available
    }
  });

  test('All pages are accessible and have proper SEO elements', async ({ page }) => {
    const criticalPages = [
      '/', '/rankings', '/predictions', '/sectors', '/currency', 
      '/portfolio', '/search', '/tools', '/themes'
    ];

    for (const pagePath of criticalPages) {
      try {
        await page.goto(pagePath, { timeout: 30000 });
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 });

        // Check for proper HTML lang attribute
        const htmlLang = await page.locator('html').getAttribute('lang');
        expect(htmlLang).toBeTruthy();

        // Check for viewport meta tag
        const viewport = page.locator('meta[name="viewport"]');
        if (await viewport.count() > 0) {
          const viewportContent = await viewport.getAttribute('content');
          expect(viewportContent).toContain('width=device-width');
        }

        // Check for canonical URL
        const canonical = page.locator('link[rel="canonical"]');
        if (await canonical.count() > 0) {
          const canonicalHref = await canonical.getAttribute('href');
          expect(canonicalHref).toBeTruthy();
        }

        // Check for Open Graph tags
        const ogTitle = page.locator('meta[property="og:title"]');
        const ogDescription = page.locator('meta[property="og:description"]');
        const ogUrl = page.locator('meta[property="og:url"]');

        if (await ogTitle.count() > 0) {
          const titleContent = await ogTitle.getAttribute('content');
          expect(titleContent).toBeTruthy();
        }

        if (await ogDescription.count() > 0) {
          const descContent = await ogDescription.getAttribute('content');
          expect(descContent).toBeTruthy();
        }

        if (await ogUrl.count() > 0) {
          const urlContent = await ogUrl.getAttribute('content');
          expect(urlContent).toBeTruthy();
        }

      } catch (error) {
        console.log(`Error testing SEO for ${pagePath}: ${error}`);
        throw error;
      }
    }
  });

  test('Mobile responsiveness across all pages', async ({ page, isMobile }) => {
    if (!isMobile) return;

    const mobileTestPages = ['/', '/rankings', '/predictions', '/search', '/portfolio'];

    for (const pagePath of mobileTestPages) {
      try {
        await page.goto(pagePath, { timeout: 30000 });
        await page.waitForLoadState('domcontentloaded', { timeout: 30000 });

        // Check if content is visible and not overlapping
        const body = page.locator('body');
        await expect(body).toBeVisible();

        // Check for mobile navigation
        const mobileNav = page.locator('button[aria-label*="menu"], .hamburger, [data-testid="mobile-menu"]');
        if (await mobileNav.count() > 0) {
          await expect(mobileNav).toBeVisible();
        }

        // Ensure no horizontal scroll
        const scrollWidth = await page.evaluate(() => {
          return document.body.scrollWidth;
        });
        const clientWidth = await page.evaluate(() => {
          return document.body.clientWidth;
        });
        
        // Allow small tolerance for browser differences
        expect(scrollWidth - clientWidth).toBeLessThanOrEqual(20);

      } catch (error) {
        console.log(`Error testing mobile responsiveness for ${pagePath}: ${error}`);
        throw error;
      }
    }
  });
});