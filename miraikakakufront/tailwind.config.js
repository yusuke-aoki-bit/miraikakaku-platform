/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'youtube-red': {
          500: '#FF0000',
          600: '#CC0000',
          700: '#B30000',
        },
        'youtube-dark': {
          50: '#0F0F0F',
          100: '#1A1A1A',
          200: '#272727',
          300: '#3F3F3F',
          400: '#606060',
          500: '#909090',
        },
        'gradient-pink': {
          500: '#FF1744',
          600: '#E91E63',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'youtube-gradient': 'linear-gradient(135deg, #FF0000 0%, #FF1744 50%, #E91E63 100%)',
        'dark-gradient': 'linear-gradient(135deg, #0F0F0F 0%, #1A1A1A 50%, #272727 100%)',
      },
      backdropBlur: {
        'xs': '2px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}