// WebSocketテスト用スクリプト
const WebSocket = require('ws');

const wsUrl = 'ws://localhost:8001/ws';

console.log(`WebSocket接続テスト: ${wsUrl}`);

const ws = new WebSocket(wsUrl);

ws.on('open', function open() {
  console.log('✅ WebSocket接続成功');
});

ws.on('message', function message(data) {
  console.log('📥 受信メッセージ:', data.toString());
});

ws.on('error', function error(err) {
  console.log('❌ WebSocketエラー:', err.message);
});

ws.on('close', function close() {
  console.log('🔌 WebSocket接続終了');
});

// 10秒後に接続を終了
setTimeout(() => {
  ws.close();
  process.exit(0);
}, 10000);