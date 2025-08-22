# CSS スタイルガイド

## 概要
Miraikakakuプロジェクトにおけるスタイリングの統一ガイドライン。一貫性のあるデザインと保守性の向上を目的とする。

## 設計原則

### 1. デザインシステム統合
- CSS変数（カスタムプロパティ）を使用した統一されたデザイントークン
- `src/config/design-tokens.ts` との一致性を保つ
- 色、間隔、タイポグラフィの統一

### 2. Tailwind CSS優先
- Utilityファーストアプローチ
- カスタムCSSは最小限に抑制
- コンポーネント固有のスタイルのみカスタマイズ

### 3. レスポンシブデザイン
- モバイルファースト設計
- ブレークポイント: `sm`, `md`, `lg`, `xl`, `2xl`
- 柔軟なレイアウトシステム

## CSS変数（カスタムプロパティ）

### 色パレット
```css
/* プライマリカラー */
--color-primary: #2196f3;
--color-primary-light: #42a5f5;
--color-primary-dark: #1976d2;

/* セマンティックカラー */
--color-success: #10b981;
--color-danger: #ef4444;
--color-warning: #f59e0b;

/* 背景階層 */
--bg-primary: #000000;      /* メイン背景 */
--bg-secondary: #111111;    /* エレベート背景 */
--bg-tertiary: #1a1a1a;     /* カード背景 */
--bg-card: #2a2a2a;         /* コンポーネントカード */

/* テキストカラー */
--text-primary: #ffffff;
--text-secondary: #b0b0b0;
--text-tertiary: #808080;
--text-muted: #606060;
```

### スペーシングシステム
```css
--space-xs: 0.25rem;    /* 4px */
--space-sm: 0.5rem;     /* 8px */
--space-md: 1rem;       /* 16px */
--space-lg: 1.5rem;     /* 24px */
--space-xl: 2rem;       /* 32px */
--space-2xl: 3rem;      /* 48px */
```

### アニメーション
```css
--duration-instant: 75ms;
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
```

## コンポーネントクラス

### 汎用カードスタイル
```css
.card-base {
  @apply bg-gray-900/50 border border-gray-800/50 rounded-xl p-4;
}

.card-elevated {
  @apply bg-gray-800/50 border border-gray-700/50 rounded-xl p-6 shadow-lg;
}

.card-interactive {
  @apply card-base hover:bg-gray-800/50 transition-colors cursor-pointer;
}
```

### ボタンバリエーション
```css
.btn-primary {
  @apply bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg 
         transition-colors font-medium;
}

.btn-secondary {
  @apply bg-gray-800 hover:bg-gray-700 text-gray-200 px-4 py-2 rounded-lg 
         border border-gray-600 transition-colors;
}

.btn-ghost {
  @apply hover:bg-gray-800/50 text-gray-300 hover:text-white px-3 py-2 
         rounded-lg transition-colors;
}
```

### ステータスインジケーター
```css
.status-positive {
  @apply text-green-400 bg-green-500/10 border border-green-500/30;
}

.status-negative {
  @apply text-red-400 bg-red-500/10 border border-red-500/30;
}

.status-neutral {
  @apply text-gray-400 bg-gray-500/10 border border-gray-500/30;
}

.status-warning {
  @apply text-yellow-400 bg-yellow-500/10 border border-yellow-500/30;
}
```

## 特殊効果

### グラデーション
```css
.gradient-primary {
  @apply bg-gradient-to-r from-blue-600 to-purple-600;
}

.gradient-success {
  @apply bg-gradient-to-r from-green-500 to-emerald-500;
}

.gradient-card {
  @apply bg-gradient-to-br from-gray-900/90 to-gray-800/90;
}
```

### グラスモーフィズム
```css
.glass-effect {
  @apply backdrop-blur-lg bg-white/10 border border-white/20;
}

.glass-card {
  @apply backdrop-blur-md bg-gray-900/80 border border-gray-700/50;
}
```

### アニメーション
```css
.animate-fade-in {
  animation: fadeIn var(--duration-normal) ease-out;
}

.animate-slide-up {
  animation: slideUp var(--duration-normal) ease-out;
}

.animate-pulse-subtle {
  animation: pulseSubtle 2s ease-in-out infinite;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes pulseSubtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
```

## チャート・データビジュアライゼーション

### チャートコンテナ
```css
.chart-container {
  @apply bg-gray-900/50 rounded-xl p-4 border border-gray-800/50;
}

.chart-header {
  @apply flex items-center justify-between mb-4 pb-2 border-b border-gray-800/50;
}

.chart-legend {
  @apply flex items-center space-x-4 text-sm text-gray-400 mt-2;
}
```

### データ表示
```css
.data-metric {
  @apply text-2xl font-bold text-white;
}

.data-label {
  @apply text-sm text-gray-400;
}

.data-change-positive {
  @apply text-green-400;
}

.data-change-negative {
  @apply text-red-400;
}

.data-percentage {
  @apply font-medium text-xs;
}
```

## レスポンシブガイドライン

### ブレークポイント使用例
```css
/* モバイル */
.mobile-layout {
  @apply block md:hidden;
}

/* タブレット */
.tablet-layout {
  @apply hidden md:block lg:hidden;
}

/* デスクトップ */
.desktop-layout {
  @apply hidden lg:block;
}

/* グリッドレスポンシブ */
.responsive-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}
```

### フレキシブルタイポグラフィ
```css
.heading-responsive {
  @apply text-lg md:text-xl lg:text-2xl font-bold;
}

.text-responsive {
  @apply text-sm md:text-base;
}
```

## ダークテーマ最適化

### コントラスト確保
```css
.high-contrast {
  @apply text-white bg-gray-900 border-gray-700;
}

.medium-contrast {
  @apply text-gray-200 bg-gray-800 border-gray-600;
}

.low-contrast {
  @apply text-gray-400 bg-gray-700 border-gray-500;
}
```

### 透明度の活用
```css
.bg-alpha-10 { @apply bg-white/10; }
.bg-alpha-20 { @apply bg-white/20; }
.bg-alpha-30 { @apply bg-white/30; }

.border-alpha-10 { @apply border-white/10; }
.border-alpha-20 { @apply border-white/20; }
.border-alpha-30 { @apply border-white/30; }
```

## パフォーマンス最適化

### GPU加速の活用
```css
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
}

.smooth-animation {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000;
}
```

### 効率的なセレクター
```css
/* 推奨: 特異性の低いクラスセレクター */
.btn { }
.card { }

/* 非推奨: 深いネストや複雑なセレクター */
.sidebar .nav .item .link { }
#header nav ul li a { }
```

## アクセシビリティ

### フォーカス管理
```css
.focus-visible {
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50;
}

.focus-within-highlight {
  @apply focus-within:ring-2 focus-within:ring-blue-500;
}
```

### カラーコントラスト
```css
/* WCAG AA準拠のコントラスト比 */
.text-high-contrast {
  color: #ffffff; /* 背景#000000に対して21:1 */
}

.text-medium-contrast {
  color: #b0b0b0; /* 背景#000000に対して7.8:1 */
}
```

## 命名規則

### BEMベース
```css
/* Block */
.search-form { }

/* Element */
.search-form__input { }
.search-form__button { }

/* Modifier */
.search-form--large { }
.search-form__button--primary { }
```

### 状態クラス
```css
.is-active { }
.is-loading { }
.is-disabled { }
.is-hidden { }
.has-error { }
```

## 最適化チェックリスト

### CSS
- [ ] 未使用のスタイルを削除
- [ ] セレクターの特異性を最小化
- [ ] アニメーションにGPU加速を活用
- [ ] クリティカルCSS を特定

### パフォーマンス
- [ ] CSSファイルサイズの監視
- [ ] 重複スタイルの排除
- [ ] プリプロセッサの適切な使用
- [ ] ベンダープレフィックスの最適化

### メンテナンス性
- [ ] コメントの充実
- [ ] モジュール化の推進
- [ ] デザイントークンとの同期
- [ ] ドキュメントの更新

## 参考資料

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [BEM Methodology](http://getbem.com/)