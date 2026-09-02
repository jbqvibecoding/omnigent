# Omnigent UI reference

A complete inventory of the product's user interface, extracted from the source
so a designer, a new contributor, or an agent can see the whole surface without
reading 640 files.

| File | What's in it |
| --- | --- |
| [`DESIGN_TOKENS.md`](DESIGN_TOKENS.md) | Color tokens, the six palettes, typography, radii, motion, glass, safe-area insets |
| [`COMPONENTS.md`](COMPONENTS.md) | Every component: shadcn primitives, chat blocks, shell panels, dialogs, icons |
| [`SCREENS.md`](SCREENS.md) | Routes, the app-shell layout, each screen, panels/drawers, keyboard shortcuts, native shells |
| [`tokens.json`](tokens.json) | Machine-readable token dump — every palette × light/dark |
| [`extract_tokens.py`](extract_tokens.py) | Regenerates `tokens.json` from `web/src/index.css` |

Regenerate the token dump after touching any palette block:

```bash
python3 designs/UI/extract_tokens.py
```

## Where the UI lives

The product is one React SPA wrapped in four shells. The web bundle is the
entire UI — the desktop and mobile apps embed the same build and add only OS
chrome.

| Surface | Path | Stack |
| --- | --- | --- |
| Web app (the UI) | `web/src` | React 18 · Vite 8 · Tailwind 4 · Radix (`radix-ui`) · shadcn-style primitives |
| Desktop shell | `web/electron` | Electron main + preload; frameless window on macOS, native `WebContentsView` browser pane |
| iOS shell | `web/ios/Omnigent` | SwiftUI + `WKWebView`; native connect screen, chat/terminal bar, server switcher |
| Android shell | `web/android/app` | Kotlin + `WebView`; native connect activity, safe-area injection |
| Editor extension | `editors/vscode` | VS Code webview |

State and data:

- **Server state** — TanStack Query (`web/src/hooks/use*.ts`), one hook per resource.
- **Streaming chat state** — a module-scope Zustand store (`web/src/store/chatStore.ts`)
  that lives outside the React tree so an in-flight turn survives URL changes.
- **Live updates** — SSE + a session-updates WebSocket (`lib/sse.ts`, `lib/sessionUpdatesSocket.ts`).
- **Preferences** — `localStorage`, one small read/write/apply module per setting
  (`lib/themePalette.ts`, `lib/uiFontPreferences.ts`, `lib/panelSizePreferences.ts`, …).

## The shape of the app in one paragraph

A three-column workspace: a floating **conversations sidebar** on the left, the
**chat column** in the middle under a transparent header overlay, and a
**workspace rail** on the right with tabs for Files, Agents, Shells, Tasks and
Browser. Cards float on a near-white (light) or aurora-gradient (dark) canvas
painted by `.app-shell`; in dark mode every top-level card is frosted glass. The
composer is a single rounded card at the bottom of the chat column with trays
that tuck behind its top and bottom edges. Below `md` (768px) the sidebar
becomes a full-screen drawer, the rail collapses into a FAB dropdown of
full-screen drawers, and the root font-size steps up 12.5%.
