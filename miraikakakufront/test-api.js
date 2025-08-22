// API接続テスト用スクリプト
const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:8000';

async function testAPI() {
  console.log('=== API接続テスト開始 ===');
  
  // 1. ヘルスチェック
  try {
    const response = await fetch(`${BASE_URL}/`);
    const data = await response.json();
    console.log('✅ ヘルスチェック:', data.message);
  } catch (error) {
    console.log('❌ ヘルスチェック失敗:', error.message);
    return;
  }
  
  // 2. 検索API
  try {
    const response = await fetch(`${BASE_URL}/api/finance/stocks/search?query=AAPL&limit=3`);
    const data = await response.json();
    console.log('✅ 検索API:', data.length, '件の結果');
    console.log('  - サンプル:', data[0]);
  } catch (error) {
    console.log('❌ 検索API失敗:', error.message);
  }
  
  // 3. 株価データAPI
  try {
    const response = await fetch(`${BASE_URL}/api/finance/stocks/AAPL/price?days=7`);
    const data = await response.json();
    console.log('✅ 株価データAPI:', data.length, '日分のデータ');
    console.log('  - 最新価格:', data[0]);
  } catch (error) {
    console.log('❌ 株価データAPI失敗:', error.message);
  }
  
  // 4. 予測API
  try {
    const response = await fetch(`${BASE_URL}/api/finance/stocks/AAPL/predictions?days=7`);
    const data = await response.json();
    console.log('✅ 予測API:', data.length, '日分の予測');
    console.log('  - 明日の予測:', data[0]);
  } catch (error) {
    console.log('❌ 予測API失敗:', error.message);
  }
  
  console.log('\n=== API接続テスト完了 ===');
}

testAPI();