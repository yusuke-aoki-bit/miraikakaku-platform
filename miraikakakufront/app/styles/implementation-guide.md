# カラーフレームワーク実装ガイド

## 🚀 Tailwind CSS + カスタムCSS変数ハイブリッド実装

### ファイル構成
```
app/styles/
├── theme-framework.css          # メインフレームワーク（このファイルを使用）
├── color-system.md             # 設計ドキュメント
├── implementation-guide.md     # 実装ガイド（この文書）
└── examples/
    └── ThemeFrameworkExample.tsx # 実装例コンポーネント
```

## 📋 導入手順

### 1. フレームワークファイルのインポート
```tsx
// app/layout.tsx または globals.css に追加
import './styles/theme-framework.css'
```

### 2. 既存のglobals.cssとの統合
```css
/* globals.css */
@import './theme-framework.css';

/* 既存のスタイルがある場合は、theme-framework.css の後に配置 */
```

## 🎯 実装パターン

### パターン1: 完全フレームワーク使用
```tsx
// 推奨: フレームワークのクラスを最大限活用
export default function MyComponent() {
  return (
    <div className="theme-page">
      <div className="theme-container">
        <div className="theme-section">
          <h1 className="theme-heading-xl">タイトル</h1>
          <p className="theme-body">本文テキスト</p>
          <button className="theme-btn-primary">
            アクション
          </button>
        </div>
      </div>
    </div>
  );
}
```

### パターン2: カスタムスタイルとの併用
```tsx
// カスタムスタイルが必要な場合
export default function CustomComponent() {
  return (
    <div className="theme-page">
      <div
        className="theme-card"
        style={{
          // カスタムプロパティを直接使用
          backgroundColor: 'rgb(var(--theme-bg-secondary))',
          borderColor: 'rgb(var(--theme-primary))'
        }}
      >
        <h2 className="theme-heading-md">
          カスタマイズされたカード
        </h2>
      </div>
    </div>
  );
}
```

### パターン3: 動的スタイル
```tsx
// 状態に応じたスタイル変更
export default function DynamicComponent() {
  const [isActive, setIsActive] = useState(false);
  const [status, setStatus] = useState<'success' | 'error' | 'warning'>('success');

  return (
    <div className="theme-page">
      <button
        className={`theme-card ${isActive ? 'border-2' : ''}`}
        style={{
          borderColor: isActive ? 'rgb(var(--theme-primary))' : 'rgb(var(--theme-border))',
          transform: isActive ? 'scale(1.02)' : 'scale(1)'
        }}
        onClick={() => setIsActive(!isActive)}
      >
        <span className={`theme-badge-${status}`}>
          ステータス: {status}
        </span>
      </button>
    </div>
  );
}
```

## 🔧 コンポーネント別実装例

### SearchBar Component
```tsx
export default function SearchBar({ onSearch }: { onSearch: (query: string) => void }) {
  const [query, setQuery] = useState('');

  return (
    <div className="theme-section">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 theme-text-secondary" />
        <input
          className="theme-input pl-10"
          type="text"
          placeholder="銘柄を検索..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && onSearch(query)}
        />
      </div>
    </div>
  );
}
```

### RankingCard Component
```tsx
export default function RankingCard({ rankings }: { rankings: RankingItem[] }) {
  return (
    <div className="theme-section">
      <h2 className="theme-heading-md mb-4">ランキング</h2>
      <div className="space-y-4">
        {rankings.map((item, index) => (
          <div key={item.symbol} className="theme-ranking-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="theme-ranking-number">{index + 1}</span>
                <div>
                  <div className="theme-ranking-company">{item.company}</div>
                  <div className="theme-ranking-symbol">{item.symbol}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="theme-ranking-price">
                  ${item.price.toFixed(2)}
                </div>
                <div className={item.change >= 0
                  ? 'theme-ranking-change-positive'
                  : 'theme-ranking-change-negative'
                }>
                  {item.change >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                  {item.change.toFixed(2)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### SystemStatus Component
```tsx
export default function SystemStatus() {
  const [status, setStatus] = useState({
    api: 'success',
    database: 'success',
    batch: 'warning'
  });

  return (
    <div className="theme-section">
      <h2 className="theme-heading-md mb-4">システム状態</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="theme-card">
          <div className="flex items-center justify-between mb-2">
            <span className="theme-body font-medium">API サーバー</span>
            <div className={`theme-badge-${status.api}`}>
              {status.api === 'success' ? '正常' : 'エラー'}
            </div>
          </div>
          <p className="theme-caption">最終確認: 1分前</p>
        </div>

        <div className="theme-card">
          <div className="flex items-center justify-between mb-2">
            <span className="theme-body font-medium">データベース</span>
            <div className={`theme-badge-${status.database}`}>
              {status.database === 'success' ? '正常' : 'エラー'}
            </div>
          </div>
          <p className="theme-caption">最終確認: 30秒前</p>
        </div>

        <div className="theme-card">
          <div className="flex items-center justify-between mb-2">
            <span className="theme-body font-medium">バッチ処理</span>
            <div className={`theme-badge-${status.batch}`}>
              {status.batch === 'warning' ? '遅延中' : '正常'}
            </div>
          </div>
          <p className="theme-caption">最終実行: 5分前</p>
        </div>
      </div>
    </div>
  );
}
```

## 💡 ベストプラクティス

### 1. クラス命名規則
```tsx
// ✅ 良い例: フレームワークのクラスを使用
<div className="theme-section">
  <h2 className="theme-heading-md">タイトル</h2>
  <button className="theme-btn-primary">アクション</button>
</div>

// ❌ 避ける例: 直接的なスタイル指定
<div style={{ backgroundColor: '#1a1a1a', padding: '24px' }}>
  <h2 style={{ color: '#f1f1f1', fontSize: '20px' }}>タイトル</h2>
  <button style={{ backgroundColor: '#3ea6ff' }}>アクション</button>
</div>
```

### 2. レスポンシブデザイン
```tsx
// フレームワークにはレスポンシブ対応が組み込まれている
<div className="theme-stock-metrics"> {/* 自動的にレスポンシブグリッド */}
  <div className="theme-stock-metric-card">メトリック1</div>
  <div className="theme-stock-metric-card">メトリック2</div>
  <div className="theme-stock-metric-card">メトリック3</div>
</div>
```

### 3. ホバー効果
```tsx
// フレームワークのカードには自動的にホバー効果が適用される
<button className="theme-card"> {/* hover:scale-[1.01] が自動適用 */}
  クリック可能なカード
</button>

// カスタムホバー効果が必要な場合
<div
  className="theme-card"
  onMouseEnter={(e) => {
    e.currentTarget.style.borderColor = 'rgb(var(--theme-primary))';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.borderColor = 'rgb(var(--theme-border))';
  }}
>
  カスタムホバー効果
</div>
```

### 4. 状態管理との統合
```tsx
// 状態に応じたスタイル変更
const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'success': return 'theme-badge-success';
    case 'error': return 'theme-badge-error';
    case 'warning': return 'theme-badge-warning';
    default: return 'theme-badge-info';
  }
};

<div className={getStatusBadgeClass(systemStatus)}>
  {statusText}
</div>
```

## 🔄 アップグレード・メンテナンス

### 1. 新しいコンポーネントの追加
```css
/* theme-framework.css に新しいコンポーネントを追加 */
@layer components {
  .theme-notification {
    @apply fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50;
    background-color: rgb(var(--theme-bg-secondary));
    border: 1px solid rgb(var(--theme-border));
    color: rgb(var(--theme-text-primary));
  }
}
```

### 2. カラーバリエーションの拡張
```css
:root {
  /* 新しいカラーを追加 */
  --theme-purple: 156 39 176;     /* #9c27b0 */
  --theme-orange: 255 152 0;      /* #ff9800 */
}

.theme-badge-purple {
  @apply px-3 py-1 rounded-full text-sm font-medium;
  background-color: rgb(var(--theme-purple) / 0.1);
  color: rgb(var(--theme-purple));
  border: 1px solid rgb(var(--theme-purple) / 0.3);
}
```

### 3. パフォーマンス最適化
```tsx
// クラスの結合にはclsxライブラリを使用
import clsx from 'clsx';

const buttonClass = clsx(
  'theme-btn-primary',
  isLoading && 'opacity-50 cursor-not-allowed',
  isActive && 'ring-2 ring-blue-500'
);

<button className={buttonClass}>
  ボタン
</button>
```

## 📊 テスト・デバッグ

### 1. 色のテスト
```tsx
// 開発用: 色の確認コンポーネント
export function ColorPalette() {
  return (
    <div className="theme-page">
      <div className="theme-container">
        <h1 className="theme-heading-xl mb-6">Color Palette Test</h1>

        <div className="grid grid-cols-4 gap-4">
          <div className="theme-card">
            <div className="w-full h-12 mb-2" style={{ backgroundColor: 'rgb(var(--theme-primary))' }}></div>
            <p className="theme-caption">Primary</p>
          </div>

          <div className="theme-card">
            <div className="w-full h-12 mb-2" style={{ backgroundColor: 'rgb(var(--theme-success))' }}></div>
            <p className="theme-caption">Success</p>
          </div>

          <div className="theme-card">
            <div className="w-full h-12 mb-2" style={{ backgroundColor: 'rgb(var(--theme-error))' }}></div>
            <p className="theme-caption">Error</p>
          </div>

          <div className="theme-card">
            <div className="w-full h-12 mb-2" style={{ backgroundColor: 'rgb(var(--theme-warning))' }}></div>
            <p className="theme-caption">Warning</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 2. ブラウザ互換性確認
```css
/* 古いブラウザのフォールバック */
.theme-card {
  background-color: #0f0f0f; /* フォールバック */
  background-color: rgb(var(--theme-bg-secondary)); /* CSS変数 */
}
```

## 🚀 本番環境への適用

### 1. 段階的ロールアウト
```tsx
// Feature flagを使った段階的適用
const useThemeFramework = process.env.NEXT_PUBLIC_USE_THEME_FRAMEWORK === 'true';

export default function MyComponent() {
  if (useThemeFramework) {
    return <NewThemeComponent />;
  }
  return <LegacyComponent />;
}
```

### 2. パフォーマンス監視
```tsx
// CSS-in-JSからCSSクラスへの移行でパフォーマンス向上を確認
console.time('render-time');
// コンポーネントレンダリング
console.timeEnd('render-time');
```

このフレームワークにより、統一されたデザインシステムを効率的に実装・維持できます。