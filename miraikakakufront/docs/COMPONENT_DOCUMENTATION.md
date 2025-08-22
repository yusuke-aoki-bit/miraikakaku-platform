# コンポーネントドキュメント

## 概要
Miraikakakuプロジェクトで使用されるReactコンポーネントの詳細仕様とガイドライン。

---

## チャートコンポーネント

### StockChart.tsx
**場所**: `src/components/charts/StockChart.tsx`

#### 用途
単一銘柄の株価チャートを表示するコンポーネント。リアルタイムデータとAI予測を可視化。

#### Props
```typescript
interface StockChartProps {
  symbol: string;                    // 株式シンボル (例: "AAPL")
  height?: number;                   // チャートの高さ (デフォルト: 400px)
  timeframe?: '1D' | '1W' | '1M' | '3M' | '1Y';  // 表示期間
  showPrediction?: boolean;          // AI予測表示の有無
  className?: string;                // 追加CSSクラス
}
```

#### 使用例
```tsx
<StockChart 
  symbol="AAPL" 
  height={500}
  timeframe="1M"
  showPrediction={true}
  className="my-4"
/>
```

#### 機能
- リアルタイム価格更新
- LSTM・Vertex AI予測線表示
- インタラクティブなズーム・パン操作
- レスポンシブデザイン

---

### TripleChart.tsx
**場所**: `src/components/charts/TripleChart.tsx`

#### 用途
複数時間軸（短期・中期・長期）での株価比較チャート。

#### Props
```typescript
interface TripleChartProps {
  symbol: string;                    // 株式シンボル
  showLegend?: boolean;              // 凡例表示
  height?: number;                   // 各チャートの高さ
  className?: string;
}
```

#### 使用例
```tsx
<TripleChart 
  symbol="GOOGL" 
  showLegend={true}
  height={300}
/>
```

#### 機能
- 3つの時間軸同期表示
- 各時間軸での予測精度表示
- 相関分析結果表示

---

### VolumeChart.tsx
**場所**: `src/components/charts/VolumeChart.tsx`

#### 用途
出来高データの実績値・予測値を可視化するコンポーネント。

#### Props
```typescript
interface VolumeChartProps {
  symbol: string;                    // 株式シンボル
  viewMode?: 'combined' | 'volume' | 'price';  // 表示モード
  showCorrelation?: boolean;         // 価格相関表示
  height?: number;
  className?: string;
}
```

#### 使用例
```tsx
<VolumeChart 
  symbol="TSLA" 
  viewMode="combined"
  showCorrelation={true}
  height={450}
/>
```

#### 機能
- 出来高実績・予測の棒グラフ表示
- 価格との相関関係可視化
- 統計的分析結果表示
- 3つの表示モード切り替え

---

### CurrencyPrediction.tsx
**場所**: `src/components/charts/CurrencyPrediction.tsx`

#### 用途
外国為替（8通貨ペア）の予測と分析を行うコンポーネント。

#### Props
```typescript
interface CurrencyPredictionProps {
  selectedPair?: string;             // 選択通貨ペア (例: "USD/JPY")
  showEconomicCalendar?: boolean;    // 経済カレンダー表示
  showTechnicalIndicators?: boolean; // テクニカル指標表示
  height?: number;
  className?: string;
}
```

#### 使用例
```tsx
<CurrencyPrediction 
  selectedPair="EUR/USD"
  showEconomicCalendar={true}
  showTechnicalIndicators={true}
  height={600}
/>
```

#### 機能
- 8通貨ペアのレート予測
- 経済カレンダー統合
- RSI、MACD、ボリンジャーバンド表示
- トレーディングシグナル生成

---

### PredictionChart.tsx
**場所**: `src/components/charts/PredictionChart.tsx`

#### 用途
AI予測結果を専門的に表示するコンポーネント。

#### Props
```typescript
interface PredictionChartProps {
  symbol: string;
  modelType?: 'lstm' | 'vertex' | 'both';  // 表示モデル
  confidenceThreshold?: number;            // 信頼度しきい値
  predictionDays?: number;                 // 予測日数
  className?: string;
}
```

#### 使用例
```tsx
<PredictionChart 
  symbol="NVDA"
  modelType="both"
  confidenceThreshold={0.8}
  predictionDays={30}
/>
```

#### 機能
- LSTM・Vertex AI予測の比較表示
- 信頼度バンド表示
- 予測精度メトリクス
- リスク評価インジケーター

---

## 共通コンポーネント

### LoadingSpinner.tsx
**場所**: `src/components/common/LoadingSpinner.tsx`

#### 用途
データ読み込み中の表示コンポーネント。

#### Props
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';     // サイズ
  type?: 'default' | 'ai' | 'chart';    // スタイルタイプ
  message?: string;                      // 表示メッセージ
  className?: string;
}
```

#### 使用例
```tsx
<LoadingSpinner 
  size="lg" 
  type="ai" 
  message="AI分析中..." 
/>
```

#### バリエーション
- **default**: 一般的なローディング
- **ai**: AI処理用（脳のアイコン）
- **chart**: チャート読み込み用

---

### CommandPalette.tsx
**場所**: `src/components/common/CommandPalette.tsx`

#### 用途
キーボードショートカットによる高速ナビゲーション。

#### Props
```typescript
interface CommandPaletteProps {
  isOpen?: boolean;                      // 表示状態
  onClose?: () => void;                  // 閉じるコールバック
  className?: string;
}
```

#### 使用例
```tsx
<CommandPalette 
  isOpen={showPalette} 
  onClose={() => setShowPalette(false)} 
/>
```

#### 機能
- `Cmd/Ctrl + K`で起動
- 銘柄検索、ページナビゲーション
- 最近の検索履歴表示
- ファジー検索対応

---

### UserModeToggle.tsx
**場所**: `src/components/common/UserModeToggle.tsx`

#### 用途
初心者・上級者モード切り替えコンポーネント。

#### Props
```typescript
interface UserModeToggleProps {
  currentMode?: 'beginner' | 'advanced';
  onModeChange?: (mode: 'beginner' | 'advanced') => void;
  className?: string;
}
```

#### 使用例
```tsx
<UserModeToggle 
  currentMode={userMode}
  onModeChange={handleModeChange}
/>
```

#### 機能
- UI複雑度の調整
- 表示情報レベル制御
- パーソナライゼーション

---

## ダッシュボードコンポーネント

### RealTimeDashboard.tsx
**場所**: `src/components/dashboard/RealTimeDashboard.tsx`

#### 用途
リアルタイム市場データの統合ダッシュボード。

#### Props
```typescript
interface RealTimeDashboardProps {
  watchlistSymbols?: string[];           // 監視銘柄リスト
  updateInterval?: number;               // 更新間隔（ミリ秒）
  showAlerts?: boolean;                  // アラート表示
  layout?: 'grid' | 'list';             // レイアウト
  className?: string;
}
```

#### 使用例
```tsx
<RealTimeDashboard 
  watchlistSymbols={['AAPL', 'GOOGL', 'MSFT']}
  updateInterval={30000}
  showAlerts={true}
  layout="grid"
/>
```

#### 機能
- WebSocketリアルタイム更新
- 価格アラート機能
- パフォーマンス指標表示
- カスタマイズ可能レイアウト

---

### GridDashboard.tsx
**場所**: `src/components/dashboard/GridDashboard.tsx`

#### 用途
カスタマイズ可能なウィジェット型ダッシュボード。

#### Props
```typescript
interface GridDashboardProps {
  widgets?: WidgetConfig[];              // ウィジェット設定
  editable?: boolean;                    // 編集可能
  onLayoutChange?: (layout: Layout[]) => void;
  className?: string;
}
```

#### 使用例
```tsx
<GridDashboard 
  widgets={dashboardConfig}
  editable={true}
  onLayoutChange={saveDashboardLayout}
/>
```

#### 機能
- ドラッグ&ドロップ配置
- ウィジェットサイズ調整
- レイアウト保存・復元

---

## レイアウトコンポーネント

### Header.tsx
**場所**: `src/components/layout/Header.tsx`

#### 用途
アプリケーションのメインヘッダー。

#### Props
```typescript
interface HeaderProps {
  showSearch?: boolean;                  // 検索バー表示
  showUserMenu?: boolean;                // ユーザーメニュー表示
  className?: string;
}
```

#### 使用例
```tsx
<Header 
  showSearch={true} 
  showUserMenu={true} 
/>
```

#### 機能
- ブランドロゴ表示
- グローバル検索
- ユーザーアカウントメニュー
- レスポンシブ対応

---

### Sidebar.tsx
**場所**: `src/components/layout/Sidebar.tsx`

#### 用途
メインナビゲーションサイドバー。

#### Props
```typescript
interface SidebarProps {
  collapsed?: boolean;                   // 折りたたみ状態
  onToggle?: () => void;                 // 折りたたみトグル
  className?: string;
}
```

#### 使用例
```tsx
<Sidebar 
  collapsed={sidebarCollapsed} 
  onToggle={toggleSidebar} 
/>
```

#### 機能
- ページナビゲーション
- 折りたたみ対応
- アクティブ状態表示
- アクセス制御

---

### AppContainer.tsx
**場所**: `src/components/layout/AppContainer.tsx`

#### 用途
アプリケーション全体のレイアウトコンテナ。

#### Props
```typescript
interface AppContainerProps {
  children: React.ReactNode;
  showSidebar?: boolean;                 // サイドバー表示
  fullWidth?: boolean;                   // 全幅表示
  className?: string;
}
```

#### 使用例
```tsx
<AppContainer showSidebar={true} fullWidth={false}>
  <YourPageContent />
</AppContainer>
```

#### 機能
- レスポンシブレイアウト
- サイドバー制御
- コンテンツ領域管理

---

## 検索コンポーネント

### StockSearch.tsx
**場所**: `src/components/StockSearch.tsx`

#### 用途
株式銘柄のインテリジェント検索コンポーネント。

#### Props
```typescript
interface StockSearchProps {
  placeholder?: string;                  // プレースホルダー
  onSelect?: (stock: StockInfo) => void; // 選択コールバック
  maxResults?: number;                   // 最大表示件数
  showDetails?: boolean;                 // 詳細情報表示
  className?: string;
}
```

#### 使用例
```tsx
<StockSearch 
  placeholder="銘柄名またはシンボルを入力..."
  onSelect={handleStockSelect}
  maxResults={10}
  showDetails={true}
/>
```

#### 機能
- リアルタイム候補表示
- ファジー検索対応
- 企業名・シンボル検索
- 詳細情報プレビュー

---

## スタイリング規則

### 共通クラス
- `.youtube-card`: カード型UI用の基本スタイル
- `.price-positive`: 価格上昇時の色（緑）
- `.price-negative`: 価格下落時の色（赤）
- `.loading-skeleton`: ローディング時のスケルトンUI

### 色の使用方針
- **成功/上昇**: `text-icon-green` (#10b981)
- **危険/下落**: `text-icon-red` (#ef4444)
- **プライマリ**: `text-primary-500` (#2196f3)
- **テキスト**: `text-text-white`, `text-base-gray-400`

### レスポンシブデザイン
- **モバイル**: `sm:` (640px+)
- **タブレット**: `md:` (768px+)
- **デスクトップ**: `lg:` (1024px+)
- **大画面**: `xl:` (1280px+)

---

## パフォーマンス最適化

### 遅延読み込み
```tsx
// 重いチャートコンポーネントの遅延読み込み
const LazyStockChart = lazy(() => import('./StockChart'));

<Suspense fallback={<LoadingSpinner type="chart" />}>
  <LazyStockChart symbol="AAPL" />
</Suspense>
```

### メモ化
```tsx
// 高コストな計算の最適化
const memoizedChartData = useMemo(() => 
  processChartData(rawData), [rawData]
);
```

### 仮想化
大きなデータセットには`react-window`を使用：
```tsx
<FixedSizeList
  height={400}
  itemCount={stockList.length}
  itemSize={60}
>
  {StockListItem}
</FixedSizeList>
```

---

## テスト方針

### 単体テスト
```tsx
// コンポーネントテストの例
describe('StockChart', () => {
  it('should render chart with correct symbol', () => {
    render(<StockChart symbol="AAPL" />);
    expect(screen.getByText(/AAPL/)).toBeInTheDocument();
  });
  
  it('should handle prediction toggle', async () => {
    const { user } = setup(<StockChart symbol="AAPL" />);
    await user.click(screen.getByRole('button', { name: /prediction/i }));
    expect(screen.getByTestId('prediction-line')).toBeInTheDocument();
  });
});
```

### E2Eテスト
```tsx
// Playwright E2Eテストの例
test('should navigate to stock details from chart', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="stock-chart-AAPL"]');
  await expect(page).toHaveURL(/\/stock\/AAPL/);
});
```

---

## 今後の拡張予定

### 新機能コンポーネント
- **PortfolioOptimization.tsx**: ポートフォリオ最適化
- **SocialSentiment.tsx**: ソーシャルメディア感情分析
- **NewsAnalysis.tsx**: ニュース影響分析
- **RiskAssessment.tsx**: リスク評価ダッシュボード

### 改善予定
- WebGL活用による高速チャート描画
- WebAssembly統合による計算最適化
- Service Worker活用によるオフライン対応強化

---

## 貢献ガイドライン

### 新規コンポーネント作成時
1. TypeScript型定義を必須とする
2. Props interface にJSDocコメントを追加
3. ストーリーブック（Storybook）対応
4. 単体テスト作成
5. アクセシビリティ対応（ARIA属性）

### コードレビューポイント
- パフォーマンス影響の確認
- メモリリークの防止
- 型安全性の担保
- UI一貫性の維持

---

このドキュメントは継続的に更新され、新しいコンポーネントの追加や既存コンポーネントの変更に合わせて保守されます。