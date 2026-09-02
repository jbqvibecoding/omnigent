# Design tokens

Everything visual is expressed as a CSS custom property in `web/src/index.css`
and surfaced to Tailwind through `@theme inline`, so a palette swap re-skins the
whole app without any component knowing a theme changed. `tokens.json` is a
generated mirror of this file.

## The two appearance axes

| Axis | Owner | Mechanism |
| --- | --- | --- |
| **Mode** — light / dark / system | `next-themes` (`components/theme/ThemeProvider.tsx`) | `.dark` class on `<html>` |
| **Palette** — Omnigent / Dracula / GitHub / Catppuccin / Gruvbox / Nord / custom | `lib/themePalette.ts` | `data-theme="<id>"` on `<html>` |

They compose: `:root:not(.dark)[data-theme="github"]` is GitHub-light,
`.dark[data-theme="github"]` is GitHub-dark. The default `omni` palette declares
no overrides — it removes the attribute and falls through to the base
`:root` / `.dark` blocks.

Two more user-controlled axes ride on the root element:

- `--ui-font-scale` (unitless multiplier on `html { font-size }`) and
  `--ui-font-family` — Appearance settings, `lib/uiFontPreferences.ts`.
- Code font — `lib/codeFontPreferences.ts`; Monaco and xterm pin `--font-mono`
  and are deliberately immune to the UI font override.

## Color tokens (Omnigent brand palette)

`--background` is white in light mode on purpose: the lavender brand canvas is
painted by the `.app-shell` gradient, so `bg-background` tiles (inputs, code
blocks, tables) don't render as lavender patches on white cards.

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--background` | `#fff` | `#0d1218` | Page canvas fallback (auth pages use it full-bleed) |
| `--foreground` | `#11171c` | `oklch(0.965 0.003 240)` | Body text |
| `--card` | `#fff` | `rgba(40, 34, 58, 0.6)` | Sidebar / composer / panel surfaces (translucent glass in dark) |
| `--card-solid` | `#fff` | `#201c30` | Opaque stand-in where tucked tray corners must not ghost through |
| `--tray` | `#fff` | `rgba(40, 34, 58, 0.6)` | Composer footer tray, consumed with an opacity modifier (`bg-tray/40`) |
| `--popover` | `#fff` | `rgba(26, 33, 41, 0.8)` | Menus, dropdowns, tooltips, dialogs |
| `--primary` | `#11171c` | `#e8ecf0` | Primary buttons, focus ring |
| `--secondary` | `#eceef1` | `#1f272d` | Secondary badges/headers |
| `--muted` | `#0000000f` | `color-mix(… 15%, #28223a)` | Hover rows, user bubbles, ~160 solid utility surfaces |
| `--muted-foreground` | `#6f6f6f` | `#92a4b3` | Captions, icons, placeholder text |
| `--code-bg` | `#0000000f` | `oklch(0.38 0.005 240)` | Inline-code chips (a stronger step than `--muted`) |
| `--accent` | `#d7edfe` | `#04355d` | Selected/active wash |
| `--accent-foreground` | `#04355d` | `#4299e0` | Text on that wash |
| `--destructive` | `#c8324c` | `#e65b77` | Errors, interrupt button |
| `--border` | `#e8ecf0` | `oklch(0.28 0.005 240)` | Dividers, card outlines |
| `--border-strong` | `#a3b1bf` | — | Higher-contrast dividers |
| `--button-border` | `#d6d6d6` | — | Neutral button outline (lighter than `--border-strong`) |
| `--input` | `#e8ecf0` | `oklch(0.28 0.005 240)` | Field outlines |
| `--ring` | `#11171c` | `#e8ecf0` | Focus ring (matches `--primary`) |

### Status hues (identical in light and dark — the status palette is hue-stable)

| Token | Value | Used by |
| --- | --- | --- |
| `--brand-accent` | `#df3c85` | Brand moments only: unseen-session dot, `/slash` token, sub-agent tray, text selection |
| `--status-blue` / `--info` | `#3b8ff5` | Running tools, in-flight state |
| `--status-green` / `--success` | `#2ea65c` | Completed, working sub-agent counts |
| `--status-yellow` / `--warning` | `#d4972a` | "Needs response" badge, inbox count |
| `--status-red` | `#f04858` | Failures |
| `--status-gray` | `#8e99a4` | Neutral/idle |
| `--session-active` | `#2f7fd4` (light) / `#5ca4f5` (dark) | Sub-agent launching / idle-alive dot — deliberately distinct from `--warning` |
| `--chart-1…5` | `#3b8ff5 · #2272b4 · #2ea65c · #d4972a · #8e99a4` | Charts (dark mode uses oklch equivalents) |

### Sidebar sub-palette

`--sidebar`, `--sidebar-foreground`, `--sidebar-primary`, `--sidebar-accent`,
`--sidebar-border`, `--sidebar-ring`, plus three interaction tokens derived with
`color-mix`:

```css
--sidebar-hover:  color-mix(in srgb, var(--sidebar-foreground) 3%, transparent);
--sidebar-active: color-mix(in srgb, var(--sidebar-foreground) 7%, var(--sidebar));
--sidebar-active-foreground: var(--sidebar-foreground);
```

Light `--sidebar` is `#fdfafa` — the lightest tone of the canvas gradient — so
`bg-sidebar` chrome disappears into the canvas instead of painting a band. Dark
`--sidebar` is translucent (`rgba(17, 23, 28, 0.75)`) so it tracks the diagonal
gradient underneath, which a flat color can't do.

## The six palettes

Each palette re-points ~31 tokens plus its own `.app-shell` canvas. Swatches
below are the preview colors declared in `lib/themePalette.ts`; the authoritative
values are in `tokens.json`.

| Palette | Blurb | Light bg / card / accent | Dark bg / card / accent |
| --- | --- | --- | --- |
| `omni` (default) | The signature pink brand look | `#fdf7fb` · `#ffffff` · `#df3c85` | `#160e24` · `#28223a` · `#df3c85` |
| `dracula` | Moody purple with a pink pop | `#f7f5fd` · `#ffffff` · `#7c3aed` | `#282a36` · `#343746` · `#bd93f9` |
| `github` | Clean neutrals with a signal blue | `#f6f8fa` · `#ffffff` · `#0969da` | `#0d1117` · `#161b22` · `#58a6ff` |
| `catppuccin` | Soft pastels — Latte & Mocha | `#eff1f5` · `#ffffff` · `#8839ef` | `#1e1e2e` · `#313244` · `#cba6f7` |
| `gruvbox` | Warm retro earth tones | `#fbf1c7` · `#fffdf2` · `#d65d0e` | `#282828` · `#3c3836` · `#fe8019` |
| `nord` | Arctic frost over polar night | `#eceff4` · `#e5e9f0` · `#5e81ac` | `#2e3440` · `#3b4252` · `#88c0d0` |

A seventh selection, **`custom`**, derives its whole block from user-picked hex
values (`lib/customTheme.ts` + `components/theme/ThemeColorPicker.tsx`, an
HSV square + hue slider + hex field with a dice-roll randomizer), which is why
`tokens.json` shows `var(--custom-light-*)` indirections there rather than
literals.

## The canvas

`.app-shell` paints the page. Light Omnigent is a 45° near-white sweep with a
faint warm drift (13 stops from `rgb(253,250,250)` to `rgb(254,253,253)`); dark
Omnigent is three radial aurora blooms over a 145° violet→ink base:

```css
.dark .app-shell {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(100, 40, 180, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(80, 30, 140, 0.10) 0%, transparent 45%),
    radial-gradient(ellipse at 60% 80%, rgba(140, 30, 100, 0.08) 0%, transparent 40%),
    linear-gradient(145deg, #1e1035 0%, #11171c 50%, #161020 100%);
}
```

Every palette ships its own light and dark canvas — see `appShellCanvas` in
`tokens.json`.

## Glass (dark mode only)

Top-level cards get a frosted treatment. The rule targets `.bg-card` (and
responsive `md:bg-card`) but explicitly **not** a `bg-card` nested inside another
`bg-card` — an interior fill re-decorated with its own border would visually
carve the parent card into pieces — and not `[data-collapsed]` panels, which
would otherwise paint as a glowing strip at the screen edge.

| Surface | Backdrop filter | Border | Shadow |
| --- | --- | --- | --- |
| Cards, sidebar, panels | `blur(32px) saturate(180%)` | `1px rgba(255,255,255,0.09)`, top edge `0.14` | `0 4px 16px rgba(0,0,0,.22)`, `0 1px 3px rgba(0,0,0,.16)` |
| Popovers, menus, poppers | `blur(24px) saturate(150%)` | `1px rgba(255,255,255,0.08)` | — |

Cards also carry a 135° white-to-transparent sheen (`0.04` → `0`). The
`-webkit-` prefixed property must precede the unprefixed one — LightningCSS
collapses the pair and keeps the last.

## Typography

| Token | Value |
| --- | --- |
| `--font-sans` | `ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"` — deliberately the OS face so the app reads as native chrome |
| `--font-mono` | `"Geist Mono Variable", "JetBrains Mono", ui-monospace, monospace` |
| `--font-heading` | `var(--font-sans)` |
| `--text-13` | `13px / 20px` — a step between `text-xs` and `text-sm`, for composer footer chrome and slash-command rows |
| `--text-3xl` | `32px / 36px` (overrides Tailwind's 30/36) |
| `--sidebar-font-size` | `0.8125rem` (13px at default root), applied via `.sidebar-compact-text` |

Scaling rules:

- `html { font-size: calc(1em * var(--ui-font-scale)) }` — `1em` preserves a
  customized browser default; the Appearance setting multiplies on top.
- Below `48rem` the root steps to `calc(1.125em * var(--ui-font-scale))`, a
  uniform ~12.5% bump of type **and** spacing (Tailwind 4 sizes both in `rem`).
- Streamdown inline code and code blocks are scaled to `0.875em` so Geist Mono
  matches the surrounding prose optically.
- Streamdown's heading ramp is flattened to `1.4 / 1.2 / 1.05 / 1em`.
- iOS native shell forces `16px` on inputs to stop WebKit's focus zoom.

Text selection tracks the palette's brand accent: light is a 22% accent wash with
accent-colored glyphs, dark is a solid accent with white glyphs.

## Radii

`--radius: 0.5rem` is the base; the scale is multiplicative, so one variable
retunes every corner in the app.

| Utility | Formula | At 0.5rem |
| --- | --- | --- |
| `rounded-sm` | `--radius × 0.6` | 4.8px |
| `rounded-md` | `× 0.8` | 6.4px |
| `rounded-lg` | `× 1` | 8px |
| `rounded-xl` | `× 1.4` | 11.2px |
| `rounded-2xl` | `× 1.8` | 14.4px |
| `rounded-3xl` | `× 2.2` | 17.6px |
| `rounded-4xl` | `× 2.6` | 20.8px |

Three fixed "Otto" radii sit outside the scale for shell chrome:
`--radius-otto-button: 6px`, `--radius-otto-sm: 8px`, `--radius-otto-md: 12px`
(the sidebar card, nav rows).

## Motion

| Token / keyframe | Timing | Where |
| --- | --- | --- |
| `--ease-otto` | `cubic-bezier(0.34, 1.4, 0.64, 1)` | Brand spring — wordmark hover, shell chrome |
| `--duration-otto-fast` | `180ms` | Same |
| `user-msg-flash` | `800ms ease-out` | Ring pulse when the turn rail jumps to a message (mirrors `FLASH_DURATION_MS`) |
| `imc-verdict-ping` | `650ms ease-out`, once | Smart-routing verdict ring on the composer sparkle |
| `shimmer-sweep` | `var(--shimmer-duration, 2s)` linear infinite | "Working…" text shimmer — pure CSS to keep framer-motion (~165KB) out of the bundle |
| `otto-bob` / `otto-blink` | `1.6s` / `3.4s` ease-in-out infinite | The Otto mascot while the agent works (`.otto-working`) |
| `compaction-slide` | `translateX(-100% → 200%)` | Context-compaction indicator |
| Mobile drawer | `360ms cubic-bezier(0.32, 0.72, 0, 1)` on `transform, translate` | iOS/Android sidebar; suppressed inline while a finger drag is live |
| Sidebar / rail width | none — snaps | Animating width lagged drag-to-resize |

A global `prefers-reduced-motion` gate collapses every animation and transition
to `0.01ms`; the two scoped blocks (smart-routing toggle, message flash) keep
their static state so nothing loses legibility.

## Layout, safe areas and insets

One inset system serves browser, Electron, iOS and Android — the runtime-specific
inputs default to zero, so no component branches on `isIOSShell()`.

| Variable | Value | Meaning |
| --- | --- | --- |
| `--omnigent-header-height` | `3.5rem` | The web `ChatHeader` band (`h-14`) |
| `--omnigent-safe-top` / `-bottom` | `max(env(safe-area-inset-*), --omnigent-android-safe-area-*)` | OS safe area; Android injects measured values because `env()` is unreliable in its WebView |
| `--omnigent-native-top-bar` / `-bottom-bar` | `0px`, set by the native bridge | Pixel height of the iOS floating switcher / chat-terminal bar |
| `--omnigent-top-bar-visible` / `-bottom-bar-visible` | `0｜1`, web-owned | Folded in by multiplication so a hidden bar contributes nothing |
| `--omnigent-inset-top` / `-bottom` | derived | What `<PageScroll>` and the scoped rules consume |
| `--omnigent-viewport-height` | `visualViewport.height`, iOS | Locks the shell so the soft keyboard can't pan the document |

The top bar is tracked but deliberately **not** added to the content top inset —
it floats inside the header band, so content clearing the header already clears it.

Two mask-based fades replace opaque overlays, because a flat fill can't track the
canvas gradient:

- `.chat-scroll-fade` — transparent through 48px, opaque by 80px, pinned to the
  scroll viewport so it doesn't move with the text. Offsets shift by the safe
  area on iOS, and by the switcher pill's footprint on Android.
- `.turn-rail-fade` — symmetric ramps whose width comes from the `FADE`
  constant in `TurnRail.tsx`, so the mask and the thumb math can't desync.

## Platform-scoped chrome

- **macOS Electron** (`[data-electron-mac]`): the sidebar drops `2.25rem` so the
  traffic lights float over freed canvas, which doubles as the window's only
  drag strip (`inset: 0 20rem auto 0`, so the header's right cluster stays
  clickable). A blanket `-webkit-app-region: no-drag` re-arms every interactive
  element, since drag regions are geometric, not z-ordered.
- **iOS / Android native** (`[data-ios-native]`, `[data-android-native]`):
  full-bleed webview with padded drawers, a leading-edge drawer shadow while
  sliding, and a composer bottom pad of `0.75rem + safe-area`.
- **Share button** (`.share-button-glassy`): the one hand-tuned gradient in the
  app — a vertical pink emboss (`#fa3d99 → #f22286 → #d51d74`) with no border;
  dark mode adds a 150° sweep and a grounding shadow.
