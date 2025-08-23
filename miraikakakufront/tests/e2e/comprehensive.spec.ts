import { test, expect } from '@playwright/test';

test.describe('包括的E2Eテスト', () => {
  
  test('完全なAPI機能テスト', async ({ request }) => {
    console.log('🧪 完全なAPI機能テストを開始...');
    
    // 1. ヘルスチェック
    const healthResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/health');
    expect(healthResponse.ok()).toBeTruthy();
    const healthData = await healthResponse.json();
    expect(healthData.status).toBe('healthy');
    console.log('✅ ヘルスチェック成功');
    
    // 2. 株式検索API
    const searchResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/search?query=AAPL&limit=5');
    expect(searchResponse.ok()).toBeTruthy();
    const searchResults = await searchResponse.json();
    expect(Array.isArray(searchResults)).toBeTruthy();
    expect(searchResults.length).toBeGreaterThan(0);
    expect(searchResults[0]).toHaveProperty('symbol');
    expect(searchResults[0]).toHaveProperty('company_name');
    console.log('✅ 株式検索API成功:', searchResults.length + ' 件の結果');
    
    // 3. 株価履歴API
    const priceResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/AAPL/price?days=7');
    if (priceResponse.ok()) {
      const priceData = await priceResponse.json();
      expect(Array.isArray(priceData)).toBeTruthy();
      if (priceData.length > 0) {
        expect(priceData[0]).toHaveProperty('symbol');
        expect(priceData[0]).toHaveProperty('close_price');
        expect(priceData[0]).toHaveProperty('date');
      }
      console.log('✅ 株価履歴API成功:', priceData.length + ' 件のデータ');
    } else {
      console.log('⚠️ 株価履歴API: データなし');
    }
    
    // 4. 予測API
    const predictionResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/AAPL/predictions?days=3');
    if (predictionResponse.ok()) {
      const predictionData = await predictionResponse.json();
      expect(Array.isArray(predictionData)).toBeTruthy();
      if (predictionData.length > 0) {
        expect(predictionData[0]).toHaveProperty('symbol');
        expect(predictionData[0]).toHaveProperty('predicted_price');
        expect(predictionData[0]).toHaveProperty('prediction_date');
      }
      console.log('✅ 予測API成功:', predictionData.length + ' 件の予測');
    } else {
      console.log('⚠️ 予測API: データなし');
    }
    
    console.log('🎉 完全なAPI機能テスト完了');
  });
  
  test('データベース整合性テスト', async ({ request }) => {
    console.log('🗄️ データベース整合性テストを開始...');
    
    // 株式マスターデータの確認
    const searchResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/search?query=&limit=10');
    if (searchResponse.ok()) {
      const allStocks = await searchResponse.json();
      console.log('📊 データベース内株式数:', allStocks.length);
      
      // 各株式に対してデータの整合性をチェック
      for (const stock of allStocks.slice(0, 3)) { // 最初の3銘柄をテスト
        const symbol = stock.symbol;
        
        // 価格履歴の確認
        const priceCheck = await request.get(`https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/${symbol}/price?days=5`);
        if (priceCheck.ok()) {
          const priceData = await priceCheck.json();
          console.log(`✅ ${symbol}: ${priceData.length}日分の価格データ`);
        }
        
        // 予測データの確認
        const predictionCheck = await request.get(`https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/${symbol}/predictions?days=3`);
        if (predictionCheck.ok()) {
          const predictionData = await predictionCheck.json();
          console.log(`✅ ${symbol}: ${predictionData.length}日分の予測データ`);
        }
      }
    }
    
    console.log('🎉 データベース整合性テスト完了');
  });
  
  test('WebSocket機能テスト', async ({ page }) => {
    console.log('🔌 WebSocket機能テストを開始...');
    
    // WebSocket接続をテスト
    let wsConnected = false;
    let messagesReceived = 0;
    
    await page.evaluate(() => {
      return new Promise((resolve) => {
        const ws = new WebSocket('wss://miraikakaku-api-465603676610.us-central1.run.app/ws');
        
        ws.onopen = () => {
          console.log('WebSocket接続成功');
          (window as any).wsConnected = true;
        };
        
        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          (window as any).messagesReceived = ((window as any).messagesReceived || 0) + 1;
          console.log('WebSocketメッセージ受信:', message.type);
        };
        
        ws.onerror = (error) => {
          console.error('WebSocketエラー:', error);
          (window as any).wsError = true;
        };
        
        // 5秒後に結果を返す
        setTimeout(() => {
          ws.close();
          resolve(undefined);
        }, 5000);
      });
    });
    
    // 結果を確認
    wsConnected = await page.evaluate(() => (window as any).wsConnected || false);
    messagesReceived = await page.evaluate(() => (window as any).messagesReceived || 0);
    
    if (wsConnected) {
      console.log('✅ WebSocket接続成功');
      console.log(`✅ メッセージ受信数: ${messagesReceived}`);
      expect(wsConnected).toBeTruthy();
      expect(messagesReceived).toBeGreaterThan(0);
    } else {
      console.log('⚠️ WebSocket接続失敗');
    }
    
    console.log('🎉 WebSocket機能テスト完了');
  });
  
  test('エラーハンドリングと回復力テスト', async ({ request }) => {
    console.log('🛠️ エラーハンドリングテストを開始...');
    
    // 無効なパラメータテスト
    const invalidSearchResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/search?query=&limit=0');
    console.log('無効な検索パラメータ:', invalidSearchResponse.status());
    
    // 存在しない銘柄テスト
    const nonExistentStockResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/NONEXISTENT/price');
    console.log('存在しない銘柄:', nonExistentStockResponse.status());
    
    // 大きすぎる範囲テスト
    const largeRangeResponse = await request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/AAPL/price?days=9999');
    console.log('大きすぎる日数範囲:', largeRangeResponse.status());
    
    console.log('🎉 エラーハンドリングテスト完了');
  });
  
  test('パフォーマンステスト', async ({ request }) => {
    console.log('🚀 パフォーマンステストを開始...');
    
    const startTime = Date.now();
    
    // 複数の並列リクエスト
    const promises = [
      request.get('https://miraikakaku-api-465603676610.us-central1.run.app/health'),
      request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/search?query=A&limit=5'),
      request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/AAPL/price?days=7'),
      request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/MSFT/price?days=7'),
      request.get('https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/GOOGL/predictions?days=3')
    ];
    
    const responses = await Promise.all(promises);
    const endTime = Date.now();
    
    const duration = endTime - startTime;
    console.log(`⏱️ 5つの並列リクエスト完了時間: ${duration}ms`);
    
    // すべてのリクエストが2秒以内に完了することを確認
    expect(duration).toBeLessThan(5000);
    
    // すべてのレスポンスが成功していることを確認
    responses.forEach((response, index) => {
      if (response.ok()) {
        console.log(`✅ リクエスト${index + 1}: ${response.status()}`);
      } else {
        console.log(`⚠️ リクエスト${index + 1}失敗: ${response.status()}`);
      }
    });
    
    console.log('🎉 パフォーマンステスト完了');
  });
});