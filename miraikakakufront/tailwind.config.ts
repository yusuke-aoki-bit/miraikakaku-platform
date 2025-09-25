
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}"
    "./pages/**/*.{js,ts,jsx,tsx,mdx}"
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
    "./src/**/*.{js,ts,jsx,tsx,mdx}"
  ]
  theme: {
    extend: {
      colors: {
        // Map CSS variables to Tailwind colors for consistency
        primary: {
          DEFAULT: 'var(--yt-music-primary)'
          hover: 'var(--yt-music-primary-hover)'
        }
        secondary: 'var(--yt-music-secondary)'
        accent: 'var(--yt-music-accent)'
        success: {
          DEFAULT: 'var(--yt-music-success)'
          hover: 'var(--yt-music-success-hover)'
        }
        warning: {
          DEFAULT: 'var(--yt-music-warning)'
          hover: 'var(--yt-music-warning-hover)'
        }
        error: {
          DEFAULT: 'var(--yt-music-error)'
          hover: 'var(--yt-music-error-hover)'
        }
        info: {
          DEFAULT: 'var(--yt-music-info)'
          hover: 'var(--yt-music-info-hover)'
        }
        surface: {
          DEFAULT: 'var(--yt-music-surface)'
          variant: 'var(--yt-music-surface-variant)'
          hover: 'var(--yt-music-surface-hover)'
        }
        text: {
          primary: 'var(--yt-music-text-primary)'
          secondary: 'var(--yt-music-text-secondary)'
          disabled: 'var(--yt-music-text-disabled)'
        }
        border: {
          DEFAULT: 'var(--yt-music-border)'
        }
        content: {
          bg: 'var(--content-bg)'
          text: 'var(--content-text)'
          'text-secondary': 'var(--content-text-secondary)'
          border: 'var(--content-border)'
        }
        chart: {
          blue: 'var(--yt-music-chart-blue)'
          red: 'var(--yt-music-chart-red)'
          green: 'var(--yt-music-chart-green)'
          orange: 'var(--yt-music-chart-orange)'
          purple: 'var(--yt-music-chart-purple)'
        }
      }
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out'
        'slide-up': 'slideUp 0.3s ease-out'
      }
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' }
          '100%': { opacity: '1' }
        }
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' }
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    }
  }
  plugins: []
};
export default config;
