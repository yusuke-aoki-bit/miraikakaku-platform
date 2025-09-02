const axios = require('axios');

const testFrontendAPI = async () => {
  const API_BASE_URL = 'https://miraikakaku-api-465603676610.us-central1.run.app';
  
  const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    paramsSerializer: (params) => {
      return Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
    },
  });

  console.log('=== Frontend API Client Test ===');
  console.log('Testing with same configuration as React app...');
  console.log('');

  // Test Japanese search mapping
  const companyNameMap = {
    'アップル': 'AAPL',
    'テスラ': 'TSLA',
    'グーグル': 'GOOGL',
    '値上がり率': 'growth-potential'
  };
  
  const testQueries = ['AAPL', 'アップル', 'tesla', 'テスラ', '値上がり率'];
  
  for (const query of testQueries) {
    console.log(`🔍 Search test: "${query}"`);
    
    const lowerQuery = query.toLowerCase().trim();
    const mappedSymbol = companyNameMap[query] || companyNameMap[lowerQuery];
    
    console.log(`   Mapped to: ${mappedSymbol || 'No mapping'}`);
    
    if (mappedSymbol === 'growth-potential') {
      try {
        const response = await api.get('/api/finance/rankings/growth-potential');
        console.log(`   ✅ Growth rankings: ${response.data.length} items`);
        console.log(`      Sample: ${response.data[0].symbol} - ${response.data[0].company_name}`);
      } catch (error) {
        console.log(`   ❌ Error: ${error.message}`);
      }
    } else {
      const searchQuery = mappedSymbol && mappedSymbol !== 'growth-potential' ? mappedSymbol : query;
      const containsJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(query);
      
      if (containsJapanese && !mappedSymbol) {
        console.log('   ⏭️  Japanese query without mapping - skipped');
      } else {
        try {
          const response = await api.get('/api/finance/stocks/search', {
            params: { q: searchQuery, limit: 3 }
          });
          console.log(`   ✅ Search results: ${response.data.length} items`);
          if (response.data.length > 0) {
            console.log(`      Result: ${response.data[0].symbol} - ${response.data[0].shortName}`);
          }
        } catch (error) {
          console.log(`   ❌ Error: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
        }
      }
    }
    console.log('');
  }

  // Test full stock data retrieval
  console.log('📊 Testing full stock data retrieval for AAPL...');
  try {
    const symbol = 'AAPL';
    
    const priceHistoryReq = api.get(`/api/finance/stocks/${symbol}/price`, { params: { days: 730 } });
    const predictionsReq = api.get(`/api/finance/stocks/${symbol}/predictions`, { params: { days: 180 } });
    const historicalPredictionsReq = api.get(`/api/finance/stocks/${symbol}/predictions/history`, { params: { days: 730 } });
    const aiFactorsReq = api.get(`/api/ai/factors/${symbol}`);
    const searchReq = api.get('/api/finance/stocks/search', { params: { q: symbol, limit: 1 } });
    
    const [priceHistory, predictions, historicalPredictions, aiFactors, searchResults] = await Promise.allSettled([
      priceHistoryReq, predictionsReq, historicalPredictionsReq, aiFactorsReq, searchReq
    ]);
    
    console.log(`   Price History: ${priceHistory.status === 'fulfilled' ? `✅ ${priceHistory.value.data.length} records` : `❌ ${priceHistory.reason.response?.data?.detail || priceHistory.reason.message}`}`);
    console.log(`   Predictions: ${predictions.status === 'fulfilled' ? `✅ ${predictions.value.data.length} records` : `❌ ${predictions.reason.response?.data?.detail || predictions.reason.message}`}`);
    console.log(`   Historical Predictions: ${historicalPredictions.status === 'fulfilled' ? `✅ ${historicalPredictions.value.data.length} records` : `❌ ${historicalPredictions.reason.response?.data?.detail || historicalPredictions.reason.message}`}`);
    console.log(`   AI Factors: ${aiFactors.status === 'fulfilled' ? `✅ ${aiFactors.value.data.length} factors` : `❌ ${aiFactors.reason.response?.data?.detail || aiFactors.reason.message}`}`);
    console.log(`   Search Details: ${searchResults.status === 'fulfilled' ? `✅ ${searchResults.value.data.length} results` : `❌ ${searchResults.reason.response?.data?.detail || searchResults.reason.message}`}`);
    
  } catch (error) {
    console.log(`   ❌ Full data test error: ${error.message}`);
  }
};

testFrontendAPI().catch(console.error);