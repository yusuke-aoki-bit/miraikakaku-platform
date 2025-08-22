#!/usr/bin/env node

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

// アイコンサイズのリスト
const iconSizes = [72, 96, 128, 144, 152, 192, 384, 512];

// SVGテンプレート（シンプルな株価チャートアイコン）
const svgTemplate = (size) => `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2563eb;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="chart" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#34d399;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 背景 -->
  <rect width="${size}" height="${size}" rx="${size * 0.1}" fill="url(#bg)"/>
  
  <!-- チャートアイコン -->
  <g transform="translate(${size * 0.2}, ${size * 0.3})">
    <!-- 上昇トレンドライン -->
    <path d="M 0 ${size * 0.4} 
             L ${size * 0.15} ${size * 0.35} 
             L ${size * 0.3} ${size * 0.25} 
             L ${size * 0.45} ${size * 0.15} 
             L ${size * 0.6} ${size * 0.05}" 
          stroke="url(#chart)" 
          stroke-width="${size * 0.03}" 
          fill="none" 
          stroke-linecap="round" 
          stroke-linejoin="round"/>
    
    <!-- 矢印 -->
    <path d="M ${size * 0.55} ${size * 0.05} 
             L ${size * 0.6} ${size * 0.05} 
             L ${size * 0.6} ${size * 0.1}" 
          stroke="url(#chart)" 
          stroke-width="${size * 0.03}" 
          fill="none" 
          stroke-linecap="round" 
          stroke-linejoin="round"/>
  </g>
  
  <!-- "M"ロゴ -->
  <text x="${size * 0.5}" 
        y="${size * 0.75}" 
        font-family="Arial, sans-serif" 
        font-size="${size * 0.25}" 
        font-weight="bold" 
        fill="white" 
        text-anchor="middle">M</text>
</svg>
`;

async function generateIcons() {
  const outputDir = path.join(__dirname, '..', 'public', 'icons');
  
  // ディレクトリが存在しない場合は作成
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log('Generating PWA icons...');

  for (const size of iconSizes) {
    const svg = svgTemplate(size);
    const outputPath = path.join(outputDir, `icon-${size}x${size}.png`);
    
    try {
      await sharp(Buffer.from(svg))
        .png()
        .toFile(outputPath);
      
      console.log(`✓ Generated ${size}x${size} icon`);
    } catch (error) {
      console.error(`✗ Failed to generate ${size}x${size} icon:`, error);
    }
  }

  // favicon.icoの生成（複数サイズを含む）
  try {
    const svg = svgTemplate(32);
    await sharp(Buffer.from(svg))
      .resize(32, 32)
      .toFile(path.join(__dirname, '..', 'public', 'favicon.ico'));
    console.log('✓ Generated favicon.ico');
  } catch (error) {
    console.error('✗ Failed to generate favicon.ico:', error);
  }

  // Apple Touch Icon
  try {
    const svg = svgTemplate(180);
    await sharp(Buffer.from(svg))
      .png()
      .toFile(path.join(__dirname, '..', 'public', 'apple-touch-icon.png'));
    console.log('✓ Generated apple-touch-icon.png');
  } catch (error) {
    console.error('✗ Failed to generate apple-touch-icon:', error);
  }

  console.log('\nIcon generation complete!');
}

// スクリプトを実行
if (require.main === module) {
  generateIcons().catch(console.error);
}

module.exports = { generateIcons };