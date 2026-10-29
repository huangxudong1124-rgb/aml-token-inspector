# AML Design Token Inspector

把 **AML Design 设计系统**的全部设计 token 渲染成一个**离线、双击即开**的单文件 HTML 自检页，供设计师与前端查阅、复制。

页面含 6 大板块：**Color / Typography / Spacing / Border / Shadow / Radius**。

- 点击任意卡片 → 复制对应 CSS 声明
- 全站字体按字符类型分流：中文 → 微软雅黑，英文 → Roboto，数字与标点 → Noto Sans Arabic
- 完全离线：字体以 base64 内嵌，无外网依赖

---

## 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/__OWNER__/aml-token-inspector/main/install.sh | bash
```

或先克隆再本地执行：

```bash
git clone https://github.com/__OWNER__/aml-token-inspector.git
cd aml-token-inspector && ./install.sh
```

脚本会自动：

1. 识别当前客户端（WorkBuddy → `~/.workbuddy/skills/`，CodeBuddy → `~/.codebuddy/skills/`）
2. 把仓库里所有含 `SKILL.md` 的一级目录复制过去（已存在则覆盖更新）

装完后重启会话（或刷新技能列表）即可生效。

### 手动安装

把 `aml-token-inspector/` 整个文件夹复制到 `~/.workbuddy/skills/` 下即可，或直接双击 `aml-token-inspector/index.html` 打开页面（不装 skill 也能当工具用）。

---

## 仓库结构

```
aml-token-inspector/
├── install.sh                    一键安装脚本
├── aml-token-inspector/          skill 本体（自检页）
│   ├── SKILL.md                  skill 说明（AI 读这份）
│   ├── index.html                产物：单文件自检页 ← 直接双击打开这个
│   └── scripts/
│       ├── build_inspector.py    生成器：读 tokens.json → 输出 index.html
│       ├── tokens.json           唯一数据源：颜色 / 字体 / 间距 / 圆角 / 投影
│       └── index.html            构建产物副本
└── 规范样式/                      孪生 skill：从规范源文件抽取 token
    ├── SKILL.md
    ├── scripts/extract.py        抽取
    ├── scripts/apply.py          回写
    ├── scripts/tokens.json
    ├── colors.csv / shadows.csv / radius.csv
    └── index.html
```

> 两个 skill 共用同一套自检页与 `tokens.json`，内容保持一致。

---

## 改数据后重新生成

**不要直接改 `index.html`**（会被覆盖）。正确流程：

```bash
cd aml-token-inspector/scripts

# 1. 改数据源
#    tokens.json  →  颜色 / 字体 / 间距 / 圆角 / 投影

# 2. 重新生成
python3 build_inspector.py          # 输出到 scripts/index.html

# 3. 同步到 skill 根目录
cp scripts/index.html ../index.html
```

生成后双击 `aml-token-inspector/index.html` 即可看到新页面。

若同时维护 `规范样式` skill，记得把 `build_inspector.py` 和 `tokens.json` 同步过去再重建一次。

---

## 设计规范速览

| 板块 | 要点 |
| --- | --- |
| Color | 语义色分组：主色 → 中性色 → 功能色 → 分类色 → 安全色；另有 Primitives 基础色板（6 色系 × 12 档） |
| Typography | 字体族 3 类、字号 10 级、字重、等宽 Roboto Mono、文本色阶 Text/1–5 |
| Spacing | 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 px |
| Border & Radius | 内圆角统一 4 / 8px |
| Shadow | 按组件分组的投影层级 |

---

## 许可

内部设计规范资产，仅供团队内部使用。
