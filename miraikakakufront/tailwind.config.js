/** @type {import('tailwindcss').Config} */
const { COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS, SHADOWS, ANIMATION } = require('./src/config/design-tokens');

module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Design Token Integration
        primary: COLORS.PRIMARY,
        success: COLORS.SUCCESS,
        danger: COLORS.DANGER,
        warning: COLORS.WARNING,
        neutral: COLORS.NEUTRAL,
        background: COLORS.BACKGROUND,
        
        // Legacy compatibility (to be phased out)
        'brand-primary': COLORS.PRIMARY.DEFAULT,
        'brand-secondary': COLORS.PRIMARY.LIGHT,
        'brand-accent': COLORS.PRIMARY.DARK,
        'dark-bg': COLORS.BACKGROUND.PRIMARY,
        'dark-card': COLORS.BACKGROUND.CARD,
        'dark-border': COLORS.BACKGROUND.TERTIARY,
        'text-light': COLORS.NEUTRAL.WHITE,
        'text-medium': COLORS.NEUTRAL[400],
        'text-dark': COLORS.NEUTRAL[600],
        
        // Semantic colors
        'icon-red': COLORS.DANGER.DEFAULT,
        'icon-green': COLORS.SUCCESS.DEFAULT,
        'text-white': COLORS.NEUTRAL.WHITE,
      },
      
      spacing: {
        ...SPACING,
        // Layout specific
        'layout-gap': '24px',
        'section-py': '48px',
        'section-px': '32px',
      },
      
      borderRadius: {
        ...BORDER_RADIUS,
        // Component specific
        'card-lg': '16px',
        'card-md': '12px', 
        'card-sm': '8px',
      },
      
      boxShadow: {
        ...SHADOWS,
        // Glass morphism
        'glass-light': SHADOWS.GLASS_LIGHT,
        'glass-dark': SHADOWS.GLASS,
      },
      
      fontSize: {
        xs: [TYPOGRAPHY.FONT_SIZE.XS, { lineHeight: TYPOGRAPHY.LINE_HEIGHT.TIGHT }],
        sm: [TYPOGRAPHY.FONT_SIZE.SM, { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NORMAL }],
        base: [TYPOGRAPHY.FONT_SIZE.BASE, { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NORMAL }],
        lg: [TYPOGRAPHY.FONT_SIZE.LG, { lineHeight: TYPOGRAPHY.LINE_HEIGHT.RELAXED }],
        xl: [TYPOGRAPHY.FONT_SIZE.XL, { lineHeight: TYPOGRAPHY.LINE_HEIGHT.RELAXED }],
        '2xl': [TYPOGRAPHY.FONT_SIZE['2XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.TIGHT }],
        '3xl': [TYPOGRAPHY.FONT_SIZE['3XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.TIGHT }],
        '4xl': [TYPOGRAPHY.FONT_SIZE['4XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.TIGHT }],
        '5xl': [TYPOGRAPHY.FONT_SIZE['5XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NONE }],
        '6xl': [TYPOGRAPHY.FONT_SIZE['6XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NONE }],
        '7xl': [TYPOGRAPHY.FONT_SIZE['7XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NONE }],
        '8xl': [TYPOGRAPHY.FONT_SIZE['8XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NONE }],
        '9xl': [TYPOGRAPHY.FONT_SIZE['9XL'], { lineHeight: TYPOGRAPHY.LINE_HEIGHT.NONE }],
      },
      
      fontFamily: {
        sans: TYPOGRAPHY.FONT_FAMILY.PRIMARY.split(', '),
        mono: TYPOGRAPHY.FONT_FAMILY.MONO.split(', '),
      },
      
      fontWeight: TYPOGRAPHY.FONT_WEIGHT,
      
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scale-in': 'scaleIn 0.2s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s ease-in-out',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: `scale(${ANIMATION.SCALE.ACTIVE})`, opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      
      transitionDuration: {
        instant: ANIMATION.DURATION.INSTANT,
        fast: ANIMATION.DURATION.FAST,
        normal: ANIMATION.DURATION.NORMAL,
        slow: ANIMATION.DURATION.SLOW,
        slower: ANIMATION.DURATION.SLOWER,
        slowest: ANIMATION.DURATION.SLOWEST,
      },
      
      transitionTimingFunction: {
        'ease-smooth': ANIMATION.TIMING.SMOOTH,
        'ease-bounce': ANIMATION.TIMING.BOUNCE,
      },
      
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [],
}