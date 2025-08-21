# 🧩 Miraikakaku Components Documentation

This document provides comprehensive documentation for all React components in the Miraikakaku platform. Each component is designed following our design system principles with consistent APIs, accessibility features, and performance optimizations.

## 📋 Table of Contents

- [Component Architecture](#component-architecture)
- [Common Components](#common-components)
- [Chart Components](#chart-components)
- [Layout Components](#layout-components)
- [Feature Components](#feature-components)
- [Usage Guidelines](#usage-guidelines)
- [Testing Components](#testing-components)

---

## 🏗 Component Architecture

### Design Principles

1. **Consistency**: All components follow the same API patterns and design tokens
2. **Reusability**: Components are built to be composable and reusable
3. **Accessibility**: WCAG 2.1 AA compliance with proper ARIA attributes
4. **Performance**: Optimized rendering with React.memo and proper prop handling
5. **Type Safety**: Full TypeScript coverage with detailed prop interfaces

### File Structure

```
src/components/
├── common/           # Shared UI components
├── charts/          # Data visualization components
├── layout/          # Application layout components
├── home/            # Homepage-specific components
├── dashboard/       # Dashboard-specific components
├── search/          # Search and discovery components
└── investment/      # Investment analysis components
```

---

## 🔧 Common Components

### LoadingSpinner

A versatile loading indicator with multiple variants and animation types.

**Props:**
```typescript
interface LoadingSpinnerProps {
  message?: string;      // Optional loading message
  size?: 'sm' | 'md' | 'lg';  // Size variant
  type?: 'default' | 'ai' | 'chart';  // Visual theme
}
```

**Usage:**
```tsx
import LoadingSpinner from '@/components/common/LoadingSpinner';

// Basic usage
<LoadingSpinner />

// With custom message and size
<LoadingSpinner 
  message="データを読み込み中..." 
  size="lg" 
  type="ai"
/>
```

**Features:**
- Multiple visual themes (default, AI-focused, chart-focused)
- Responsive sizing (sm: 24px, md: 32px, lg: 48px)
- Animated icons for different contexts
- Accessible with proper ARIA labels
- CSS custom properties for theme consistency

---

### SkeletonLoader

Placeholder component for loading states with customizable dimensions.

**Props:**
```typescript
interface SkeletonLoaderProps {
  width?: string;        // CSS width value
  height?: string;       // CSS height value
  className?: string;    // Additional CSS classes
  variant?: 'text' | 'rectangular' | 'circular';  // Shape variant
}
```

**Usage:**
```tsx
import SkeletonLoader from '@/components/common/SkeletonLoader';

// Text skeleton
<SkeletonLoader width="80%" height="18px" />

// Card skeleton
<SkeletonLoader width="100%" height="200px" variant="rectangular" />

// Avatar skeleton
<SkeletonLoader width="40px" height="40px" variant="circular" />
```

---

### ToastNotification

System for displaying temporary messages and alerts.

**Props:**
```typescript
interface ToastNotificationProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;     // Auto-dismiss duration in ms
  onClose?: () => void;  // Close callback
  actions?: ToastAction[]; // Optional action buttons
}
```

**Usage:**
```tsx
import { useToast } from '@/hooks/useToast';

const { showToast } = useToast();

// Success notification
showToast({
  type: 'success',
  title: '予測完了',
  message: 'AI予測が正常に生成されました',
  duration: 3000
});

// Error with retry action
showToast({
  type: 'error',
  title: 'データ取得エラー',
  message: 'サーバーに接続できませんでした',
  actions: [{ label: '再試行', onClick: retryFunction }]
});
```

---

### CommandPalette

Global command interface for quick navigation and actions.

**Props:**
```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: Command[];    // Available commands
  placeholder?: string;   // Search placeholder
}
```

**Usage:**
```tsx
import CommandPalette from '@/components/common/CommandPalette';

const commands = [
  {
    id: 'search-stock',
    label: '株式を検索',
    icon: <Search />,
    action: () => navigateToSearch(),
    keywords: ['search', '検索', 'stock']
  },
  {
    id: 'view-dashboard',
    label: 'ダッシュボードを表示',
    icon: <BarChart />,
    action: () => navigateToDashboard(),
    shortcut: '⌘+D'
  }
];

<CommandPalette 
  isOpen={isCommandPaletteOpen}
  onClose={() => setIsCommandPaletteOpen(false)}
  commands={commands}
  placeholder="コマンドを検索..."
/>
```

---

## 📊 Chart Components

### StockChart

Advanced stock price visualization with predictions and historical data.

**Props:**
```typescript
interface StockChartProps {
  symbol: string;        // Stock symbol to display
  timeframe?: string;    // Time range for data
  showPredictions?: boolean;    // Show AI predictions
  showVolume?: boolean;         // Include volume data
  height?: number;              // Chart height in pixels
  interactive?: boolean;        // Enable interactions
}
```

**Usage:**
```tsx
import StockChart from '@/components/charts/StockChart';

<StockChart 
  symbol="AAPL" 
  timeframe="30d"
  showPredictions={true}
  showVolume={true}
  height={400}
  interactive={true}
/>
```

**Features:**
- Real-time price updates via WebSocket
- AI prediction overlays with confidence bands
- Historical accuracy visualization
- Volume indicators
- Interactive tooltips and crosshairs
- Responsive design with mobile optimizations
- Export functionality (PNG, SVG, CSV)

**Data Integration:**
- Connects to `/api/finance/stocks/{symbol}/price`
- Fetches predictions from `/api/finance/stocks/{symbol}/predictions`
- WebSocket updates for real-time data

---

### AdvancedStockChart

Professional-grade charting component with technical indicators.

**Props:**
```typescript
interface AdvancedStockChartProps {
  symbol: string;
  indicators?: TechnicalIndicator[];  // Technical indicators to show
  overlays?: ChartOverlay[];         // Price overlays
  timeframe?: TimeframeOption;       // Time range
  theme?: 'light' | 'dark';         // Color theme
}
```

**Usage:**
```tsx
import AdvancedStockChart from '@/components/charts/AdvancedStockChart';

<AdvancedStockChart 
  symbol="TSLA"
  indicators={['sma20', 'sma50', 'rsi', 'macd']}
  overlays={['bollinger', 'support_resistance']}
  timeframe="1y"
/>
```

**Technical Indicators:**
- Simple Moving Averages (SMA)
- Exponential Moving Averages (EMA)
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume indicators

---

### InteractiveChart

Highly interactive chart with drawing tools and analysis features.

**Props:**
```typescript
interface InteractiveChartProps {
  symbol: string;
  height?: number;
  tools?: DrawingTool[];     // Available drawing tools
  onAnalysisComplete?: (analysis: ChartAnalysis) => void;
}
```

**Usage:**
```tsx
import InteractiveChart from '@/components/charts/InteractiveChart';

<InteractiveChart 
  symbol="NVDA"
  height={600}
  tools={['trendline', 'fibonacci', 'rectangle']}
  onAnalysisComplete={handleAnalysis}
/>
```

**Drawing Tools:**
- Trend lines
- Fibonacci retracements
- Support/resistance levels
- Pattern recognition
- Annotation tools

---

### ThumbnailChart

Compact chart component for lists and grids.

**Props:**
```typescript
interface ThumbnailChartProps {
  symbol: string;
  data: PricePoint[];    // Historical price data
  width?: number;        // Chart width
  height?: number;       // Chart height
  showChange?: boolean;  // Show price change indicator
  period?: string;       // Data period label
}
```

**Usage:**
```tsx
import ThumbnailChart from '@/components/charts/ThumbnailChart';

<ThumbnailChart 
  symbol="GOOGL"
  data={priceHistory}
  width={120}
  height={60}
  showChange={true}
  period="7d"
/>
```

---

## 🏛 Layout Components

### Header

Application header with navigation and user controls.

**Props:**
```typescript
interface HeaderProps {
  user?: User;           // Current user data
  onSearch?: (query: string) => void;    // Search handler
  showUserMenu?: boolean;                 // Show user dropdown
  notifications?: Notification[];         // Notification count
}
```

**Features:**
- Global search integration
- User authentication status
- Notification center
- Theme toggle
- Mobile-responsive navigation
- Command palette trigger

---

### Sidebar

Collapsible navigation sidebar with route highlighting.

**Props:**
```typescript
interface SidebarProps {
  isCollapsed?: boolean;     // Collapsed state
  onToggle?: () => void;     // Toggle handler
  activeRoute?: string;      // Current active route
  userRole?: UserRole;       // User permissions
}
```

**Navigation Structure:**
- Dashboard
- Stock Analysis
- Portfolio Management
- AI Predictions
- Market Rankings
- Watchlists
- Settings

---

### AppContainer

Main application wrapper with layout management.

**Props:**
```typescript
interface AppContainerProps {
  children: React.ReactNode;
  sidebar?: boolean;         // Show sidebar
  header?: boolean;          // Show header
  footer?: boolean;          // Show footer
  className?: string;        // Additional CSS classes
}
```

---

## 🎯 Feature Components

### StockSearch

Intelligent stock search with autocomplete and filters.

**Props:**
```typescript
interface StockSearchProps {
  onSymbolSelect?: (symbol: string) => void;  // Selection handler
  placeholder?: string;                        // Input placeholder
  filters?: SearchFilter[];                    // Search filters
  limit?: number;                             // Results limit
}
```

**Usage:**
```tsx
import StockSearch from '@/components/StockSearch';

<StockSearch 
  onSymbolSelect={(symbol) => navigateToStock(symbol)}
  placeholder="株式シンボルまたは会社名で検索..."
  filters={['sector', 'market_cap', 'exchange']}
  limit={10}
/>
```

**Features:**
- Real-time search with debouncing
- Multi-criteria filtering
- Keyboard navigation
- Recent searches
- Search suggestions
- Error handling with fallbacks

---

### RealTimeDashboard

Comprehensive real-time market dashboard.

**Props:**
```typescript
interface RealTimeDashboardProps {
  symbols?: string[];        // Stocks to track
  updateInterval?: number;   // Refresh interval
  showAlerts?: boolean;      // Display alerts
  layout?: DashboardLayout;  // Layout configuration
}
```

**Features:**
- Real-time price updates
- AI prediction monitoring
- Market alerts and notifications
- Customizable layout
- Performance metrics
- System status indicators

---

### MarketOverview

Market summary with key indicators and trends.

**Props:**
```typescript
interface MarketOverviewProps {
  indices?: MarketIndex[];   // Market indices to show
  timeframe?: string;        // Data timeframe
  showNews?: boolean;        // Include market news
  compact?: boolean;         // Compact layout mode
}
```

---

### AIInsights

AI-powered market insights and analysis.

**Props:**
```typescript
interface AIInsightsProps {
  symbol?: string;           // Specific stock focus
  insightTypes?: InsightType[];  // Types of insights
  refreshInterval?: number;  // Auto-refresh interval
}
```

**Insight Types:**
- Price predictions
- Market sentiment analysis
- Technical pattern recognition
- Risk assessments
- Trading recommendations

---

## 🎨 Usage Guidelines

### Component Composition

```tsx
// Recommended: Compose components for complex layouts
const StockAnalysisPage = () => (
  <AppContainer sidebar header>
    <div className="page-container">
      <div className="page-content">
        <StockSearch onSymbolSelect={setSelectedSymbol} />
        {selectedSymbol && (
          <>
            <StockChart symbol={selectedSymbol} />
            <AIInsights symbol={selectedSymbol} />
          </>
        )}
      </div>
    </div>
  </AppContainer>
);
```

### Error Boundaries

All components include error boundaries for graceful failure handling:

```tsx
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

<ErrorBoundary fallback={<ErrorFallback />}>
  <StockChart symbol="AAPL" />
</ErrorBoundary>
```

### Performance Optimization

```tsx
// Use React.memo for expensive components
const OptimizedChart = React.memo(StockChart, (prevProps, nextProps) => {
  return prevProps.symbol === nextProps.symbol &&
         prevProps.timeframe === nextProps.timeframe;
});

// Lazy loading for heavy components
const InteractiveChart = React.lazy(() => 
  import('@/components/charts/InteractiveChart')
);

<Suspense fallback={<LoadingSpinner type="chart" />}>
  <InteractiveChart symbol="AAPL" />
</Suspense>
```

### Accessibility Implementation

```tsx
// Proper ARIA attributes
<button 
  aria-label="株式を検索"
  aria-describedby="search-help"
  aria-expanded={isExpanded}
>
  検索
</button>

// Focus management
const focusableElements = 'button, input, select, textarea, [tabindex]:not([tabindex="-1"])';

// Keyboard navigation
const handleKeyDown = (e: KeyboardEvent) => {
  switch(e.key) {
    case 'Escape':
      closeModal();
      break;
    case 'Enter':
      confirmAction();
      break;
  }
};
```

---

## 🧪 Testing Components

### Unit Tests

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import StockSearch from '@/components/StockSearch';

describe('StockSearch', () => {
  it('calls onSymbolSelect when stock is selected', async () => {
    const mockOnSelect = jest.fn();
    render(<StockSearch onSymbolSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText(/検索/);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    const option = await screen.findByText('Apple Inc.');
    fireEvent.click(option);
    
    expect(mockOnSelect).toHaveBeenCalledWith('AAPL');
  });
  
  it('shows loading state during search', () => {
    render(<StockSearch />);
    // Test implementation
  });
});
```

### Integration Tests

```tsx
import { render, screen } from '@testing-library/react';
import RealTimeDashboard from '@/components/dashboard/RealTimeDashboard';

describe('RealTimeDashboard Integration', () => {
  it('displays real-time data updates', async () => {
    // Mock WebSocket
    const mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
      addEventListener: jest.fn(),
    };
    
    global.WebSocket = jest.fn(() => mockWebSocket);
    
    render(<RealTimeDashboard />);
    
    // Simulate WebSocket message
    const messageHandler = mockWebSocket.addEventListener.mock.calls
      .find(([event]) => event === 'message')[1];
    
    messageHandler({
      data: JSON.stringify({
        type: 'price_update',
        data: { symbol: 'AAPL', price: 150.00 }
      })
    });
    
    expect(await screen.findByText('$150.00')).toBeInTheDocument();
  });
});
```

### Component Testing Best Practices

1. **Test User Interactions**: Focus on how users interact with components
2. **Mock External Dependencies**: Mock API calls, WebSocket connections
3. **Test Accessibility**: Verify ARIA attributes and keyboard navigation
4. **Test Error States**: Ensure components handle errors gracefully
5. **Performance Testing**: Test with large datasets and slow networks

---

## 📚 Additional Resources

### Storybook Integration

All components are documented in Storybook with interactive examples:

```bash
npm run storybook
```

### Component Generator

Use the component generator for consistent component creation:

```bash
npm run generate:component MyNewComponent
```

### Related Documentation

- [Design System](./DESIGN_SYSTEM.md) - Design tokens and guidelines
- [API Documentation](./API_DOCUMENTATION.md) - Backend integration
- [Testing Guide](./TESTING.md) - Comprehensive testing strategies

### Support

- **Component Issues**: [GitHub Issues](https://github.com/yourusername/miraikakaku/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/miraikakaku/discussions)
- **Design System Updates**: [Design System Board](https://github.com/yourusername/miraikakaku/projects/1)

---

**Last Updated**: January 2025 | **Components Version**: 1.0.0