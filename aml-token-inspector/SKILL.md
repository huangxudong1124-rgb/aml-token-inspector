---
name: aml-token-inspector
description: AML Design 设计 token 自检页 — 单文件离线 HTML（含 6 大板块：Color / Typography / Spacing / Border / Shadow / Radius）。Color 页为双折叠区结构：Primitives 基础色板（默认折叠）+ Color Styles 语义色 Token（主色→中性色→功能色→分类色→安全色，每组白色卡片背景）。点击任意卡片复制对应 CSS/HEX，顶栏右侧「创建文件夹」按钮的小手在 hover 时先转到 25° 基线，再以 ±13° 快速左右晃动。触发词：设计 token 自检、token inspector、样式规范页、AML 设计系统预览、规范样式自检。
agent_created: true
---

# AML Design Token Inspector

## 用途

把 AML Design 设计系统的全部 token 渲染到一个离线、可双击打开的 HTML 自检页里。给设计师 / 开发查阅设计规范用，方便：

- 一眼看全 6 大板块（Color / Typography / Spacing / Border / Shadow / Radius）
- 点击任一卡片复制对应的 CSS 变量或 HEX
- 在 file:// 协议下也能完整工作（无外部请求；Roboto / Noto Sans Arabic 以 latin 分片 woff2 base64 内嵌，微软雅黑走系统字体）

## 文件结构

```
aml-token-inspector/
├── SKILL.md              ← 本文件
├── index.html            ← 双击这个文件就能看（生成产物，~210KB 含内嵌字体）
└── scripts/
    ├── build_inspector.py  ← 页面生成器（读 tokens.json → 渲染 index.html）
    ├── tokens.json          ← 单一数据源（颜色/字号/间距/边框/阴影/圆角/基础色板）
    ├── folder_btn_default.svg   ← 顶栏「创建文件夹」按钮默认态（含黄色小手抠图）
    ├── folder_btn_active.svg    ← 顶栏按钮点击激活态（紫色）
    └── pill_brand.svg           ← 顶栏品牌胶囊（渐变大脑 logo + AML Design 字标）
```

## 触发场景

- 用户说「打开 AML 设计系统」「看 token」「打开样式规范页」
- 用户要求把当前页面分享给同事/上传到作品集
- 用户想基于这套 token 起一个新项目

## 页面当前内容结构（与 index.html 一致）

### Color 页 — 双折叠区

1. **Primitives 基础色板**（默认折叠；6 色系 × 12 档 25/50/100/…/900/950）
   - Brand Purple（品牌紫）/ Purple Gray / Gray / Yellow / Teal / green
   - 色值 1:1 对应 Pixso 导出 react 工程 `src/assets/styles/variables.css` 参数层
2. **Color Styles — 语义色 Token**（默认展开；5 组，组间 64px 间距，每组白色卡片背景 #fff + 1px 描边 + 10px 圆角 + 24px 内边距）
   - 主色 Primary（Brand Purple 品牌紫 + purple-gray 紫灰）
   - 中性色 · color（color-text 文字 / icon-color-fill 图标填充 / color-fill 填充 / color-bg 背景 8 档 / color-border 描边 / color-nav 导航）
   - 功能色 · color（success 成功 / danger 危险 / warning 警告 / link 链接 / grey 灰）
   - 分类色 Categorical（red / yellow / green / teal / brand-purple）
   - 安全色 Safety（danger / risk-3 / green / info / unknown / unknown2，roles：背景/悬浮/常规/点击）

- 两区头可点击折叠/展开（chev 旋转，状态跨渲染保持）
- 每行色卡：整卡颜色填充 stage + Lv / 角色 + HEX；行标签与卡片顶部对齐

### Typography 页

- **Font-family 4 卡**：微软雅黑（中文「数据知识管理系统」）/ Roboto（英文 "Volcengine"）/ Noto Sans Arabic ×2（数字 "1234567890" + 标点 "@%……"），样例统一 13px、以对应字体真实渲染
- 字号 10 级 + 行高合并列 + 3 种字重；无行高独立板块（已删）
- 字体栈不含苹方，统一微软雅黑

### 其余板块

- Spacing：9 级 `--s-*`（4/8/12/16/20/24/32/40/48px）
- Border：分割线无圆角、卡片白底、展示区与文字区两端内缩分隔线
- Shadow：与 Border 卡片样式统一（白底 + 同款分隔线）
- Radius：三分组竖排，方块品牌紫 Lv3 #CEAEFF

### 全站通用

- 卡片网格：每行最多 6 个等宽卡（≤1280px 降 4 列 / ≤720px 降 2 列��
- 导航选中项无圆点；内容板块间距加大

## 使用流程

### 1. 直接打开看

```bash
open ~/.workbuddy/skills/aml-token-inspector/index.html
```

或在访达里双击 `index.html`。

### 2. �� token → 重生成

1. 编辑 `scripts/tokens.json`（颜色、字号、间距、阴影、圆角的唯一数据源）
2. 重跑生成器：

```bash
cd ~/.workbuddy/skills/aml-token-inspector/scripts
python3 build_inspector.py
cp scripts/index.html ./index.html   # 或 cp index.html ../index.html
```

### 3. 与设计稿（Pixso 导出 react 工程）同步

设计稿侧改色后（如 `~/Desktop/react`），从 `src/assets/styles/variables.css` 提取权威色值更新 tokens.json：

- **参数层**（`--brand-purple-25` 等）→ Primitives 基础色板
- **Mode 层**（`--color-color-bg-1` 等语义变量 → 参数层链）→ 语义色 Token
- 页面文字标注在 `src/views/Frame*.tsx` 的 `{"..."}` 文本里

注意：Pixso 每次重新导出都可能复现**空名变量 bug**（参数层出现 `--: rgba(...)`，导出时变量名丢失），需手动补回长名（如 `--7db8221d93c34bd6b1cb72fdbe30ba302065d03b-0-4: rgba(11,11,15,1)`）；重导出还会清掉 node_modules，验证构建前需 `npm install --cache /tmp/npm-cache-clean`。

### 4. 改页面布局 → 改生成器

`scripts/build_inspector.py` 是一个 ~1300 行的 Python 脚本，CSS/HTML/JS 全部内嵌在 Python 字符串里。修改它，再跑第 2 步。

关键位置：
- **双��叠区**：`COLOR_SEMANTIC`（语义 5 组顺序）/ `COLOR_PRIMITIVES`（基础色板 family）/ `accState`（primitives 默认 false=折叠）/ `renderColors()`
- **卡片 6 列网格**：`.shadow-cards{grid-template-columns:repeat(6,minmax(0,1fr))}` + 两档响应式
- **语义组白卡**：`main .shadow-group.color-group{background:#fff;...}`
- **字体卡 webfont**：`@font-face`（Roboto / Noto Sans Arabic latin woff2 base64，内嵌于 CSS）；微软雅黑走系统栈
- **字体卡样式拼接坑**：stack 含双引号，拼进 `style="font-family:..."` 必须 `f.stack.replace(/"/g,'&quot;')`，否则 HTML 属性被截断、font-size 失效回落 96px
- **顶栏 SVG 内联**：`_load_svg()` 读取三个 svg 并嵌入模板
- **小手 hover 动效**：`@keyframes aml-hand-tilt` + `@keyframes aml-hand-wave`
- **6 大板块渲染**：`renderColors()` / `renderTypography()` / `renderSpacing()` / `renderBorders()` / `renderShadows()` / `renderRadius()`
- **侧栏导航单页切换**：`showPage(name)` + 各 `<section data-page="X">`

### 5. 替换按钮默认态 SVG

如果用户给了新的「创建文件夹」PNG 抠图 SVG（比如桌面 `~/Desktop/创建文件夹.svg`），按以下步骤替换：

1. 把新 SVG 拷贝到 `scripts/folder_btn_default.svg`
2. 如果 PNG 内嵌太大（>100KB），用 PIL 裁剪：

```python
from PIL import Image
import base64, io, re
src = open('scripts/folder_btn_default.svg', encoding='utf-8').read()
m = re.search(r'<image id="image_1" width="(\d+(?:\.\d+)?)" height="(\d+(?:\.\d+)?)" xlink:href="data:image/png;base64,([A-Za-z0-9+/=]+)"', src)
W, H, b64 = m.group(1), m.group(2), m.group(3)
img = Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGBA')
bbox = img.split()[-1].getbbox()       # 透明 bbox
crop = img.crop(bbox).resize((80, 80), Image.LANCZOS)
buf = io.BytesIO()
crop.save(buf, format='PNG', optimize=True)
new_b64 = base64.b64encode(buf.getvalue()).decode()
# 替换 image 标签 + 改 pattern matrix 为 matrix(1/80,0,0,1/80,0,0)
```

3. 重新跑生成器
4. **关键**：如果新 SVG 的 `clipPath_N` 后缀号跟旧的不一样，确认 `build_inspector.py` 里的 `re.sub` 正则用 `\d+` 兼容任意后缀

### 6. 双 skill 同步

`~/.workbuddy/skills/规范样式/` 是本 skill 的姊妹版，**改任何一侧都要同步另一侧**：

```bash
cp aml-token-inspector/scripts/build_inspector.py 规范样式/scripts/
cp aml-token-inspector/scripts/tokens.json 规范样式/scripts/
cd 规范样式/scripts && python3 build_inspector.py && cp index.html ../index.html
```

再重打包桌面分发包��在 skills 目录下打，保持 `aml-token-inspector/` 前缀）：

```bash
cd ~/.workbuddy/skills && rm -f ~/Desktop/aml-token-inspector.zip
zip -r -q ~/Desktop/aml-token-inspector.zip aml-token-inspector/index.html aml-token-inspector/SKILL.md \
  aml-token-inspector/scripts/build_inspector.py aml-token-inspector/scripts/tokens.json \
  aml-token-inspector/scripts/index.html aml-token-inspector/scripts/pill_brand.svg \
  aml-token-inspector/scripts/folder_btn_default.svg aml-token-inspector/scripts/folder_btn_active.svg
```

## 维护要点

- **小手动画规格**：hover 时 0.15s ease 从 0° 过冲到 29° 落在 25° 基线，随后 0.7s 循环不均节奏挥动（幅度递减：33°→18°→31°→20°）
- **小手 transform-origin**：50% 50% + `transform-box: fill-box`
- **复制反馈**：点击卡片复制 CSS / HEX；顶部 toast + 卡片 1.2s `.copied` 高亮；file:// 下降级 `execCommand('copy')`
- **验证方式**：puppeteer-core 无头浏览器（NODE_PATH=/Users/happy/.workbuddy/binaries/node/workspace/node_modules + Chrome headless=new + 独立 user-data-dir）；改完重建后核对 DOM 结构/色值/间距/交互

## 不要做的事

- **不要**让 `build_inspector.py` 依赖 `~/.claude/skills/...` 路径，新 skill 必须是自包含的
- **不要**在 HTML 里内嵌 otf/ttf 字体（MB 级膨胀）；只用 latin 分片 woff2 base64（~30KB）
- **不要**给 SVG id 写硬编码的 `clipPath_17`，`re.sub` 用 `\d+` 兼容
- **不要**让 transform 用绝对坐标，用 `50% 50% + fill-box` 居中
- **不要**把字体 stack 未转义直接拼进 HTML style 属性（引号截断坑）

## 验证清单

每次改完跑一遍：

1. `python3 scripts/build_inspector.py` 不报错，双 skill `diff` 一致
2. `cp scripts/index.html ./index.html` + 重打包桌面 zip
3. Color 页：Primitives 默认折叠可展开（6 色系 × 12 档）；语义区 5 组顺序 = 主色→中性色→功能色→分类色→安全色，每组白色卡片背景
4. 卡片每行最多 6 个等宽；颜色行标签与卡片顶对齐
5. Typography：4 字体卡样例 13px、以对应字体渲染（微软雅黑系统栈 / Roboto / Noto Sans Arabic 内嵌）
6. 顶栏小手动效、toast 复制、侧栏切换正常
