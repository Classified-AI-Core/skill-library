---
name: common-mistakes
description: Common mistakes when building with Remotion and how to avoid them
metadata:
  tags: errors, debugging, gotchas, mistakes, best-practices
---

# Common Remotion Mistakes

Avoid these frequent pitfalls when building with Remotion.

## Top 10 Mistakes

### 1. Missing 'flex' Class with Tailwind Centering

**❌ WRONG:**
```tsx
<AbsoluteFill className="items-center justify-center">
```

**✅ CORRECT:**
```tsx
<AbsoluteFill className="flex items-center justify-center">
```

**Why:** `items-center` and `justify-center` are flexbox utilities that require `display: flex` to work.

**Symptom:** Content appears in top-left corner instead of centered.

---

### 2. Using CSS Animations Instead of Frame-Based

**❌ WRONG:**
```tsx
<div className="transition-opacity animate-fade-in">
```

**✅ CORRECT:**
```tsx
const opacity = interpolate(frame, [0, 30], [0, 1]);
<div style={{opacity}}>
```

**Why:** CSS animations are time-based, Remotion is frame-based. CSS animations will flicker during rendering.

**Symptom:** Animations look wrong in rendered video, different from preview.

---

### 3. Forgetting to Import CSS

**❌ WRONG:**
```tsx
// src/index.tsx
import {registerRoot} from 'remotion';
import {RemotionRoot} from './Root';
registerRoot(RemotionRoot);
// Missing CSS import!
```

**✅ CORRECT:**
```tsx
// src/index.tsx
import {registerRoot} from 'remotion';
import {RemotionRoot} from './Root';
import './style.css';  // REQUIRED
registerRoot(RemotionRoot);
```

**Why:** CSS file must be imported for Tailwind to process.

**Symptom:** All Tailwind classes ignored, components have no styling.

---

### 4. Hardcoding System-Dependent Values

**❌ WRONG:**
```typescript
// remotion.config.ts
Config.setConcurrency(50);  // Fails on systems with fewer cores
Config.setPort(3000);       // May conflict with other services
```

**✅ CORRECT:**
```typescript
// Let Remotion auto-detect
// Omit setConcurrency entirely
```

**Why:** Different systems have different resources. Auto-detection is safer.

**Symptom:** Build fails with "Maximum for --concurrency is X" error.

---

### 5. Importing from Wrong Package

**❌ WRONG:**
```tsx
import {useState, useEffect} from 'react';
import {AbsoluteFill} from 'react';  // Wrong!
```

**✅ CORRECT:**
```tsx
import {useCurrentFrame, interpolate, AbsoluteFill, Sequence} from 'remotion';
```

**Why:** Remotion components come from 'remotion' package, not 'react'.

**Symptom:** TypeScript errors, components don't exist.

---

### 6. Not Using useCurrentFrame for Animations

**❌ WRONG:**
```tsx
const [opacity, setOpacity] = useState(0);
useEffect(() => {
  setTimeout(() => setOpacity(1), 1000);
}, []);
```

**✅ CORRECT:**
```tsx
const frame = useCurrentFrame();
const opacity = interpolate(frame, [0, 30], [0, 1]);
```

**Why:** Remotion renders each frame independently. Time-based animations won't work.

**Symptom:** No animation in rendered video.

---

### 7. Missing Extrapolation

**❌ RISKY:**
```tsx
const opacity = interpolate(frame, [0, 30], [0, 1]);
// What happens after frame 30?
```

**✅ SAFE:**
```tsx
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateRight: 'clamp',  // Stay at 1 after frame 30
});
```

**Why:** Without extrapolation, values can exceed bounds causing visual glitches.

**Symptom:** Unexpected values after animation completes (opacity > 1, positions off-screen).

---

### 8. Using Relative Time Instead of Frames

**❌ WRONG:**
```tsx
const progress = Date.now() / 1000;  // Real-time seconds
```

**✅ CORRECT:**
```tsx
const frame = useCurrentFrame();
const {fps} = useVideoConfig();
const progress = frame / fps;  // Frame-based time
```

**Why:** Remotion renders frames independently, not in real-time.

**Symptom:** Animation timing is completely wrong.

---

### 9. Missing Type Definitions

**❌ WRONG:**
```tsx
export const MyComponent = ({title, duration}) => {
  // Props have no types
```

**✅ CORRECT:**
```tsx
interface MyComponentProps {
  title: string;
  duration: number;
}

export const MyComponent: React.FC<MyComponentProps> = ({title, duration}) => {
```

**Why:** TypeScript catches errors early and improves IDE experience.

**Symptom:** Prop typos, incorrect prop usage, poor autocomplete.

---

### 10. Not Clamping Values

**❌ RISKY:**
```tsx
const x = interpolate(frame, [0, 100], [-100, 100]);
// Could go beyond bounds!
```

**✅ SAFE:**
```tsx
const x = interpolate(frame, [0, 100], [-100, 100], {
  extrapolateLeft: 'clamp',   // Don't go below -100
  extrapolateRight: 'clamp',  // Don't go above 100
});
```

**Why:** Unclamped values can cause elements to render off-screen or with invalid CSS.

**Symptom:** Content disappears, renders outside visible area.

---

## Quick Prevention Checklist

Before running `npm run build`, verify:

**Setup:**
- [ ] All required packages installed (including @remotion/tailwind if using)
- [ ] Entry point imports CSS file
- [ ] Remotion config has enableTailwind() if using Tailwind
- [ ] No hardcoded system values in config

**Components:**
- [ ] Use `useCurrentFrame()` for all animations
- [ ] Use `interpolate()` or `spring()`, not CSS animations
- [ ] Add `flex` class before flexbox utilities
- [ ] Include extrapolateRight/Left on interpolations
- [ ] Import from 'remotion', not 'react'
- [ ] Define TypeScript prop interfaces

**Composition:**
- [ ] Sequences have correct from/durationInFrames
- [ ] Total frames match composition duration
- [ ] All compositions registered in Root.tsx

**Testing:**
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Studio opens: `npm start`
- [ ] Test render works: `npm run build`

---

## Debugging Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Black screen | Tailwind not loading | Check all 5 setup steps in tailwind.md |
| Content in corner | Missing 'flex' class | Add 'flex' before centering utilities |
| No animation | Using CSS animations | Use useCurrentFrame + interpolate |
| Build error (concurrency) | Hardcoded concurrency | Remove setConcurrency line |
| TypeScript errors | Wrong imports | Import from 'remotion' not 'react' |
| Flickering | CSS animations | Remove transition/animate classes |
| Content off-screen | Missing clamp | Add extrapolateRight: 'clamp' |

---

## Related Rules

- [tailwind.md](tailwind.md) - Complete Tailwind setup guide
- [animations.md](animations.md) - Animation fundamentals
- [troubleshooting.md](troubleshooting.md) - Detailed debugging guide

---

## Prevention Strategy

**Read these rules FIRST before starting:**
1. [tailwind.md](tailwind.md) - If using Tailwind
2. [animations.md](animations.md) - For any animations
3. This file (common-mistakes.md) - To avoid pitfalls

**Then generate code** following the patterns.

**Finally verify** using the checklist above.

This approach catches 90% of issues before they happen.
