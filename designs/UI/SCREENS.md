# Screens, layout and navigation

## Route table (`web/src/App.tsx`)

`AppShell` is the parent layout route: it renders the sidebar plus a main
`<Outlet />`, and every child route lands in that outlet.

| Path | Screen | Notes |
| --- | --- | --- |
| `/` | `ChatPage` (new session) | The landing composer — owns session creation end to end |
| `/c/:conversationId` | `ChatPage` (session) | Same component, stays mounted across the `/` ↔ `/c/:id` transition; the Zustand chat store lives outside the React tree so an in-flight turn survives the URL change |
| `/inbox` | `InboxPage` | |
| `/tasks` | `TasksPage` | Labeled **Automations** in the sidebar |
| `/settings` · `/settings/:section` | `SettingsPage` | Renders into the chat outlet so the sidebar stays put and only swaps its body to the section nav |
| `/members` → `/settings/members`, `/policies` → `/settings/policies` | redirects | Legacy bookmarks |
| `/approve/:sessionId/:elicitationId` | `ApprovePage` | **Outside** the shell — the URL the REPL prints when a policy returns ASK in URL mode |
| `/login`, `/register` | `LoginPage`, `RegisterPage` | **Outside** the shell (the shell's hooks need an authed identity), each with its own centered-card layout. Registered only when `/v1/info` reports `accounts_enabled` |
| `*` | `NotFoundPage` | Inside the shell, so the sidebar stays visible |

Two conditional modes come from the `/v1/info` probe:

- **First run** (`accounts_enabled && needs_setup`) — *every* path renders
  `SetupPage`, the create-admin form, so the first visitor lands on it however
  they arrived.
- **Header / OIDC deploys** — `/login`, `/register`, `/members` are not in the
  route table at all; they ship as lazy chunks that are never downloaded.

Every page is wrapped with an analytics page-view id (`withPageView`);
`SettingsPage` opts out because its id is param-derived (`settings.<section>`).

## The app shell

```
┌───────────────────────────────────────────────────────────────────────┐
│ .app-shell  (canvas gradient; h-dvh; the document itself never scrolls)│
│ ┌──────────┐ ┌──────────────────────────────────────────────────────┐ │
│ │ Sidebar  │ │ ChatHeader  (h-14 transparent overlay, spans chat +   │ │
│ │ (card,   │ │              workspace but never the push panels)     │ │
│ │  m-2,    │ │ ┌────────────────────────────┐ ┌───────────────────┐  │ │
│ │  resiz-  │ │ │ main  <Outlet />           │ │ WorkspacePanel    │  │ │
│ │  able)   │ │ │  · TurnRail (left, md+)    │ │  Files · Agents · │  │ │
│ │          │ │ │  · transcript (max-w-3xl)  │ │  Shells · Tasks · │  │ │
│ │          │ │ │  · composer + trays        │ │  Browser          │  │ │
│ │          │ │ └────────────────────────────┘ └───────────────────┘  │ │
│ └──────────┘ └──────────────────────────────────────────────────────┘ │
│                     ▲ push panels (FileViewer / Terminals / …) mount   │
│                       as siblings to the right of this group           │
└───────────────────────────────────────────────────────────────────────┘
```

- **Chat column width**: `max-w-3xl`, widening to `max-w-4xl` above 1921px and
  `max-w-5xl` above 2561px.
- **Sidebar**: desktop is a floating card (`md:m-2`, `--radius-otto-md`, drag to
  resize via a 1px right-edge handle); closed it animates to `w-0` with its
  margin and border collapsed. Mobile is `fixed inset-0 z-50` sliding on
  `translate-x`, opaque (`max-md:bg-card-solid`) because WebKit drops the glass
  backdrop-filter once a Radix popper opens.
- **Push panels** (FileViewer, TerminalsPanel, FilesPanelDrawer, ExecutionLogs)
  are flex siblings that animate width and take the right side; only one is open
  at a time. In terminal-first sessions the terminal renders *inline* in main
  instead, so the workspace card stays visible beside it.
- **Right rail** is gated on having at least one available tab, so a
  no-filesystem agent with no terminals never shows an empty white rectangle.

### Mobile (< 768px)

The sidebar and every rail tab become full-screen drawers (`MobilePanelDrawer`),
reached from the header's ⋮ menu and a panel FAB whose dropdown mirrors the
desktop tab strip (Files · Agents · Shells · Tasks · Logs), each row carrying the
same count badge. Root font-size steps up 12.5%; the TurnRail is hidden.

## ChatPage

**Empty state** — centered `text-2xl` "What should we work on?" over a muted
"Send a message to get started." During a cold launch (terminal-first spin-up or
a managed-sandbox boot) a `RunnerStartingIndicator` hero replaces it.

**Transcript** — `gap-4` between bubbles so consecutive agent turns read as one
thread; `pt-20` clears the header; `md:pl-12` opens a gap for the TurnRail.
`chat-scroll-fade` dissolves content into the canvas before it reaches the
header controls. History pages prepend with scroll anchoring preserved. Pending
elicitation cards float to the bottom of the flow so an outstanding question
stays in view, with the Working… shimmer last.

**TurnRail** — a left-edge column of ticks, one per user turn, each previewing
the reply it drew; clicking jumps and flashes the target with a ring pulse.

**Composer** — a single `rounded-2xl` card (`border-border`, `shadow-sm`,
`dark:bg-card-solid`) with four things tucked around it:

| Slot | Content |
| --- | --- |
| Above, peeking | `QueuedMessagesStrip` (FIFO follow-ups held while busy — edit, steer, reorder, delete) and the sub-agent tray (`bg-brand-accent/10`, `-mb-4`, names the sub-agent you're messaging) |
| Inside, floating | `SlashCommandMenu`, `FileMentionMenu` |
| Inside, stacked | Quote chips → auto-growing textarea (with a mirrored highlight overlay that tints the `/command` token brand-pink) → attachment chips → `@`-mention chips → inline command/attachment errors |
| Action row | Left: attach (📎) + mic. Right: Plan-mode toggle, `GoalControl`, model/effort label, config gear, and a circular Send that flips to a destructive Interrupt while streaming |
| Below, peeking | `ComposerStatusLine` (`bg-tray/40`, `-mt-4`): host badge · worktree branch on the left; Plan mode · goal pill · context ring on the right |

Both trays overlap the card by 16px — more than its ~14px corner radius — so
their square corners hide behind its straight sides.

Drag-and-drop lifts an inset `ring-2 ring-ring` and a "Drop files here" scrim.
The placeholder is state-aware: read-only, offline, pending-elicitation, waiting,
streaming ("Send a follow-up (queued) — Esc to stop"), sandbox-asleep, reconnect,
or the default "Ask the agent anything…".

## Sidebar

Wordmark (links to `/`, `dark:invert`) · search · settings · collapse. Then the
nav group — **New session**, **Automations**, **Inbox** (amber count pill) — the
**My sessions / Shared with me** tabs in multi-user deploys, and the scrolling
list: **Pinned**, **Projects** (collapsible folders, per-project actions, "New
project"), **Sessions**. Rows carry a `SessionStateBadge`, a hover action menu
(pin, rename, fork, archive, delete, stop) and support shift-select for bulk
archive/delete. Infinite scroll via an `IntersectionObserver` sentinel that
pre-fetches 200px early and stays clickable as a fallback.

## Other screens

| Screen | Shape |
| --- | --- |
| **InboxPage** | `h1` "Inbox" over every approval prompt waiting across all of the user's sessions, as actionable cards |
| **TasksPage** | `h1` "Automations", search + Active/Paused filter, "New task", card rows (`ScheduledTaskRow`), and a Suggestions section of seed chips below |
| **SettingsPage** | Section list in the sidebar, content in main. **Desktop**: Local CLI, Updates. **General**: Account, Appearance, Git, Keyboard shortcuts. **Admin** (admins only): Members, Policies, Sharing. **Archived**: archived sessions. Appearance holds Mode, Color theme (+ custom Accent / Background tint / contrast / translucent sidebars), Terminal theme, Workspace panel, and interface/code font size + family |
| **MembersPage / PoliciesPage / SharingPage** | Admin tables — accounts and invites, global default policies, and the server-wide sharing tier |
| **LoginPage / RegisterPage / SetupPage** | Centered card, no chrome, full-page `--background` |
| **ApprovePage** | Standalone allow/deny for one elicitation |
| **NotFoundPage** | 404 inside the shell |

## Keyboard shortcuts (`components/KeyboardShortcutsDialog.tsx`)

| Group | Shortcut |
| --- | --- |
| General | `⌘K` command palette · `⌘/` this sheet |
| In chats | `↵` send · `⇧↵` newline · `↑`/`↓` recall prompts · `⌘↵` accept approval · `⌘⌥V` voice dictation · `Esc` stop |
| Navigation | `⌘↑`/`⌘↓` previous/next session · `⌘1…0` jump to pinned session (`⌘⌥1…0` off the native shells) |
| View | `⌘⌥[` conversations sidebar · `⌘⌥]` workspace sidebar |
| Slash commands | `↑`/`↓` navigate · `Tab` apply · `Esc` dismiss |

## Native shells

| Shell | Native UI it adds |
| --- | --- |
| **Electron** (`web/electron/src`) | 1280×860 default window, `backgroundColor: #0b0b0c`, `titleBarStyle: "hiddenInset"` on macOS. The web layer supplies the drag strip and traffic-light clearance; the main process adds a native find bar, a browser pane painted as a `WebContentsView`, an update overlay, deep links and a local-CLI server manager |
| **iOS** (`web/ios/Omnigent`) | `AppRootView` → `ConnectView` (logo, "Server URL" field, primary Connect button, recent-servers list) or `WebShellView`. Floating **server switcher** at the top and a **Chat / Terminal** capsule bar at the bottom, both in system Liquid Glass (`glassEffect`, falling back to `.ultraThinMaterial`). `DesignTokens.swift` mirrors four web tokens — background, foreground, muted-foreground, border — plus `radius: 8` |
| **Android** (`web/android/app`) | `ConnectActivity` + `MainActivity` WebView; injects measured safe-area insets as `--omnigent-android-safe-area-*` and floats its own server-switcher pill (8px margin, 25px height — the values the Android scroll-fade math reads back) |
| **VS Code** (`editors/vscode`) | Webview embedding the same build |

The web bundle detects all three via `lib/nativeBridge.ts` and stamps
`data-electron-mac` / `data-ios-native` / `data-android-native` on the shell root;
everything else is plain CSS scoped to those attributes.
