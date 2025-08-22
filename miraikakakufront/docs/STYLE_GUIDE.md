# 🎨 Miraikakaku Frontend Style Guide

## 📅 Last Updated: 2025-08-22

## 🎯 **Overview**

This style guide ensures consistent UI/UX across the Miraikakaku financial platform. All components follow a unified design system with centralized tokens and standardized patterns.

## 🏗️ **Architecture**

### **Design System Structure**
```
src/config/
├── constants.ts          # Application constants & magic numbers
├── design-tokens.ts      # Centralized design tokens
└── ...

tailwind.config.js        # Integrated with design tokens
src/app/globals.css       # Global styles
```

## 🎨 **Design Tokens**

### **Color Palette**

#### **Primary Colors**
```typescript
// Usage: bg-primary-500, text-primary-DEFAULT
primary: {
  DEFAULT: '#2196f3',  // Main brand color
  50: '#e3f2fd',       // Lightest
  500: '#2196f3',      // Standard
  900: '#0d47a1',      // Darkest
}
```

#### **Semantic Colors**
```typescript
success: { DEFAULT: '#10b981', LIGHT: '#34d399', DARK: '#059669' }
danger:  { DEFAULT: '#ef4444', LIGHT: '#f87171', DARK: '#dc2626' }
warning: { DEFAULT: '#f59e0b', LIGHT: '#fbbf24', DARK: '#d97706' }
```

#### **Background Hierarchy**
```typescript
background: {
  PRIMARY: '#000000',    // Main background
  SECONDARY: '#111111',  // Card backgrounds
  TERTIARY: '#1a1a1a',   // Elevated elements
  CARD: '#2a2a2a',       // Component cards
}
```

### **Typography Scale**

#### **Font Sizes** (with line heights)
```typescript
xs:   '0.75rem'   // 12px - Small labels
sm:   '0.875rem'  // 14px - Secondary text
base: '1rem'      // 16px - Body text
lg:   '1.125rem'  // 18px - Emphasized text
xl:   '1.25rem'   // 20px - Headings
2xl:  '1.5rem'    // 24px - Section titles
3xl:  '1.875rem'  // 30px - Page titles
```

#### **Font Weights**
```typescript
LIGHT: 300     // Subtle text
NORMAL: 400    // Body text
MEDIUM: 500    // Emphasized
SEMIBOLD: 600  // Headings
BOLD: 700      // Strong emphasis
```

### **Spacing System**

#### **Base Unit: 0.25rem (4px)**
```typescript
1:  '0.25rem'   // 4px  - Tight spacing
2:  '0.5rem'    // 8px  - Small spacing
4:  '1rem'      // 16px - Standard spacing
6:  '1.5rem'    // 24px - Layout gap
8:  '2rem'      // 32px - Section padding
12: '3rem'      // 48px - Large sections
```

## 🧩 **Component Standards**

### **Button Variants**

#### **Primary Button**
```tsx
<button className="bg-primary-500 hover:bg-primary-600 text-white 
                   px-4 py-2 rounded-md transition-colors fast">
  Primary Action
</button>
```

#### **Secondary Button**
```tsx
<button className="border border-primary-500 text-primary-500 
                   hover:bg-primary-50 px-4 py-2 rounded-md 
                   transition-colors fast">
  Secondary Action
</button>
```

### **Card Component**
```tsx
<div className="bg-background-CARD border border-background-TERTIARY 
                rounded-lg p-6 shadow-md">
  {/* Card content */}
</div>
```

### **Input Fields**
```tsx
<input className="bg-background-SECONDARY border border-background-TERTIARY 
                  rounded-md px-3 py-2 text-neutral-WHITE 
                  focus:ring-2 focus:ring-primary-500 focus:border-transparent
                  transition-all fast" />
```

## 📱 **Responsive Design**

### **Breakpoint Usage**
```typescript
// Mobile First Approach
sm:  '640px'   // Small tablets
md:  '768px'   // Tablets
lg:  '1024px'  // Desktop
xl:  '1280px'  // Large desktop
2xl: '1536px'  // Extra large
```

### **Component Responsive Pattern**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Responsive grid layout */}
</div>
```

## ⚡ **Animation Standards**

### **Transition Durations**
```typescript
instant: '75ms'   // Immediate feedback
fast: '150ms'     // Hover effects
normal: '300ms'   // Standard transitions
slow: '500ms'     // Complex animations
```

### **Common Animations**
```tsx
// Hover effect
"hover:scale-105 transition-transform fast"

// Fade in
"animate-fade-in"

// Slide up
"animate-slide-up"
```

## 🚫 **Anti-Patterns**

### **❌ Avoid These**

1. **Hardcoded Values**
```tsx
// ❌ DON'T
<div style={{ padding: '24px', margin: '16px' }}>

// ✅ DO
<div className="p-6 m-4">
```

2. **Inconsistent Colors**
```tsx
// ❌ DON'T
<div className="bg-gray-800 text-gray-300">

// ✅ DO
<div className="bg-background-CARD text-neutral-400">
```

3. **Magic Numbers**
```tsx
// ❌ DON'T
const accuracy = 75 + Math.random() * 20;

// ✅ DO
const accuracy = INVESTMENT_CONFIG.LSTM_ACCURACY.BASE + 
                 Math.random() * INVESTMENT_CONFIG.LSTM_ACCURACY.VARIANCE;
```

## 📏 **Layout Patterns**

### **Page Layout**
```tsx
<div className="min-h-screen bg-background-PRIMARY">
  <Header />
  <main className="container mx-auto px-6 py-8">
    <section className="space-y-6">
      {/* Content sections */}
    </section>
  </main>
  <Footer />
</div>
```

### **Card Grid**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <Card key={item.id} className="p-6">
      {/* Card content */}
    </Card>
  ))}
</div>
```

### **Form Layout**
```tsx
<form className="space-y-4 max-w-md">
  <div className="space-y-2">
    <label className="block text-sm font-medium text-neutral-300">
      Field Label
    </label>
    <input className="w-full px-3 py-2 bg-background-SECONDARY 
                      border border-background-TERTIARY rounded-md" />
  </div>
</form>
```

## 🎯 **Best Practices**

### **1. Use Design Tokens**
Always reference `design-tokens.ts` for consistent values.

### **2. Component Composition**
```tsx
// ✅ Compose components from tokens
const ButtonVariants = {
  primary: 'bg-primary-500 text-white',
  secondary: 'border border-primary-500 text-primary-500',
  danger: 'bg-danger-500 text-white',
};
```

### **3. Consistent Spacing**
Use the spacing scale for predictable layouts.

### **4. Semantic Class Names**
```tsx
// ✅ Semantic naming
<div className="dashboard-card financial-metric-display">

// ❌ Generic naming  
<div className="box1 thing">
```

## 🔧 **Development Workflow**

### **1. Before Adding Styles**
- Check if design tokens exist
- Verify responsive behavior
- Consider dark mode (already implemented)

### **2. New Component Checklist**
- [ ] Uses design tokens
- [ ] Responsive design
- [ ] Consistent spacing
- [ ] Proper typography scale
- [ ] Accessible contrast ratios
- [ ] Smooth animations

### **3. Code Review Focus**
- No hardcoded values
- Consistent pattern usage
- Proper responsive design
- Performance considerations

## 📊 **Component Library Reference**

### **Available Components**
- `StockSearch` - Stock search with suggestions
- `ThumbnailChart` - Compact price visualization
- `SkeletonLoader` - Loading state component
- `ToastNotification` - User feedback
- `CommandPalette` - Quick actions
- `RealTimeDashboard` - Live data display

### **Utility Classes**
```css
/* Custom utilities in globals.css */
.glass-morphism { backdrop-filter: blur(10px); }
.text-gradient { background: linear-gradient(...); }
.financial-card { /* Financial-specific styling */ }
```

## 🌟 **Innovation Guidelines**

### **Financial UI Patterns**
- Price changes: Green (up) / Red (down)
- High confidence: Stronger colors
- Low confidence: Muted colors
- Real-time data: Subtle animations

### **Data Visualization**
- Consistent chart colors
- Clear axis labels
- Responsive chart sizing
- Accessible color combinations

---

## 📚 **Resources**

- **Design Tokens**: `src/config/design-tokens.ts`
- **Tailwind Config**: `tailwind.config.js`
- **Global Styles**: `src/app/globals.css`
- **Constants**: `src/config/constants.ts`

---

## 🔄 **Migration Path**

### **Phase 1: Token Integration** ✅
- Design tokens created
- Tailwind integration complete
- Magic numbers centralized

### **Phase 2: Component Standardization** (Current)
- Standardize existing components
- Create component library
- Document patterns

### **Phase 3: Optimization**
- Performance optimization
- Bundle size reduction
- A11y improvements

---

*Style Guide maintained by Frontend Team*  
*Last updated: 2025-08-22*