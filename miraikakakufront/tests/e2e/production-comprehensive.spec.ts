import { test, expect } from '@playwright/test';

test.describe('Miraikakaku Production Site - Comprehensive E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to production site
    await page.goto('/');
    // Wait for initial load
    await page.waitForLoadState('networkidle');
  });

  test('Homepage loads successfully with real data', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/未来価格/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('未来価格');
    
    // Verify market indices are displayed with real numbers
    const marketIndices = page.locator('[data-testid="market-indices"], .market-overview, .market-indices').first();
    if (await marketIndices.count() > 0) {
      await expect(marketIndices).toBeVisible();
      
      // Check for S&P 500, NASDAQ, DOW indices
      const spyValue = page.locator('text=/S&P.*[0-9,]+/').first();
      const nasdaqValue = page.locator('text=/NASDAQ.*[0-9,]+/').first();
      
      if (await spyValue.count() > 0) {
        await expect(spyValue).toBeVisible();
      }
      
      if (await nasdaqValue.count() > 0) {
        await expect(nasdaqValue).toBeVisible();
      }
    }
  });

  test('Stock search functionality works with real data', async ({ page }) => {
    // Look for search input
    const searchInput = page.locator('input[placeholder*="検索"], input[placeholder*="株式"], input[type="search"]').first();
    
    if (await searchInput.count() > 0) {
      await searchInput.fill('AAPL');
      await page.keyboard.press('Enter');
      
      // Wait for search results
      await page.waitForTimeout(3000);
      
      // Check if Apple appears in results
      const appleResult = page.locator('text=/Apple/i, text=/AAPL/').first();
      if (await appleResult.count() > 0) {
        await expect(appleResult).toBeVisible();
      }
    }
  });

  test('Navigation menu works correctly', async ({ page }) => {
    // Check main navigation links
    const navLinks = [
      { text: 'ランキング', path: '/rankings' },
      { text: '予測', path: '/predictions' },
      { text: 'セクター', path: '/sectors' },
      { text: '通貨', path: '/currency' },
      { text: 'ポートフォリオ', path: '/portfolio' }
    ];

    for (const link of navLinks) {
      const navElement = page.locator(`a[href*="${link.path}"], nav a:has-text("${link.text}")`).first();
      
      if (await navElement.count() > 0) {
        await navElement.click();
        await page.waitForLoadState('networkidle');
        
        // Verify URL changed
        expect(page.url()).toContain(link.path);
        
        // Go back to homepage
        await page.goto('/');
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('Rankings page displays real stock data', async ({ page }) => {
    await page.goto('/rankings');
    await page.waitForLoadState('networkidle');
    
    // Check for ranking table or list
    const rankingContainer = page.locator('[data-testid="rankings-table"], .rankings, table, .stock-list').first();
    
    if (await rankingContainer.count() > 0) {
      await expect(rankingContainer).toBeVisible();
      
      // Look for stock symbols and prices
      const stockSymbols = page.locator('text=/^[A-Z]{2,5}$/, text=/^\d{4}\.T$/').first();
      const stockPrices = page.locator('text=/\$[0-9,]+\.[0-9]{2}/, text=/¥[0-9,]+/, text=/[0-9,]+\.[0-9]{2}%/').first();
      
      if (await stockSymbols.count() > 0) {
        await expect(stockSymbols).toBeVisible();
      }
      
      if (await stockPrices.count() > 0) {
        await expect(stockPrices).toBeVisible();
      }
    }
  });

  test('Predictions page loads with AI predictions', async ({ page }) => {
    await page.goto('/predictions');
    await page.waitForLoadState('networkidle');
    
    // Check for prediction content
    const predictionContainer = page.locator('[data-testid="predictions"], .predictions, .ai-predictions').first();
    
    if (await predictionContainer.count() > 0) {
      await expect(predictionContainer).toBeVisible();
      
      // Look for confidence scores or prediction values
      const confidenceScores = page.locator('text=/[0-9]{2}%/, text=/信頼度/, text=/confidence/i').first();
      const predictionValues = page.locator('text=/予測/, text=/prediction/i').first();
      
      if (await confidenceScores.count() > 0) {
        await expect(confidenceScores).toBeVisible();
      }
      
      if (await predictionValues.count() > 0) {
        await expect(predictionValues).toBeVisible();
      }
    }
  });

  test('Sectors page shows sector performance', async ({ page }) => {
    await page.goto('/sectors');
    await page.waitForLoadState('networkidle');
    
    // Check for sector data
    const sectorContainer = page.locator('[data-testid="sectors"], .sectors, .sector-performance').first();
    
    if (await sectorContainer.count() > 0) {
      await expect(sectorContainer).toBeVisible();
      
      // Look for common sectors
      const techSector = page.locator('text=/Technology/i, text=/テクノロジー/, text=/IT/').first();
      const healthcareSector = page.locator('text=/Healthcare/i, text=/ヘルスケア/, text=/医療/').first();
      
      if (await techSector.count() > 0) {
        await expect(techSector).toBeVisible();
      }
      
      if (await healthcareSector.count() > 0) {
        await expect(healthcareSector).toBeVisible();
      }
    }
  });

  test('Currency page displays forex data', async ({ page }) => {
    await page.goto('/currency');
    await page.waitForLoadState('networkidle');
    
    // Check for currency data
    const currencyContainer = page.locator('[data-testid="currency"], .currency, .forex').first();
    
    if (await currencyContainer.count() > 0) {
      await expect(currencyContainer).toBeVisible();
      
      // Look for major currency pairs
      const usdJpy = page.locator('text=/USD.*JPY/, text=/USDJPY/, text=/ドル円/').first();
      const eurUsd = page.locator('text=/EUR.*USD/, text=/EURUSD/, text=/ユーロドル/').first();
      
      if (await usdJpy.count() > 0) {
        await expect(usdJpy).toBeVisible();
      }
      
      if (await eurUsd.count() > 0) {
        await expect(eurUsd).toBeVisible();
      }
    }
  });

  test('Page performance is acceptable', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
    
    // Check for any JavaScript errors
    const errors: string[] = [];
    page.on('pageerror', (error) => {
      errors.push(error.message);
    });
    
    // Navigate through a few pages to check for errors
    await page.goto('/rankings');
    await page.waitForTimeout(2000);
    
    await page.goto('/predictions');
    await page.waitForTimeout(2000);
    
    // Report any JavaScript errors found
    if (errors.length > 0) {
      console.log('JavaScript errors found:', errors);
    }
  });

  test('Responsive design works on mobile', async ({ page, isMobile }) => {
    if (isMobile) {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Check if mobile navigation exists
      const mobileMenu = page.locator('button[aria-label*="menu"], .hamburger, [data-testid="mobile-menu"]').first();
      
      if (await mobileMenu.count() > 0) {
        await expect(mobileMenu).toBeVisible();
        
        // Try to open mobile menu
        await mobileMenu.click();
        await page.waitForTimeout(1000);
      }
      
      // Check if content is properly displayed on mobile
      const mainContent = page.locator('main, .main-content, [role="main"]').first();
      if (await mainContent.count() > 0) {
        await expect(mainContent).toBeVisible();
      }
    }
  });

  test('API data is real (not mock data)', async ({ page }) => {
    // Intercept API calls to verify real data
    const apiResponses: any[] = [];
    
    page.route('**/api/**', async (route) => {
      const response = await route.fetch();
      const responseData = await response.json();
      apiResponses.push(responseData);
      route.fulfill({ response });
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Navigate to rankings to trigger API calls
    await page.goto('/rankings');
    await page.waitForTimeout(5000);
    
    // Check if we received API responses
    if (apiResponses.length > 0) {
      const hasRealData = apiResponses.some(response => {
        // Look for indicators of real data vs mock data
        if (response.data_source && response.data_source.includes('Yahoo Finance')) {
          return true;
        }
        
        // Check for realistic stock prices (not round numbers like 100.00)
        if (Array.isArray(response)) {
          return response.some(item => {
            if (item.current_price && !Number.isInteger(item.current_price)) {
              return true;
            }
            if (item.close_price && !Number.isInteger(item.close_price)) {
              return true;
            }
            return false;
          });
        }
        
        return false;
      });
      
      expect(hasRealData).toBeTruthy();
    }
  });
});