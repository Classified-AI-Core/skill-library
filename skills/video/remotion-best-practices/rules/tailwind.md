---
name: tailwind
description: Using TailwindCSS in Remotion - complete setup guide with integration requirements and common gotchas
metadata:
  tags: tailwind, css, styling, configuration, setup
---

# TailwindCSS in Remotion

TailwindCSS works great with Remotion, but requires **special integration setup**. Standard Tailwind installation is NOT enough.

## Critical Requirements (ALL 5 REQUIRED)

### 1. Install Required Packages

```bash
# Standard Tailwind packages
npm install -D tailwindcss postcss autoprefixer

# CRITICAL: Remotion Tailwind integration
npm install -D @remotion/tailwind@[MATCH_REMOTION_VERSION]
```

**⚠️ CRITICAL:** The `@remotion/tailwind` package is REQUIRED. Without it, Tailwind classes will be completely ignored during video rendering.

**Version matching:** The `@remotion/tailwind` version MUST match your `remotion` version exactly:
- remotion@4.0.234 → @remotion/tailwind@4.0.234
- remotion@4.0.250 → @remotion/tailwind@4.0.250

### 2. Enable Tailwind in remotion.config.ts

```typescript
import {Config} from '@remotion/cli/config';
import {enableTailwind} from '@remotion/tailwind';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// CRITICAL: Enable Tailwind CSS processing
Config.overrideWebpackConfig((config) => {
  return enableTailwind(config);
});
```

**⚠️ CRITICAL:** Without `enableTailwind()`, Remotion's Webpack bundler will not process Tailwind CSS.

### 3. Create CSS File with Tailwind Directives

**File:** `src/style.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. Import CSS in Entry Point

**File:** `src/index.tsx`

```typescript
import {registerRoot} from 'remotion';
import {RemotionRoot} from './Root';
import './style.css';  // ⚠️ REQUIRED for Tailwind

registerRoot(RemotionRoot);
```

**⚠️ CRITICAL:** If you forget this import, Tailwind directives will never be processed and all classes will be ignored.

### 5. Configure Tailwind Content Paths

**File:** `tailwind.config.js`

```javascript
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],  // Tell Tailwind where to look
  theme: {
    extend: {},
  },
  plugins: [],
};
```

## Common Mistakes

### Mistake #1: Missing @remotion/tailwind Package

**Symptom:** All Tailwind classes ignored, video renders with no styling

**Fix:** Install `@remotion/tailwind` with matching version:
```bash
npm install -D @remotion/tailwind@4.0.234
```

### Mistake #2: Not Enabling Tailwind in Config

**Symptom:** Tailwind classes ignored even with package installed

**Fix:** Add `enableTailwind()` to remotion.config.ts:
```typescript
import {enableTailwind} from '@remotion/tailwind';

Config.overrideWebpackConfig((config) => {
  return enableTailwind(config);
});
```

### Mistake #3: Forgetting CSS Import

**Symptom:** Components compile but have no styles

**Fix:** Import style.css in src/index.tsx:
```typescript
import './style.css';
```

### Mistake #4: Missing 'flex' Class

**Symptom:** Content appears in top-left corner instead of centered

**The Problem:**
```tsx
// ❌ WRONG - Won't center content
<AbsoluteFill className="items-center justify-center">
```

**The Fix:**
```tsx
// ✅ CORRECT - Must add 'flex' first
<AbsoluteFill className="flex items-center justify-center">
```

**Why:** `items-center` and `justify-center` are **flexbox utilities**. They require `display: flex` to work. AbsoluteFill defaults to `display: block`, so you must add the `flex` class.

## AbsoluteFill + Tailwind Patterns

### Centered Content (Vertical Stack)

```tsx
<AbsoluteFill className="flex flex-col items-center justify-center">
  <h1 className="text-6xl">Title</h1>
  <p className="text-2xl">Subtitle</p>
</AbsoluteFill>
```

### Centered Content (Horizontal Row)

```tsx
<AbsoluteFill className="flex flex-row items-center justify-center gap-4">
  <Icon />
  <Text />
</AbsoluteFill>
```

### Centered with Background Gradient

```tsx
<AbsoluteFill className="flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-800">
  {/* Content */}
</AbsoluteFill>
```

### Grid Layout

```tsx
<AbsoluteFill className="grid grid-cols-2 gap-4 p-8">
  {/* Grid items */}
</AbsoluteFill>
```

## Animation Rules

### NEVER Use CSS Transition/Animation Classes

```tsx
// ❌ WRONG - Will cause flickering during render
<div className="transition-opacity duration-500 animate-fade-in">

// ✅ CORRECT - Use useCurrentFrame + interpolate
<div style={{
  opacity: interpolate(frame, [0, 30], [0, 1])
}}>
```

**Why:** CSS animations are time-based. Remotion is frame-based. CSS animations will flicker and behave incorrectly during video rendering.

### DO Use Tailwind for Layout and Static Styles

```tsx
// ✅ GOOD - Static styles via Tailwind classes
<div className="flex items-center gap-4 bg-blue-500 rounded-lg p-4">

// ✅ GOOD - Animated values via inline styles
<div
  className="text-6xl font-bold"
  style={{
    opacity: interpolate(frame, [0, 30], [0, 1]),
    transform: `scale(${scale})`
  }}
>
```

**Pattern:** Use className for layout/appearance, use style for animations.

## Verification Checklist

After setting up Tailwind in a Remotion project, verify:

- [ ] `@remotion/tailwind` installed (check package.json)
- [ ] `enableTailwind()` in remotion.config.ts
- [ ] `style.css` created with @tailwind directives
- [ ] `style.css` imported in src/index.tsx
- [ ] `tailwind.config.js` has content paths
- [ ] `postcss.config.js` exists
- [ ] Test: Add `className="bg-red-500"` to any component
- [ ] Run `npm start` - should see red background
- [ ] If no red background, Tailwind isn't working

## Troubleshooting

### Tailwind Classes Not Working

**Check 1:** Is @remotion/tailwind installed?
```bash
grep "@remotion/tailwind" package.json
```

**Check 2:** Is enableTailwind() in config?
```bash
grep "enableTailwind" remotion.config.ts
```

**Check 3:** Is CSS imported?
```bash
grep "import.*style.css" src/index.tsx
```

**Check 4:** Are content paths configured?
```bash
grep "content:" tailwind.config.js
```

If any check fails, Tailwind won't work.

### Content Not Centering

**Problem:** Used `items-center justify-center` but forgot `flex` class

**Fix:** Always add `flex` before flexbox utilities:
```tsx
<AbsoluteFill className="flex items-center justify-center">
```

### Black Screen

**Likely cause:** Tailwind not processing

**Debug:**
1. Check all 5 setup requirements above
2. Add `className="bg-red-500"` to AbsoluteFill
3. If still black, Tailwind isn't loading
4. Verify CSS import in index.tsx
5. Verify enableTailwind() in config

## Custom Theme Configuration

### Adding Custom Colors

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [],
};
```

Then use in components:
```tsx
<div className="bg-brand-900 text-brand-50">
```

### Custom Fonts

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
};
```

## Performance Considerations

### Purge Unused Styles

Tailwind automatically purges unused styles based on `content` configuration:

```javascript
content: ['./src/**/*.{ts,tsx}'],  // Only scans these files
```

This keeps the CSS bundle small.

### JIT Mode

Tailwind v3+ uses Just-In-Time mode by default - generates only the classes you use.

No additional configuration needed.

## Complete Setup Example

### Minimal Working Setup

```bash
# 1. Install packages
npm install -D tailwindcss postcss autoprefixer
npm install -D @remotion/tailwind@4.0.234

# 2. Initialize Tailwind
npx tailwindcss init -p

# 3. Update tailwind.config.js
# Set content: ['./src/**/*.{ts,tsx}']

# 4. Create src/style.css
# Add @tailwind directives

# 5. Update remotion.config.ts
# Add enableTailwind()

# 6. Update src/index.tsx
# Import './style.css'

# 7. Test
npm start
# Try className="bg-red-500" - should see red
```

## Integration with Other Tools

### Tailwind + TypeScript

Works seamlessly - no special configuration needed.

### Tailwind + PostCSS

The `postcss.config.js` file is created by `npx tailwindcss init -p`:

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### Tailwind + Custom CSS

You can add custom CSS to `style.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
@layer components {
  .video-title {
    @apply text-6xl font-bold text-center;
  }
}
```

## Related Rules

- [animations.md](animations.md) - For animation patterns (use with Tailwind)
- [compositions.md](compositions.md) - Component composition patterns
- [common-mistakes.md](common-mistakes.md) - Common Tailwind + Remotion mistakes

## Summary

**To use Tailwind in Remotion:**
1. ✅ Install `tailwindcss` AND `@remotion/tailwind`
2. ✅ Enable with `enableTailwind()` in config
3. ✅ Create style.css with @tailwind directives
4. ✅ Import style.css in entry point
5. ✅ Configure content paths in tailwind.config.js

**Critical gotcha:**
- Always use `flex` class before `items-center` or `justify-center`

**For animations:**
- Use Tailwind for static styles (layout, colors, spacing)
- Use inline styles for animated values (opacity, transform)
- Never use CSS transition/animation classes

Missing any required step will cause Tailwind to silently fail.
