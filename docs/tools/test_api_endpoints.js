const baseUrl = 'https://miraikakaku-api-465603676610.us-central1.run.app';

const endpoints = [
  { path: '/', method: 'GET', description: 'Root' },
  { path: '/health', method: 'GET', description: 'Health Check' },
  { path: '/api/finance/stocks/search?q=AAPL', method: 'GET', description: 'Stock Search' },
  { path: '/api/finance/stocks/AAPL/price', method: 'GET', description: 'Stock Price' },
  { path: '/api/finance/stocks/AAPL/predictions', method: 'GET', description: 'Stock Predictions' },
  { path: '/api/finance/stocks/AAPL/indicators', method: 'GET', description: 'Stock Indicators' },
  { path: '/api/finance/rankings/universal', method: 'GET', description: 'Universal Rankings' },
  { path: '/api/finance/stocks/AAPL/volume', method: 'GET', description: 'Stock Volume' },
  { path: '/api/finance/stocks/AAPL/volume-predictions', method: 'GET', description: 'Volume Predictions' },
  { path: '/api/finance/volume-rankings', method: 'GET', description: 'Volume Rankings' },
  { path: '/api/finance/sectors', method: 'GET', description: 'Sectors' },
  { path: '/api/insights/themes', method: 'GET', description: 'Themes' },
  { path: '/api/forex/currency-pairs', method: 'GET', description: 'Currency Pairs' },
  { path: '/api/forex/currency-rate/USD-JPY', method: 'GET', description: 'Currency Rate' },
  { path: '/api/contests/stats', method: 'GET', description: 'Contest Stats' },
  { path: '/api/contests/active', method: 'GET', description: 'Active Contests' },
  { path: '/api/news', method: 'GET', description: 'News' },
  { path: '/api/user/profile', method: 'GET', description: 'User Profile' },
  { path: '/api/user/watchlist', method: 'GET', description: 'User Watchlist' },
  { path: '/api/portfolios', method: 'GET', description: 'Portfolios' },
  { path: '/api/analytics/market-overview', method: 'GET', description: 'Market Overview' },
];

async function testEndpoints() {
  console.log('API Endpoint Test - ' + new Date().toISOString());
  console.log('Base URL:', baseUrl);
  console.log('=' .repeat(60));
  
  for (const endpoint of endpoints) {
    const url = baseUrl + endpoint.path;
    try {
      const start = Date.now();
      const response = await fetch(url, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      const elapsed = Date.now() - start;
      
      const status = response.status;
      const statusText = response.statusText;
      
      let result = '✓';
      if (status >= 400) {
        result = '✗';
      } else if (status >= 300) {
        result = '→';
      }
      
      console.log(`${result} [${status}] ${endpoint.description.padEnd(20)} - ${elapsed}ms`);
      
      if (status === 200 && endpoint.path === '/health') {
        const data = await response.json();
        console.log('  Health:', JSON.stringify(data));
      }
    } catch (error) {
      console.log(`✗ [ERR] ${endpoint.description.padEnd(20)} - ${error.message}`);
    }
  }
  
  console.log('=' .repeat(60));
  console.log('Test completed');
}

testEndpoints().catch(console.error);