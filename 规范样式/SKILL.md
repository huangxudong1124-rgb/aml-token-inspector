---
name: 规范样式
description: Extract design tokens (colors, shadows/投影, corner radius/圆角) from any Figma design-system file or URL into CSS custom properties, JSON, or Markdown. Use when the user shares a Figma link and wants the palette/shadows/radii pulled out, asks to "extract design tokens", "get the colors/shadows/radius from Figma", convert a Figma design system into code tokens, or build a theme/tailwind config from a Figma file. Handles Arco/Volcengine-style files with Figma Variables where style nodes return null from the REST API (falls back to reading the token canvas swatches directly and pairing each swatch with its role label by position).
---

# 规范样式

Extract **colors, shadows, and corner radius** from a Figma file into ready-to-use tokens.

The heavy lifting is done by `scripts/extract.py` (in this skill's directory), which calls the Figma REST API directly. Run the script via its path inside this skill folder.

## Setup

1. **Figma API token** — resolve in any of these ways (first hit wins): `--token <figd_…>` flag, `$FIGMA_TOKEN` / `$FIGMA_API_KEY` env var, or `~/.mcp-figma/config.json` (key `apiKey`, the mcp-figma MCP server config). If none is present, ask the user for a Figma personal access token.
2. **Python 3** is required (stdlib only — no pip install).

## Usage

Replace `SKILL` below with this skill's directory path (e.g. `~/.claude/skills/规范样式`).

### 1) 直接输出内置规范 token（无需 Figma，推荐）

skill 自带全套规范 token（主色紫 #7B32DE / 中性纯灰 / 功能色 / 分类色 / 安全色 / 阴影 / 圆角），装上即可输出：

```bash
python3 SKILL/scripts/extract.py --builtin --format css     # CSS 变量(:root)
python3 SKILL/scripts/extract.py --builtin --format json    # JSON
python3 SKILL/scripts/extract.py --builtin --format md      # Markdown 表
```

### 2) 把网页刷成规范样式（一键改写 HTML）

```bash
python3 SKILL/scripts/apply.py path/to/index.html           # 自动备份后改写
```

把任意 HTML 的颜色重映射成规范 token（蓝/青→品牌紫、slate→纯灰、红/绿/橙→功能色），并注入规范 `:root` 变量。备份为 `.bak<时间>`。颜色映射可在 `apply.py` 的 `HEX_MAP` / `TUPLE_MAP` 里增删。

### 3) 从 Figma 实时抽取（可选，需要 token）

```bash
# Markdown 表（默认）
python3 SKILL/scripts/extract.py "<figma-url-or-fileKey>"

# CSS / JSON
python3 SKILL/scripts/extract.py m4zkJ7ZJYAZqfCrdziD77N --format css

# Token 临时传入
FIGMA_TOKEN=figd_xxx python3 SKILL/scripts/extract.py "<figma-url>" --format json
```

### 附带数据

- `colors.csv` / `shadows.csv` / `radius.csv` — 规范 token 表格（Excel 可直接打开）
- `scripts/tokens.json` — **权威 token 数据源（单一数据源）**，所有颜色/阴影/圆角的真值都在这里
- `scripts/build_inspector.py` — token 自检页生成器。它**只读取同目录 `tokens.json`** 并生成可视化 HTML：

```bash
python3 ~/.workbuddy/skills/规范样式/scripts/build_inspector.py
# → 生成 index.html（token 自检页）
```

> ⚠️ **网页只是 skill 的映射**：自检页（index.html）不存任何颜色值，它 100% 从 `scripts/tokens.json` 渲染。改 token 只改 `tokens.json`，再跑 `build_inspector.py` 刷新页面（并 `cp scripts/index.html ../index.html`）。

> ⚠️ **与 aml-token-inspector 双份同步**：`~/.workbuddy/skills/aml-token-inspector/` 是本 skill 的姊妹版（同一份自检页的两个入口）。任何一侧改了 `build_inspector.py` / `tokens.json` 都要拷贝到另一侧并各自重建，两边的 index.html 必须保持 `diff` ��致；分发用桌面 `~/Desktop/aml-token-inspector.zip`（在 skills 目录下打包，带 `aml-token-inspector/` 前缀）。

### 自检页当前内容结构（与 index.html 一致）

- **Color 页双折叠区**：1) Primitives 基础色板（默认折叠；6 色系 Brand Purple / Purple Gray / Gray / Yellow / Teal / green，各 12 档 25→950）2) Color Styles — 语义色 Token（默认展开；主色 → 中性色 → 功能色 → 分类色 → 安全色 5 组，组间 64px，每组白底卡片 + 1px 描边 + 10px 圆角 + 24px 内边距）
- **卡片网格**：每行最多 6 个等宽卡（≤1280px 4 列 / ≤720px 2 列）；颜色行标签与卡片顶部对齐
- **Typography**：Font-family 4 卡（微软雅黑 / Roboto / Noto Sans Arabic 数字+标点），样例统一 13px 以对应字体真实渲染（Roboto / Noto Sans Arabic 为 latin woff2 base64 内嵌，微软雅黑走系统栈）；字号行高合并列，无独立行高板块
- **Border / Shadow**：卡片统一白底 + 展示区/文字区两端内缩分隔线；分割线无圆角
- **Radius**：三分组竖排，方块品牌紫 Lv3 #CEAEFF
- 色值与 Pixso 导出 react 工程 `src/assets/styles/variables.css` 1:1 对齐（参数层→Primitives，Mode 层语义链→语义色）


## How it works (and where to intervene)

- **Shadows** — reads every `EFFECT` published style, fetches each node, and renders real CSS `box-shadow` strings (handles `DROP_SHADOW`, `INNER_SHADOW`, spread, alpha). Inner-shadow "borders" (`inset 0 0 0 1px …`) come through as-is.
- **Colors** — walks the Color canvas: `Section → SubSection (family) → Row → swatches`. Each row becomes a level scale where **rightmost swatch = level-1 (lightest)** … **leftmost = level-8 (darkest)**; `level-6` is the "regular/常规" anchor. Families and row names come straight from the Figma frame names.
- **Radius** — reads the Radius/圆角 canvas and pairs every `Npx` text label with the rectangle(s) near it, so each radius ships with its usage note (button/card/modal…).

## Two failure modes worth knowing

1. **Library component nodes return `null`** from `/files/{key}/nodes`. This is a known Figma quirk for styles whose backing node lives in a linked library. The script does **not** rely on those for colors — it reads the token-canvas swatches instead, which always carry a resolved fill.
2. **Canvas isn't named 颜色/投影/圆角.** Auto-detection matches `颜色|/Color`, `投影|/Shadow`, `圆角|/Radius`. If the file uses other names, pass the canvas nodeId explicitly via the URL's `node-id` (for color) and `--radius-node` (for radius), or tell the user the canvases weren't found and ask which page to read.

## Delivering the result

After the script runs, present the tokens grouped by family (color scales, shadows, radius) and offer to emit a specific format the project can consume: `tokens.css`, `tailwind.config.js` theme extension, SCSS variables, or a JSON token file. Match the project's existing token format/naming if one already exists — prefer augmenting it over inventing a parallel scheme.

## Notes

- Values are 1:1 with the Figma source at extraction time. If a value looks wrong, the file was likely edited since — re-run.
- This extracts a *snapshot*; it does not sync ongoing Figma changes.
