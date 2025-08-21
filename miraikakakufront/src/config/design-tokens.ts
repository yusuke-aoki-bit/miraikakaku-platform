/**
 * Design System Tokens
 * Centralized design constants for consistent UI
 */

// ===== Color Palette =====
export const COLORS = {
  // Primary Palette
  PRIMARY: {
    DEFAULT: '#2196f3',
    LIGHT: '#42a5f5',
    DARK: '#1976d2',
    50: '#e3f2fd',
    100: '#bbdefb',
    200: '#90caf9',
    300: '#64b5f6',
    400: '#42a5f5',
    500: '#2196f3',
    600: '#1e88e5',
    700: '#1976d2',
    800: '#1565c0',
    900: '#0d47a1',
  },

  // Semantic Colors
  SUCCESS: {
    DEFAULT: '#10b981',
    LIGHT: '#34d399',
    DARK: '#059669',
  },
  
  DANGER: {
    DEFAULT: '#ef4444',
    LIGHT: '#f87171',
    DARK: '#dc2626',
  },
  
  WARNING: {
    DEFAULT: '#f59e0b',
    LIGHT: '#fbbf24',
    DARK: '#d97706',
  },

  // Neutral Palette
  NEUTRAL: {
    BLACK: '#000000',
    WHITE: '#ffffff',
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },

  // Brand Specific
  BACKGROUND: {
    PRIMARY: '#000000',
    SECONDARY: '#111111',
    TERTIARY: '#1a1a1a',
    CARD: '#2a2a2a',
    OVERLAY: 'rgba(0, 0, 0, 0.8)',
  },
} as const;

// ===== Typography Scale =====
export const TYPOGRAPHY = {
  FONT_FAMILY: {
    PRIMARY: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    MONO: 'SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },

  FONT_SIZE: {
    XS: '0.75rem',    // 12px
    SM: '0.875rem',   // 14px
    BASE: '1rem',     // 16px
    LG: '1.125rem',   // 18px
    XL: '1.25rem',    // 20px
    '2XL': '1.5rem',  // 24px
    '3XL': '1.875rem', // 30px
    '4XL': '2.25rem', // 36px
    '5XL': '3rem',    // 48px
    '6XL': '3.75rem', // 60px
    '7XL': '4.5rem',  // 72px
    '8XL': '6rem',    // 96px
    '9XL': '8rem',    // 128px
  },

  FONT_WEIGHT: {
    THIN: 100,
    EXTRALIGHT: 200,
    LIGHT: 300,
    NORMAL: 400,
    MEDIUM: 500,
    SEMIBOLD: 600,
    BOLD: 700,
    EXTRABOLD: 800,
    BLACK: 900,
  },

  LINE_HEIGHT: {
    NONE: 1,
    TIGHT: 1.25,
    SNUG: 1.375,
    NORMAL: 1.5,
    RELAXED: 1.625,
    LOOSE: 2,
  },
} as const;

// ===== Spacing Scale =====
export const SPACING = {
  // Base unit: 0.25rem (4px)
  0: '0',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem',      // 384px
} as const;

// ===== Border Radius =====
export const BORDER_RADIUS = {
  NONE: '0',
  SM: '0.125rem',   // 2px
  DEFAULT: '0.25rem', // 4px
  MD: '0.375rem',   // 6px
  LG: '0.5rem',     // 8px
  XL: '0.75rem',    // 12px
  '2XL': '1rem',    // 16px
  '3XL': '1.5rem',  // 24px
  FULL: '9999px',
} as const;

// ===== Shadows =====
export const SHADOWS = {
  NONE: 'none',
  SM: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  MD: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  LG: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  XL: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2XL': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  INNER: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  
  // Glass morphism
  GLASS: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  GLASS_LIGHT: '0 4px 16px 0 rgba(31, 38, 135, 0.2)',
} as const;

// ===== Animation & Timing =====
export const ANIMATION = {
  DURATION: {
    INSTANT: '75ms',
    FAST: '150ms',
    NORMAL: '300ms',
    SLOW: '500ms',
    SLOWER: '750ms',
    SLOWEST: '1000ms',
  },

  TIMING: {
    LINEAR: 'linear',
    EASE: 'ease',
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out',
    SMOOTH: 'cubic-bezier(0.4, 0, 0.2, 1)',
    BOUNCE: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  SCALE: {
    HOVER: 1.05,
    ACTIVE: 0.95,
    MODAL: 1.1,
  },
} as const;

// ===== Layout Constraints =====
export const LAYOUT = {
  CONTAINER: {
    SM: '640px',
    MD: '768px',
    LG: '1024px',
    XL: '1280px',
    '2XL': '1536px',
  },

  SIDEBAR: {
    WIDTH: '256px',
    COLLAPSED_WIDTH: '64px',
  },

  HEADER: {
    HEIGHT: '64px',
    MOBILE_HEIGHT: '56px',
  },

  FOOTER: {
    HEIGHT: '80px',
  },
} as const;

// ===== Component Specific =====
export const COMPONENTS = {
  BUTTON: {
    HEIGHT: {
      SM: '32px',
      DEFAULT: '40px',
      LG: '48px',
    },
    PADDING: {
      SM: '8px 12px',
      DEFAULT: '12px 16px',
      LG: '16px 24px',
    },
  },

  INPUT: {
    HEIGHT: {
      SM: '32px',
      DEFAULT: '40px',
      LG: '48px',
    },
  },

  CARD: {
    PADDING: '24px',
    BORDER_WIDTH: '1px',
    MIN_HEIGHT: '120px',
  },

  MODAL: {
    MAX_WIDTH: '500px',
    BACKDROP_BLUR: '4px',
  },
} as const;

// Type exports for usage in components
export type ColorToken = keyof typeof COLORS;
export type SpacingToken = keyof typeof SPACING;
export type BorderRadiusToken = keyof typeof BORDER_RADIUS;
export type ShadowToken = keyof typeof SHADOWS;