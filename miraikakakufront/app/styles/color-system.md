# カラーシステムフレームワーク

## 🎨 デザインコンセプト
YouTube Music風のダークテーマを基調とした統一されたカラーシステム

## 📐 カラーパレット定義

### ベースカラー
```css
--yt-music-bg: #030303;                /* メイン背景色 */
--yt-music-surface: #0f0f0f;           /* カード・パネルの背景色 */
--yt-music-surface-variant: #1a1a1a;   /* セクションコンテナの背景色 */
--yt-music-surface-hover: #212121;     /* ホバー時の背景色 */
```

### テキストカラー
```css
--yt-music-text-primary: #f1f1f1;      /* メインテキスト */
--yt-music-text-secondary: #aaaaaa;    /* サブテキスト・説明文 */
--yt-music-text-disabled: #717171;     /* 無効化されたテキスト */
```

### アクセントカラー
```css
--yt-music-primary: #3ea6ff;           /* プライマリーアクション */
--yt-music-primary-hover: #66b8ff;     /* プライマリーホバー */
--yt-music-accent: #f44336;            /* アクセント・重要な情報 */
```

### ボーダー・区切り線
```css
--yt-music-border: #303030;            /* 標準ボーダー */
--yt-music-divider: #404040;           /* 区切り線 */
```

### ステータスカラー
```css
/* 成功・上昇 */
--yt-music-success: #4caf50;
--yt-music-success-bg: rgba(76, 175, 80, 0.1);

/* エラー・下降 */
--yt-music-error: #f44336;
--yt-music-error-bg: rgba(244, 67, 54, 0.1);

/* 警告 */
--yt-music-warning: #ff9800;
--yt-music-warning-bg: rgba(255, 152, 0, 0.1);

/* 情報 */
--yt-music-info: #2196f3;
--yt-music-info-bg: rgba(33, 150, 243, 0.1);
```

## 🔧 使用パターン

### 1. ページ全体の背景
```tsx
<div style={{ backgroundColor: 'var(--yt-music-bg)' }}>
  {/* ページコンテンツ */}
</div>
```

### 2. カード・パネル
```tsx
<div style={{
  backgroundColor: 'var(--yt-music-surface)',
  border: '1px solid var(--yt-music-border)'
}}>
  {/* カードコンテンツ */}
</div>
```

### 3. セクションコンテナ
```tsx
<div style={{
  backgroundColor: 'var(--yt-music-surface-variant)',
  border: '1px solid var(--yt-music-border)'
}}>
  {/* セクションコンテンツ */}
</div>
```

### 4. ホバー効果
```tsx
<button
  style={{ backgroundColor: 'var(--yt-music-surface)' }}
  onMouseEnter={(e) => {
    e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
    e.currentTarget.style.borderColor = 'var(--yt-music-primary)';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.backgroundColor = 'var(--yt-music-surface)';
    e.currentTarget.style.borderColor = 'var(--yt-music-border)';
  }}
>
  {/* ボタンコンテンツ */}
</button>
```

### 5. テキスト階層
```tsx
<div>
  <h1 style={{ color: 'var(--yt-music-text-primary)' }}>メインタイトル</h1>
  <p style={{ color: 'var(--yt-music-text-secondary)' }}>説明テキスト</p>
  <span style={{ color: 'var(--yt-music-text-disabled)' }}>無効化テキスト</span>
</div>
```

### 6. ステータス表示
```tsx
{/* 上昇・ポジティブ */}
<span className="text-green-500">+10.5%</span>

{/* 下降・ネガティブ */}
<span className="text-red-500">-5.2%</span>

{/* 警告・注意 */}
<div style={{
  backgroundColor: 'var(--yt-music-warning-bg)',
  color: 'var(--yt-music-warning)'
}}>
  警告メッセージ
</div>
```

### 7. テーブルスタイル
```tsx
<table>
  <thead>
    <tr style={{ borderBottom: '1px solid var(--yt-music-border)' }}>
      <th style={{ color: 'var(--yt-music-text-secondary)' }}>ヘッダー</th>
    </tr>
  </thead>
  <tbody>
    {data.map((item, index) => (
      <tr
        key={index}
        style={{
          backgroundColor: index % 2 === 0
            ? 'var(--yt-music-surface)'
            : 'var(--yt-music-surface-variant)',
          borderBottom: '1px solid var(--yt-music-border)'
        }}
      >
        <td style={{ color: 'var(--yt-music-text-primary)' }}>{item.value}</td>
      </tr>
    ))}
  </tbody>
</table>
```

### 8. プライマリボタン
```tsx
<button
  style={{
    backgroundColor: 'var(--yt-music-primary)',
    color: 'white'
  }}
  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--yt-music-primary-hover)'}
  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--yt-music-primary)'}
>
  アクション
</button>
```

## 📋 コンポーネント別適用ガイド

### SearchBar（検索バー）
- 背景: `var(--yt-music-surface)`
- ボーダー: `var(--yt-music-border)`
- テキスト: `var(--yt-music-text-primary)`
- プレースホルダー: `var(--yt-music-text-secondary)`

### RankingCard（ランキングカード）
- コンテナ背景: `var(--yt-music-surface-variant)`
- アイテム背景: `var(--yt-music-surface)`
- ランク番号: `var(--yt-music-primary)`
- 会社名: `var(--yt-music-text-primary)`
- シンボル: `var(--yt-music-text-secondary)`

### StockChart（株価チャート）
- 背景: `var(--yt-music-surface-variant)`
- グリッド線: `var(--yt-music-border)`
- 実績線: `var(--yt-music-primary)`
- 予測線: `var(--yt-music-accent)`

### DetailsPage（詳細ページ）
- ページ背景: `var(--yt-music-bg)`
- ヘッダーカード: `var(--yt-music-surface-variant)`
- メトリクスカード: `var(--yt-music-surface)`
- テーブル行（偶数）: `var(--yt-music-surface)`
- テーブル行（奇数）: `var(--yt-music-surface-variant)`

### SystemStatus（システム状態）
- 背景: `var(--yt-music-surface-variant)`
- 正常状態: `var(--yt-music-success)`
- エラー状態: `var(--yt-music-error)`
- 警告状態: `var(--yt-music-warning)`

## 🎯 ベストプラクティス

1. **一貫性の維持**
   - 必ずCSS変数を使用し、直接的な色指定は避ける
   - 例外: Tailwindの`text-green-500`、`text-red-500`は株価の上下表示のみ使用可

2. **階層の明確化**
   - bg → surface-variant → surface の順で視覚的階層を作る
   - 重要度に応じてtext-primary/secondaryを使い分ける

3. **インタラクティブ要素**
   - ホバー効果は必ず実装する
   - surface → surface-hover への変化でフィードバックを提供

4. **アクセシビリティ**
   - コントラスト比を確保（最小4.5:1）
   - 色だけでなくアイコンや形状でも情報を伝える

5. **パフォーマンス**
   - CSS変数は`:root`で一度定義し、再利用する
   - インラインスタイルとCSSクラスを適切に使い分ける

## 🚀 実装例

### 完全なコンポーネント例
```tsx
export default function ExampleCard({ data }) {
  return (
    <div
      className="rounded-lg p-6 transition-all duration-200 hover:scale-[1.02]"
      style={{
        backgroundColor: 'var(--yt-music-surface-variant)',
        border: '1px solid var(--yt-music-border)'
      }}
    >
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold" style={{ color: 'var(--yt-music-text-primary)' }}>
          タイトル
        </h2>
        <span className="text-sm" style={{ color: 'var(--yt-music-text-secondary)' }}>
          サブテキスト
        </span>
      </div>

      {/* コンテンツ */}
      <div
        className="rounded p-4"
        style={{
          backgroundColor: 'var(--yt-music-surface)',
          border: '1px solid var(--yt-music-border)'
        }}
      >
        <p style={{ color: 'var(--yt-music-text-primary)' }}>
          メインコンテンツ
        </p>
      </div>

      {/* アクション */}
      <button
        className="mt-4 px-4 py-2 rounded transition-colors"
        style={{
          backgroundColor: 'var(--yt-music-primary)',
          color: 'white'
        }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--yt-music-primary-hover)'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--yt-music-primary)'}
      >
        アクション実行
      </button>
    </div>
  );
}
```

## 📝 メンテナンス

### CSS変数の定義場所
`/app/globals.css` の `:root` セクションで管理

### 変更時の確認事項
1. 全コンポーネントへの影響を確認
2. ダークモード/ライトモードの切り替え対応
3. アクセシビリティ基準の維持
4. ブラウザ互換性のテスト

### 今後の拡張
- ライトテーマの追加
- 高コントラストモード
- カスタムテーマ機能
- アニメーション・トランジションの統一