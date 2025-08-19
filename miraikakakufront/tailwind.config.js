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
        'brand-primary': '#DC2626', // A vibrant red for primary actions and branding
        'brand-secondary': '#EC4899', // A complementary pink for accents
        'brand-accent': '#8B5CF6', // A purple for highlights or interactive elements
        'dark-bg': '#0A0A0A', // Main background color
        'dark-card': '#1A1A1A', // Background for cards and sections
        'dark-border': '#3F3F3F', // Border color for elements
        'text-light': '#E5E7EB', // Light text color for dark backgrounds
        'text-medium': '#9CA3AF', // Medium gray text for secondary info
        'text-dark': '#6B7280', // Dark gray text for tertiary info
      },
      spacing: {
        'layout-gap': '24px', // Consistent spacing for sections and cards
        'section-py': '48px', // Vertical padding for main sections
        'section-px': '32px', // Horizontal padding for main sections
      },
      borderRadius: {
        'card-lg': '16px', // Large border radius for cards
        'card-md': '12px', // Medium border radius
        'card-sm': '8px', // Small border radius
      },
      boxShadow: {
        'glass-light': '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
        'glass-dark': '0 10px 15px rgba(0, 0, 0, 0.2), 0 4px 6px rgba(0, 0, 0, 0.1)',
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, var(--tw-colors-brand-primary) 0%, var(--tw-colors-brand-secondary) 100%)',
        'gradient-dark': 'linear-gradient(135deg, var(--tw-colors-dark-bg) 0%, var(--tw-colors-dark-card) 100%)',
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
