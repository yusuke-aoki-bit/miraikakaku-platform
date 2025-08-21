# 🎨 Miraikakaku Design System

The Miraikakaku design system provides a comprehensive set of design tokens, components, and guidelines to ensure consistent and cohesive user experiences across the entire platform.

## 🌈 Color System

### Brand Colors
Our primary brand colors convey trust, technology, and financial sophistication.

```css
/* Primary Palette */
--brand-primary: #2196f3          /* Main brand blue */
--brand-primary-hover: #1976d2    /* Hover states */
--brand-primary-light: #42a5f5    /* Light variations */
```

### Semantic Colors
Colors with specific meaning and usage contexts.

```css
/* Success - Positive metrics, gains, confirmation */
--status-success: #10b981
--status-success-hover: #059669
--status-success-light: #34d399

/* Danger - Negative metrics, losses, errors */
--status-danger: #ef4444
--status-danger-hover: #dc2626
--status-danger-light: #f87171

/* Warning - Caution, alerts, pending states */
--status-warning: #f59e0b
--status-warning-hover: #d97706
--status-warning-light: #fbbf24
```

### Surface Colors
Background and surface colors create depth and hierarchy.

```css
/* Surface Hierarchy */
--surface-background: #000000         /* Main background */
--surface-background-secondary: #111111  /* Secondary areas */
--surface-card: #1a1a1a              /* Card backgrounds */
--surface-elevated: #2a2a2a          /* Elevated surfaces */
--surface-overlay: rgba(0, 0, 0, 0.8) /* Modal overlays */
```

### Text Colors
Typography colors ensure proper contrast and readability.

```css
/* Text Hierarchy */
--text-primary: #ffffff      /* Primary text, headings */
--text-secondary: #b0b0b0    /* Secondary text */
--text-tertiary: #808080     /* Tertiary text */
--text-muted: #6b6b6b        /* Muted text */
--text-disabled: #555555     /* Disabled text */
```

### Color Usage Guidelines

#### ✅ Do
- Use brand primary for interactive elements and CTAs
- Use semantic colors consistently (green for gains, red for losses)
- Maintain proper contrast ratios (4.5:1 minimum for normal text)
- Use surface colors to create visual hierarchy

#### ❌ Don't
- Mix semantic meanings (don't use red for positive actions)
- Use low contrast color combinations
- Override brand colors without design approval
- Use more than 3 colors in a single component

## 📏 Spacing System

### Base Unit System
Our spacing system is based on a 4px base unit for mathematical consistency.

```css
--space-unit: 0.25rem;  /* 4px base unit */

/* Spacing Scale */
--space-1: 4px    /* calc(var(--space-unit) * 1) */
--space-2: 8px    /* calc(var(--space-unit) * 2) */
--space-3: 12px   /* calc(var(--space-unit) * 3) */
--space-4: 16px   /* calc(var(--space-unit) * 4) */
--space-5: 20px   /* calc(var(--space-unit) * 5) */
--space-6: 24px   /* calc(var(--space-unit) * 6) */
--space-8: 32px   /* calc(var(--space-unit) * 8) */
--space-10: 40px  /* calc(var(--space-unit) * 10) */
--space-12: 48px  /* calc(var(--space-unit) * 12) */
--space-16: 64px  /* calc(var(--space-unit) * 16) */
--space-20: 80px  /* calc(var(--space-unit) * 20) */
```

### Spacing Usage Guide

| Scale | Usage | Example |
|-------|-------|---------|
| `space-1` | Micro spacing | Icon-text gap |
| `space-2` | Small gaps | Button padding (vertical) |
| `space-3` | Standard gaps | Button padding (horizontal) |
| `space-4` | Medium gaps | Card padding, input padding |
| `space-6` | Large gaps | Section padding |
| `space-8` | XL gaps | Component margins |
| `space-12` | Section spacing | Between major sections |
| `space-16+` | Layout spacing | Page margins, major layouts |

## 🔤 Typography

### Font Families
```css
--font-family-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
--font-family-mono: 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', monospace;
```

### Font Scale
```css
/* Font Sizes */
--font-size-xs: 0.75rem;    /* 12px - Fine print, captions */
--font-size-sm: 0.875rem;   /* 14px - Small text, labels */
--font-size-base: 1rem;     /* 16px - Body text */
--font-size-lg: 1.125rem;   /* 18px - Emphasized text */
--font-size-xl: 1.25rem;    /* 20px - Small headings */
--font-size-2xl: 1.5rem;    /* 24px - Section headings */
--font-size-3xl: 1.875rem;  /* 30px - Page headings */
--font-size-4xl: 2.25rem;   /* 36px - Display headings */
--font-size-5xl: 3rem;      /* 48px - Hero headings */
```

### Font Weights
```css
--font-weight-normal: 400;    /* Body text */
--font-weight-medium: 500;    /* Emphasized text */
--font-weight-semibold: 600;  /* Subheadings */
--font-weight-bold: 700;      /* Headings, strong emphasis */
```

### Line Heights
```css
--line-height-tight: 1.25;    /* Headlines */
--line-height-normal: 1.5;    /* Body text */
--line-height-relaxed: 1.625; /* Long-form content */
```

### Typography Scale Usage

| Class | Size | Weight | Usage |
|-------|------|--------|--------|
| `text-xs` | 12px | normal | Captions, timestamps |
| `text-sm` | 14px | normal | Labels, small text |
| `text-base` | 16px | normal | Body text |
| `text-lg` | 18px | medium | Emphasized body |
| `text-xl` | 20px | semibold | Small headings |
| `text-2xl` | 24px | semibold | Section headings |
| `text-3xl` | 30px | bold | Page titles |
| `text-4xl` | 36px | bold | Display headings |
| `text-5xl` | 48px | bold | Hero titles |

## 📦 Component System

### Card Components

#### Base Card
```css
.card-base {
  background: var(--surface-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-2xl);
  backdrop-filter: blur(8px);
  transition: all var(--duration-normal) var(--timing-smooth);
}
```

#### Card Variants
- `card-primary` - Standard content cards
- `card-interactive` - Hoverable/clickable cards
- `card-glass` - Glass morphism effect cards

### Button System

#### Base Button
```css
.btn-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--component-padding-md);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-lg);
  transition: all var(--duration-normal) var(--timing-smooth);
}
```

#### Button Variants
- `btn-primary` - Primary actions
- `btn-secondary` - Secondary actions
- `btn-success` - Positive actions
- `btn-danger` - Destructive actions
- `btn-ghost` - Subtle actions
- `btn-outline-primary` - Outlined style

#### Button Sizes
- `btn-sm` - Compact buttons (32px height)
- `btn-base` - Standard buttons (40px height)
- `btn-lg` - Large buttons (48px height)

### Input System

#### Base Input
```css
.input-base {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  transition: border-color var(--duration-normal);
}

.input-base:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px var(--brand-primary)25;
}
```

## 🎭 Animation System

### Duration Scale
```css
--duration-instant: 75ms;   /* Micro-interactions */
--duration-fast: 150ms;     /* Quick transitions */
--duration-normal: 300ms;   /* Standard transitions */
--duration-slow: 500ms;     /* Emphasis transitions */
--duration-slower: 750ms;   /* Major state changes */
```

### Timing Functions
```css
--timing-linear: linear;
--timing-ease: ease;
--timing-smooth: cubic-bezier(0.4, 0, 0.2, 1);
--timing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Animation Usage Guidelines

#### ✅ Do
- Use consistent timing across similar interactions
- Apply easing curves for natural feel
- Keep animations purposeful and functional
- Test animations on slower devices

#### ❌ Don't
- Overuse animations or make them too flashy
- Use different timings for similar actions
- Animate layout-affecting properties excessively
- Ignore user preferences for reduced motion

## 📐 Layout System

### Grid System
```css
.grid-main { grid-template-columns: 1fr; }
@media (lg) { .grid-main { grid-template-columns: 1fr 1fr 1fr; } }

.grid-2col { grid-template-columns: 1fr; }
@media (md) { .grid-2col { grid-template-columns: 1fr 1fr; } }

.grid-3col { grid-template-columns: 1fr; }
@media (md) { .grid-3col { grid-template-columns: 1fr 1fr; } }
@media (lg) { .grid-3col { grid-template-columns: 1fr 1fr 1fr; } }

.grid-4col { grid-template-columns: 1fr; }
@media (md) { .grid-4col { grid-template-columns: 1fr 1fr; } }
@media (lg) { .grid-4col { grid-template-columns: 1fr 1fr 1fr 1fr; } }
```

### Layout Constants
```css
--layout-header-height: 4rem;        /* 64px */
--layout-sidebar-width: 16rem;       /* 256px */
--layout-sidebar-collapsed: 4rem;    /* 64px */
--layout-container-padding: var(--space-6);
--layout-section-gap: var(--space-12);
```

## 🎯 Stock-Specific Components

### Stock Price Display
```css
.stock-price-up { color: var(--status-success); }
.stock-price-down { color: var(--status-danger); }
.stock-price-neutral { color: var(--text-tertiary); }
```

### Stock Card Component
```css
.stock-card {
  @apply card-interactive p-4;
}

.stock-symbol {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.stock-name {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}
```

### Status Colors
```css
.status-success { 
  color: var(--status-success);
  background: var(--status-success)1a;
  border-color: var(--status-success)4d;
}

.status-danger { 
  color: var(--status-danger);
  background: var(--status-danger)1a;
  border-color: var(--status-danger)4d;
}

.status-warning { 
  color: var(--status-warning);
  background: var(--status-warning)1a;
  border-color: var(--status-warning)4d;
}
```

## 🔧 Implementation Guidelines

### CSS Custom Properties Usage
Always use CSS custom properties for consistent theming:

```css
/* ✅ Good */
.my-component {
  background: var(--surface-card);
  color: var(--text-primary);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}

/* ❌ Avoid */
.my-component {
  background: #1a1a1a;
  color: #ffffff;
  padding: 16px;
  border-radius: 8px;
}
```

### Tailwind Class Usage
Use Tailwind classes that align with our design tokens:

```html
<!-- ✅ Good -->
<div class="card-primary card-content">
  <h2 class="card-title">Title</h2>
  <p class="text-secondary">Content</p>
</div>

<!-- ❌ Avoid -->
<div class="bg-gray-900 p-6 rounded-xl">
  <h2 class="text-xl font-semibold text-white">Title</h2>
  <p class="text-gray-400">Content</p>
</div>
```

## 📋 Component Checklist

When creating new components:

- [ ] Uses design system tokens
- [ ] Follows naming conventions
- [ ] Includes hover/focus states
- [ ] Supports dark theme
- [ ] Is accessible (ARIA, keyboard navigation)
- [ ] Is responsive
- [ ] Has consistent spacing
- [ ] Follows animation guidelines

## 🎨 Tools & Resources

- **Design Tokens**: `/src/config/design-tokens.ts`
- **CSS Variables**: `/src/app/globals.css`
- **Tailwind Config**: `tailwind.config.js`
- **Component Library**: `/src/components/`

## 📚 References

- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Color System](https://material.io/design/color/the-color-system.html)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)