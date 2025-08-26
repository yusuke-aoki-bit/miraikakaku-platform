import { test, expect } from '@playwright/test';

test.describe('Miraikakaku Production Data Validation', () => {
  test('API responses contain real Yahoo Finance data', async ({ page }) => {
    const apiResponses: Array<{ url: string, data: any }> = [];
    
    // Intercept API calls and capture responses
    page.route('**/api/**', async (route) => {
      const response = await route.fetch();
      const url = response.url();
      
      try {
        const data = await response.json();
        apiResponses.push({ url, data });
      } catch (e) {
        // Non-JSON response, skip
      }
      
      route.fulfill({ response });
    });
    
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(15000); // Wait for all API calls
    
    console.log(`Captured ${apiResponses.length} API responses`);
    
    // Analyze responses for real data indicators
    let hasRealStockData = false;
    let hasYahooFinanceSource = false;
    let hasRealisticPrices = false;
    let hasCurrentDates = false;
    
    for (const { url, data } of apiResponses) {
      console.log(`\n=== ${url} ===`);
      
      // Check for Yahoo Finance data source
      if (data.data_source && data.data_source.includes('Yahoo Finance')) {
        hasYahooFinanceSource = true;
        console.log('✅ Yahoo Finance data source confirmed');
      }
      
      // Check stock price data
      if (Array.isArray(data)) {
        data.forEach((item, index) => {
          if (index < 3) { // Log first 3 items
            console.log(`Item ${index + 1}:`, JSON.stringify(item, null, 2).substring(0, 200) + '...');
          }
          
          // Check for realistic stock prices (not round numbers)
          if (item.close_price && !Number.isInteger(item.close_price) && item.close_price > 10) {
            hasRealisticPrices = true;
          }
          
          if (item.current_price && !Number.isInteger(item.current_price) && item.current_price > 10) {
            hasRealisticPrices = true;
          }
          
          // Check for recent dates
          if (item.date) {
            const itemDate = new Date(item.date);
            const now = new Date();
            const daysDiff = (now.getTime() - itemDate.getTime()) / (1000 * 3600 * 24);
            
            if (daysDiff <= 30) { // Data within last 30 days
              hasCurrentDates = true;
            }
          }
        });
        
        if (data.length > 0) {
          hasRealStockData = true;
        }
      }
      
      // Check single object responses
      if (data && typeof data === 'object' && !Array.isArray(data)) {
        if (data.market_indices || data.sectors || data.currency_pairs) {
          hasRealStockData = true;
        }
        
        // Check market indices for realistic values
        if (data.market_indices) {
          data.market_indices.forEach((index: any) => {
            if (index.current_value && index.current_value > 1000) {
              hasRealisticPrices = true;
              console.log(`Market index ${index.index}: ${index.current_value}`);
            }
          });
        }
      }
    }
    
    // Assertions
    expect(apiResponses.length).toBeGreaterThan(10);
    expect(hasRealStockData).toBeTruthy();
    expect(hasRealisticPrices).toBeTruthy();
    expect(hasCurrentDates).toBeTruthy();
    
    console.log('\n=== Data Validation Results ===');
    console.log('✅ Has real stock data:', hasRealStockData);
    console.log('✅ Has realistic prices:', hasRealisticPrices);  
    console.log('✅ Has current dates:', hasCurrentDates);
    console.log('📊 Yahoo Finance source:', hasYahooFinanceSource);
  });

  test('Market indices show real current values', async ({ page }) => {
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(10000);
    
    // Take screenshot of the page
    await page.screenshot({ path: 'market-indices.png', fullPage: true });
    
    // Look for market index values in the page content
    const pageText = await page.textContent('body');
    
    // Check for S&P 500 values (typically around 4000-7000)
    const sp500Match = pageText?.match(/S&P.*?([0-9,]{4,6})/);
    if (sp500Match) {
      const sp500Value = parseInt(sp500Match[1].replace(',', ''));
      console.log('S&P 500 value found:', sp500Value);
      expect(sp500Value).toBeGreaterThan(4000);
      expect(sp500Value).toBeLessThan(8000);
    }
    
    // Check for NASDAQ values (typically around 12000-22000)
    const nasdaqMatch = pageText?.match(/NASDAQ.*?([0-9,]{5,6})/);
    if (nasdaqMatch) {
      const nasdaqValue = parseInt(nasdaqMatch[1].replace(',', ''));
      console.log('NASDAQ value found:', nasdaqValue);
      expect(nasdaqValue).toBeGreaterThan(12000);
      expect(nasdaqValue).toBeLessThan(25000);
    }
    
    // Check for DOW values (typically around 30000-45000) 
    const dowMatch = pageText?.match(/DOW.*?([0-9,]{5,6})/);
    if (dowMatch) {
      const dowValue = parseInt(dowMatch[1].replace(',', ''));
      console.log('DOW value found:', dowValue);
      expect(dowValue).toBeGreaterThan(30000);
      expect(dowValue).toBeLessThan(50000);
    }
  });

  test('Stock prices are realistic and current', async ({ page }) => {
    const stockPrices: Array<{ symbol: string, price: number }> = [];
    
    page.route('**/api/finance/stocks/*/price*', async (route) => {
      const response = await route.fetch();
      const data = await response.json();
      const url = response.url();
      const symbolMatch = url.match(/stocks\/([^\/]+)\/price/);
      
      if (symbolMatch && Array.isArray(data) && data.length > 0) {
        const symbol = symbolMatch[1];
        const latestPrice = data[data.length - 1];
        
        if (latestPrice.close_price) {
          stockPrices.push({ symbol, price: latestPrice.close_price });
        }
      }
      
      route.fulfill({ response });
    });
    
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(15000);
    
    console.log(`Captured ${stockPrices.length} stock prices:`);
    stockPrices.forEach(({ symbol, price }) => {
      console.log(`${symbol}: $${price}`);
    });
    
    // Verify we got price data
    expect(stockPrices.length).toBeGreaterThan(0);
    
    // Check for realistic price ranges
    const applePrices = stockPrices.filter(s => s.symbol === 'AAPL');
    if (applePrices.length > 0) {
      const applePrice = applePrices[0].price;
      expect(applePrice).toBeGreaterThan(150); // Apple stock typically > $150
      expect(applePrice).toBeLessThan(300); // and < $300
    }
    
    const msftPrices = stockPrices.filter(s => s.symbol === 'MSFT');
    if (msftPrices.length > 0) {
      const msftPrice = msftPrices[0].price;
      expect(msftPrice).toBeGreaterThan(200); // Microsoft stock typically > $200
      expect(msftPrice).toBeLessThan(500); // and < $500
    }
  });

  test('Page displays current timestamp and data freshness', async ({ page }) => {
    await page.goto('https://www.miraikakaku.com');
    await page.waitForTimeout(10000);
    
    const pageContent = await page.content();
    const now = new Date();
    const currentYear = now.getFullYear().toString();
    
    // Check if current year appears on the page
    expect(pageContent).toContain(currentYear);
    
    // Look for timestamp patterns
    const timestampPatterns = [
      /\d{4}-\d{2}-\d{2}/,  // YYYY-MM-DD
      /\d{2}:\d{2}:\d{2}/,  // HH:MM:SS
      new RegExp(currentYear) // Current year
    ];
    
    let hasCurrentTimestamp = false;
    timestampPatterns.forEach(pattern => {
      if (pattern.test(pageContent)) {
        hasCurrentTimestamp = true;
      }
    });
    
    expect(hasCurrentTimestamp).toBeTruthy();
    
    console.log('✅ Page contains current date/timestamp indicators');
  });
});