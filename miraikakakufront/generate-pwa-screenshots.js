const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const screenshotsDir = path.join(__dirname, 'public', 'screenshots');

// スクリーンショットディレクトリが存在しない場合は作成
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

// カラーパレット
const colors = {
  primary: '#2196f3',
  background: '#000000',
  secondary: '#111111',
  tertiary: '#1a1a1a',
  card: '#2a2a2a',
  text: '#ffffff',
  textSecondary: '#b0b0b0',
  success: '#10b981',
  danger: '#ef4444'
};

// ヘルパー関数：グラデーション背景を作成
function createGradientBackground(width, height) {
  return Buffer.from(
    `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${colors.background};stop-opacity:1" />
          <stop offset="50%" style="stop-color:${colors.secondary};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${colors.tertiary};stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#bg)" />
    </svg>`
  );
}

// ヘルパー関数：チャートSVGを作成
function createChartSVG(width, height, isPositive = true) {
  const chartColor = isPositive ? colors.success : colors.danger;
  const points = [];
  const baseY = height * 0.7;
  const amplitude = height * 0.3;
  
  for (let i = 0; i <= width; i += 20) {
    const trend = isPositive ? -0.5 : 0.5;
    const y = baseY + Math.sin(i / 100) * amplitude * 0.6 + trend * (i / width) * amplitude;
    points.push(`${i},${Math.max(10, Math.min(height - 10, y))}`);
  }
  
  return `
    <polyline
      points="${points.join(' ')}"
      fill="none"
      stroke="${chartColor}"
      stroke-width="3"
      opacity="0.8"
    />
    <circle cx="${width * 0.8}" cy="${points[points.length - 1].split(',')[1]}" r="5" fill="${chartColor}" />
  `;
}

// スクリーンショット1: デスクトップ - ダッシュボード
async function generateDesktopDashboard() {
  const width = 1280;
  const height = 720;
  
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      ${createGradientBackground(width, height)}
      
      <!-- ヘッダー -->
      <rect x="0" y="0" width="${width}" height="70" fill="${colors.secondary}" opacity="0.9"/>
      <text x="40" y="45" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="${colors.primary}">
        Miraikakaku
      </text>
      <text x="${width - 200}" y="45" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">
        AI株価予測プラットフォーム
      </text>
      
      <!-- サイドバー -->
      <rect x="0" y="70" width="280" height="${height - 70}" fill="${colors.secondary}" opacity="0.7"/>
      <text x="30" y="120" font-family="Arial, sans-serif" font-size="16" fill="${colors.text}">📊 ダッシュボード</text>
      <text x="30" y="160" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">📈 分析</text>
      <text x="30" y="200" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">🎯 ランキング</text>
      <text x="30" y="240" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">📋 ウォッチリスト</text>
      
      <!-- メインコンテンツ -->
      <rect x="300" y="90" width="960" height="610" fill="${colors.background}" opacity="0.3"/>
      
      <!-- チャートカード1 -->
      <rect x="320" y="110" width="280" height="180" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="340" y="140" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">AAPL</text>
      <text x="340" y="165" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="${colors.success}">$225.50</text>
      <text x="340" y="185" font-family="Arial, sans-serif" font-size="14" fill="${colors.success}">+2.45%</text>
      <svg x="340" y="200" width="240" height="80">
        ${createChartSVG(240, 80, true)}
      </svg>
      
      <!-- チャートカード2 -->
      <rect x="620" y="110" width="280" height="180" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="640" y="140" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">GOOGL</text>
      <text x="640" y="165" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="${colors.danger}">$142.30</text>
      <text x="640" y="185" font-family="Arial, sans-serif" font-size="14" fill="${colors.danger}">-1.23%</text>
      <svg x="640" y="200" width="240" height="80">
        ${createChartSVG(240, 80, false)}
      </svg>
      
      <!-- チャートカード3 -->
      <rect x="920" y="110" width="280" height="180" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="940" y="140" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">MSFT</text>
      <text x="940" y="165" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="${colors.success}">$378.90</text>
      <text x="940" y="185" font-family="Arial, sans-serif" font-size="14" fill="${colors.success}">+0.87%</text>
      <svg x="940" y="200" width="240" height="80">
        ${createChartSVG(240, 80, true)}
      </svg>
      
      <!-- 大きなチャート -->
      <rect x="320" y="320" width="880" height="350" rx="12" fill="${colors.card}" opacity="0.6"/>
      <text x="340" y="350" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="${colors.text}">
        AI予測チャート
      </text>
      <text x="340" y="375" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">
        LSTM・Vertex AI による株価予測
      </text>
      <svg x="340" y="390" width="840" height="260">
        ${createChartSVG(840, 260, true)}
        <line x1="560" y1="0" x2="560" y2="260" stroke="${colors.textSecondary}" stroke-width="2" stroke-dasharray="5,5" opacity="0.5"/>
        <text x="570" y="20" font-family="Arial, sans-serif" font-size="12" fill="${colors.textSecondary}">予測開始</text>
      </svg>
    </svg>
  `;
  
  await sharp(Buffer.from(svg))
    .png()
    .toFile(path.join(screenshotsDir, 'screenshot1.png'));
  
  console.log('✅ Desktop dashboard screenshot generated');
}

// スクリーンショット2: デスクトップ - 分析ページ
async function generateDesktopAnalysis() {
  const width = 1280;
  const height = 720;
  
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      ${createGradientBackground(width, height)}
      
      <!-- ヘッダー -->
      <rect x="0" y="0" width="${width}" height="70" fill="${colors.secondary}" opacity="0.9"/>
      <text x="40" y="45" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="${colors.primary}">
        市場分析
      </text>
      
      <!-- メインコンテンツ -->
      <rect x="40" y="90" width="${width - 80}" height="610" fill="${colors.background}" opacity="0.3"/>
      
      <!-- 分析カード群 -->
      <rect x="60" y="110" width="360" height="280" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="80" y="140" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">AAPL</text>
      <text x="80" y="165" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">現在価格: $225.50</text>
      <text x="80" y="185" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">目標価格: $240.00</text>
      <text x="80" y="205" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">P/E比: 28.5</text>
      
      <rect x="80" y="230" width="80" height="30" rx="6" fill="${colors.success}" opacity="0.8"/>
      <text x="110" y="250" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="${colors.text}">BUY</text>
      
      <svg x="80" y="270" width="320" height="100">
        ${createChartSVG(320, 100, true)}
      </svg>
      
      <rect x="440" y="110" width="360" height="280" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="460" y="140" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">GOOGL</text>
      <text x="460" y="165" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">現在価格: $142.30</text>
      <text x="460" y="185" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">目標価格: $155.00</text>
      <text x="460" y="205" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">P/E比: 22.1</text>
      
      <rect x="460" y="230" width="80" height="30" rx="6" fill="${colors.primary}" opacity="0.8"/>
      <text x="490" y="250" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="${colors.text}">HOLD</text>
      
      <svg x="460" y="270" width="320" height="100">
        ${createChartSVG(320, 100, false)}
      </svg>
      
      <rect x="820" y="110" width="360" height="280" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="840" y="140" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">MSFT</text>
      <text x="840" y="165" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">現在価格: $378.90</text>
      <text x="840" y="185" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">目標価格: $395.00</text>
      <text x="840" y="205" font-family="Arial, sans-serif" font-size="14" fill="${colors.textSecondary}">P/E比: 31.2</text>
      
      <rect x="840" y="230" width="80" height="30" rx="6" fill="${colors.success}" opacity="0.8"/>
      <text x="870" y="250" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="${colors.text}">BUY</text>
      
      <svg x="840" y="270" width="320" height="100">
        ${createChartSVG(320, 100, true)}
      </svg>
      
      <!-- 下部の統計情報 -->
      <rect x="60" y="410" width="1160" height="280" rx="12" fill="${colors.card}" opacity="0.6"/>
      <text x="80" y="440" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="${colors.text}">
        AI予測精度
      </text>
      
      <text x="80" y="470" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">LSTM精度: 89.5%</text>
      <rect x="200" y="455" width="200" height="20" rx="10" fill="${colors.secondary}"/>
      <rect x="200" y="455" width="179" height="20" rx="10" fill="${colors.success}"/>
      
      <text x="80" y="510" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">Vertex AI精度: 87.2%</text>
      <rect x="200" y="495" width="200" height="20" rx="10" fill="${colors.secondary}"/>
      <rect x="200" y="495" width="174" height="20" rx="10" fill="${colors.primary}"/>
      
      <text x="80" y="550" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">総合信頼度: 91.3%</text>
      <rect x="200" y="535" width="200" height="20" rx="10" fill="${colors.secondary}"/>
      <rect x="200" y="535" width="183" height="20" rx="10" fill="${colors.success}"/>
    </svg>
  `;
  
  await sharp(Buffer.from(svg))
    .png()
    .toFile(path.join(screenshotsDir, 'screenshot2.png'));
  
  console.log('✅ Desktop analysis screenshot generated');
}

// スクリーンショット3: モバイル - ダッシュボード
async function generateMobileDashboard() {
  const width = 720;
  const height = 1280;
  
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      ${createGradientBackground(width, height)}
      
      <!-- ヘッダー -->
      <rect x="0" y="0" width="${width}" height="100" fill="${colors.secondary}" opacity="0.9"/>
      <text x="40" y="60" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="${colors.primary}">
        Miraikakaku
      </text>
      
      <!-- 検索バー -->
      <rect x="40" y="120" width="${width - 80}" height="60" rx="30" fill="${colors.card}" opacity="0.8"/>
      <text x="70" y="155" font-family="Arial, sans-serif" font-size="18" fill="${colors.textSecondary}">
        🔍 株式コード、銘柄名で検索...
      </text>
      
      <!-- 株価カード1 -->
      <rect x="40" y="200" width="${width - 80}" height="160" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="60" y="240" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="${colors.text}">AAPL</text>
      <text x="60" y="270" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="${colors.success}">$225.50</text>
      <text x="60" y="300" font-family="Arial, sans-serif" font-size="20" fill="${colors.success}">+2.45% (+$5.40)</text>
      <svg x="60" y="320" width="580" height="30">
        ${createChartSVG(580, 30, true)}
      </svg>
      
      <!-- 株価カード2 -->
      <rect x="40" y="380" width="${width - 80}" height="160" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="60" y="420" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="${colors.text}">GOOGL</text>
      <text x="60" y="450" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="${colors.danger}">$142.30</text>
      <text x="60" y="480" font-family="Arial, sans-serif" font-size="20" fill="${colors.danger}">-1.23% (-$1.77)</text>
      <svg x="60" y="500" width="580" height="30">
        ${createChartSVG(580, 30, false)}
      </svg>
      
      <!-- 株価カード3 -->
      <rect x="40" y="560" width="${width - 80}" height="160" rx="12" fill="${colors.card}" opacity="0.8"/>
      <text x="60" y="600" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="${colors.text}">MSFT</text>
      <text x="60" y="630" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="${colors.success}">$378.90</text>
      <text x="60" y="660" font-family="Arial, sans-serif" font-size="20" fill="${colors.success}">+0.87% (+$3.27)</text>
      <svg x="60" y="680" width="580" height="30">
        ${createChartSVG(580, 30, true)}
      </svg>
      
      <!-- AI予測セクション -->
      <rect x="40" y="740" width="${width - 80}" height="320" rx="12" fill="${colors.card}" opacity="0.6"/>
      <text x="60" y="780" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="${colors.text}">
        🤖 AI予測
      </text>
      <text x="60" y="810" font-family="Arial, sans-serif" font-size="18" fill="${colors.textSecondary}">
        機械学習による株価予測
      </text>
      
      <svg x="60" y="830" width="580" height="160">
        ${createChartSVG(580, 160, true)}
        <line x1="290" y1="0" x2="290" y2="160" stroke="${colors.textSecondary}" stroke-width="2" stroke-dasharray="5,5" opacity="0.5"/>
        <text x="300" y="20" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">予測</text>
      </svg>
      
      <text x="60" y="1020" font-family="Arial, sans-serif" font-size="16" fill="${colors.success}">LSTM予測: ↗ +3.2%</text>
      <text x="350" y="1020" font-family="Arial, sans-serif" font-size="16" fill="${colors.primary}">Vertex: ↗ +2.8%</text>
      
      <!-- 下部ナビゲーション -->
      <rect x="0" y="${height - 100}" width="${width}" height="100" fill="${colors.secondary}" opacity="0.9"/>
      <text x="80" y="${height - 60}" font-family="Arial, sans-serif" font-size="16" fill="${colors.primary}">📊</text>
      <text x="200" y="${height - 60}" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">📈</text>
      <text x="320" y="${height - 60}" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">🎯</text>
      <text x="440" y="${height - 60}" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">📋</text>
      <text x="560" y="${height - 60}" font-family="Arial, sans-serif" font-size="16" fill="${colors.textSecondary}">⚙️</text>
    </svg>
  `;
  
  await sharp(Buffer.from(svg))
    .png()
    .toFile(path.join(screenshotsDir, 'screenshot3.png'));
  
  console.log('✅ Mobile dashboard screenshot generated');
}

// メイン関数
async function generateAllScreenshots() {
  try {
    console.log('🎨 PWAスクリーンショット生成開始...');
    
    await generateDesktopDashboard();
    await generateDesktopAnalysis();
    await generateMobileDashboard();
    
    console.log('✅ 全てのPWAスクリーンショットを生成しました！');
    console.log('📁 場所: public/screenshots/');
    console.log('🔗 manifest.jsonで参照されています');
    
  } catch (error) {
    console.error('❌ スクリーンショット生成エラー:', error);
    process.exit(1);
  }
}

// 実行
if (require.main === module) {
  generateAllScreenshots();
}

module.exports = {
  generateAllScreenshots,
  generateDesktopDashboard,
  generateDesktopAnalysis,
  generateMobileDashboard
};