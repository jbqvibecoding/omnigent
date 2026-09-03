# Component catalog

Every component in `web/src`, grouped the way the directories are. Test files
are omitted; each component has a co-located `*.test.tsx` unless noted.

## 1. Primitives — `components/ui/` (26 files)

shadcn-style wrappers over `radix-ui`, styled with `class-variance-authority`
and merged through `cn()` (`clsx` + `tailwind-merge`). Every primitive stamps a
`data-slot` attribute so global CSS (the dark glass rules, popper overrides) can
target it without class coupling.

| Primitive | Exports | Variants / notes |
| --- | --- | --- |
| `button` | `Button`, `buttonVariants` | **variant**: `default` · `outline` · `secondary` · `ghost` · `destructive` · `link`. **size**: `default` (h-8) · `xs` (h-6) · `sm` (h-7) · `lg` (h-9) · `icon` (size-10, md:size-8) · `icon-xs` · `icon-sm` · `icon-lg`. Also `loading` (overlays a spinner, keeps width), `asChild`, and `componentId` for click analytics. Pressed state nudges via `transform: translateY(1px)` so it composes with `translate`-based centering |
| `badge` | `Badge`, `badgeVariants` | `default` · `secondary` · `destructive` · `outline` · `ghost` · `link`; fixed `h-5`, `rounded-4xl` |
| `alert` | `Alert`, `AlertTitle`, `AlertDescription`, `AlertAction` | `default` · `destructive`; auto two-column grid when an SVG is present |
| `card` | `Card`, `CardHeader`, `CardFooter`, `CardTitle`, `CardAction`, `CardDescription`, `CardContent` | The glass surface in dark mode |
| `input` | `Input` | `h-8`, `rounded-lg`, `text-base` → `md:text-sm` (16px on mobile avoids iOS focus zoom); focus lifts a 3px `ring-ring/50`; `aria-invalid` recolors to destructive |
| `textarea` | `Textarea` | Same treatment; the chat composer uses a bare `<textarea>` with `useAutoGrowTextarea` instead |
| `tabs` | `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`, `tabsListVariants` | `default` (segmented, `bg-muted`) · `line` · `pill` (used by the workspace rail so fixed and file tabs read as one set); horizontal + vertical |
| `dialog` | Radix Dialog set | Backed by `lib/dialogDismissGuard.ts` so an open Select can't dismiss its parent modal |
| `dropdown-menu`, `context-menu`, `popover`, `hover-card`, `tooltip` | Radix sets | All get the dark-mode popover glass rule |
| `command` | cmdk set | Powers the command palette and every combobox |
| `select` | Radix Select set | |
| `accordion`, `collapsible` | Radix sets | Tool cards and reasoning sections use `Collapsible` |
| `avatar` | `Avatar`, `AvatarImage`, `AvatarFallback`, `AvatarGroup`, `AvatarGroupCount`, `AvatarBadge` | Presence stack overflow chip |
| `button-group` | `ButtonGroup`, `ButtonGroupSeparator`, `ButtonGroupText`, `buttonGroupVariants` | Children re-round via `in-data-[slot=button-group]` |
| `input-group` | Composite field with leading/trailing slots | |
| `progress`, `spinner`, `separator`, `scroll-area`, `switch`, `toast` | | `toast` is the app's transient-notification surface |

## 2. Chat blocks — `components/blocks/`

The transcript is a stream of typed blocks (`lib/blocks.ts`, `lib/blockStream.ts`,
`lib/itemsToBlocks.ts`) rendered by one dispatcher. Compact tool-like surfaces
share `TOOL_SURFACE_WIDTH_CLASS` (`w-[48rem] max-w-full min-w-0`).

| Component | What it renders |
| --- | --- |
| `BlockRenderer` | The dispatcher. Also turns inline `` `src/foo.ts` `` code spans into links that open the FileViewer |
| `ToolCard` | A tool call: collapsed one-line summary (verb + target + duration + status glyph), expanding into args/output with a fade-out gradient and a maximize toggle. Status glyphs: spinner `text-info`, `XCircle` destructive, `CircleSlash` skipped |
| `ApprovalCard` | Permission elicitation — allow / allow-always / deny, `⌘↵` accepts |
| `AskUserQuestionForm` | Single- and multi-select answer forms from a requested schema |
| `ExitPlanModeReview` | Renders the proposed plan markdown with accept/reject |
| `ReasoningView` | Adapter onto the vendored `<Reasoning>` chain — auto-open while streaming, "Thought for N seconds" once settled |
| `SlashCommandCard` | Skill vs. surfaced CLI command, each with its own prefix + icon |
| `SmartRoutingCard` | The orchestrator's planned dispatches |
| `StatusBlocks` | Loud destructive banner for `error` blocks; falls back to the raw code when the message is empty |
| `SystemMessage` | Centered muted marker for injected `[System: …]` turns (task completion, timer firings, terminal-idle) |
| `TerminalCommandCard` | Runner-side `!cmd` lines forwarded from the Claude Code TUI — input and output variants |
| `TerminalView` + `TerminalSession` | xterm.js surface with WebGL/fit/web-links addons and a backoff re-attach schedule |

## 3. Message rendering — `components/ai-elements/`

Vendored from `ai-elements`, adapted. Markdown is Streamdown (GFM, math via
KaTeX, mermaid, CJK) hardened by `streamdown-security.ts`.

| Component | Notes |
| --- | --- |
| `message` | The bubble. **User**: `ml-auto`, `rounded-2xl`, `bg-muted`, `px-4 py-3`, `ring-1 ring-border/60`. **Assistant**: no bubble — bare prose on the canvas |
| `conversation` | Scroll container built on `use-stick-to-bottom`, plus `ConversationEmptyState` (centered `text-2xl` heading + muted line) and `ConversationScrollButton` |
| `code-block` + `lazyCodePlugin` | Shiki highlighting, lazily loaded; copy button; word-wrap toggle (`.chat-code-wrap` hang-indents wrapped lines past the line-number gutter) |
| `reasoning` | Collapsible thinking section; renders flat and non-interactive when there's nothing to show |
| `shimmer` | CSS-only text shimmer for the "Working…" indicator |
| `mathMarkdown` | KaTeX wiring; display math gets its own horizontal scroll surface |

## 4. Chat & composer components — `components/`

| Component | What it does |
| --- | --- |
| `SlashCommandMenu` | Suggestion menu floating above the composer; ↑↓ navigate, Tab applies, Esc dismisses |
| `FileMentionMenu` | `@`-mention workspace browser (native coding-agent sessions), with a loading row during runner cold-boot |
| `SkillPills` | Compact skill row inline on the new-session composer's first line; hidden once typing starts |
| `ComposerMicButton` | Voice dictation with interim + final transcripts (`⌘⌥V`) |
| `CostRoutingControl` | The smart-routing sparkle toggle — two cross-fading sparkle layers, a brand-pink halo, and a one-shot verdict ping replayed by React key remount |
| `HarnessConfigControls` | Labeled config rows (bold label + muted sub-description left, control right) |
| `ModelValueCombobox` | Free-form multi-select for policy array params |
| `PermissionsModal` | Session grants, revokes and public visibility — manage-level only |
| `KeyboardShortcutsDialog` | The shortcut sheet (`⌘/`) |
| `AgentCard`, `AgentHoverCard`, `AgentInfo` | Agent picker cards, Cursor-style flyout, and the tools-and-policies popover |
| `HostBadge` | Host binding label + status (sandbox provider name, or the host) with a reconnect affordance |
| `SessionStateBadge` | Sidebar status: `awaiting` → amber "Needs response" badge, `running`/`starting` → grey `RunningDot`, `unseen` → brand-pink dot |
| `RunningDot` | The shared spinner dot |
| `PresenceAvatars` | Other viewers on this session; renders nothing when alone |
| `UserMessageNav` | Prev/next user-turn navigation |
| `SessionImage`, `ImageLightbox` | Workspace-resolved images and their full-screen viewer |
| `OttoIcon`, `OttoEyes` | The mascot; `.otto-working` bobs and blinks while a turn is live |
| `UpdateBanner` | Desktop update toast — `floating` (bottom-right) and `bare` (host-supplied chrome) variants |
| `PageScroll` | The single scroll primitive for routed pages; owns header + safe-area clearance |
| `pwa/PWAUpdateBanner` | Service-worker update prompt (standalone app root only) |
| `theme/ThemeProvider`, `theme/ThemeColorPicker`, `theme/themeMode` | Mode wiring (also mirrors onto native shell chrome) and the custom-palette HSV picker |
| `goal/` | `GoalControl`, `GoalDialog`, `CommandGoalDialog`, `useGoalState` — persistent "run until X" goals, native-command mode for Claude/Codex |
| `scheduled/` | `CreateScheduledTaskDialog`, `ScheduledTaskRow` (card layout), `ScheduleFields`, `ModelEffortFields`, `Label`, `suggestions` |
| `BrowserPane/BrowserPane` | Placeholder `<div>` the Electron main process paints a native `WebContentsView` over, measured via `getBoundingClientRect` → IPC |
| `icons/` | Harness glyphs: Antigravity, Claude, Codex, Cursor, Goose, Hermes, Kimi, Kiro, Nessie, OpenCode, Otto, Pi |

## 5. Shell — `src/shell/` (the workspace chrome)

### Frame

| Component | Role |
| --- | --- |
| `AppShell` | The layout route. Paints `.app-shell`, hosts the sidebar, the chat+workspace group, the push panels, and every shell-level dialog. Sets `data-electron-mac` / `data-ios-native` / `data-android-native` |
| `Sidebar` | Conversations rail — wordmark (links home), search, settings, collapse; nav rows (New session · Automations · Inbox with an amber count); My sessions / Shared-with-me tabs; Pinned / Projects / Sessions sections; row actions, multi-select bulk archive/delete, rename, infinite scroll. Desktop: a floating card (`md:m-2`, resizable, `--radius-otto-md`). Mobile: a full-screen `fixed inset-0 z-50` drawer with edge-swipe drag |
| `ChatHeader` | Transparent `h-14` overlay: sidebar toggle / back-to-parent + sub-agent identity on the left; presence, agent info, view-mode toggle, glassy pink **Share**, right-panel toggle on the right. Below `md` it collapses into a ⋮ menu plus a rail FAB |
| `WorkspacePanel` + `SessionRail` | The right card and its tab strip: Files · Agents · Shells · Tasks · Browser, each with a count/status badge (`TAB_BADGE_BASE` — a circle at one digit, a pill at two or `n/m`) |
| `CommandPalette` | `⌘K` — sessions, navigation, actions |
| `TitleBarServerPicker` | Centered title + server switcher in the macOS Electron title-bar strip |
| `settingsNav` | The settings section list that replaces the conversation list in-place |

### Panels and viewers

| Component | Role |
| --- | --- |
| `FilesPanel`, `FolderTree`, `FlatFileList`, `FilesPanelDrawer` | Changed-files and full-tree views, sort + flat/tree + hidden-file toggles |
| `FileViewer` + `FileViewerContext` | The file surface; owns comment classification (open vs. addressed) and offset remapping when content changes |
| `CodeViewer` + `codeViewerRendering` + `codeViewerHelpers` | Shiki-highlighted read-only body with find-in-file and selection comments |
| `MonacoCodeEditor`, `MonacoDiffViewer`, `monacoSetup`, `useMonacoCommentLayer` | Editable code + diffs, Shiki-themed Monaco, decoration-based comment layer, autosave |
| `MarkdownRichTextViewer` + `MarkdownEditorToolbar` + `TipTap*` | TipTap markdown editor: comments, search, GitHub alerts, task lists, workspace images, HTML passthrough, table bubble menu |
| `NotebookPreview`, `PdfViewer`, `ModelViewer`, `HtmlCommentViewer` | `.ipynb`, PDF (react-pdf), 3D models (three.js), and commentable rendered HTML |
| `CommentsPanel` | Review comments with an "Address All" action |
| `TerminalsPanel`, `InlineTerminalsSection`, `MainTerminalView`, `NewTerminalButton`, `terminalStatus` | Shell surfaces for panel, inline and terminal-first layouts |
| `SubagentsPanel`, `SubagentsGraphView`, `subagentGraphLayout`, `subagentStatus` | The agent tree as a list and as an `@xyflow/react` graph |
| `TodoPanel` | The harness-published task list |
| `ExecutionLogsPanel` | Debug-mode agent-loop logs |
| `MobilePanelDrawer` | The shared full-screen drawer wrapper for all of the above below `md` |
| `TruncatedBanner`, `RunnerAsleepHint`, `FileDownloadButton`, `CliCommandBlock`, `PreviewSearchBar`, `MarkdownSearchBar` | Supporting chrome |

### Dialogs

`NewChatDialog` · `AddAgentDialog` · `CreateAgentDialog` · `SwitchAgentDialog`
(currently unmounted) · `ForkSessionDialog` · `ReconnectSessionDialog` ·
`ResumeWithDirectoryDialog` · `HarnessSetupDialog` + `HarnessCredentialForm` ·
`ProjectSettingsDialog` · `NewProjectButton` · `WorkspacePicker` +
`WorkspacePathField` · plus `PermissionsModal`, `KeyboardShortcutsDialog`,
`CreateScheduledTaskDialog`, `GoalDialog` / `CommandGoalDialog` and the
composer's config modal in `ChatPage`.

## 6. Pages — `src/pages/`

`ChatPage` (6.1k lines — transcript, composer, config gear, status line, quote
chips, queue strip) · `InboxPage` · `TasksPage` · `SettingsPage` ·
`MembersPage` · `PoliciesPage` · `SharingPage` · `LoginPage` · `RegisterPage` ·
`SetupPage` · `ApprovePage` · `NotFoundPage`, plus the chat-local
`TurnRail`, `QueuedMessagesStrip`, `ConnectionIndicator` and
`RunnerStartingIndicator`. See [`SCREENS.md`](SCREENS.md).

## 7. UI-shaping hooks — `src/hooks/`

Not components, but they define behavior you can see:

- **Resize**: `useResizableSidebar`, `useResizablePanel`, `useResizableColumn`,
  `useResizableInlinePanel`, `useResizableCommentsPanel` — widths persist via
  `lib/panelSizePreferences.ts`.
- **Hotkeys**: `useCommandPaletteHotkey`, `useApproveHotkey`,
  `useSessionSwitchHotkey`, `usePinnedSessionHotkeys`, `useSidebarToggleHotkeys`,
  `useVoiceDictationHotkey` (`react-hotkeys-hook`).
- **Chat behavior**: `useAutoGrowTextarea`, `usePromptHistory`,
  `useUserMessageNav`, `useDictationInsert`, `useThrottledValue`,
  `useWorkingLabelTick`.
- **Presence & liveness**: `useSessionLiveness`, `useSessionState`,
  `useRunnerHealth`, `useIdleNotifications`, `useUnseenConversations`,
  `useSeenComments`.
- **Mobile / native**: `useIsMobileViewport`, `useIOSViewportLock`,
  `useIOSNativeKeyboardInset`, `useNativeServerSwitcher`.
