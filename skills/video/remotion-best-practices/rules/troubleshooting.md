---
name: troubleshooting
description: Debugging guide for common Remotion issues - black screens, build errors, animations not working, and more
metadata:
  tags: debugging, errors, troubleshooting, fixes, problems
---

# Remotion Troubleshooting Guide

Step-by-step debugging for common Remotion issues.

## Black Screen Issues

### Symptom: Video renders but shows only black screen

**Most common causes:**

#### 1. Tailwind CSS Not Loading

**Check:**
```bash
# Is @remotion/tailwind installed?
grep "@remotion/tailwind" package.json

# Is enableTailwind in config?
grep "enableTailwind" remotion.config.ts

# Is CSS imported?
grep "import.*style.css" src/index.tsx
```

**Fix:** Follow all 5 steps in [tailwind.md](tailwind.md)

**Quick test:**
```tsx
// Add to any component
<AbsoluteFill className="bg-red-500">
```

If you don't see red, Tailwind isn't working.

#### 2. Background Not Set

**Check:** Do your components have background colors?

```tsx
// ❌ No background - will be transparent/black
<AbsoluteFill>

// ✅ Has background
<AbsoluteFill className="bg-blue-900">
```

#### 3. Z-Index Issues

**Check:** Are components layered incorrectly?

```tsx
// Later Sequences render on top
<Sequence from={0}>...</Sequence>  // Bottom layer
<Sequence from={0}>...</Sequence>  // Top layer (hides bottom)
```

---

## Content Not Centering

### Symptom: Content appears in top-left corner

**Cause:** Missing 'flex' class on AbsoluteFill

**❌ WRONG:**
```tsx
<AbsoluteFill className="items-center justify-center">
```

**✅ CORRECT:**
```tsx
<AbsoluteFill className="flex items-center justify-center">
```

**Why:** Centering utilities require flexbox. See [tailwind.md](tailwind.md) for patterns.

---

## Build Errors

### Error: "Maximum for --concurrency is X"

**Full error:**
```
Error: Maximum for --concurrency is 16 (number of cores on this system)
```

**Cause:** Hardcoded concurrency value in remotion.config.ts

**Fix:** Remove setConcurrency line:
```typescript
// ❌ Remove this:
Config.setConcurrency(50);

// ✅ Let Remotion auto-detect (omit line entirely)
```

---

### Error: "No entry point specified"

**Full error:**
```
No entry point specified. Pass more arguments:
   npx remotion render [entry-point] [composition-name] [out-name]
```

**Cause:** Build script missing entry point

**Fix:** Update package.json:
```json
{
  "scripts": {
    "build": "remotion render src/index.tsx Main out/video.mp4"
  }
}
```

---

### Error: "Cannot find module '@remotion/tailwind'"

**Cause:** Package not installed

**Fix:**
```bash
npm install -D @remotion/tailwind@4.0.234
```

**Note:** Version must match your remotion version exactly.

---

### Error: "ERESOLVE could not resolve" (peer dependency)

**Full error:**
```
npm error ERESOLVE could not resolve
npm error Conflicting peer dependency: @remotion/bundler@4.0.417
```

**Cause:** Version mismatch between remotion packages

**Fix:** Install with exact matching versions:
```bash
npm install -D @remotion/tailwind@4.0.234  # Match remotion@4.0.234
```

Or use --legacy-peer-deps:
```bash
npm install -D @remotion/tailwind --legacy-peer-deps
```

---

## Animations Not Working

### Symptom: Animations look fine in preview but broken in render

**Cause:** Using CSS animations instead of frame-based

**❌ WRONG:**
```tsx
<div className="transition-opacity animate-fade-in">
```

**✅ CORRECT:**
```tsx
const frame = useCurrentFrame();
const opacity = interpolate(frame, [0, 30], [0, 1]);
<div style={{opacity}}>
```

**Why:** CSS animations are time-based. Remotion renders frames independently. See [animations.md](animations.md).

---

### Symptom: Animation values go crazy (negative, > 1, etc.)

**Cause:** Missing extrapolation

**Fix:** Always clamp interpolations:
```tsx
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateRight: 'clamp',  // Stay at 1 after frame 30
  extrapolateLeft: 'clamp',   // Stay at 0 before frame 0
});
```

---

## Tailwind Classes Not Applying

### Systematic Debug Process

**Step 1:** Is @remotion/tailwind installed?
```bash
npm ls @remotion/tailwind
```

**Step 2:** Is enableTailwind in config?
```bash
cat remotion.config.ts | grep enableTailwind
```

**Step 3:** Is CSS file created?
```bash
cat src/style.css
# Should contain @tailwind directives
```

**Step 4:** Is CSS imported?
```bash
cat src/index.tsx | grep style.css
```

**Step 5:** Are content paths configured?
```bash
cat tailwind.config.js | grep content
# Should have: content: ['./src/**/*.{ts,tsx}']
```

If ANY step fails, Tailwind won't work. Fix in order.

---

## TypeScript Errors

### Error: "Property 'X' does not exist on type 'Y'"

**Cause:** Missing or incorrect prop types

**Fix:** Define proper interfaces:
```tsx
interface MyComponentProps {
  title: string;
  duration: number;
}

export const MyComponent: React.FC<MyComponentProps> = ({title, duration}) => {
```

---

### Error: "Cannot find module 'remotion'"

**Cause:** Package not installed

**Fix:**
```bash
npm install remotion @remotion/cli
```

---

### Error: "JSX element type 'X' does not have any construct"

**Cause:** Wrong export or component structure

**Fix:** Ensure proper export:
```tsx
export const MyComponent: React.FC = () => {
  // Component code
};
```

---

## Studio Won't Start

### Error: "Port 3000 is already in use"

**Fix:** Use different port:
```bash
remotion studio --port 3001
```

Or update package.json:
```json
"start": "remotion studio --port 3001"
```

---

### Error: "Cannot find entry point"

**Fix:** Specify entry point in command:
```bash
remotion studio src/index.tsx
```

Update package.json:
```json
"start": "remotion studio src/index.tsx"
```

---

## Performance Issues

### Symptom: Slow rendering / high memory usage

**Causes:**
1. Too many components re-rendering
2. Expensive calculations every frame
3. Large unoptimized assets
4. Missing memoization

**Fixes:**

**1. Memoize expensive calculations:**
```tsx
const expensiveValue = useMemo(() => {
  return heavyCalculation();
}, [dependency]);
```

**2. Memoize child components:**
```tsx
const MemoizedChild = React.memo(ChildComponent);
```

**3. Optimize assets:**
- Compress images
- Use appropriate video codecs
- Reduce resolution if possible

**4. Use Sequence for optimization:**
```tsx
// Only renders when in frame range
<Sequence from={100} durationInFrames={50}>
  <ExpensiveComponent />
</Sequence>
```

---

## Render Quality Issues

### Symptom: Video looks pixelated or blurry

**Fix:** Increase output quality in config:
```typescript
Config.setVideoImageFormat('png');  // Better than jpeg
Config.setQuality(90);  // 0-100, higher = better
```

---

### Symptom: Colors look different in render vs preview

**Cause:** Color space differences

**Fix:** Set codec explicitly:
```typescript
Config.setCodec('h264-mkv');  // Or 'prores' for better color
```

---

## Asset Loading Issues

### Error: "Cannot find asset"

**Cause:** Wrong file path

**Fix:** Use staticFile() for public assets:
```tsx
import {staticFile} from 'remotion';

<Img src={staticFile('image.png')} />  // From public/image.png
```

Or use imports for bundled assets:
```tsx
import logoSrc from './assets/logo.png';

<Img src={logoSrc} />
```

---

### Error: "Audio/Video won't load"

**Check:**
1. File format supported? (mp4, webm for video; mp3, wav for audio)
2. File path correct?
3. File exists in public/ or imported?

**Fix:** Verify file:
```bash
ls public/myfile.mp4
```

Use Video component correctly:
```tsx
import {Video, staticFile} from 'remotion';

<Video src={staticFile('video.mp4')} />
```

---

## Composition Issues

### Error: "Composition 'X' not found"

**Cause:** Composition not registered in Root.tsx

**Fix:** Add to RemotionRoot:
```tsx
<Composition
  id="MyComposition"
  component={MyComposition}
  durationInFrames={300}
  fps={30}
  width={1920}
  height={1080}
/>
```

---

### Symptom: Sequences don't appear

**Cause:** from + durationInFrames outside composition range

**Example:**
```tsx
// Composition is 300 frames
<Composition durationInFrames={300} />

// Sequence starts at frame 350 - NEVER VISIBLE!
<Sequence from={350} durationInFrames={50}>
```

**Fix:** Ensure sequences fit within composition:
```tsx
<Sequence from={0} durationInFrames={100}>   // 0-100 ✓
<Sequence from={100} durationInFrames={100}> // 100-200 ✓
<Sequence from={200} durationInFrames={100}> // 200-300 ✓
```

---

## Getting Help

### Enable Verbose Logging

```bash
remotion render src/index.tsx Main out/video.mp4 --log=verbose
```

### Check Remotion Version

```bash
npx remotion versions
```

### Common Error Messages

**"Exceeded timeout while waiting for... "**
- Increase timeout: `--timeout=120000`
- Or fix slow component code

**"No compositions found"**
- Check Root.tsx exports RemotionRoot
- Check Composition components are imported
- Verify entry point is correct

**"Module not found"**
- Run `npm install`
- Check import paths are correct
- Verify file extensions (.tsx not .ts for JSX)

---

## Best Practices to Avoid Issues

1. **Start simple** - Get basic composition working first
2. **Test frequently** - Run `npm start` after each component
3. **Use TypeScript** - Catches errors early
4. **Follow checklists** - See [common-mistakes.md](common-mistakes.md)
5. **Read error messages** - They're usually accurate
6. **Check the docs** - [remotion.dev/docs](https://remotion.dev/docs)

---

## Still Stuck?

If you've tried everything:

1. Check [common-mistakes.md](common-mistakes.md) - Top 10 mistakes
2. Check [tailwind.md](tailwind.md) - If using Tailwind
3. Simplify - Remove complexity until it works
4. Compare with working example
5. Check Remotion Discord/GitHub issues

Most issues are configuration-related and can be fixed by verifying all setup steps.
