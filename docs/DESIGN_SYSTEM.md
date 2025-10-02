# Koko Trader Design System

## Typography

### Fonts
- **Primary**: Inter (UI elements, body text)
- **Monospace**: IBM Plex Sans (headings, data, numbers, labels)

### Font Sizes
- Extra Small: `0.813rem` (13px)
- Small: `0.875rem` (14px)
- Base: `0.938rem` (15px)
- Medium: `1rem` (16px)
- Large: `1.125rem` (18px)
- XL: `1.375rem` (22px)

### Font Weights
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## Colors

### Backgrounds
- **Primary**: `#0a0e17` - Main background
- **Secondary**: `#141821` - Cards, header
- **Tertiary**: `#1a1f2e` - Hover states, inputs

### Text
- **Primary**: `#e4e7eb` - Main text
- **Secondary**: `#9ca3af` - Subdued text
- **Tertiary**: `#6b7280` - Least prominent

### Borders
- **Default**: `#2d3748`
- **Hover**: `#4a5568`

### Accents
- **Primary**: `#3b82f6` - Interactive elements
- **Hover**: `#2563eb`

### Status Colors
- **Success**: `#10b981` (Green)
- **Success BG**: `#064e3b`
- **Error**: `#ef4444` (Red)
- **Error BG**: `#7f1d1d`
- **Warning**: `#f59e0b` (Orange)
- **Warning BG**: `#78350f`

## Spacing Scale

```css
--space-xs: 0.25rem   /* 4px */
--space-sm: 0.5rem    /* 8px */
--space-md: 1rem      /* 16px */
--space-lg: 1.5rem    /* 24px */
--space-xl: 2rem      /* 32px */
--space-2xl: 3rem     /* 48px */
```

## Border Radius

```css
--radius-sm: 0.375rem  /* 6px */
--radius-md: 0.5rem    /* 8px */
--radius-lg: 0.75rem   /* 12px */
```

## Component Patterns

### Cards
```css
background: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: var(--radius-lg);
padding: var(--space-lg);
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
```

### Buttons
```css
background: var(--bg-tertiary);
border: 1px solid var(--border-color);
color: var(--text-secondary);
padding: var(--space-sm) var(--space-md);
border-radius: var(--radius-md);
font-family: var(--font-mono);
font-weight: 600;
```

### Badges
```css
padding: var(--space-sm) var(--space-md);
border-radius: var(--radius-md);
font-weight: 600;
font-size: 0.813rem;
font-family: var(--font-mono);
letter-spacing: 0.02em;
text-transform: uppercase;
```

### Inputs
```css
background: var(--bg-secondary);
border: 1px solid var(--border-color);
color: var(--text-primary);
padding: var(--space-sm) var(--space-md);
border-radius: var(--radius-md);
font-family: var(--font-mono);
```

## Design Principles

### 1. No Gradients
- Use flat, solid colors
- Clean, modern aesthetic
- Better performance

### 2. Consistent Spacing
- Use spacing scale variables
- Maintain visual rhythm
- Predictable layouts

### 3. Typography Hierarchy
- Inter for readability
- IBM Plex Sans for data/emphasis
- Clear size relationships

### 4. Subtle Transitions
- 200ms ease timing
- Smooth color changes
- No jarring animations

### 5. High Contrast
- Dark backgrounds
- Light text
- Clear visual separation

## Usage Examples

### Signal Badge (LONG)
```jsx
<div className="badge badge-long">
  LONG
</div>
```

CSS:
```css
background: var(--success-bg);
color: var(--success);
border: 1px solid var(--success);
```

### Card Header
```jsx
<div className="card-header">
  <h2 className="card-title">Signal</h2>
</div>
```

CSS:
```css
font-family: var(--font-mono);
font-size: 1.125rem;
font-weight: 600;
color: var(--text-primary);
letter-spacing: -0.02em;
```

### Status Indicator
```jsx
<div className="ws-status connected">
  <div className="status-dot"></div>
  Live
</div>
```

CSS:
```css
background: var(--success-bg);
color: var(--success);
border: 1px solid var(--success);
font-family: var(--font-mono);
```

## Accessibility

- Minimum contrast ratio: 7:1
- Focus states on all interactive elements
- Keyboard navigation support
- Semantic HTML structure

## Performance

- System fonts loaded via Google Fonts
- Preconnect for faster font loading
- CSS variables for theme consistency
- Minimal transitions for smooth 60fps

---

**Koko Trader** - Clean, professional, data-focused design

