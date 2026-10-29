#!/usr/bin/env python3
"""Build a self-contained token-inspector index.html from tokens.json.

Run:  python3 build.py
Reads ./tokens.json (output of the figma-tokens skill) and writes ./index.html
with the data inlined, so the page works by double-clicking (no server needed).

Layout (2026-09-15 重构): 顶栏 + 左侧导航参照 Frame_1117_58 设计稿
(react 2 的 Topbar/Sidebar)，导航项参照 Frame 338_863 (react 3):
Color 颜色 / Typography 字体 / Border 边框 / Shadow 投影 / Radius 圆角。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# 单一数据源：本 skill 自身的 scripts/tokens.json
with open(os.path.join(HERE, "tokens.json"), encoding="utf-8") as f:
    TOKENS = json.load(f)

# Radius usages were not auto-paired from the canvas; fill from the spec.
RADIUS_USAGE = {
    2: "细小元素",
    4: "下拉菜单 / 卡片 / 气泡 / 弹窗 / 输入框（内圆角）",
    6: "主按钮、偏大的标签 / 按钮",
    8: "小卡片",
    12: "大卡片（超过内容区 1/4 宽度）",
    20: "特殊场景（如首页大模块）",
    24: "页面 / 大容器外圆角",
}

# Typography tokens (源自 react 2 · Font 设计稿 Frame2620)。
# 渲染时只用 web-safe 兜底栈（PingFang SC / Microsoft YaHei / Roboto / Noto Sans Arabic / DM Sans），
# 设计稿里的 otf/ttf 文件体积过大不在本页面嵌入。
TYPOGRAPHY = {
    "families": [
        {"key":"cn",   "name":"微软雅黑", "sub":"Microsoft YaHei",
         "stack":"\"Microsoft YaHei\", \"微软雅黑\", \"Source Han Sans CN\", sans-serif",
         "tag":"中文", "sample":"数据知识管理系统", "glyph_size":13},
        {"key":"en",   "name":"Roboto",   "sub":"Roboto",
         "stack":"Roboto, -apple-system, BlinkMacSystemFont, \"Segoe UI\", \"Helvetica Neue\", Arial, sans-serif",
         "tag":"英文", "sample":"Volcengine", "glyph_size":13},
        {"key":"num",  "name":"Noto Sans Arabic", "sub":"Noto Sans Arabic",
         "stack":"\"Noto Sans Arabic\", \"Geeza Pro\", \"Segoe UI\", Tahoma, sans-serif",
         "tag":"数字", "sample":"1234567890", "glyph_size":13},
        {"key":"punct","name":"Noto Sans Arabic", "sub":"Noto Sans Arabic",
         "stack":"\"Noto Sans Arabic\", \"Geeza Pro\", \"Segoe UI\", Tahoma, sans-serif",
         "tag":"标点符号", "sample":"@%……", "glyph_size":13},
    ],
    "sizes": [
        {"key":"display-3", "name":"Display 3",   "size":56, "line_height":64, "letter_spacing":0,    "usage":"首屏巨型展示标题",     "sample_zh":"数据知识管理系统", "weight":700},
        {"key":"display-2", "name":"Display 2",   "size":36, "line_height":44, "letter_spacing":0.3,  "usage":"顶部 / 引导页大标题",  "sample_zh":"ABC 数据知识管理系统", "weight":700},
        {"key":"display-1", "name":"Display 1",   "size":36, "line_height":44, "letter_spacing":0.3,  "usage":"顶部 / 引导页大标题",  "sample_zh":"ABC 数据知识管理系统", "weight":700},
        {"key":"title-3",   "name":"Title 3",     "size":30, "line_height":38, "letter_spacing":0.3,  "usage":"Section 标题",          "sample_zh":"ABC 数据知识管理系统", "weight":600},
        {"key":"title-2",   "name":"Title 2",     "size":30, "line_height":38, "letter_spacing":0.3,  "usage":"Section 标题",          "sample_zh":"ABC 数据知识管理系统", "weight":600},
        {"key":"title-1",   "name":"Title 1",     "size":24, "line_height":32, "letter_spacing":0.3,  "usage":"卡片标题 / 子标题",     "sample_zh":"ABC 数据知识管理系统", "weight":600},
        {"key":"body-3",    "name":"Body 3",      "size":18, "line_height":26, "letter_spacing":0.3,  "usage":"正文（多行说明）",      "sample_zh":"ABC 数据知识管理系统", "weight":400},
        {"key":"body-2",    "name":"Body 2",      "size":16, "line_height":24, "letter_spacing":0.3,  "usage":"正文（多行说明）",      "sample_zh":"ABC 数据知识管理系统", "weight":400},
        {"key":"body-1",    "name":"Body 1",      "size":14, "line_height":22, "letter_spacing":0.3,  "usage":"正文（多行说明）",      "sample_zh":"ABC 数据知识管理系统", "weight":400},
        {"key":"caption",   "name":"Caption",     "size":12, "line_height":18, "letter_spacing":0.3,  "usage":"辅助说明 / 标签",       "sample_zh":"ABC 数据知识管理系统", "weight":400},
    ],
    "weights_cn": [
        {"weight":"Regular", "val":400, "label":"Microsoft YaHei-Regular", "text":"ABC 数据知识管理系统"},
        {"weight":"Medium",  "val":500, "label":"Microsoft YaHei-Medium",  "text":"ABC 数据知识管理系统"},
        {"weight":"Bold",    "val":700, "label":"Microsoft YaHei-Bold",    "text":"ABC 数据知识管理系统"},
    ],
    "weights_en": [
        {"weight":"Regular", "val":400, "label":"Roboto-Regular", "text":"ABC Data and Knowledge Governance System"},
        {"weight":"Medium",  "val":500, "label":"Roboto-Medium",  "text":"ABC Data and Knowledge Governance System"},
        {"weight":"Bold",    "val":700, "label":"Roboto-Bold",    "text":"ABC Data and Knowledge Governance System"},
    ],
    "mono": [
        {"weight":"Regular", "val":400, "text":"Source force shapes all things and stimulates digital vitality"},
        {"weight":"Medium",  "val":500, "text":"Source force shapes all things and stimulates digital vitality"},
        {"weight":"Bold",    "val":700, "text":"Source force shapes all things and stimulates digital vitality"},
    ],
    "text_tones": [
        {"key":"text-5", "name":"Text/5 · 一级/正文", "hex":"#0B0B0F", "use":"一级/正文（强调正文标题）",     "sample":"ABC 数据知识管理系统"},
        {"key":"text-4", "name":"Text/4 · 次级/正文", "hex":"#61646C", "use":"次级/正文（次强调正文标题）",   "sample":"ABC 数据知识管理系统"},
        {"key":"text-3", "name":"Text/3 · 次要信息",  "hex":"#85888E", "use":"次要信息",                     "sample":"ABC 数据知识管理系统"},
        {"key":"text-2", "name":"Text/2 · 置灰信息",  "hex":"#B1B3BB", "use":"置灰信息",                     "sample":"ABC 数据知识管理系统"},
        {"key":"text-1", "name":"Text/1 · 反白文字",  "hex":"#FFFFFF", "use":"反白文字",                     "sample":"ABC 数据知识管理系统"},
    ],
    "line_height": [
        {"name":"line-height:1",   "val":"1",   "desc":"无行高（图标、单行）",  "sample":"ABC 数据知识管理系统，ABC 数据知识管理系统"},
        {"name":"line-height:1.3", "val":"1.3", "desc":"紧凑（小标题、卡片）",  "sample":"ABC 数据知识管理系统，ABC 数据知识管理系统"},
        {"name":"line-height:1.5", "val":"1.5", "desc":"常规（正文）",          "sample":"ABC 数据知识管理系统，ABC 数据知识管理系统"},
        {"name":"line-height:1.7", "val":"1.7", "desc":"宽松（长文 / 描述）",  "sample":"ABC 数据知识管理系统，ABC 数据知识管理系统"},
    ],
    "font_family_css": 'font-family: "Noto Sans Arabic", Roboto, "Microsoft YaHei", "PingFang SC", sans-serif;  /* 数字/标点→Noto Sans Arabic（unicode-range 截胡）、英文→Roboto、中文→微软雅黑 */',
}

# Spacing token（截图 Spacing.png · 间距）
SPACING = [
    {"key":"xxxs", "name":"xxxs", "px":4,  "rem":0.25, "usage":"最小间距（图标与文字）"},
    {"key":"xxs",  "name":"xxs",  "px":8,  "rem":0.5,  "usage":"紧凑（表单内元素）"},
    {"key":"xs",   "name":"xs",   "px":12, "rem":0.75, "usage":"小间距（按钮内边距）"},
    {"key":"s",    "name":"s",    "px":16, "rem":1.0,  "usage":"标准（卡片内元素）"},
    {"key":"m",    "name":"m",    "px":20, "rem":1.25, "usage":"中等（卡片间距）"},
    {"key":"l",    "name":"l",    "px":24, "rem":1.5,  "usage":"大间距（Section 间距）"},
    {"key":"xl",   "name":"xl",   "px":32, "rem":2.0,  "usage":"特大（页面分段）"},
    {"key":"xxl",  "name":"xxl",  "px":40, "rem":2.5,  "usage":"页面边距"},
    {"key":"xxxl", "name":"xxxl", "px":48, "rem":3.0,  "usage":"页面级间距"},
]
for r in TOKENS["radius"]:
    r["usage"] = RADIUS_USAGE.get(r["value"], r.get("usage", ""))

LEVEL_ROLE = {
    1: "浅色场景", 2: "Tag 背景", 3: "描边 Stroke", 4: "一般禁用",
    5: "特殊场景", 6: "常规 Default", 7: "悬浮 Hover", 8: "点击 Active",
}

JSON_STR = json.dumps({"colors":TOKENS.get("colors",[]),"shadows":TOKENS.get("shadows",[]),"radius":TOKENS.get("radius",[]),"typography":TYPOGRAPHY,"spacing":SPACING}, ensure_ascii=False)

# 顶栏左胶囊视觉 = react 2 设计稿导出的 Component 266.svg（207.87×44：大脑 logo + 分隔线 + AML Design 字标）
SVG_PATH = os.path.join(HERE, "pill_brand.svg")
with open(SVG_PATH, encoding="utf-8") as f:
    PILL_SVG = f.read().strip()

# 「创建文件夹」按钮组件（react 2 · Component338242）：默认态 104.57×24 / 点击态 139.63×24
def _load_svg(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        s = f.read().strip()
    s = s.replace("<svg ", '<svg class="aml-folder-btn-art" ', 1)
    # 给小手 group（外层 id="容器 268"）加 class="aml-hand"，CSS 旋转用它
    if name == "folder_btn_default.svg":
        # 给小手 group 加 class="aml-hand"（任意 clipPath_N 后缀都兼容）
        s = re.sub(
            r'(<g id="容器 268")( customFrame="url\(#clipPath_\d+\)">)',
            r'\1 class="aml-hand"\2', s
        )
        # 去掉内层重复 id，避免选择器歧义（保留渲染）
        s = s.replace(
            '<rect id="容器 268"',
            '<rect class="aml-hand-rect" fill="none" pointer-events="none"'
        )
    return s

FOLDER_DEFAULT_SVG = _load_svg("folder_btn_default.svg")
FOLDER_ACTIVE_SVG = _load_svg("folder_btn_active.svg")

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AML Design Tokens · Inspector</title>
<style>
  :root{
    /* theme primary = Pixso「数据知识管理系统」Brand Purple 600 (#7B32DE) */
    --primary:#7B32DE; --primary-hover:#6512AD; --primary-soft:#F4F0FF;
    --ink:#0B0B0F; --text-2:#3C3E43; --text-3:#61646C; --text-4:#85888E;
    --border:#E2E2E3; --border-soft:#ECECED;
    --bg:#FAFAFA; --surface:#FFFFFF; --surface-2:#F5F5F6;
    --code:#2B303A;
    --shadow-card:0 2px 6px 0 rgba(0,0,0,.05);
    --shadow-float:0 5px 15px 0 rgba(0,0,0,.05),0 15px 35px -2px rgba(0,0,0,.05);
    --shadow-ring:0 1px 2px 0 rgba(0,0,0,.05),0 0 0 1px var(--border-soft);
    --radius:10px; --radius-sm:6px;
    --topbar-h:66px; --sidebar-w:244px;
    /* Spacing scale（与 SPACING token 对齐） */
    --s-xxxs:4px;  --s-xxs:8px;  --s-xs:12px;  --s-s:16px;
    --s-m:20px;    --s-l:24px;  --s-xl:32px;  --s-xxl:40px;
    --s-xxxl:48px;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{
    /* 全站字体路由（字符级分流）：数字/标点 → Noto Sans Arabic（@font-face 用 unicode-range 截胡），
       英文字母 → Roboto，中文 → 微软雅黑（系统字体） */
    font-family:"Noto Sans Arabic",Roboto,"Microsoft YaHei","PingFang SC",sans-serif;
    background:var(--bg); color:var(--ink);
    -webkit-font-smoothing:antialiased; line-height:1.5;
  }
  code,mono,.mono{font-family:"SF Mono",ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}

  /* ================= 顶栏 — 设计稿「容器 37」：Component 266 SVG + 右侧真实输入组件 ================= */
  header.aml-topbar{
    position:fixed; top:0; left:0; right:0; z-index:40;
    height:var(--topbar-h);
    background:#fff;
    border-bottom:1px solid var(--border-soft);
  }
  .aml-brand-pill{
    position:absolute; left:10px; top:11px;
    display:flex; align-items:center;
    height:44px; padding-right:16px;
  }
  .aml-brand-pill>svg{display:block; flex:none}
  .aml-menu-btn{
    position:absolute; right:10px; top:50%; transform:translateY(-50%); z-index:2;
    display:none; flex:none; width:34px; height:34px;
    align-items:center; justify-content:center;
    border:1px solid var(--border); border-radius:8px;
    background:#fff; color:var(--text-2); cursor:pointer;
  }
  .aml-menu-btn:hover{color:var(--ink)}

  /* ---- 右侧「创建文件夹」按钮组件（react 2 · Component338242，默认/点击两态 SVG） ---- */
  .aml-folder-btn{
    flex:none; display:flex; align-items:center; height:24px; margin-left:12px;
    padding:0; border:none; background:transparent; cursor:pointer; user-select:none;
  }
  .aml-folder-btn .aml-folder-btn-art{display:block; height:24px; width:auto; overflow:visible}
  .aml-folder-btn{position:relative; z-index:3}
  .aml-folder-btn .state-default, .aml-folder-btn .state-active{display:block; overflow:visible}
  .aml-folder-btn .state-active{display:none}
  .aml-folder-btn.pressed .state-default{display:none}
  .aml-folder-btn.pressed .state-active{display:block}

  /* ---- 手掌以手心为轴自然挥动：先转腕到位，再不均节奏挥两下、幅度递减后归位 ---- */
  @keyframes aml-hand-tilt{
    /* 0 → 微过冲 29° → 回落 25° 基线（模拟手腕带一点弹性） */
    0%{transform:rotate(0deg)}
    70%{transform:rotate(29deg)}
    100%{transform:rotate(25deg)}
  }
  @keyframes aml-hand-wave{
    /* 25° 基线：挥出(-8°)→带回(+7°)→再挥(-6°)→归位，节奏不均 + 幅度递减 */
    0%{transform:rotate(25deg)}
    18%{transform:rotate(33deg)}
    40%{transform:rotate(18deg)}
    60%{transform:rotate(31deg)}
    80%{transform:rotate(20deg)}
    100%{transform:rotate(25deg)}
  }
  /* 把手做成悬停命中区，pointer-events 接管鼠标事件 */
  .aml-folder-btn .state-default .aml-folder-btn-art .aml-hand,
  .aml-folder-btn .state-default .aml-folder-btn-art .aml-hand-rect{
    transform-box:fill-box;
    transform-origin:50% 65%;
    pointer-events:all;
    cursor:pointer;
  }
  /* 整按钮 hover 或精确 hover 小手都触发 */
  .aml-folder-btn:hover .state-default .aml-folder-btn-art .aml-hand,
  .aml-folder-btn:hover .state-default .aml-folder-btn-art .aml-hand-rect,
  .aml-folder-btn .state-default .aml-folder-btn-art .aml-hand:hover,
  .aml-folder-btn .state-default .aml-folder-btn-art .aml-hand-rect:hover{
    animation:
      aml-hand-tilt .15s cubic-bezier(.3,.7,.4,1) forwards,
      aml-hand-wave .7s cubic-bezier(.45,0,.55,1) .15s infinite;
  }

  /* ================= 侧边导航 — Element 文档风格，AML token ================= */
  .aml-sidebar{
    position:fixed; top:var(--topbar-h); left:0; bottom:0; z-index:35;
    display:flex; flex-direction:column;
    width:var(--sidebar-w);
    background:#fff; border-right:1px solid var(--border-soft);
    overflow-y:auto; overscroll-behavior:contain;
  }
  .aml-sidenav{flex:1; padding:12px 8px 20px}
  .aml-sidenav-group{margin-bottom:4px}
  .aml-sidenav-title{
    margin:16px 14px 4px;
    font-size:13px; font-weight:500; color:var(--text-3);
    text-transform:none; letter-spacing:0;
    display:flex; align-items:center; gap:6px;
    padding:6px 8px; border-radius:8px;
    cursor:pointer; user-select:none;
    transition:background .12s, color .12s;
  }
  .aml-sidenav-title:hover{background:var(--surface-2); color:var(--ink)}
  .aml-sidenav-icon{font-style:normal;font-size:13px;line-height:1;filter:grayscale(.2)}
  .aml-sidenav-title .cnt{
    font-size:12px;color:var(--text-4);font-weight:400;margin-left:2px;
  }
  .aml-sidenav-title .chev{
    margin-left:auto; width:14px; height:14px;
    display:inline-flex; align-items:center; justify-content:center;
    color:var(--text-4); transition:transform .18s;
  }
  .aml-sidenav-group.collapsed .chev{transform:rotate(-90deg)}
  .aml-sidenav-group.collapsed .aml-sidenav-items{display:none}
  .aml-sidenav-group:first-child .aml-sidenav-title{margin-top:4px}
  .aml-sidenav-items{display:flex;flex-direction:column;gap:1px}
  .aml-sidenav-item{
    display:flex; align-items:center; gap:10px;
    margin:0; padding:8px 14px;
    border-radius:8px;
    font-size:13.5px; font-weight:500; color:var(--text-2); text-decoration:none;
    transition:background .12s, color .12s;
    position:relative;
  }
  .aml-sidenav-item .en{color:var(--text-4); font-weight:400; margin-right:1px}
  .aml-sidenav-item:hover{background:var(--surface-2); color:var(--ink)}
  .aml-sidenav-item.active{background:transparent; color:var(--primary)}
  .aml-sidenav-item.active .en{color:var(--primary); font-weight:500}
  .aml-sidebar-foot{
    flex:none; padding:14px 20px;
    border-top:1px solid var(--border-soft);
    font-size:11px; line-height:1.7; color:var(--text-4);
  }
  .aml-scrim{
    display:none; position:fixed; inset:var(--topbar-h) 0 0 0; z-index:34;
    background:rgba(11,11,15,.32);
  }
  .aml-scrim.show{display:block}

  /* ================= 内容区 ================= */
  main{
    margin-left:var(--sidebar-w);
    padding:calc(var(--topbar-h) + var(--s-xl)) var(--s-l) var(--s-xxxl);
    max-width:calc(1240px + var(--sidebar-w));
  }
  .doc-head{display:flex; align-items:flex-end; gap:var(--s-s); flex-wrap:wrap; margin-bottom:var(--s-xxs)}
  .doc-title{font-size:24px; font-weight:650; letter-spacing:-.01em; margin:0; color:var(--text-3)}
  .doc-sub{font-size:13px; color:var(--text-4); margin:0 0 var(--s-xxs)}
  .doc-toolbar{margin-left:auto; display:flex; align-items:center; gap:10px; flex-wrap:wrap}
  .stat{font-size:12px;color:var(--text-3);background:var(--surface-2);border:1px solid var(--border-soft);padding:5px 10px;border-radius:999px;white-space:nowrap}
  .stat b{color:var(--ink);font-weight:600}
  .btn{font-size:12px;color:var(--text-2);background:var(--surface);border:1px solid var(--border);padding:7px 11px;border-radius:8px;cursor:pointer;font-weight:500;transition:.15s}
  .btn:hover{border-color:var(--text-4);color:var(--ink)}
  .btn.on{background:var(--ink);color:#fff;border-color:var(--ink)}

  /* 单页切换：默认隐藏所有板块，.page-view 指定的板块才显示 */
  .section{margin-top:0;scroll-margin-top:calc(var(--topbar-h) + var(--s-s));display:none;animation:aml-page-fade .18s ease-out}
  .section.is-active{display:block}
  @keyframes aml-page-fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
  .section>h2{font-size:28px;font-weight:700;color:var(--ink);text-transform:none;letter-spacing:-.01em;margin:0 0 var(--s-xs)}
  .section>p.lead{font-size:15px;line-height:1.6;color:var(--text-3);margin:0 0 var(--s-xxl);max-width:none;white-space:nowrap}
  .family{margin-top:var(--s-xxxl)}
  .family>h3{font-size:15px;margin:0 0 var(--s-l);font-weight:600;display:flex;align-items:center;gap:var(--s-xxs)}
  .family>h3 .cnt{font-size:11px;color:var(--text-4);font-weight:400;background:var(--surface-2);border:1px solid var(--border-soft);padding:2px 7px;border-radius:999px}

  /* 建设中占位（Typography / Border） */
  .emptycard{
    margin-top:var(--s-m); padding:var(--s-xxxl) var(--s-l); text-align:center;
    border:1.5px dashed var(--border); border-radius:var(--radius);
    background:var(--surface); color:var(--text-4);
  }
  .emptycard svg{opacity:.5}
  .emptycard .t{font-size:15px;font-weight:600;color:var(--text-3);margin:var(--s-xs) 0 var(--s-xxs)}
  .emptycard .d{font-size:12.5px;line-height:1.7}
  .emptycard code{background:var(--surface-2);padding:1px 6px;border-radius:4px;font-size:11.5px}

  /* ============== Typography 板块（Element 文档风格） ============== */
  /* 字体族：代码块 + 3 个 sample 卡片 */
  .ty-family-stack{margin:var(--s-xxs) 0 var(--s-m)}
  .ty-family-code{
    display:block; background:var(--surface-2);
    border:1px solid var(--border-soft); border-radius:8px;
    padding:var(--s-s) var(--s-s); font-family:"SF Mono",ui-monospace,monospace;
    font-size:13px; line-height:1.7; color:var(--text-2);
    overflow-x:auto; white-space:nowrap; cursor:pointer;
    transition:border-color .12s;
  }
  .ty-family-code:hover{border-color:var(--border)}
  .ty-family-code .mono-str{color:var(--primary)}
  .ty-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--s-s)}
  .ty-grid .ty-family{min-width:0}
  .ty-grid .ty-family .glyph{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  @media(max-width:1080px){.ty-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  @media(max-width:640px){.ty-grid{grid-template-columns:1fr}}
  .ty-family{
    border:1px solid var(--border-soft); border-radius:var(--radius);
    background:var(--surface); padding:var(--s-l); min-height:180px;
    display:flex; flex-direction:column; gap:var(--s-s); cursor:pointer;
    transition:border-color .15s, box-shadow .15s;
  }
  .ty-family:hover{border-color:var(--border); box-shadow:var(--shadow-ring)}
  .ty-family .name{font-size:18px;font-weight:700;color:var(--ink);line-height:1.2}
  .ty-family .sub{font-size:12px;color:var(--text-4);margin-top:-8px}
  .ty-family .glyph{
    flex:1; display:flex; align-items:center; justify-content:center;
    color:var(--ink); font-size:96px; line-height:1; letter-spacing:-.04em;
  }
  .ty-family .meta{display:flex;justify-content:space-between;align-items:baseline;font-size:12px;color:var(--text-3);padding-top:var(--s-xs);border-top:1px solid var(--border-soft)}
  .ty-family .meta b{color:var(--ink);font-weight:600}

  /* Element 风格表格：表头 + 行 hover */
  .ty-size-table{display:flex;flex-direction:column;border:1px solid var(--border-soft);border-radius:var(--radius);background:var(--surface);overflow:hidden}
  .ty-size-head{
    display:grid; grid-template-columns:140px 130px 1fr 200px;
    gap:var(--s-l); padding:var(--s-xs) var(--s-l);
    background:var(--surface-2); color:var(--text-3);
    font-size:13px; font-weight:500;
    border-bottom:1px solid var(--border-soft);
  }
  .ty-size-row{
    display:grid; grid-template-columns:140px 130px 1fr 200px;
    gap:var(--s-l); align-items:center; padding:var(--s-s) var(--s-l);
    border-top:1px solid var(--border-soft); cursor:pointer; transition:background .12s;
  }
  .ty-size-row:first-of-type{border-top:none}
  .ty-size-row:hover{background:var(--surface-2)}
  .ty-size-row .key{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-2);font-weight:500}
  .ty-size-row .px{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-3)}
  .ty-size-row .sample{color:var(--ink);letter-spacing:0.003em;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .ty-size-row .desc{font-size:13px;color:var(--text-3)}
  @media(max-width:960px){
    .ty-size-head,.ty-size-row{grid-template-columns:120px 1fr}
    .ty-size-head .col3,.ty-size-head .col4,
    .ty-size-row .col3,.ty-size-row .col4{display:none}
  }

  /* 行高：4 档（紧凑 1.3 / 常规 1.5 / 宽松 1.7）+ 元数据列 */
  .ty-lineheight{display:flex;flex-direction:column;border:1px solid var(--border-soft);border-radius:var(--radius);background:var(--surface);overflow:hidden}
  .ty-lh-head{
    display:grid; grid-template-columns:140px 1fr 100px 140px;
    gap:var(--s-l); padding:var(--s-xs) var(--s-l);
    background:var(--surface-2); color:var(--text-3);
    font-size:13px; font-weight:500;
    border-bottom:1px solid var(--border-soft);
  }
  .ty-lh-row{
    display:grid; grid-template-columns:140px 1fr 100px 140px;
    gap:var(--s-l); align-items:center; padding:var(--s-m) var(--s-l);
    border-top:1px solid var(--border-soft); cursor:pointer; transition:background .12s;
  }
  .ty-lh-row:first-of-type{border-top:none}
  .ty-lh-row:hover{background:var(--surface-2)}
  .ty-lh-row .name{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--ink);font-weight:500}
  .ty-lh-row .sample{color:var(--ink);line-height:1;letter-spacing:0.003em;font-size:15px}
  .ty-lh-row .val{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-3)}
  .ty-lh-row .desc{font-size:13px;color:var(--text-3)}

  /* 字重：表头 + 行（Element 风格：左侧 token 名 + 大号样本） */
  .ty-weight-table{display:flex;flex-direction:column;border:1px solid var(--border-soft);border-radius:var(--radius);background:var(--surface);overflow:hidden}
  .ty-w-head{
    display:grid; grid-template-columns:140px 1fr 100px;
    gap:var(--s-l); padding:var(--s-xs) var(--s-l);
    background:var(--surface-2); color:var(--text-3);
    font-size:13px; font-weight:500;
    border-bottom:1px solid var(--border-soft);
  }
  .ty-weight-row{
    display:grid; grid-template-columns:140px 1fr 100px;
    gap:var(--s-l); align-items:center; padding:var(--s-l) var(--s-l);
    border-top:1px solid var(--border-soft); cursor:pointer; transition:background .12s;
  }
  .ty-weight-row:first-of-type{border-top:none}
  .ty-w-head+.ty-weight-row{border-top:none}
  .ty-weight-row:hover{background:var(--surface-2)}
  .ty-weight-row .name{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-2);font-weight:500}
  .ty-weight-row .sample{color:var(--ink);font-size:20px;line-height:28px;letter-spacing:0.003em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .ty-weight-row .num{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-3);text-align:right}
  .ty-weight-row.mono .sample{font-family:"Roboto Mono","SF Mono",ui-monospace,monospace;font-size:16px;line-height:24px}
  .ty-weight-row.cn .sample{font-family:inherit}
  .ty-weight-row.en .sample{font-family:Roboto,"Microsoft YaHei",sans-serif}

  /* 文本色阶：左侧色块 + token 名 + HEX + sample + 用途（Element 风格） */
  .ty-text-table{display:flex;flex-direction:column;border:1px solid var(--border-soft);border-radius:var(--radius);background:var(--surface);overflow:hidden}
  .ty-text-head{
    display:grid; grid-template-columns:36px 100px 120px 1fr 180px;
    gap:24px; padding:12px 24px;
    background:var(--surface-2); color:var(--text-3);
    font-size:13px; font-weight:500;
    border-bottom:1px solid var(--border-soft);
  }
  .ty-text-tone{
    display:grid; grid-template-columns:36px 100px 120px 1fr 180px;
    gap:var(--s-l); align-items:center; padding:var(--s-s) var(--s-l);
    border-top:1px solid var(--border-soft); cursor:pointer; transition:background .12s;
  }
  .ty-text-tone:first-of-type{border-top:none}
  .ty-text-tone:hover{background:var(--surface-2)}
  .ty-text-tone .sw{width:24px;height:24px;min-height:0;aspect-ratio:1/1;border-radius:6px;border:1px solid var(--border-soft)}
  .ty-text-tone .key{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-2);font-weight:500}
  .ty-text-tone .hex{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-3)}
  .ty-text-tone .sample{font-size:16px;letter-spacing:0.003em}
  .ty-text-tone .use{font-size:13px;color:var(--text-3)}
  /* 反白文字行：默认整行纯黑背景色 token（color-bg Lv8 #0B0B0F），hover 用 #3C3E43 */
  .ty-text-tone.dark-row{background:#0B0B0F}
  .ty-text-tone.dark-row:hover{background:#3C3E43}
  .ty-text-tone.dark-row .key{color:#B1B3BB}
  .ty-text-tone.dark-row .hex{color:#85888E}
  .ty-text-tone.dark-row .use{color:#85888E}
  .ty-text-tone.dark-row .sw{border-color:rgba(255,255,255,.18)}
  @media(max-width:960px){.ty-text-head,.ty-text-tone{grid-template-columns:24px 90px 1fr}.ty-text-head .col4,.ty-text-head .col5,.ty-text-tone .col4,.ty-text-tone .col5{display:none}}

  /* ============== Spacing 板块（间距） ============== */
  .spacing-table{display:flex;flex-direction:column;border:1px solid var(--border-soft);border-radius:var(--radius);background:var(--surface);overflow:hidden}
  .spacing-head{
    display:grid; grid-template-columns:90px 120px 100px 1fr 120px;
    gap:var(--s-l); padding:var(--s-xs) var(--s-l);
    background:var(--surface-2); color:var(--text-3);
    font-size:13px; font-weight:500;
    border-bottom:1px solid var(--border-soft);
  }
  .spacing-row{
    display:grid; grid-template-columns:90px 120px 100px 1fr 120px;
    gap:var(--s-l); align-items:center; padding:var(--s-s) var(--s-l);
    border-top:1px solid var(--border-soft); cursor:pointer; transition:background .12s;
  }
  .spacing-row:first-of-type{border-top:none}
  .spacing-row:hover{background:var(--surface-2)}
  .spacing-row .key{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-2);font-weight:500}
  .spacing-row .px{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--ink)}
  .spacing-row .rem{font-family:"SF Mono",ui-monospace,monospace;font-size:13px;color:var(--text-3)}
  .spacing-row .bar{display:flex;align-items:center;height:56px}
  .spacing-row .bar i{
    display:block;border-radius:0;min-width:2px;min-height:2px;
    background:#CEAEFF;border:1px solid #CEAEFF;
  }
  .spacing-row .use{font-size:13px;color:var(--text-3)}
  @media(max-width:960px){
    .spacing-head,.spacing-row{grid-template-columns:80px 1fr 80px}
    .spacing-head .col-bar,.spacing-row .col-bar{display:none}
  }

  /* color rows */
  .rowcard{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;margin-bottom:14px;box-shadow:var(--shadow-card)}
  .rowhead{display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
  .rowhead .name{font-size:13px;font-weight:600}
  .rowhead .name .en{color:var(--text-4);font-weight:400;margin-left:6px}
  .regchip{display:inline-flex;align-items:center;gap:7px;font-size:12px;color:var(--text-2);background:var(--surface-2);border:1px solid var(--border-soft);padding:3px 9px 3px 4px;border-radius:999px;cursor:pointer}
  .regchip .dot{width:14px;height:14px;border-radius:4px;border:1px solid rgba(0,0,0,.08)}
  .copyrow{margin-left:auto;font-size:11px;color:var(--primary);background:none;border:none;cursor:pointer;font-weight:500;padding:4px 8px;border-radius:6px}
  .copyrow:hover{background:var(--primary-soft)}
  .scale{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:8px}
  @media(max-width:720px){.scale{grid-template-columns:repeat(4,1fr)}}
  .sw{
    border-radius:8px;overflow:hidden;border:1px solid rgba(0,0,0,.06);cursor:pointer;position:relative;
    min-height:84px;display:flex;flex-direction:column;transition:transform .12s, box-shadow .12s
  }
  .sw:hover{transform:translateY(-2px);box-shadow:var(--shadow-float)}
  .sw .chip{flex:1;position:relative}
  .sw .lvl{position:absolute;top:7px;left:8px;font-size:11px;font-weight:700;letter-spacing:.02em}
  .sw .meta{background:var(--surface);padding:6px 8px;border-top:1px solid var(--border-soft)}
  .sw .hex{font-size:11.5px;font-weight:600;color:var(--ink)}
  .sw .role{font-size:10px;color:var(--text-4);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .sw .ccheck{display:none;font-size:9.5px;margin-top:2px;font-weight:600;letter-spacing:.01em}
  body.contrast-on .sw .ccheck{display:block}
  .sw .ccheck.v-ok{color:#0A7B3E}
  .sw .ccheck.v-mid{color:#B26A00}
  .sw .ccheck.v-bad{color:#C01048}
  body.contrast-on .sw.fail{outline:2px solid #C01048;outline-offset:-2px}
  #cstats{display:none;font-size:12px;color:var(--text-2);background:var(--surface-2);border:1px solid var(--border-soft);padding:7px 12px;border-radius:8px}
  body.contrast-on #cstats{display:inline-flex;gap:14px;align-items:center}
  #cstats b{color:var(--ink)}
  .sw.copied .meta{background:var(--primary-soft)}

  /* shadows */
  /* ============== Shadow / Color / Radius 统一布局 ============== */
  main .shadow-group.color-group{
    margin-top:64px;
    background:#fff; border:1px solid var(--border-soft); border-radius:var(--radius);
    padding:var(--s-l);
  }
  main .shadow-group.color-group .shadow-group-head{border-bottom-color:var(--border-soft); padding-left:0; padding-right:0}
  .shadow-group{margin-top:var(--s-xxl)}
  /* 仅当不是 color 板块时才清零第一组；Color 内部多组都要间距 */
  .shadow-group:first-child:not(.color-group){margin-top:0}
  .shadow-group-head{
    display:grid; grid-template-columns:168px 1fr auto;
    gap:var(--s-l); align-items:baseline; padding:var(--s-xxs) var(--s-xxs) var(--s-s);
    border-bottom:1px solid var(--border-soft); margin-bottom:var(--s-l);
  }
  .shadow-group-head .zh{font-size:15px;font-weight:600;color:var(--ink);line-height:1.2}
  .shadow-group-head .en{font-size:12px;color:var(--text-4);font-weight:500;letter-spacing:.02em}
  .shadow-group-head .cnt{font-size:11px;color:var(--text-4);font-weight:400;background:var(--surface-2);border:1px solid var(--border-soft);padding:2px 7px;border-radius:999px;justify-self:end}
  .shadow-row{
    display:grid; grid-template-columns:168px 1fr;
    gap:var(--s-l); align-items:center;
  }
  .shadow-row .row-label{
    display:flex; flex-direction:column; gap:var(--s-xxs);
    color:var(--text-3);
  }
  .shadow-row .row-label .zh{font-size:14px;color:var(--text-2);font-weight:500;line-height:1.3}
  .shadow-row .row-label .en{font-size:11px;color:var(--text-4);font-family:"SF Mono",ui-monospace,monospace;letter-spacing:.02em}
  .shadow-cards{
    display:grid; grid-template-columns:repeat(6,minmax(0,1fr));
    gap:var(--s-s); align-items:stretch;
  }
  /* 投影页卡片：一行 3 个（Color 页仍保持 6 个，用 #shadows 作用域隔离） */
  #shadows .shadow-cards{grid-template-columns:repeat(3,minmax(0,1fr))}
  @media(max-width:1280px){.shadow-cards{grid-template-columns:repeat(4,minmax(0,1fr))}#shadows .shadow-cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
  @media(max-width:720px){.shadow-cards{grid-template-columns:repeat(2,minmax(0,1fr))}#shadows .shadow-cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
  @media(max-width:960px){
    .shadow-row{grid-template-columns:1fr;gap:var(--s-xs)}
    .shadow-row .row-label{padding-top:0}
    .shadow-cards{grid-auto-flow:row; grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:var(--s-xs)}
  }

  .scard{
    background:var(--surface); border:1px solid var(--border-soft); border-radius:var(--radius);
    overflow:hidden; cursor:pointer; transition:transform .15s, box-shadow .15s;
    display:flex; flex-direction:column; height:100%;
  }
  .scard:hover{transform:translateY(-2px);box-shadow:0 6px 16px -4px rgba(11,11,15,.08),0 2px 4px -1px rgba(11,11,15,.06)}
  .scard.copied{}
  .scard .stage{
    background:var(--surface-2);
    padding:var(--s-l) var(--s-xs) var(--s-l); display:flex; align-items:center; justify-content:center;
    min-height:104px; flex:1;
  }
  .scard .tile{width:84px;height:56px;background:#fff;border-radius:8px}
  .scard .rtile{background:#CEAEFF;border-radius:8px}
  /* Border 分割线卡片：白色底（stage 白底承托 box-shadow 分割线） */
  .bcard-group .scard{background:#fff}
  .bcard-group .scard .stage{background:#fff}
  /* 卡片展示区与文字区之间的分隔线：两端留边，不顶到卡片边 */
  .scard .body{position:relative}
  .bcard-group .scard .body::before,
  .scard-group .scard .body::before{
    content:""; position:absolute; top:0; left:var(--s-xs); right:var(--s-xs);
    height:1px; background:var(--border-soft);
  }
  /* 投影卡片与边框卡片一致：白底 */
  .scard-group .scard{background:#fff}
  .scard-group .scard .stage{background:#fff}
  .scard .body{padding:var(--s-xs) var(--s-xs) var(--s-xs)}

  /* Input 输入展示卡：90×90 大圆角矩形 + 状态描边 */
  .scard .itile{
    width:120px; height:90px; background:#fff;
    border:1.5px solid var(--border);
    border-radius:12px;
    display:flex; align-items:center; justify-content:center;
    transition:border-color .12s, box-shadow .12s;
  }
  .scard .itile.is-hover{border-color:var(--primary);box-shadow:0 0 0 1px var(--primary),0 0 0 4px rgba(123,50,222,.12)}
  .scard .itile.is-active{border-color:var(--primary);border-width:1.5px}
  .scard .itile.is-error{border-color:#E31B54}
  .scard .itile.is-error.is-hover{border-color:#E31B54;box-shadow:0 0 0 1px #E31B54,0 0 0 4px rgba(227,27,84,.15)}
  .scard .itile.is-error.is-active{border-color:#E31B54;box-shadow:0 0 0 1px #E31B54,0 0 0 4px rgba(227,27,84,.3)}

  /* Color card：8 阶色带 */
  /* Color card：与 .scard 完全一致结构（stage + body + sname + scss），无选中描边 */
  /* 颜色页两大折叠区：Color Styles 语义色 / Primitives 基础色板 */
  .color-acc{margin-bottom:var(--s-l)}
  .color-acc-head{
    display:flex; align-items:center; gap:var(--s-s);
    padding:var(--s-xs) 0; margin-bottom:var(--s-m);
    border-bottom:1px solid var(--border);
    cursor:pointer; user-select:none;
  }
  .color-acc-head .chev{display:flex; color:var(--text-3); transition:transform .18s ease}
  .color-acc.is-collapsed .color-acc-head .chev{transform:rotate(-90deg)}
  .color-acc-head .en{font-size:18px;font-weight:700;color:var(--ink);letter-spacing:-.01em}
  .color-acc-head .zh{font-size:13px;color:var(--text-3)}
  .color-acc-head .cnt{margin-left:auto; font-size:12px; color:var(--text-4); white-space:nowrap}
  .color-acc-head:hover .chev{color:var(--primary)}
  .color-acc.is-collapsed .color-acc-body{display:none}
  .color-acc.is-collapsed .color-acc-head{margin-bottom:0}
  /* 每个色系行（整行）之间的间距加大 */
  .color-row:not(:last-child){margin-bottom:var(--s-xl)}
  .color-row .row-label{padding-top:0}
  .color-row{gap:var(--s-l); align-items:start}
  /* 颜色直接填充整个 stage（无内嵌小卡片），撑满卡片宽度 */
  .color-card .stage{background:var(--surface-2); height:64px; min-height:64px; flex:1; margin:0; align-self:stretch; width:100%}
  .scard .sname{font-size:11.5px;font-weight:600;color:var(--ink);line-height:1.3;text-transform:capitalize}
  .scard .scss{
    font-size:10px;color:var(--text-3);margin-top:var(--s-xxs);
    font-family:"SF Mono",ui-monospace,monospace;
    overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
    line-height:1.45;
  }
  /* Radius / 长描述场景：scard 自适应高度，scss 不截断 */
  .shadow-row.align-top{align-items:flex-start}
  .shadow-row.align-top .row-label{padding-top:20px}

  /* radius */
  .rgrid{display:flex;flex-direction:column}
  .rcard{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow-card);cursor:pointer;transition:transform .12s}
  .rcard:hover{transform:translateY(-2px)}
  .rblock{height:74px;background:#ECECED;margin-bottom:12px}
  .rval{font-size:22px;font-weight:700;letter-spacing:-.02em}
  .rval small{font-size:13px;font-weight:500;color:var(--text-4)}
  .ruse{font-size:11.5px;color:var(--text-3);margin-top:4px;line-height:1.4}

  /* toast */
  #toast{position:fixed;top:80px;left:50%;transform:translateX(-50%) translateY(-12px);
    background:var(--ink);color:#fff;padding:10px 18px;border-radius:10px;font-size:13px;font-weight:500;
    box-shadow:var(--shadow-float);opacity:0;pointer-events:none;transition:.22s;z-index:90;display:flex;align-items:center;gap:8px}
  #toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  /* alignment grid overlay */
  body.grid-on::before{
    content:"";position:fixed;inset:0;pointer-events:none;z-index:30;
    background-image:linear-gradient(rgba(123,50,222,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(123,50,222,.07) 1px,transparent 1px);
    background-size:8px 8px;
  }
  .empty{padding:40px;text-align:center;color:var(--text-4);font-size:14px}
  .foot{margin-top:60px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--text-4);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}

  /* ================= 响应式 — ≤960px 折叠侧栏 ================= */
  /* font-sample webfonts: Roboto + Noto Sans Arabic (latin woff2 base64); YaHei uses system font */
  @font-face{font-family:"Roboto";font-style:normal;font-weight:400;font-display:swap;src:url(data:font/woff2;base64,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) format("woff2");unicode-range:U+0021-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
  @font-face{font-family:"Noto Sans Arabic";font-style:normal;font-weight:400;font-display:swap;src:url(data:font/woff2;base64,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) format("woff2");unicode-range:U+0020-002F,U+0030-0039,U+003A-0040,U+005B-0060,U+007B-007E,U+2000-206F,U+3001-301F,U+FF01-FF20,U+FF3B-FF40,U+FF5B-FF65}

  @media(max-width:960px){
    .aml-menu-btn{display:flex}
    .aml-sidebar{
      transform:translateX(-100%);
      transition:transform .22s ease;
      box-shadow:var(--shadow-float);
    }
    .aml-sidebar.open{transform:none}
    main{margin-left:0; padding-top:calc(var(--topbar-h) + 16px)}
    .doc-toolbar{margin-left:0}
    .rgrid{grid-template-columns:repeat(2,1fr)}
  }
</style>
</head>
<body>

<!-- ============ 顶栏（容器 37：Component 266 SVG + 右侧真实输入组件） ============ -->
<header class="aml-topbar">
  <div class="aml-brand-pill">
    __PILL_SVG__
    <button class="aml-folder-btn" type="button" aria-label="创建文件夹">
      <span class="state-default">__FOLDER_DEFAULT__</span>
      <span class="state-active">__FOLDER_ACTIVE__</span>
    </button>
  </div>
  <button class="aml-menu-btn" id="menuBtn" aria-label="打开导航" type="button">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
  </button>
</header>

<!-- ============ 侧边导航（Element 文档风格） ============ -->
<div class="aml-scrim" id="scrim" aria-hidden="true"></div>
<aside class="aml-sidebar" id="sidebar">
  <nav class="aml-sidenav">
    <div class="aml-sidenav-group" data-group="design">
      <div class="aml-sidenav-title">
        <span class="aml-sidenav-icon">🔖</span>
        <span>基础样式</span><span class="cnt">(6)</span>
        <span class="chev"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span>
      </div>
      <div class="aml-sidenav-items">
        <a class="aml-sidenav-item" data-page="colors" href="#colors"><span class="en">Color</span>颜色</a>
        <a class="aml-sidenav-item" data-page="typography" href="#typography"><span class="en">Typography</span>字体</a>
        <a class="aml-sidenav-item" data-page="spacing" href="#spacing"><span class="en">Spacing</span>间距</a>
        <a class="aml-sidenav-item" data-page="border" href="#border"><span class="en">Border</span>边框</a>
        <a class="aml-sidenav-item" data-page="shadows" href="#shadows"><span class="en">Shadow</span>投影</a>
        <a class="aml-sidenav-item" data-page="radius" href="#radius"><span class="en">Radius</span>圆角</a>
      </div>
    </div>
  </nav>
  <div class="aml-sidebar-foot">
    AML Design Tokens · 规范样式
    <br>
    值与设计源 1:1 对齐
  </div>
</aside>

<main>
  <section class="section is-active" id="colors" data-page="colors" style="margin-top:0">
    <h2>颜色 · Color</h2>
    <p class="lead">点击任意色块复制 HEX。每行为一组色阶（Lv1 最浅 → Lv8 最深，Lv6 为常规锚点）。</p>
    <div id="colorHost"></div>
  </section>

  <section class="section" id="typography" data-page="typography">
    <h2>字体 · Typography</h2>
    <p class="lead">四类字体族（微软雅黑 / Roboto / Noto Sans Arabic），10 级字号 + 3 种字重。点击任意条目复制 <span class="mono">font</span> 简写。</p>

    <!-- 字体族：代码块 + 三个 sample 卡片 -->
    <div class="family">
      <h3>字体 Font-family</h3>
      <div class="ty-family-stack">
        <code class="ty-family-code">font-family: <span class="mono-str">"Noto Sans Arabic", Roboto, "Microsoft YaHei", "PingFang SC", sans-serif</span>;</code>
      </div>
      <div class="ty-grid" id="tyFamilyHost"></div>
    </div>

    <!-- 字号层级：Element 风格表格 -->
    <div class="family">
      <h3>字号 Font-size</h3>
      <div class="ty-size-table" id="tySizeHost"></div>
    </div>

    <!-- 字重 + 样本：Element 表格风格 -->
    <div class="family">
      <h3>字重 Font-weight</h3>
      <div class="ty-weight-table" id="tyWeightHost"></div>
    </div>

    <!-- 等宽字体 -->
    <div class="family">
      <h3>等宽字体 · Roboto Mono</h3>
      <div class="ty-weight-table" id="tyMonoHost"></div>
    </div>

    <!-- 文本色阶：Element 风格（色块 + token 名 + HEX + 用法） -->
    <div class="family">
      <h3>文本色阶 Text Color</h3>
      <div class="ty-text-table" id="tyTextHost"></div>
    </div>
  </section>

  <section class="section" id="spacing" data-page="spacing">
    <h2>间距 · Spacing</h2>
    <p class="lead">9 级间距尺度（4/8/12/16/20/24/32/40/48 px），按 rem 等比缩放。点击任意条目复制 <span class="mono">gap / padding / margin</span> 简写。</p>
    <div class="spacing-table" id="spacingHost"></div>
  </section>

  <section class="section" id="border" data-page="border">
    <h2>边框 · Border</h2>
    <p class="lead">分割线 / 描边样式，点击卡片复制 box-shadow（all 全边框 · top 上 · bottom 下 · left 左 · right 右）。</p>
    <div id="borderHost"></div>
  </section>

  <section class="section" id="shadows" data-page="shadows">
    <h2>投影 · Shadow</h2>
    <p class="lead">点击卡片复制 box-shadow。按用途分组：卡片投影 / Icon / 弹窗浮层 / 按钮（黑·灰·紫），每组用一个代表色保持一致。</p>
    <div id="shadowHost"></div>
  </section>

  <section class="section" id="radius" data-page="radius">
    <h2>圆角 · Radius</h2>
    <p class="lead">点击卡片复制 <span class="mono">border-radius</span>。设计原则：内圆角统一 4 / 8px。</p>
    <div class="rgrid" id="radiusHost"></div>
  </section>

  <div class="foot">
    <span>由 <span class="mono">规范样式</span> skill 从规范源文件抽取 · 值与规范 1:1 对齐</span>
    <span>双击即可打开 · 自包含离线页</span>
  </div>
</main>

<div id="toast">已复制</div>

<script id="data" type="application/json">__TOKENS__</script>
<script>
const TOKENS = JSON.parse(document.getElementById('data').textContent);
const LEVEL_ROLE = {1:"浅色场景",2:"Tag 背景",3:"描边 Stroke",4:"一般禁用",5:"特殊场景",6:"常规 Default",7:"悬浮 Hover",8:"点击 Active"};
const $ = s => document.querySelector(s);
const el = (t,c,h)=>{const e=document.createElement(t); if(c)e.className=c; if(h!=null)e.innerHTML=h; return e;};

/* ---------- toast + copy ---------- */
let toastT;
function toast(msg){
  const t=$('#toast'); t.textContent='✓ '+msg; t.classList.add('show');
  clearTimeout(toastT); toastT=setTimeout(()=>t.classList.remove('show'),1300);
}
function copy(text,msg,el){
  // 视觉反馈：被点击元素加 .copied 类（CSS 用 outline 高亮），1.2s 还原
  if(el){
    el.classList.add('copied');
    setTimeout(()=>el.classList.remove('copied'),1200);
  }
  // 复制主路径：现代 API；失败回退到 textarea + execCommand
  const ok=()=>toast(msg||'已复制');
  const fail=()=>toast('复制失败，请手动复制');
  const fallback=()=>{
    try{
      const ta=document.createElement('textarea');
      ta.value=text;
      ta.style.cssText='position:fixed;left:-9999px;top:0;opacity:0;pointer-events:none';
      document.body.appendChild(ta);
      ta.focus(); ta.select(); ta.setSelectionRange(0,text.length);
      const k=document.execCommand('copy');
      document.body.removeChild(ta);
      k?ok():fail();
    }catch(_){fail();}
  };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(ok).catch(fallback);
  }else{
    fallback();
  }
}

/* ---------- helpers ---------- */
function hexToRgb(h){h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}
function lum(h){const[r,g,b]=hexToRgb(h).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b;}
function onColor(hex){return lum(hex)>.55?'#0B0B0F':'#FFFFFF';}
function ratio(a,b){const L1=lum(a),L2=lum(b);return (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);}
function verdict(r){return r>=7?{t:'AAA',c:'ok'}:r>=4.5?{t:'AA',c:'ok'}:r>=3?{t:'大字',c:'mid'}:{t:'×',c:'bad'};}
const SURFACE='#FFFFFF';
function cleanName(row){
  // "Row / 功能色/Success" -> "Success" ; "Row / 主色" -> "主色"
  let s=row.replace(/^Row\s*\/?\s*/,'');
  return s;
}
function familyKey(fam){return fam.replace(/\s+/g,' ').trim();}

/* ---------- render colors ---------- */
// 两大折叠区：Primitives 基础色板（当前为空，自动隐藏）/ Color Styles 语义色 Token（主色→中性色→功能色→分类色→安全色）
const COLOR_SEMANTIC=['主色 Primary','中性色 · color','功能色 · color','分类色 Categorical','安全色 Safety'];
const COLOR_PRIMITIVES=['Primitives 基础色板'];
const ACC_SEMANTIC='semantic', ACC_PRIMITIVES='primitives';
const accState={semantic:true, primitives:false}; // 语义区默认展开，Primitives 默认折叠
function colorGroupRank(k){
  const s=COLOR_SEMANTIC.indexOf(k), p=COLOR_PRIMITIVES.indexOf(k);
  if(s>=0) return s;
  if(p>=0) return 100+p;
  return 200;
}
function renderColors(filter){
  const host=$('#colorHost'); host.innerHTML='';
  const q=filter.toLowerCase();
  // group by family preserving order
  const groups={}; const order=[];
  TOKENS.colors.forEach(c=>{const k=familyKey(c.family); if(!groups[k]){groups[k]=[];order.push(k);} groups[k].push(c);});
  // Primitives 区排最前 → 语义区排后面 → 其余兜底
  order.sort((a,b)=>colorGroupRank(a)-colorGroupRank(b));
  const searching=!!q;
  let shown=0;
  // 两块折叠区容器（Primitives 在前）
  const accs={};
  [[ACC_PRIMITIVES,'Primitives','基础色板'],[ACC_SEMANTIC,'Color Styles','语义色 Token']].forEach(([key,en,zh])=>{
    const acc=el('div','color-acc'+((accState[key]||searching)?'':' is-collapsed'));
    acc.dataset.acc=key;
    const famCount=order.filter(k=>(key===ACC_SEMANTIC?COLOR_SEMANTIC:COLOR_PRIMITIVES).includes(k)
      && groups[k].some(c=>{
        if(!q) return true;
        const hay=(c.family+' '+c.row+' '+Object.values(c.scale).join(' ')+' '+c.regular).toLowerCase();
        return hay.includes(q);
      })).length;
    const head=el('div','color-acc-head',
      '<span class="chev"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span>'
      +'<span class="en">'+en+'</span><span class="zh">'+zh+'</span>'
      +'<span class="cnt">'+famCount+' 色系</span>');
    head.onclick=()=>{ accState[key]=!accState[key]; renderColors(filter); };
    const body=el('div','color-acc-body');
    acc.appendChild(head); acc.appendChild(body);
    accs[key]=acc;
  });
  order.forEach(k=>{
    const isSem=COLOR_SEMANTIC.includes(k), isPrim=COLOR_PRIMITIVES.includes(k);
    const accKey=isSem?ACC_SEMANTIC:(isPrim?ACC_PRIMITIVES:null);
    const items=groups[k].filter(c=>{
      if(!q) return true;
      const hay=(c.family+' '+c.row+' '+Object.values(c.scale).join(' ')+' '+c.regular).toLowerCase();
      return hay.includes(q);
    });
    if(!items.length) return;
    shown+=items.length;
    const fam=el('div','shadow-group color-group');
    fam.appendChild(el('div','shadow-group-head',
      '<span class="en">'+k+'</span><span class="zh">'+k+'</span><span class="cnt">'+items.length+' 组</span>'));
    // 每 row 一行：左 label + 右 cards（与 Shadow 完全一致的结构）
    const base=k.split(' ')[0];
    items.forEach(c=>{
      const shortRow=cleanName(c.row);
      const row=el('div','shadow-row color-row');
      row.appendChild(el('div','row-label',
        '<span class="zh">'+shortRow+'</span><span class="en">'+k+' / '+base+'</span>'));
      const cards=el('div','shadow-cards color-cards');
      Object.keys(c.scale).map(Number).sort((a,b)=>a-b).forEach(lvl=>{
        const hex=c.scale[lvl];
        const role=(c.roles && c.roles[lvl]) ? c.roles[lvl] : (LEVEL_ROLE[lvl]||'');
        const r=ratio(hex,SURFACE), v=verdict(r);
        const card=el('div','scard color-card');
        card.innerHTML='<div class="stage" style="background:'+hex+'"></div>'
          +'<div class="body"><div class="sname">Lv'+lvl+' · '+(role||'色阶')+'</div><div class="scss">'+hex.toUpperCase()+'</div></div>';
        card.title=hex+' · '+v.t;
        card.onclick=(e)=>{e.stopPropagation();copy(hex,shortRow+' Lv'+lvl+' '+hex+' 已复制',card);};
        cards.appendChild(card);
      });
      row.appendChild(cards);
      fam.appendChild(row);
    });
    // family 挂到对应折叠区（未识别的 family 兜底挂语义区）
    accs[accKey||ACC_SEMANTIC].querySelector('.color-acc-body').appendChild(fam);
  });
  // 空折叠区（如 Primitives 暂无内容）自动隐藏
  if(accs[ACC_PRIMITIVES].querySelector('.color-acc-body').children.length)
    host.appendChild(accs[ACC_PRIMITIVES]);
  host.appendChild(accs[ACC_SEMANTIC]);
  if(!shown) host.appendChild(el('div','empty','没有匹配的颜色'));
}

/* ---------- render shadows ---------- */
function shadowSub(name){
  const parts=name.replace(/^shadow\//,'').split('/').map(s=>s.trim());
  const head=(parts[0]||'').toLowerCase();
  if(head.startsWith('assembly')){
    const c=(parts[1]||'').toLowerCase();
    if(c.startsWith('button')){
      const color=parts[2]||'Button'; // "Black 黑" / "Gray 灰" / ...
      const baseColor=color.split(/\s+/)[0];
      return {group:'Button 按钮', sub:'按钮 · '+color, base:baseColor};
    }
    if(c.includes('data')){
      const isErr=parts[2]&&parts[2].includes('Error');
      return {group:isErr?'Input 输入 · Error':'Input 输入 · 常规', sub:isErr?'输入 · Error':'输入 · 常规'};
    }
    if(c.startsWith('list'))  return {group:'List 列表', sub:'列表 List'};
    if(c.startsWith('slider'))return {group:'Slider 滑块', sub:'滑块 Slider'};
  }
  if(head.startsWith('card')){
    const isModal=parts[1]&&parts[1].includes('弹窗浮层');
    return {group:isModal?'Modal 弹窗浮层':'Card 卡片', sub:isModal?'弹窗浮层':'卡片投影'};
  }
  if(head.startsWith('icon'))return {group:'Icon 图标', sub:'Icon 图标'};
  if(head.startsWith('border'))return null; // 分割线 → 走边框板块
  return {group:'其他', sub:'其他'};
}
const SHADOW_GROUP_ORDER=['Card 卡片','Icon 图标','Modal 弹窗浮层',
  'Slider 滑块','List 列表','Input 输入 · 常规','Input 输入 · Error',
  'Button 按钮'];
const SHADOW_SUB_ORDER={
  'Card 卡片':['卡片投影'],
  'Icon 图标':['Icon 图标'],
  'Modal 弹窗浮层':['弹窗浮层'],
  'Slider 滑块':['滑块 Slider'],
  'List 列表':['列表 List'],
  'Input 输入 · 常规':['输入 · 常规'],
  'Input 输入 · Error':['输入 · Error'],
  'Button 按钮':['按钮 · Black 黑','按钮 · Gray 灰','按钮 · Purple 紫','按钮 · Red 红','按钮 · Blue 蓝','按钮 · Yellow 黄','按钮 · Green 绿'],
};
const SHADOW_STATE_ORDER=['Default 默认','Hover 悬浮','Active 激活','Disabled 禁用','Error','基础投影','Dropdown & Pop','Modal, Notification, Message'];
function stateKey(s){
  const last=s.name.replace(/^shadow\//,'').split('/').pop().trim();
  return last;
}
/* 分割线（shadow/border/*）归属「边框 Border」板块，不在投影板块��染 */
function isBorderDivider(s){ return (s.name||'').toLowerCase().startsWith('shadow/border'); }
function renderShadows(filter){
  const host=$('#shadowHost'); host.innerHTML='';
  const q=(filter||'').toLowerCase();
  // 按 (group, sub) 二级分组，并按状态顺序归并
  const buckets={};
  TOKENS.shadows.forEach(s=>{
    if(isBorderDivider(s)) return;
    if(q){const hay=(s.name+' '+s.css).toLowerCase(); if(!hay.includes(q))return;}
    const meta=shadowSub(s.name); if(!meta) return;
    if(!buckets[meta.group]) buckets[meta.group]={};
    if(!buckets[meta.group][meta.sub]) buckets[meta.group][meta.sub]=[];
    buckets[meta.group][meta.sub].push(s);
  });
  const groupOrder=Object.keys(buckets).sort((a,b)=>(SHADOW_GROUP_ORDER.indexOf(a)+1||99)-(SHADOW_GROUP_ORDER.indexOf(b)+1||99));
  if(!groupOrder.length){host.appendChild(el('div','empty','没有匹配的投影'));return;}
  groupOrder.forEach(g=>{
    const subs=buckets[g];
    const subOrder=(SHADOW_SUB_ORDER[g]||Object.keys(subs)).sort((a,b)=>(SHADOW_SUB_ORDER[g]?.indexOf(a)+1||99)-(SHADOW_SUB_ORDER[g]?.indexOf(b)+1||99));
    subOrder.forEach(sub=>{
      const items=subs[sub]||[];
      if(!items.length) return;
      // 按状态顺序排序
      items.sort((a,b)=>{
        const ka=stateKey(a), kb=stateKey(b);
        return (SHADOW_STATE_ORDER.indexOf(ka)+1||99)-(SHADOW_STATE_ORDER.indexOf(kb)+1||99);
      });
      const wrap=el('div','shadow-group scard-group');
      wrap.innerHTML='<div class="shadow-group-head"><span class="en">'+g+'</span><span class="zh">'+sub.split(' · ').slice(-1)[0]+'</span><span class="cnt">'+items.length+'</span></div>';
      const row=el('div','shadow-row');
      row.innerHTML='<div class="row-label"><span class="zh">'+sub.split(' · ').slice(-1)[0]+'</span><span class="en">'+sub.split(' · ')[0]+'</span></div>';
      const cards=el('div','shadow-cards');
      items.forEach(s=>{
        const st=stateKey(s);
        const card=el('div','scard');
        // Input 输入分组用专属展示：90×90 大圆角 + 状态描边（参考截图）
        const isInput=g.startsWith('Input 输入');
        const isErr=g.endsWith('Error');
        const stLow=st.toLowerCase();
        let stageInner;
        if(isInput){
          const cls=['itile'];
          if(stLow.includes('hover'))cls.push('is-hover');
          else if(stLow.includes('active')||stLow.includes('激活'))cls.push('is-active');
          if(isErr)cls.push('is-error');
          stageInner='<div class="'+cls.join(' ')+'" style="box-shadow:'+s.css+'"></div>';
        }else{
          stageInner='<div class="tile" style="box-shadow:'+s.css+'"></div>';
        }
        card.innerHTML='<div class="stage">'+stageInner+'</div>'
          +'<div class="body"><div class="sname">'+st+'</div><div class="scss">'+s.css+'</div></div>';
        card.title='box-shadow: '+s.css;
        card.onclick=(e)=>{e.stopPropagation();copy('box-shadow: '+s.css+';',sub+' / '+st+' 已复制',card);};
        cards.appendChild(card);
      });
      row.appendChild(cards);
      wrap.appendChild(row);
      host.appendChild(wrap);
    });
  });
}

/* ---------- render borders（分割线 shadow/border/*，归入边框板块） ---------- */
function renderBorders(filter){
  const host=$('#borderHost'); host.innerHTML='';
  const q=(filter||'').toLowerCase();
  const items=TOKENS.shadows.filter(s=>{
    if(!isBorderDivider(s)) return false;
    if(q){const hay=(s.name+' '+s.css).toLowerCase(); return hay.includes(q);}
    return true;
  });
  if(!items.length){host.appendChild(el('div','emptycard','<div class="t">没有匹配的边框样式</div>'));return;}
  // 按方向排序：all / top / bottom / left / right
  const order={all:0,top:1,bottom:2,left:3,right:4};
  items.sort((a,b)=>{
    const da=(a.name.split('/').pop()||'').toLowerCase();
    const db=(b.name.split('/').pop()||'').toLowerCase();
    return (order[da]??99)-(order[db]??99);
  });
  const wrap=el('div','shadow-group bcard-group');
  wrap.innerHTML='<div class="shadow-group-head"><span class="en">Border 边框</span><span class="zh">分割线</span><span class="cnt">'+items.length+'</span></div>';
  const row=el('div','shadow-row');
  row.innerHTML='<div class="row-label"><span class="zh">分割线</span><span class="en">Divider</span></div>';
  const cards=el('div','shadow-cards');
  items.forEach(s=>{
    const dir=s.name.split('/').pop();
    const card=el('div','scard');
    card.innerHTML='<div class="stage"><div class="tile" style="box-shadow:'+s.css+';border-radius:0"></div></div>'
      +'<div class="body"><div class="sname">'+dir+'</div><div class="scss">'+s.css+'</div></div>';
    card.title='box-shadow: '+s.css;
    card.onclick=(e)=>{e.stopPropagation();copy('box-shadow: '+s.css+';','Border / '+dir+' 已复制',card);};
    cards.appendChild(card);
  });
  row.appendChild(cards);
  wrap.appendChild(row);
  host.appendChild(wrap);
}

/* ---------- render radius ---------- */
const RADIUS_GROUP=[
  {label:'Inner', zh:'内圆角（输入框 / 胶囊）',   range:v=>v<=4},
  {label:'Standard', zh:'常规（卡片 / 按钮 / 标签）', range:v=>v>=6 && v<=12},
  {label:'Special', zh:'特殊（弹窗 / 页面大容器）',   range:v=>v>=20},
];
const RADIUS_DESC={
  2:'细小元素',
  4:'下拉菜单 / 卡片 / 气泡 / 弹窗 / 输入框（内圆角）',
  6:'主按钮、偏大的标签 / 按钮',
  8:'小卡片',
  12:'大卡片（超过内容区 1/4 宽度）',
  20:'特殊场景（如首页大模块）',
  24:'页面 / 大容器外圆角',
};
function renderRadius(filter){
  const host=$('#radiusHost'); host.innerHTML='';
  const q=(filter||'').toLowerCase();
  // 过滤
  const all=TOKENS.radius.filter(r=>{
    if(!q) return true;
    const hay=(r.value+'px '+(RADIUS_DESC[r.value]||r.usage||'')).toLowerCase();
    return hay.includes(q);
  });
  if(!all.length){host.appendChild(el('div','empty','没有匹配的圆角'));return;}
  // 按组聚合
  RADIUS_GROUP.forEach(g=>{
    const items=all.filter(r=>g.range(r.value));
    if(!items.length) return;
    const wrap=el('div','shadow-group');
    wrap.innerHTML='<div class="shadow-group-head"><span class="en">'+g.label+'</span><span class="zh">'+g.zh+'</span><span class="cnt">'+items.length+'</span></div>';
    const row=el('div','shadow-row');
    row.innerHTML='<div class="row-label"><span class="zh">'+g.zh+'</span><span class="en">'+g.label+'</span></div>';
    const cards=el('div','shadow-cards');
    // 按值排序
    items.sort((a,b)=>a.value-b.value);
    items.forEach(r=>{
      const card=el('div','scard');
      card.innerHTML='<div class="stage"><div class="rtile" style="border-radius:'+r.value+'px;width:'+Math.min(96,40+r.value*2)+'px;height:'+Math.min(96,40+r.value*2)+'px"></div></div>'
        +'<div class="body"><div class="sname">'+r.value+' px</div><div class="scss">'+(RADIUS_DESC[r.value]||r.usage||'通用')+'</div></div>';
      card.title='border-radius: '+r.value+'px';
      card.onclick=(e)=>{e.stopPropagation();copy('border-radius: '+r.value+'px;',r.value+'px 已复制',card);};
      cards.appendChild(card);
    });
    row.appendChild(cards);
    wrap.appendChild(row);
    host.appendChild(wrap);
  });
}

/* ---------- render typography ---------- */
function renderTypography(){
  const TY=TOKENS.typography; if(!TY) return;
  // 字体族
  const famHost=$('#tyFamilyHost'); famHost.innerHTML='';
  TY.families.forEach(f=>{
    const card=el('div','ty-family');
    card.innerHTML='<div class="name">'+f.name+'</div>'
      +'<div class="sub">'+f.sub+'</div>'
      +'<div class="glyph" style="font-family:'+f.stack.replace(/"/g,'&quot;')+';font-size:'+f.glyph_size+'px;letter-spacing:0">'+f.sample+'</div>'
      +'<div class="meta"><span>'+f.sub+'</span><span>'+f.tag+'</span></div>';
    card.onclick=(e)=>{e.stopPropagation();copy('font-family: '+f.stack+';',f.name+'（'+f.tag+'）已复制',card);};
    famHost.appendChild(card);
  });
  // font-family 代码块 → 点击复制整条 CSS
  const codeEl=document.querySelector('.ty-family-code');
  if(codeEl && TY.font_family_css){
    codeEl.onclick=(e)=>{e.stopPropagation();copy(TY.font_family_css,'font-family 已复制',codeEl);};
  }

  // 字号表（Element 风格：4 列 + 表头）
  const sizeHost=$('#tySizeHost'); sizeHost.innerHTML='';
  sizeHost.appendChild(el('div','ty-size-head',
    '<div>层级</div><div>字号 / 行高</div><div class="col3">举例</div><div class="col4">辅助文字</div>'));
  TY.sizes.forEach(s=>{
    const row=el('div','ty-size-row');
    // 样例不显式指定字体栈——继承 body 的全站路由栈（数字/标点→Noto、英文→Roboto、中文→雅黑）
    row.innerHTML='<div class="key">'+s.key+'</div>'
      +'<div class="px">'+s.size+'px / '+s.line_height+'px</div>'
      +'<div class="sample col3" style="font-weight:'+s.weight+';font-size:'+s.size+'px;line-height:'+s.line_height+'px">'+s.sample_zh+'</div>'
      +'<div class="desc col4">'+s.usage+'</div>';
    row.onclick=(e)=>{e.stopPropagation();copy('font-size:'+s.size+'px;line-height:'+s.line_height+'px;letter-spacing:'+s.letter_spacing+'em;',s.key+' 已复制',row);};
    sizeHost.appendChild(row);
  });

  // 行高（Element 风格：4 列 + 表头）

  // 字重（Element 风格：表头 + 行）
  const wHost=$('#tyWeightHost'); wHost.innerHTML='';
  wHost.appendChild(el('div','ty-w-head','<div>字重</div><div>样例</div><div>数值</div>'));
  [...TY.weights_cn, ...TY.weights_en].forEach(it=>{
    const isEn=it.label.startsWith('Roboto');
    const row=el('div','ty-weight-row'+(isEn?' en':' cn'));
    // 中文行继承路由栈（雅黑）；英文行显式 Roboto——演示目的
    row.innerHTML='<div class="name">'+(isEn?'Roboto-'+it.weight:'Microsoft YaHei-'+it.weight)+'</div>'
      +'<div class="sample" style="font-weight:'+it.val+(isEn?';font-family:Roboto,"Microsoft YaHei",sans-serif':'')+'">'+it.text+'</div>'
      +'<div class="num">'+it.val+'</div>';
    row.onclick=(e)=>{e.stopPropagation();copy('font-weight:'+it.val+';',it.weight+' 已复制',row);};
    wHost.appendChild(row);
  });

  // 等宽
  const monoHost=$('#tyMonoHost'); monoHost.innerHTML='';
  monoHost.appendChild(el('div','ty-w-head','<div>字重</div><div>样例</div><div>数值</div>'));
  TY.mono.forEach(it=>{
    const row=el('div','ty-weight-row mono');
    row.innerHTML='<div class="name">Roboto Mono-'+it.weight+'</div>'
      +'<div class="sample" style="font-weight:'+it.val+'">'+it.text+'</div>'
      +'<div class="num">'+it.val+'</div>';
    row.onclick=(e)=>{e.stopPropagation();copy('font-weight:'+it.val+';font-family:"Roboto Mono",monospace;',it.weight+' Mono 已复制',row);};
    monoHost.appendChild(row);
  });

  // 文本色阶（Element 风格：表头 + 行）
  const textHost=$('#tyTextHost'); textHost.innerHTML='';
  textHost.appendChild(el('div','ty-text-head',
    '<div></div><div>色阶</div><div>HEX</div><div class="col4">样例</div><div class="col5">用途</div>'));
  TY.text_tones.forEach(t=>{
    // 反白文字行（浅色文字）：整行用纯黑背景色 token（color-bg Lv8 #0B0B0F），默认与 hover 均保持黑底
    const lum=parseInt(t.hex.slice(1,3),16)*0.299+parseInt(t.hex.slice(3,5),16)*0.587+parseInt(t.hex.slice(5,7),16)*0.114;
    const dark=(lum>180);
    const row=el('div','ty-text-tone'+(dark?' dark-row':''));
    row.innerHTML='<div class="sw" style="background:'+t.hex+'"></div>'
      +'<div class="key">'+t.key+'</div>'
      +'<div class="hex">'+t.hex+'</div>'
      +'<div class="sample col4" style="color:'+t.hex+'">'+t.sample+'</div>'
      +'<div class="use col5">'+t.use+'</div>';
    row.onclick=(e)=>{e.stopPropagation();copy('color:'+t.hex+';',t.key+' '+t.hex+' 已复制',row);};
    textHost.appendChild(row);
  });
}

/* ---------- render spacing ---------- */
function renderSpacing(){
  const SP=TOKENS.spacing; if(!SP) return;
  const host=$('#spacingHost'); host.innerHTML='';
  host.appendChild(el('div','spacing-head',
    '<div>Token</div><div>px</div><div>rem</div><div class="col-bar">示意</div><div>用途</div>'));
  const max=Math.max.apply(null,SP.map(s=>s.px));
  SP.forEach(s=>{
    const row=el('div','spacing-row');
    const widthPct=Math.round(s.px/max*100);
    row.innerHTML='<div class="key">'+s.key+'</div>'
      +'<div class="px">'+s.px+'x'+s.px+'px</div>'
      +'<div class="rem">'+s.rem+'rem</div>'
      +'<div class="col-bar bar"><i style="width:'+s.px+'px;height:'+s.px+'px"></i></div>'
      +'<div class="use">'+s.usage+'</div>';
    row.onclick=(e)=>{e.stopPropagation();copy('padding:'+s.px+'px;',s.key+' / '+s.px+'px 已复制',row);};
    host.appendChild(row);
  });
}

/* ---------- wire up ---------- */
function renderAll(q){renderColors(q);renderBorders(q);renderShadows(q);renderRadius(q);renderTypography();renderSpacing();}
renderAll('');

/* ---------- 「创建文件夹」按钮：点击切换两态（默认 ⇄ 紫色激活 5s） ---------- */
const fbtn=document.querySelector('.aml-folder-btn');
if(fbtn){
  let holdTimer=null;
  const press=()=>{ fbtn.classList.add('pressed'); clearTimeout(holdTimer); holdTimer=setTimeout(()=>fbtn.classList.remove('pressed'),5000); };
  const release=()=>{ fbtn.classList.remove('pressed'); clearTimeout(holdTimer); holdTimer=null; };
  fbtn.addEventListener('pointerdown',e=>{e.preventDefault(); fbtn.classList.contains('pressed') ? release() : press();});
  fbtn.addEventListener('keydown',e=>{ if(e.key===' '||e.key==='Enter'){e.preventDefault(); fbtn.classList.contains('pressed') ? release() : press();}});
}

/* ---------- 侧栏开合（移动端） ---------- */
const sidebar=$('#sidebar'), scrim=$('#scrim');
function closeSidebar(){sidebar.classList.remove('open');scrim.classList.remove('show');}
$('#menuBtn').addEventListener('click',()=>{sidebar.classList.toggle('open');scrim.classList.toggle('show');});
scrim.addEventListener('click',closeSidebar);

/* ---------- scroll-spy 侧栏导航 ---------- */
/* ---------- 侧栏导航：点击切换单页（无滚动同步） ---------- */
const navItems=[...document.querySelectorAll('.aml-sidenav-item')];
const pages=[...document.querySelectorAll('main .section[data-page]')];
function showPage(name){
  pages.forEach(p=>p.classList.toggle('is-active', p.getAttribute('data-page')===name));
  navItems.forEach(a=>{
    a.classList.toggle('active', a.getAttribute('data-page')===name);
  });
  try{history.replaceState(null,'','#'+name);}catch(_){}
  // 切页后回到内容区顶部
  document.querySelector('main')?.scrollTo?.(0,0);
  window.scrollTo(0,0);
  // 移动端关掉侧栏
  const sidebar=$('#sidebar'), scrim=$('#scrim');
  if(sidebar?.classList.contains('open')){sidebar.classList.remove('open');scrim.classList.remove('show');}
}
navItems.forEach(a=>a.addEventListener('click',e=>{
  e.preventDefault();
  showPage(a.getAttribute('data-page'));
}));
// 分组折叠
document.querySelectorAll('.aml-sidenav-title').forEach(t=>{
  t.addEventListener('click',()=>t.parentElement.classList.toggle('collapsed'));
});
// 支持从 URL hash 还原 + 默认 Color
function initPage(){
  let target=location.hash.replace('#','');
  if(!pages.find(p=>p.getAttribute('data-page')===target)) target='colors';
  showPage(target);
}
initPage();
window.addEventListener('hashchange',initPage);
</script>
</body>
</html>
"""

out_path = os.path.join(HERE, "index.html")
html = (HTML.replace("__TOKENS__", JSON_STR)
            .replace("__PILL_SVG__", PILL_SVG)
            .replace("__FOLDER_DEFAULT__", FOLDER_DEFAULT_SVG)
            .replace("__FOLDER_ACTIVE__", FOLDER_ACTIVE_SVG))
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", out_path)
print("colors:", len(TOKENS["colors"]), "shadows:", len(TOKENS["shadows"]), "radius:", len(TOKENS["radius"]))
