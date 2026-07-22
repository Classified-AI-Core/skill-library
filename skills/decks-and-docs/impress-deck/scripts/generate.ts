#!/usr/bin/env bun

import { readFileSync, writeFileSync } from "fs";
import { parseArgs } from "util";

const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    config: { type: "string" },
    out: { type: "string" },
    help: { type: "boolean" },
  },
});

if (values.help || !values.config) {
  console.log(`Usage: bun generate.ts --config <config.json> --out <output.html>

Options:
  --config  Path to presentation config JSON (required)
  --out     Output HTML file path (default: ./presentation.html)
  --help    Show this help

Config format: See SKILL.md for full documentation.`);
  process.exit(values.help ? 0 : 1);
}

interface SlideLayout {
  x?: number;
  y?: number;
  z?: number;
  scale?: number;
  rotate?: number;
  rotateX?: number;
  rotateY?: number;
}

interface Slide {
  id?: string;
  type: string;
  heading?: string;
  subheading?: string;
  body?: string;
  bullets?: string[];
  quote?: string;
  attribution?: string;
  imageUrl?: string;
  caption?: string;
  metrics?: { value: string; label: string }[];
  code?: string;
  language?: string;
  left?: string;
  right?: string;
  html?: string;
  layout?: SlideLayout;
}

interface Theme {
  bg: string;
  text: string;
  heading: string;
  accent: string;
  accentAlt: string;
  muted: string;
  surface: string;
  fontFamily: string;
  headingFont: string;
}

interface Config {
  title: string;
  theme?: string;
  customTheme?: Partial<Theme>;
  transitionDuration?: number;
  layoutStrategy?: string;
  zoom?: number;
  slides: Slide[];
}

const THEMES: Record<string, Theme> = {
  dark: {
    bg: "#0a0a0f",
    text: "#e4e4e7",
    heading: "#ffffff",
    accent: "#3b82f6",
    accentAlt: "#8b5cf6",
    muted: "#71717a",
    surface: "rgba(255,255,255,0.06)",
    fontFamily: "'Inter', 'SF Pro Display', -apple-system, sans-serif",
    headingFont: "'Space Grotesk', 'Inter', sans-serif",
  },
  light: {
    bg: "#fafafa",
    text: "#27272a",
    heading: "#09090b",
    accent: "#4f46e5",
    accentAlt: "#7c3aed",
    muted: "#a1a1aa",
    surface: "rgba(0,0,0,0.04)",
    fontFamily: "'Inter', -apple-system, sans-serif",
    headingFont: "'Space Grotesk', 'Inter', sans-serif",
  },
  midnight: {
    bg: "#0f172a",
    text: "#cbd5e1",
    heading: "#f1f5f9",
    accent: "#38bdf8",
    accentAlt: "#a78bfa",
    muted: "#475569",
    surface: "rgba(148,163,184,0.08)",
    fontFamily: "'Inter', sans-serif",
    headingFont: "'Space Grotesk', sans-serif",
  },
  ember: {
    bg: "#0c0a09",
    text: "#d6d3d1",
    heading: "#fafaf9",
    accent: "#f97316",
    accentAlt: "#ef4444",
    muted: "#78716c",
    surface: "rgba(255,255,255,0.05)",
    fontFamily: "'Inter', sans-serif",
    headingFont: "'Space Grotesk', sans-serif",
  },
  frost: {
    bg: "#0f1729",
    text: "#94a3b8",
    heading: "#e2e8f0",
    accent: "#06b6d4",
    accentAlt: "#22d3ee",
    muted: "#334155",
    surface: "rgba(6,182,212,0.08)",
    fontFamily: "'Inter', sans-serif",
    headingFont: "'Space Grotesk', sans-serif",
  },
};

function resolveTheme(config: Config): Theme {
  const base = THEMES[config.theme || "dark"] || THEMES.dark;
  if (config.theme === "custom" && config.customTheme) {
    return { ...base, ...config.customTheme } as Theme;
  }
  return base;
}

// Layout strategies
function autoLayout(slides: Slide[], strategy: string): Slide[] {
  const count = slides.length;
  return slides.map((slide, i) => {
    if (slide.layout) return slide;
    const layout = calculatePosition(i, count, strategy, slide.type);
    return { ...slide, layout };
  });
}

function calculatePosition(i: number, count: number, strategy: string, type: string): SlideLayout {
  if (type === "overview") {
    return { x: 0, y: 0, scale: Math.max(4, count * 0.8) };
  }

  switch (strategy) {
    case "spiral": {
      const angle = i * 0.8;
      const radius = 800 + i * 400;
      return {
        x: Math.round(Math.cos(angle) * radius),
        y: Math.round(Math.sin(angle) * radius),
        z: i % 3 === 0 ? -200 : 0,
        scale: i === 0 ? 3 : 1,
        rotate: Math.round(angle * (180 / Math.PI) * 0.15),
      };
    }
    case "grid": {
      const cols = Math.ceil(Math.sqrt(count));
      const col = i % cols;
      const row = Math.floor(i / cols);
      return {
        x: col * 1400,
        y: row * 1000,
        scale: i === 0 ? 2 : 1,
      };
    }
    case "scatter": {
      const goldenAngle = 137.508 * (Math.PI / 180);
      const angle = i * goldenAngle;
      const radius = 600 + Math.sqrt(i) * 500;
      return {
        x: Math.round(Math.cos(angle) * radius),
        y: Math.round(Math.sin(angle) * radius),
        z: (i % 4 === 0) ? -400 : (i % 4 === 2) ? -200 : 0,
        scale: i === 0 ? 3 : 0.8 + Math.random() * 0.4,
        rotate: Math.round((Math.random() - 0.5) * 20),
      };
    }
    case "story": {
      const phases = [
        { x: 0, y: 0, scale: 3 },
        ...Array.from({ length: count - 2 }, (_, j) => ({
          x: (j + 1) * 1200,
          y: Math.sin((j + 1) * 0.6) * 400,
          z: j % 3 === 1 ? -300 : 0,
          scale: 1,
          rotate: j % 4 === 2 ? 5 : j % 4 === 3 ? -5 : 0,
        })),
        { x: Math.floor((count - 1) / 2) * 1200, y: 200, scale: count * 0.7 },
      ];
      return phases[i] || { x: i * 1200, y: 0, scale: 1 };
    }
    default: // linear
      return {
        x: i * 1400,
        y: 0,
        scale: i === 0 ? 2 : 1,
      };
  }
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderSlideContent(slide: Slide, theme: Theme): string {
  switch (slide.type) {
    case "title":
      return `
        <div class="slide-title">
          <h1>${escapeHtml(slide.heading || "")}</h1>
          ${slide.subheading ? `<p class="subheading">${escapeHtml(slide.subheading)}</p>` : ""}
        </div>`;

    case "content":
      return `
        <div class="slide-content">
          ${slide.heading ? `<h2>${escapeHtml(slide.heading)}</h2>` : ""}
          ${slide.body ? `<p class="body-text">${escapeHtml(slide.body)}</p>` : ""}
          ${slide.bullets ? `<ul class="bullets">${slide.bullets.map(b => `<li>${escapeHtml(b)}</li>`).join("")}</ul>` : ""}
        </div>`;

    case "image":
      return `
        <div class="slide-image">
          ${slide.heading ? `<h2>${escapeHtml(slide.heading)}</h2>` : ""}
          <img src="${escapeHtml(slide.imageUrl || "")}" alt="${escapeHtml(slide.caption || "")}" />
          ${slide.caption ? `<p class="caption">${escapeHtml(slide.caption)}</p>` : ""}
        </div>`;

    case "quote":
      return `
        <div class="slide-quote">
          <blockquote>"${escapeHtml(slide.quote || "")}"</blockquote>
          ${slide.attribution ? `<cite>— ${escapeHtml(slide.attribution)}</cite>` : ""}
        </div>`;

    case "metrics":
      return `
        <div class="slide-metrics">
          ${slide.heading ? `<h2>${escapeHtml(slide.heading)}</h2>` : ""}
          <div class="metrics-grid">
            ${(slide.metrics || []).map(m => `
              <div class="metric">
                <span class="metric-value">${escapeHtml(m.value)}</span>
                <span class="metric-label">${escapeHtml(m.label)}</span>
              </div>
            `).join("")}
          </div>
        </div>`;

    case "code":
      return `
        <div class="slide-code">
          ${slide.heading ? `<h2>${escapeHtml(slide.heading)}</h2>` : ""}
          <pre><code class="${escapeHtml(slide.language || "")}">${escapeHtml(slide.code || "")}</code></pre>
        </div>`;

    case "split":
      return `
        <div class="slide-split">
          ${slide.heading ? `<h2>${escapeHtml(slide.heading)}</h2>` : ""}
          <div class="split-columns">
            <div class="split-left">${slide.left || ""}</div>
            <div class="split-right">${slide.right || ""}</div>
          </div>
        </div>`;

    case "overview":
      return `<div class="slide-overview"></div>`;

    case "custom":
      return `<div class="slide-custom">${slide.html || ""}</div>`;

    default:
      return `<div class="slide-content"><p>${escapeHtml(slide.body || "")}</p></div>`;
  }
}

function renderStep(slide: Slide, theme: Theme): string {
  const l = slide.layout || {};
  const attrs = [
    `class="step slide-type-${slide.type}"`,
    slide.id ? `id="${escapeHtml(slide.id)}"` : "",
    l.x !== undefined ? `data-x="${l.x}"` : "",
    l.y !== undefined ? `data-y="${l.y}"` : "",
    l.z !== undefined ? `data-z="${l.z}"` : "",
    l.scale !== undefined ? `data-scale="${l.scale}"` : "",
    l.rotate !== undefined ? `data-rotate="${l.rotate}"` : "",
    l.rotateX !== undefined ? `data-rotate-x="${l.rotateX}"` : "",
    l.rotateY !== undefined ? `data-rotate-y="${l.rotateY}"` : "",
  ].filter(Boolean).join(" ");

  return `    <div ${attrs}>${renderSlideContent(slide, theme)}
    </div>`;
}

function generateProgressBar(count: number): string {
  return `
  <div id="progress-bar">
    <div id="progress-fill"></div>
  </div>
  <div id="slide-counter">
    <span id="current-slide">1</span> / <span id="total-slides">${count}</span>
  </div>`;
}

function generateHTML(config: Config): string {
  const theme = resolveTheme(config);
  const strategy = config.layoutStrategy || "story";
  const slides = autoLayout(config.slides, strategy);
  const duration = config.transitionDuration || 1500;
  const slideCount = slides.filter(s => s.type !== "overview").length;

  const stepsHtml = slides.map(s => renderStep(s, theme)).join("\n\n");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(config.title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: ${theme.bg};
      color: ${theme.text};
      font-family: ${theme.fontFamily};
      min-height: 100vh;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    .step {
      width: 900px;
      min-height: 500px;
      padding: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0.15;
      transition: opacity 0.8s ease;
      position: relative;
    }
    .step.active, .step.present {
      opacity: 1;
    }
    .step.past {
      opacity: 0.25;
    }

    /* Title slides */
    .slide-title {
      text-align: center;
      max-width: 100%;
    }
    .slide-title h1 {
      font-family: ${theme.headingFont};
      font-size: 4rem;
      font-weight: 700;
      color: ${theme.heading};
      line-height: 1.1;
      margin-bottom: 24px;
      letter-spacing: -0.02em;
    }
    .slide-title .subheading {
      font-size: 1.5rem;
      font-weight: 300;
      color: ${theme.muted};
      max-width: 600px;
      margin: 0 auto;
      line-height: 1.5;
    }

    /* Content slides */
    .slide-content {
      max-width: 100%;
    }
    .slide-content h2 {
      font-family: ${theme.headingFont};
      font-size: 2.5rem;
      font-weight: 600;
      color: ${theme.heading};
      margin-bottom: 24px;
      letter-spacing: -0.01em;
    }
    .slide-content .body-text {
      font-size: 1.25rem;
      line-height: 1.7;
      color: ${theme.text};
      margin-bottom: 20px;
      max-width: 700px;
    }
    .bullets {
      list-style: none;
      padding: 0;
    }
    .bullets li {
      font-size: 1.2rem;
      line-height: 1.6;
      padding: 10px 0 10px 28px;
      position: relative;
      color: ${theme.text};
    }
    .bullets li::before {
      content: '';
      position: absolute;
      left: 0;
      top: 18px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: ${theme.accent};
    }

    /* Quote slides */
    .slide-quote {
      text-align: center;
      max-width: 750px;
    }
    .slide-quote blockquote {
      font-family: ${theme.headingFont};
      font-size: 2.2rem;
      font-weight: 400;
      line-height: 1.5;
      color: ${theme.heading};
      font-style: italic;
      margin-bottom: 24px;
    }
    .slide-quote cite {
      font-size: 1.1rem;
      color: ${theme.accent};
      font-style: normal;
      font-weight: 500;
    }

    /* Metrics slides */
    .slide-metrics {
      text-align: center;
      width: 100%;
    }
    .slide-metrics h2 {
      font-family: ${theme.headingFont};
      font-size: 2rem;
      color: ${theme.heading};
      margin-bottom: 40px;
    }
    .metrics-grid {
      display: flex;
      gap: 50px;
      justify-content: center;
      flex-wrap: wrap;
    }
    .metric {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 30px;
      background: ${theme.surface};
      border-radius: 16px;
      min-width: 160px;
    }
    .metric-value {
      font-family: ${theme.headingFont};
      font-size: 3.5rem;
      font-weight: 700;
      color: ${theme.accent};
      line-height: 1;
      margin-bottom: 8px;
    }
    .metric-label {
      font-size: 0.95rem;
      color: ${theme.muted};
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    /* Image slides */
    .slide-image {
      text-align: center;
      max-width: 100%;
    }
    .slide-image h2 {
      font-family: ${theme.headingFont};
      font-size: 2rem;
      color: ${theme.heading};
      margin-bottom: 24px;
    }
    .slide-image img {
      max-width: 780px;
      max-height: 400px;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.4);
      object-fit: contain;
    }
    .slide-image .caption {
      font-size: 0.95rem;
      color: ${theme.muted};
      margin-top: 16px;
    }

    /* Code slides */
    .slide-code {
      max-width: 100%;
      width: 100%;
    }
    .slide-code h2 {
      font-family: ${theme.headingFont};
      font-size: 2rem;
      color: ${theme.heading};
      margin-bottom: 24px;
    }
    .slide-code pre {
      background: rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px;
      padding: 30px;
      overflow-x: auto;
      max-width: 100%;
    }
    .slide-code code {
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 0.95rem;
      line-height: 1.6;
      color: ${theme.text};
    }

    /* Split slides */
    .slide-split {
      width: 100%;
    }
    .slide-split h2 {
      font-family: ${theme.headingFont};
      font-size: 2rem;
      color: ${theme.heading};
      margin-bottom: 30px;
    }
    .split-columns {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 40px;
    }
    .split-left, .split-right {
      font-size: 1.1rem;
      line-height: 1.7;
    }

    /* Overview slide */
    .slide-overview {
      display: none;
    }

    /* Content animations */
    .step.present .slide-title h1,
    .step.present .slide-content h2,
    .step.present .slide-metrics h2,
    .step.present .slide-image h2,
    .step.present .slide-code h2,
    .step.present .slide-split h2,
    .step.present .slide-quote blockquote {
      animation: fadeUp 0.6s ease-out both;
    }

    .step.present .subheading,
    .step.present .body-text,
    .step.present .slide-image img,
    .step.present .slide-code pre,
    .step.present .slide-quote cite {
      animation: fadeUp 0.6s ease-out 0.15s both;
    }

    .step.present .bullets li {
      animation: fadeUp 0.5s ease-out both;
    }
    .step.present .bullets li:nth-child(1) { animation-delay: 0.2s; }
    .step.present .bullets li:nth-child(2) { animation-delay: 0.35s; }
    .step.present .bullets li:nth-child(3) { animation-delay: 0.5s; }
    .step.present .bullets li:nth-child(4) { animation-delay: 0.65s; }
    .step.present .bullets li:nth-child(5) { animation-delay: 0.8s; }
    .step.present .bullets li:nth-child(6) { animation-delay: 0.95s; }

    .step.present .metric {
      animation: scaleIn 0.5s ease-out both;
    }
    .step.present .metric:nth-child(1) { animation-delay: 0.15s; }
    .step.present .metric:nth-child(2) { animation-delay: 0.3s; }
    .step.present .metric:nth-child(3) { animation-delay: 0.45s; }
    .step.present .metric:nth-child(4) { animation-delay: 0.6s; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes scaleIn {
      from { opacity: 0; transform: scale(0.85); }
      to { opacity: 1; transform: scale(1); }
    }

    /* Progress bar */
    #progress-bar {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: ${theme.surface};
      z-index: 1000;
    }
    #progress-fill {
      height: 100%;
      background: linear-gradient(90deg, ${theme.accent}, ${theme.accentAlt});
      width: 0%;
      transition: width 0.6s ease;
    }
    #slide-counter {
      position: fixed;
      bottom: 14px;
      right: 24px;
      font-size: 0.8rem;
      color: ${theme.muted};
      font-family: ${theme.fontFamily};
      z-index: 1000;
      opacity: 0.7;
    }

    /* Fallback message */
    .fallback-message {
      display: none;
    }
    .impress-not-supported .fallback-message {
      display: block;
      text-align: center;
      padding: 60px 40px;
    }
    .impress-not-supported .step {
      display: block;
      opacity: 1;
      position: relative;
      margin: 40px auto;
    }
  </style>
</head>
<body class="impress-not-supported">
  <div class="fallback-message">
    <p>Your browser doesn't support impress.js. Try Chrome, Firefox, or Safari.</p>
  </div>

  <div id="impress" data-transition-duration="${duration}" data-perspective="1000" data-autoplay="0" data-width="${Math.round(1024 / (config.zoom || 1))}" data-height="${Math.round(768 / (config.zoom || 1))}">

${stepsHtml}

  </div>

${generateProgressBar(slideCount)}

  ${config.watermark ? `<div id="watermark" style="position:fixed; bottom:28px; left:36px; z-index:10000; font-family:${theme.headingFont}; font-size:20px; font-weight:800; letter-spacing:0.22em; text-transform:uppercase; color:rgba(255,255,255,0.55); pointer-events:none; text-shadow:0 1px 8px rgba(0,0,0,0.5);">${config.watermark}</div>` : ""}

  <script src="https://cdn.jsdelivr.net/gh/impress/impress.js@2.0.0/js/impress.js"></script>
  <script>
    (function() {
      var api = impress();
      api.init();

      var steps = document.querySelectorAll('.step:not(.slide-type-overview)');
      var total = steps.length;
      var progressFill = document.getElementById('progress-fill');
      var currentEl = document.getElementById('current-slide');

      document.addEventListener('impress:stepenter', function(e) {
        var idx = Array.from(steps).indexOf(e.target);
        if (idx === -1) {
          idx = total - 1;
        }
        var pct = ((idx + 1) / total) * 100;
        progressFill.style.width = pct + '%';
        currentEl.textContent = idx + 1;
      });
    })();
  </script>
</body>
</html>`;
}

// Main
const configPath = values.config!;
const outPath = values.out || "./presentation.html";

const raw = readFileSync(configPath, "utf-8");
const config: Config = JSON.parse(raw);

if (!config.title || !config.slides?.length) {
  console.error("Error: config must have 'title' and 'slides' array");
  process.exit(1);
}

const html = generateHTML(config);
writeFileSync(outPath, html, "utf-8");
console.log(`Generated: ${outPath} (${config.slides.length} slides, theme: ${config.theme || "dark"}, layout: ${config.layoutStrategy || "story"})`);
