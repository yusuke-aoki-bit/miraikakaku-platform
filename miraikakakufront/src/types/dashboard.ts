export type WidgetType = 
  | 'price-prediction-chart'
  | 'data-table'
  | 'kpi-scorecard'
  | 'news-sentiment'
  | 'market-overview'
  | 'portfolio-summary'
  | 'watchlist'
  | 'real-time-prices'
  | 'technical-indicators'
  | 'risk-analysis'
  | 'trading-history'
  | 'alerts-panel';

export interface WidgetSize {
  width: number; // 1-24 grid columns
  height: number; // 1-18 grid rows
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
}

export interface WidgetPosition {
  x: number; // 0-23 (24 column grid)
  y: number; // 0-17 (18 row grid)
}

export interface Widget {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  position: WidgetPosition;
  config: WidgetConfig;
  isVisible: boolean;
  isLocked: boolean;
  userLevel: 'beginner' | 'intermediate' | 'advanced';
  createdAt: Date;
  updatedAt: Date;
}

export interface WidgetConfig {
  [key: string]: any;
  refreshInterval?: number; // milliseconds
  theme?: 'light' | 'dark' | 'auto';
  showTitle?: boolean;
  allowFullscreen?: boolean;
  customSettings?: Record<string, any>;
}

export interface DashboardLayout {
  id: string;
  name: string;
  description?: string;
  widgets: Widget[];
  gridColumns: number; // Default 24
  gridRows: number; // Default 18
  isDefault: boolean;
  userMode: 'light' | 'pro';
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface GridConfig {
  columns: number;
  rows: number;
  gapSize: number; // px
  containerPadding: number; // px
  breakpoints: {
    mobile: number;
    tablet: number;
    desktop: number;
    ultrawide: number;
  };
}

export interface DashboardTheme {
  name: string;
  colors: {
    background: string;
    cardBackground: string;
    text: string;
    accent: string;
    success: string;
    warning: string;
    error: string;
  };
  borderRadius: number;
  shadows: boolean;
  animations: boolean;
}

// Pre-defined widget sizes
export const WIDGET_SIZES = {
  'xs': { width: 3, height: 2 },
  'sm': { width: 6, height: 4 },
  'md': { width: 9, height: 6 },
  'lg': { width: 12, height: 8 },
  'xl': { width: 18, height: 12 },
  'full': { width: 24, height: 18 },
  
  // Specialized sizes
  'card': { width: 6, height: 4 },
  'chart': { width: 12, height: 8 },
  'table': { width: 18, height: 10 },
  'kpi': { width: 4, height: 3 },
  'news': { width: 8, height: 12 },
  'sidebar': { width: 6, height: 18 }
} as const;

export const DEFAULT_GRID_CONFIG: GridConfig = {
  columns: 24,
  rows: 18,
  gapSize: 16,
  containerPadding: 24,
  breakpoints: {
    mobile: 480,
    tablet: 1024,
    desktop: 1200,
    ultrawide: 1920
  }
};