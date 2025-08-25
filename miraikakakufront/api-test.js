// フロントエンド統合テスト用スクリプト
// ブラウザで http://localhost:3000/test にアクセスして、開発者ツールのコンソールで実行

// 基本設定
const API_BASE_URL = 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app';

console.log('=== Miraikakaku フロントエンド x API 統合テスト ===');
console.log(`API Base URL: ${API_BASE_URL}`);

// テスト1: Health Check
async function testHealthCheck() {
  console.log('\n🔍 Test 1: Health Check');
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    console.log('✅ Health Check成功:', data);
    return data;
  } catch (error) {
    console.error('❌ Health Checkエラー:', error);
    return null;
  }
}

// テスト2: 株式検索
async function testStockSearch() {
  console.log('\n🔍 Test 2: 株式検索 (AAPL)');
  try {
    const response = await fetch(`${API_BASE_URL}/api/finance/stocks/search?query=AAPL&limit=5`);
    const data = await response.json();
    console.log('✅ 株式検索成功:', data);
    return data;
  } catch (error) {
    console.error('❌ 株式検索エラー:', error);
    return null;
  }
}

// テスト3: 株価取得
async function testStockPrice() {
  console.log('\n🔍 Test 3: 株価データ (AAPL)');
  try {
    const response = await fetch(`${API_BASE_URL}/api/finance/stocks/AAPL/price?limit=5`);
    const data = await response.json();
    console.log('✅ 株価データ取得成功:', data);
    return data;
  } catch (error) {
    console.error('❌ 株価データエラー:', error);
    return null;
  }
}

// テスト4: 予測データ
async function testStockPredictions() {
  console.log('\n🔍 Test 4: 予測データ (AAPL)');
  try {
    const response = await fetch(`${API_BASE_URL}/api/finance/stocks/AAPL/predictions?limit=3`);
    const data = await response.json();
    console.log('✅ 予測データ取得成功:', data);
    return data;
  } catch (error) {
    console.error('❌ 予測データエラー:', error);
    return null;
  }
}

// テスト5: 為替データ
async function testForexData() {
  console.log('\n🔍 Test 5: 為替ペア一覧');
  try {
    const response = await fetch(`${API_BASE_URL}/api/forex/currency-pairs`);
    const data = await response.json();
    console.log('✅ 為替データ取得成功:', data);
    return data;
  } catch (error) {
    console.error('❌ 為替データエラー:', error);
    return null;
  }
}

// テスト6: ユーザープロフィール
async function testUserProfile() {
  console.log('\n🔍 Test 6: ユーザープロフィール');
  try {
    const response = await fetch(`${API_BASE_URL}/api/user/profile`);
    const data = await response.json();
    console.log('✅ ユーザープロフィール取得成功:', data);
    return data;
  } catch (error) {
    console.error('❌ ユーザープロフィールエラー:', error);
    return null;
  }
}

// 全テスト実行
async function runAllTests() {
  console.log('🚀 全テスト開始...\n');
  
  const results = {
    health: await testHealthCheck(),
    search: await testStockSearch(),
    price: await testStockPrice(),
    predictions: await testStockPredictions(),
    forex: await testForexData(),
    profile: await testUserProfile()
  };
  
  console.log('\n📊 === テスト結果サマリー ===');
  let successCount = 0;
  let totalTests = 0;
  
  for (const [testName, result] of Object.entries(results)) {
    totalTests++;
    if (result) {
      successCount++;
      console.log(`✅ ${testName}: 成功`);
    } else {
      console.log(`❌ ${testName}: 失敗`);
    }
  }
  
  console.log(`\n🎯 結果: ${successCount}/${totalTests} テスト成功`);
  
  if (successCount === totalTests) {
    console.log('🎉 全テスト成功！フロントエンド ⇔ API統合完了！');
  } else {
    console.log('⚠️ 一部テストが失敗しています。');
  }
  
  return results;
}

// 自動実行
console.log('👍 テストスクリプト読み込み完了');
console.log('📝 実行方法:');
console.log('  - runAllTests() - 全テスト実行');
console.log('  - testHealthCheck() - ヘルスチェックのみ');
console.log('  - testStockSearch() - 株式検索のみ');
console.log('等々...');

// 5秒後に自動実行（オプション）
setTimeout(() => {
  console.log('\n⏰ 5秒経過、自動テスト開始...');
  runAllTests();
}, 5000);