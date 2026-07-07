# Hermes AI Workspace 结合蓝图（omnigent × wesight × tutti）

> Design note: integration blueprint for a cloud-hosted AI workspace where a
> Hermes agent orchestrates sub-agents, maximally reusing omnigent (execution
> plane), tutti (workspace plane), and wesight (experience plane).

## Context

目标产品：**云端运行、由 Hermes agent 作为 orchestrator 编排 subagents 的 AI
workspace**（greenfield）。本蓝图是对三个 repo 的研究结论与已确认的整合路线
（策略 C：以 Omnigent 为底座）。

## 一、三个 repo 的核心资产盘点

### 1. Omnigent（Python）— 执行面，与目标重合度最高

- **Hermes 已是一等公民，两种接入**：
  - `hermes`（SDK 型）：`omnigent/inner/hermes_executor.py` — 每轮 spawn
    `hermes chat -q`，`--resume <session_id>` 续会话（Hermes 自带 SQLite
    session store），per-session `HERMES_HOME` + `pre_tool_call` shell hook
    注入 Omnigent 策略。
  - `hermes-native`（原生 TUI 型）：tmux 包装真实 `hermes` CLI，终端可被用户
    接管。
- **Subagent 编排原语现成**：agent YAML 里 `tools.<name>: {type: agent}`
  （每个子 agent 各选 harness/model）；`spawn: true` →
  `sys_session_create / sys_session_send / sys_read_inbox`（inbox 通知式
  监督，不 busy-poll）。
- **Polly（`examples/polly/`）= 参考实现**：编排 orchestrator 自己不写码，
  分解目标 → 并行 worktree 派发（含 hermes 子 agent）→ 跨厂商独立 review →
  各开各的 PR。其协议（`title` + `args.purpose`、roster preflight、
  `sys_advise_models`、inbox 收工）可直接移植。
  `omnigent run examples/polly/ --harness hermes` 可一键把大脑换成 Hermes。
- **云端底座**：server 多租户（OIDC/邀请制）、会话共享/co-drive/fork；
  **managed hosts**（`POST /v1/sessions {"host_type":"managed"}` 自动在
  Modal/Daytona/Islo/E2B 起沙箱，预烤 host 镜像秒级启动，用户凭证不进沙箱）；
  `deploy/` 17 种部署目标。
- **治理**：server/agent/session 三级策略栈、成本预算、bwrap/seatbelt 沙箱、
  L7 egress proxy。

### 2. Tutti（Go + TS）— 工作区面，"agent 间共享大脑"

- **Issue→Task→Run 领域模型**（`packages/workspace/issue-manager` +
  goal-to-tasks）：orchestrator 编排结果的持久化模型。
- **Big @ / "+" 引用**：@ 另一个 agent 的历史对话、文件、任务、app 产物——
  三个 repo 里唯一真正解决"上下文不丢失地在 agent 间流转"的实现
  （`docs/architecture/agent-reference-mention-resolution.md`）。
- **Business Event Stream**：schema-first，一份 JSON Schema 生成 Go + TS
  双端类型化契约/校验器/topic 注册表，专用 WebSocket。
- **可复用 TS 包**（host adapter 模式，本就为多宿主设计）：
  `@tutti-os/agent-activity-core`、`workbench/surface`、`browser-node`、
  `issue-manager`、`claude-sdk-sidecar`。
- **App 中心**（`services/tuttid/builtin-apps`）：人和 agent 都能调的 app，
  产物留在 workspace 被下一步引用。
- **Tutti·VM 思路**："agent 本地跑、工作状态实时上云进 Room" 的混合架构。

### 3. WeSight（Electron）— 体验面资产库

- **IM 网关矩阵**（`src/main/im/`）：钉钉/飞书/Telegram/Discord/网易 IM/微信
  （pairing、media、delivery route、reply guard）。
- **30 个 SKILLs**（docx/xlsx/pptx/pdf/remotion/生图生视频/股票/web-search +
  skill-creator 自举）+ `skills.config.json`。
- **记忆系统**：`coworkMemoryExtractor.ts`（显式+隐式抽取，三档 guard）+
  `coworkMemoryJudge.ts`（规则打分 + LLM 二审 + TTL 缓存）。
- **定时任务模型**（cron、`sessionTarget: main|isolated`、IM 通道投递）。
- **Artifacts 沙箱渲染**（html/svg/mermaid/react）与 engine router 模式
  （多引擎统一 stream events）。

## 二、分层架构

```
触达层    IM 网关(WeSight) · Web/手机(Omnigent web UI) · 桌面(Tutti workbench)
工作区层  Issue→Task→Run + Big @ 引用 + schema-first 事件流(Tutti)
          App 中心(Tutti) + Artifacts 渲染(WeSight)
编排层    Hermes orchestrator(Omnigent hermes harness, Polly 协议变体)
          记忆(WeSight extractor/judge) · 定时(WeSight cron 模型)
执行层    Omnigent server + managed hosts 云沙箱
          subagents = 各 harness 子会话 · 三级策略 + 成本预算 + 沙箱/egress
```

十个结合点：1) Hermes 大脑 = Polly 移植；2) 云端化用 managed hosts；
3) 任务持久化借 Issue→Task→Run；4) subagent 共享上下文借 Big @；
5) 实时同步借 business event stream；6) 审批 = Omnigent policies +
Control Center 聚合交互；7) 技能市场 = WeSight SKILLs × Omnigent
`skills_filter`/bundle；8) IM 即入口 + 定时投递；9) 长期记忆注入 Hermes
system context；10) 产物"生成→预览→被下个 agent 消费"闭环。

## 三、已定决策（策略 C）

```
产品 = Omnigent server（云端执行面，不 fork，pip 依赖 + 配置/插件）
     + Hermes orchestrator agent YAML（Polly 变体——核心差异化所在）
     + 自建 workspace 前端（复用 @tutti-os/* 包，写 Omnigent API host adapter）
     + WeSight 资产服务端移植（IM/SKILLs/记忆/定时，剥离 Electron）
```

## 四、分阶段路线

- **Phase 0 可行性**：本地 `omnigent run examples/polly/ --harness hermes`；
  云端 server + managed hosts（Modal/E2B）端到端。
- **Phase 1 编排核心**：自有 orchestrator YAML（见
  `examples/hermes-workspace/`）；自定义 host 镜像烤入 `hermes` CLI 与技能包；
  WeSight SKILLs 经 `skills_filter` 下发。
- **Phase 2 Workspace 层**：Issue→Task→Run（Run ↔ Omnigent session id）；
  前端基于 `@tutti-os/*` + Omnigent API adapter；schema-first 事件 topic；
  Big @ mention resolution。
- **Phase 3 体验层**：一个 IM 通道剥 Electron 接 server 侧闭环；移植记忆与
  cron 模型；artifacts 渲染嵌入前端。

## 五、风险与差距

1. 三栈异构：执行面留 Python，工作区面自建（借 Tutti TS 包）；不要同时跑
   tuttid 和 Omnigent server 两个业务核心。
2. hermes executor 事件粒度偏粗（TextChunk/TurnComplete 级），精细工具时间线
   UI 需增强事件桥。
3. Tutti 对 Hermes 是 "coming soon"：用它的语义与包，不用它跑 Hermes。
4. WeSight 深绑 Electron：逻辑可搬，进程模型要改（IPC→HTTP/WS，
   sql.js→服务端 DB）。
5. Polly 假设 coding 场景：交付物需从 "PR" 泛化为 "workspace 产物"
   （正好接 Tutti 产物引用机制）。

## 六、验证方式

- Phase 0：Polly-on-Hermes 完成一个真实多子任务目标，云端 managed host
  全程无本地依赖。
- Phase 1：`examples/hermes-workspace/` 在云端完成一次非代码任务编排，
  产物落 workspace 而非 PR。
- Phase 2：任务树实时更新；@ 引用能把 A 子 agent 的产物喂给 B 子 agent。
- Phase 3：IM 消息触发完整编排并收到回推；重启后记忆保留。
