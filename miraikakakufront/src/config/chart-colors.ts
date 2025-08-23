/**
 * Chart Color Configuration
 * Colors aligned with the design system for consistent chart styling
 */

import { COLORS } from './design-tokens';

// Chart-specific color palette based on design tokens
export const CHART_COLORS = {
  // Price and Historical Data
  PRICE: {
    UP: COLORS.SUCCESS.DEFAULT,        // #10b981 - Green for price increases
    DOWN: COLORS.DANGER.DEFAULT,       // #ef4444 - Red for price decreases
    NEUTRAL: COLORS.PRIMARY.DEFAULT,   // #2196f3 - Blue for neutral/current
  },
  
  // Prediction Models
  PREDICTIONS: {
    LSTM: COLORS.PRIMARY.DEFAULT,      // #2196f3 - Blue for LSTM predictions
    VERTEX_AI: '#8b5cf6',              // Purple for VertexAI predictions
    ENSEMBLE: COLORS.WARNING.DEFAULT,  // #f59e0b - Orange for ensemble models
  },
  
  // Chart Elements
  CANDLESTICK: {
    UP_BODY: COLORS.SUCCESS.DEFAULT,
    UP_BORDER: COLORS.SUCCESS.DARK,
    DOWN_BODY: COLORS.DANGER.DEFAULT,
    DOWN_BORDER: COLORS.DANGER.DARK,
  },
  
  // Volume
  VOLUME: {
    PRIMARY: '#6366f1',                // Indigo for volume bars
    SECONDARY: '#8b5cf6',             // Purple for secondary volume
  },
  
  // Technical Indicators
  INDICATORS: {
    SMA_20: COLORS.WARNING.DEFAULT,    // #f59e0b - Orange for SMA 20
    SMA_50: '#f97316',                 // Orange 500 for SMA 50
    EMA: '#06b6d4',                    // Cyan for EMA
    BOLLINGER_UPPER: '#ec4899',        // Pink for Bollinger upper
    BOLLINGER_LOWER: '#ec4899',        // Pink for Bollinger lower
    RSI: '#a855f7',                    // Purple for RSI
  },
  
  // Background and Grid
  BACKGROUND: {
    CHART: COLORS.BACKGROUND.TERTIARY, // #1a1a1a
    GRID: 'rgba(255, 255, 255, 0.1)',
    AXIS: 'rgba(255, 255, 255, 0.3)',
  },
  
  // Text
  TEXT: {
    PRIMARY: COLORS.NEUTRAL.WHITE,     // #ffffff
    SECONDARY: '#b0b0b0',              // Light gray
    TERTIARY: '#808080',               // Medium gray
  },
  
  // Chart categories for different data series
  SERIES: [
    COLORS.PRIMARY.DEFAULT,            // #2196f3 - Blue
    COLORS.SUCCESS.DEFAULT,            // #10b981 - Green  
    COLORS.WARNING.DEFAULT,            // #f59e0b - Orange
    '#8b5cf6',                         // Purple
    '#ec4899',                         // Pink
    '#06b6d4',                         // Cyan
    '#84cc16',                         // Lime
    '#f97316',                         // Orange 500
  ],
} as const;

// Helper functions for chart colors
export const getChartColors = {
  // Get color for price movement
  priceMovement: (change: number) => {
    if (change > 0) return CHART_COLORS.PRICE.UP;
    if (change < 0) return CHART_COLORS.PRICE.DOWN;
    return CHART_COLORS.PRICE.NEUTRAL;
  },
  
  // Get candlestick colors
  candlestick: (isUp: boolean) => ({
    body: isUp ? CHART_COLORS.CANDLESTICK.UP_BODY : CHART_COLORS.CANDLESTICK.DOWN_BODY,
    border: isUp ? CHART_COLORS.CANDLESTICK.UP_BORDER : CHART_COLORS.CANDLESTICK.DOWN_BORDER,
  }),
  
  // Get series color by index
  series: (index: number) => CHART_COLORS.SERIES[index % CHART_COLORS.SERIES.length],
  
  // Get prediction model color
  prediction: (model: 'lstm' | 'vertexai' | 'ensemble') => {
    switch (model.toLowerCase()) {
      case 'lstm': return CHART_COLORS.PREDICTIONS.LSTM;
      case 'vertexai': return CHART_COLORS.PREDICTIONS.VERTEX_AI;
      case 'ensemble': return CHART_COLORS.PREDICTIONS.ENSEMBLE;
      default: return CHART_COLORS.PREDICTIONS.LSTM;
    }
  },
};

// Chart.js compatible color configuration
export const CHARTJS_COLORS = {
  borderColor: CHART_COLORS.SERIES,
  backgroundColor: CHART_COLORS.SERIES.map(color => color + '20'), // Add 20% opacity
  pointBackgroundColor: CHART_COLORS.SERIES,
  pointBorderColor: CHART_COLORS.SERIES,
  gridColor: CHART_COLORS.BACKGROUND.GRID,
  tickColor: CHART_COLORS.TEXT.SECONDARY,
};

// Plotly compatible color configuration
export const PLOTLY_COLORS = {
  colorway: CHART_COLORS.SERIES,
  paper_bgcolor: COLORS.BACKGROUND.PRIMARY,
  plot_bgcolor: COLORS.BACKGROUND.TERTIARY,
  font: { color: CHART_COLORS.TEXT.PRIMARY },
  grid: { color: CHART_COLORS.BACKGROUND.GRID },
  axis: { 
    gridcolor: CHART_COLORS.BACKGROUND.GRID,
    linecolor: CHART_COLORS.BACKGROUND.AXIS,
  },
};