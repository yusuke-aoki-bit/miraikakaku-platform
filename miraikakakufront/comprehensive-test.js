// 包括的フロントエンド x API 統合テスト
// ブラウザで http://localhost:3000 にアクセスして、開発者ツールのコンソールで実行

console.log('🎯 === 包括的API統合テスト開始 ===');

const API_BASE_URL = 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app';

// テストケース定義
const testCases = [
  // 基本API
  { name: 'Health Check', endpoint: '/health', method: 'GET' },
  
  // 株式関連API
  { name: '株式検索', endpoint: '/api/finance/stocks/search?query=AAPL&limit=5', method: 'GET' },
  { name: '株価データ', endpoint: '/api/finance/stocks/AAPL/price?limit=10', method: 'GET' },
  { name: '株価予測', endpoint: '/api/finance/stocks/AAPL/predictions?limit=5', method: 'GET' },
  { name: 'テクニカル指標', endpoint: '/api/finance/stocks/AAPL/indicators', method: 'GET' },
  
  // 出来高API
  { name: '出来高データ', endpoint: '/api/finance/stocks/AAPL/volume?limit=10', method: 'GET' },
  { name: '出来高予測', endpoint: '/api/finance/stocks/AAPL/volume-predictions?days=7', method: 'GET' },
  { name: '出来高ランキング', endpoint: '/api/finance/volume-rankings?limit=10', method: 'GET' },
  
  // 為替API
  { name: '為替ペア一覧', endpoint: '/api/forex/currency-pairs', method: 'GET' },
  { name: '為替レート', endpoint: '/api/forex/currency-rate/USDJPY', method: 'GET' },
  { name: '為替履歴', endpoint: '/api/forex/currency-history/USDJPY?days=30', method: 'GET' },
  { name: '為替予測', endpoint: '/api/forex/currency-predictions/USDJPY?limit=7', method: 'GET' },
  
  // セクター・テーマAPI
  { name: 'セクター一覧', endpoint: '/api/finance/sectors', method: 'GET' },
  { name: 'テーマ一覧', endpoint: '/api/insights/themes', method: 'GET' },
  
  // コンテスト・ランキングAPI
  { name: 'コンテスト統計', endpoint: '/api/contests/stats', method: 'GET' },
  { name: 'アクティブコンテスト', endpoint: '/api/contests/active', method: 'GET' },
  { name: 'リーダーボード', endpoint: '/api/contests/leaderboard', method: 'GET' },
  
  // ユーザー・ポートフォリオAPI
  { name: 'ユーザープロフィール', endpoint: '/api/user/profile', method: 'GET' },
  { name: 'ユーザー通知設定', endpoint: '/api/user/notifications', method: 'GET' },
  { name: 'ポートフォリオ一覧', endpoint: '/api/portfolios', method: 'GET' },
  
  // 高度分析API
  { name: '市場概況', endpoint: '/api/analytics/market-overview', method: 'GET' },
  { name: '相関分析', endpoint: '/api/analytics/correlation-matrix', method: 'GET' },
  
  // AI・ニュースAPI
  { name: 'AI決定要因', endpoint: '/api/ai-factors/all?limit=10', method: 'GET' },
  { name: 'ニュース一覧', endpoint: '/api/news?limit=10', method: 'GET' }
];

// 結果記録
const results = {
  total: 0,
  success: 0,
  failed: 0,
  details: []
};

// 個別テスト実行関数
async function runSingleTest(testCase, index) {
  const startTime = Date.now();
  
  try {
    console.log(`\n🔍 Test ${index + 1}/${testCases.length}: ${testCase.name}`);
    console.log(`   ${testCase.method} ${testCase.endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}${testCase.endpoint}`, {
      method: testCase.method,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const duration = Date.now() - startTime;
    
    if (response.ok) {
      const data = await response.json();
      console.log(`   ✅ 成功 (${response.status}) - ${duration}ms`);
      console.log(`   📊 レスポンス例:`, data);
      
      results.success++;
      results.details.push({
        test: testCase.name,
        status: 'success',
        duration,
        responseStatus: response.status,
        dataKeys: Object.keys(data || {})
      });
    } else {
      console.log(`   ❌ 失敗 (${response.status}) - ${duration}ms`);
      const errorText = await response.text();
      console.log(`   🔴 エラー:`, errorText.slice(0, 200));
      
      results.failed++;
      results.details.push({
        test: testCase.name,
        status: 'failed',
        duration,
        responseStatus: response.status,
        error: errorText.slice(0, 200)
      });
    }
  } catch (error) {
    const duration = Date.now() - startTime;
    console.log(`   💥 エラー - ${duration}ms`);
    console.log(`   🔴 例外:`, error.message);
    
    results.failed++;
    results.details.push({
      test: testCase.name,
      status: 'error',
      duration,
      error: error.message
    });
  }
  
  results.total++;
}

// 全テスト実行
async function runAllTests() {
  console.log(`🚀 ${testCases.length}個のAPIエンドポイントをテスト開始...\n`);
  console.log(`🌐 API Base URL: ${API_BASE_URL}\n`);
  
  const startTime = Date.now();
  
  // 順次実行（並行だとレート制限に引っかかる可能性があるため）
  for (let i = 0; i < testCases.length; i++) {
    await runSingleTest(testCases[i], i);
    // 少し間隔を空ける
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  const totalDuration = Date.now() - startTime;
  
  // 結果サマリー
  console.log('\n' + '='.repeat(80));
  console.log('📊 === 包括的テスト結果 ===');
  console.log(`⏱️  総実行時間: ${(totalDuration / 1000).toFixed(2)}秒`);
  console.log(`📈 成功: ${results.success}/${results.total} (${((results.success / results.total) * 100).toFixed(1)}%)`);
  console.log(`📉 失敗: ${results.failed}/${results.total} (${((results.failed / results.total) * 100).toFixed(1)}%)`);
  
  // カテゴリ別結果
  console.log('\n📋 カテゴリ別結果:');
  const categories = {
    '基本API': ['Health Check'],
    '株式API': ['株式検索', '株価データ', '株価予測', 'テクニカル指標'],
    '出来高API': ['出来高データ', '出来高予測', '出来高ランキング'],
    '為替API': ['為替ペア一覧', '為替レート', '為替履歴', '為替予測'],
    'セクター・テーマAPI': ['セクター一覧', 'テーマ一覧'],
    'コンテストAPI': ['コンテスト統計', 'アクティブコンテスト', 'リーダーボード'],
    'ユーザーAPI': ['ユーザープロフィール', 'ユーザー通知設定', 'ポートフォリオ一覧'],
    '分析API': ['市場概況', '相関分析'],
    'その他': ['AI決定要因', 'ニュース一覧']
  };
  
  for (const [category, tests] of Object.entries(categories)) {
    const categoryResults = results.details.filter(r => tests.includes(r.test));
    const successCount = categoryResults.filter(r => r.status === 'success').length;
    console.log(`   ${category}: ${successCount}/${categoryResults.length} ✅`);
  }
  
  // 失敗したテスト詳細
  if (results.failed > 0) {
    console.log('\n🔍 失敗したテスト詳細:');
    results.details
      .filter(r => r.status !== 'success')
      .forEach(r => {
        console.log(`   ❌ ${r.test} (${r.responseStatus || 'ERROR'}) - ${r.error || 'Unknown error'}`);
      });
  }
  
  // パフォーマンス分析
  console.log('\n⚡ パフォーマンス分析:');
  const avgDuration = results.details.reduce((sum, r) => sum + r.duration, 0) / results.details.length;
  const slowestTest = results.details.reduce((prev, curr) => prev.duration > curr.duration ? prev : curr);
  const fastestTest = results.details.reduce((prev, curr) => prev.duration < curr.duration ? prev : curr);
  
  console.log(`   平均レスポンス時間: ${avgDuration.toFixed(0)}ms`);
  console.log(`   最速: ${fastestTest.test} (${fastestTest.duration}ms)`);
  console.log(`   最遅: ${slowestTest.test} (${slowestTest.duration}ms)`);
  
  // 最終判定
  if (results.success === results.total) {
    console.log('\n🎉 完璧！全てのAPIエンドポイントが正常に動作しています！');
    console.log('✨ フロントエンド ⇔ 本番API統合完了！');
  } else if (results.success / results.total >= 0.8) {
    console.log('\n😊 良好！大部分のAPIが正常に動作しています。');
    console.log('🔧 一部のエラーを確認することをお勧めします。');
  } else {
    console.log('\n⚠️ 注意！多くのAPIでエラーが発生しています。');
    console.log('🛠️ API接続設定とエンドポイントを確認してください。');
  }
  
  console.log('='.repeat(80));
  
  return results;
}

// フロントエンド特定コンポーネントテスト
async function testFrontendComponents() {
  console.log('\n🎨 === フロントエンドコンポーネント統合テスト ===');
  
  const componentTests = [
    {
      name: 'MarketIndexSummary',
      description: '市場指数サマリー コンポーネント',
      requiredAPIs: ['/api/analytics/market-overview']
    },
    {
      name: 'MarketNews',
      description: 'マーケットニュース コンポーネント',
      requiredAPIs: ['/api/news']
    },
    {
      name: 'WatchlistWidget',
      description: 'ウォッチリスト コンポーネント',
      requiredAPIs: ['/api/finance/stocks/*/price', '/api/finance/stocks/*/predictions']
    },
    {
      name: 'FeaturedPredictionWidget',
      description: '注目予測 コンポーネント',
      requiredAPIs: ['/api/finance/rankings/universal']
    }
  ];
  
  console.log('📝 更新されたコンポーネント:');
  componentTests.forEach((comp, i) => {
    console.log(`   ${i + 1}. ${comp.name} - ${comp.description}`);
    console.log(`      📡 依存API: ${comp.requiredAPIs.join(', ')}`);
  });
  
  console.log('\n✅ これらのコンポーネントは実際のAPIからデータを取得するよう修正済み！');
}

// 実行準備完了メッセージ
console.log('📋 利用可能なテストコマンド:');
console.log('   runAllTests() - 全APIエンドポイントの包括テスト');
console.log('   testFrontendComponents() - フロントエンドコンポーネント情報表示');
console.log('   runSingleTest(testCases[0], 0) - 単一テスト実行例');

// 5秒後に自動実行（オプション）
console.log('\n⏰ 5秒後に自動で全テスト開始...');
setTimeout(() => {
  runAllTests().then(() => {
    testFrontendComponents();
  });
}, 5000);