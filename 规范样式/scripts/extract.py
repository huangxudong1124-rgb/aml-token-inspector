#!/usr/bin/env python3
"""
extract.py — Extract design tokens (color / shadow / radius) from a Figma file.

Figma token resolution (first hit wins):
  --token <tok>                       CLI flag
  $FIGMA_TOKEN / $FIGMA_API_KEY       environment variable
  $FIGMA_CONFIG                       path to a config json with the key
  ~/.mcp-figma/config.json            the mcp-figma MCP server config (`apiKey`)

Usage:
  python3 extract.py <fileKey|figma-url|fileKey/nodeId>
  python3 extract.py m4zkJ7ZJYAZqfCrdziD77N --format css        # css|json|md
  python3 extract.py m4zkJ7ZJYAZqfCrdziD77N --radius-node 106873:224543
  FIGMA_TOKEN=figd_xxx python3 extract.py "<figma-url>"

The optional nodeId points at a "Color" canvas; the script also auto-detects the
Shadow (投影) and Radius (圆角) canvases by name. nodeIds use the API form with a
colon (106873:224079) — a URL node-id like 106873-224079 is accepted too.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://api.figma.com/v1"
CONFIG_PATHS = ["~/.mcp-figma/config.json"]

# Brand primary — Pixso「数据知识管理系统」Brand Purple.
# Applied to the 主色/Primary family by default so the skill's primary is purple
# (never the source file's blue). Disable with --no-brand-primary for raw extraction.
BRAND_PRIMARY = {
    "family": "主色  Primary",
    "row": "Row / 主色 · Brand Purple（Pixso）",
    "scale": {  # 50/100/300/400/500/600/700/800 → levels 1..8
        "1": "#F4F0FF", "2": "#E9E0FC", "3": "#CEAEFF", "4": "#A179F2",
        "5": "#8E55F2", "6": "#7B32DE", "7": "#6512AD", "8": "#511086",
    },
    "regular": "#7B32DE",
}

def apply_brand_primary(colors):
    """Replace any 主色 family with the Brand Purple scale (no blue in primary)."""
    return [BRAND_PRIMARY] + [c for c in colors if not c["family"].startswith("主色")]

# Neutral tokens — from「中性色 Neutral」spec screenshot (pure neutral grey ramp,
# no blue tint). Arco-style semantic naming matches the React lib
# (--color-text-1, --color-bg-1, ...). Replaces the extracted 中性色 family entirely.
NEUTRAL_TOKENS = [
    {"family": "中性色 · color", "row": "Row / color-text · 文字",
     "scale": {"1": "#0B0B0F", "2": "#3C3E43", "3": "#61646C", "4": "#85888E", "5": "#FFFFFF"},
     "regular": "#0B0B0F",
     "roles": {"1": "强调正文标题", "2": "次强调正文标题", "3": "次要信息", "4": "置灰信息", "5": "纯白文字"}},
    {"family": "中性色 · color", "row": "Row / icon-color-fill · 图标填充",
     "scale": {"1": "#FFFFFF", "2": "#B1B3BB", "3": "#85888E", "4": "#61646C",
               "5": "#6200EE", "6": "#0B0B0F"},
     "regular": "#61646C",
     "roles": {"1": "纯白填充", "2": "提示类填充", "3": "禁用图标填充", "4": "默认状态", "5": "悬浮纯白图标填充", "6": "纯黑填充"}},
    {"family": "中性色 · color", "row": "Row / color-fill · 填充",
     "scale": {"1": "#FFFFFF", "2": "#FAFAFA", "3": "#F5F5F6", "4": "#F4F0FF",
               "5": "#2C2E33", "6": "#0B0B0F"},
     "regular": "#FFFFFF",
     "roles": {"1": "纯白填充", "2": "框类内部背景填充", "3": "icon 白底悬浮背景色", "4": "icon 灰底悬浮背景色", "5": "tooltip 背景", "6": "纯黑填充"}},
    {"family": "中性色 · color", "row": "Row / color-bg · 背景",
     "scale": {"1": "#FFFFFF", "2": "#FAFAFA", "3": "#F5F5F6", "4": "#FAF9FC",
               "5": "#FBFBFC", "6": "#ECECED", "7": "#2C2E33", "8": "#0B0B0F"},
     "regular": "#FFFFFF",
     "roles": {"1": "白色背景色", "2": "浅灰色背景", "3": "浅灰色背景2", "4": "嵌套场景1", "5": "浅灰色背景 hover", "6": "黑色背景色"}},
    {"family": "中性色 · color", "row": "Row / color-border · 描边",
     "scale": {"1": "#ECECED", "2": "#ECECED", "3": "#E2E2E3"},
     "regular": "#E2E2E3",
     "roles": {"1": "页面分割描边 (gray-200)", "2": "表格描边 (gray-200)", "3": "控件描边 (gray-300)"}},
    {"family": "中性色 · color", "row": "Row / color-nav · 导航",
     "scale": {"1": "#FFFFFF", "2": "#F5F5F6", "3": "#F4F0FF"},
     "regular": "#FFFFFF",
     "roles": {"1": "导航背景色", "2": "导航悬停色", "3": "导航选中色"}},
]

def apply_neutral_tokens(colors):
    """Replace extracted neutrals with Pixso Gray + React/Arco semantic naming."""
    kept = [c for c in colors if not c["family"].startswith("中性色")]
    return NEUTRAL_TOKENS + kept

# Functional tokens — from react lib variables.css (authoritative). Three groups:
# success(green) / danger(red) / oranged(yellow), mapped to the design-system scales.
# 8 levels = Arco roles: 1 浅色场景 · 2 Tag 背景 · 3 一般禁用 · 4 特殊场景
#                       · 5 悬浮 · 6 常规 · 7 点击 · 8 描边. Naming --color-<role>-N.
FUNC_TOKENS = [
    {"family": "功能色 · color", "row": "Row / success · 成功",
     "scale": {"1": "#F3FAFA", "2": "#E8F7F7", "3": "#91DEDE", "4": "#4EC7C7",
               "5": "#0D9292", "6": "#007878", "7": "#006161", "8": "#004444"},
     "regular": "#007878"},
    {"family": "功能色 · color", "row": "Row / danger · 危险",
     "scale": {"1": "#FFF5F6", "2": "#FCEBED", "3": "#F7A2B2", "4": "#F27993",
               "5": "#EF4A71", "6": "#E31B54", "7": "#C01048", "8": "#A11043"},
     "regular": "#E31B54"},
    {"family": "功能色 · color", "row": "Row / warning · 警告",
     "scale": {"1": "#FFF7E8", "2": "#FFEEDB", "3": "#FFCC8C", "4": "#FFBB66",
               "5": "#FF860F", "6": "#F27000", "7": "#D35B00", "8": "#913F00"},
     "regular": "#F27000"},
    {"family": "功能色 · color", "row": "Row / link · 链接",
     "scale": {"1": "#F4F0FF", "2": "#E9E0FC", "3": "#CEAEFF", "4": "#A179F2",
               "5": "#8E55F2", "6": "#6512AD", "7": "#7B32DE", "8": "#511086"},
     "regular": "#6512AD"},
    {"family": "功能色 · color", "row": "Row / grey · 灰",
     "scale": {"1": "#FAFAFA", "2": "#F0F1F1", "3": "#E2E2E3", "4": "#B1B3BB",
               "5": "#85888E", "6": "#61646C", "7": "#3C3E43", "8": "#0B0B0F"},
     "regular": "#61646C"},
    {"family": "功能色 · color", "row": "Row / purple-gray · 紫灰",
     "scale": {"1": "#FAF9FC", "2": "#F7F5FB", "3": "#C9C2D7", "4": "#A298BC",
               "5": "#665C7A", "6": "#0B0B0F", "7": "#332847", "8": "#4A405B"},
     "regular": "#0B0B0F"},
]

# Categorical / Safety — derived from Pixso「设计体系-基础组件库」hue scales
# (red/yellow/green/blue/purple, 25–950). Loaded from pixso_colors.json next to
# this script so the values stay machine-generated from the Pixso source.
def apply_pixso_colors(colors):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pixso_colors.json")
    data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    drop = ("功能色", "分类色", "安全色")
    kept = [c for c in colors if not any(c["family"].startswith(k) for k in drop)]
    return data.get("categorical", []) + FUNC_TOKENS + data.get("safety", []) + kept



# ───────────────────────── Figma API helpers ─────────────────────────

def load_token(cli_token=None):
    tok = cli_token or os.environ.get("FIGMA_TOKEN") or os.environ.get("FIGMA_API_KEY")
    if tok:
        return tok
    paths = [os.environ.get("FIGMA_CONFIG")] + [os.path.expanduser(p) for p in CONFIG_PATHS]
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        try:
            with open(p) as f:
                cfg = json.load(f)
        except (OSError, ValueError):
            continue
        tok = cfg.get("apiKey") or cfg.get("figma_api_key") or cfg.get("api_key")
        if tok:
            return tok
    sys.exit(
        "No Figma API token found. Provide one via:\n"
        "  - --token <figd_...>\n"
        "  - $FIGMA_TOKEN or $FIGMA_API_KEY\n"
        "  - ~/.mcp-figma/config.json  ({\"apiKey\": \"figd_...\"})"
    )

def figma_get(path, token, qs=None):
    url = API + path
    if qs:
        url += "?" + urllib.parse.urlencode(qs)
    req = urllib.request.Request(url, headers={"X-Figma-Token": token})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit(f"Figma API error {e.code} for {url}:\n{body[:400]}")

def get_nodes(file_key, token, node_ids, depth=1):
    ids = [n.replace("-", ":") for n in node_ids]
    data = figma_get(f"/files/{file_key}/nodes", token,
                     {"ids": ",".join(ids), "depth": depth})
    return data.get("nodes", {})

def get_styles(file_key, token):
    return figma_get(f"/files/{file_key}/styles", token).get("meta", {}).get("styles", [])

def get_file(file_key, token, depth=1):
    return figma_get(f"/files/{file_key}", token, {"depth": depth})

# ───────────────────────── color helpers ─────────────────────────

def hex_of(c):
    r, g, b = round(c["r"] * 255), round(c["g"] * 255), round(c["b"] * 255)
    return f"#{r:02X}{g:02X}{b:02X}"

def rgba_of(c):
    r, g, b = round(c["r"] * 255), round(c["g"] * 255), round(c["b"] * 255)
    a = round(c.get("a", 1), 3)
    a = int(a) if a == int(a) else a  # 1.0 → 1, 0.0 → 0
    return f"rgba({r},{g},{b},{a})" if a != 1 else f"#{r:02X}{g:02X}{b:02X}"

def _num(v):
    """Render a length number without trailing .0 (0.0 → 0, 1.5 → 1.5)."""
    return str(int(v)) if float(v) == int(v) else str(v)

def first_solid(node):
    for key in ("fills", "background"):
        for fl in (node.get(key) or []):
            if fl.get("type") == "SOLID" and fl.get("visible", True) is not False:
                return hex_of(fl["color"])
    return None

# ───────────────────────── extraction ─────────────────────────

def extract_shadows(file_key, token):
    """FILL→skip, EFFECT→box-shadow. Each effect style node is fetched to read values."""
    styles = get_styles(file_key, token)
    eff = [s for s in styles if s["style_type"] == "EFFECT"]
    name_by = {s["node_id"]: s["name"] for s in eff}
    nodes = get_nodes(file_key, token, list(name_by.keys()), depth=1)
    out = []
    for nid, name in name_by.items():
        nd = nodes.get(nid) or {}
        doc = nd.get("document", {}) if isinstance(nd, dict) else {}
        shadows = []
        for e in doc.get("effects", []):
            t = e.get("type")
            if t in ("DROP_SHADOW", "INNER_SHADOW"):
                inset = "inset " if t == "INNER_SHADOW" else ""
                off = e.get("offset", {})
                col = rgba_of(e.get("color", {}))
                shadows.append(
                    f"{inset}{_num(off.get('x', 0))}px {_num(off.get('y', 0))}px "
                    f"{_num(e.get('radius', 0))}px {_num(e.get('spread', 0))}px {col}"
                )
            elif t == "LAYER_BLUR":
                shadows.append(f"blur({e.get('radius',0)}px)")
        if shadows:
            out.append({"name": name, "css": ", ".join(shadows)})
    return out

def _collect_swatch_row(row):
    """Return sorted list of (x, hex) swatches plus (x,y,text) labels under a Row frame."""
    sws, txs = [], []

    def walk(n):
        t = n.get("type")
        bb = n.get("absoluteBoundingBox") or {}
        if t == "RECTANGLE":
            for fl in (n.get("fills") or []):
                if fl.get("type") == "SOLID" and fl.get("visible", True) is not False:
                    if bb.get("width", 0) > 4 and bb.get("height", 0) > 4:
                        sws.append((bb.get("x", 0), bb.get("y", 0), hex_of(fl["color"])))
                    break
        elif t == "TEXT" and n.get("characters"):
            txs.append((bb.get("x", 0), bb.get("y", 0), bb.get("width", 0), n["characters"].strip()))
        for c in n.get("children", []) or []:
            walk(c)

    walk(row)
    return sws, txs

ROLE_BY_LEVEL = {
    1: "浅色场景/白底悬浮", 2: "Tag 背景色", 3: "一般禁用", 4: "特殊场景",
    5: "悬浮 Hover", 6: "常规 Default", 7: "点击 Active", 8: "描边 Stroke",
}

def _scale_from_swatches(sws):
    """A row of swatches → level-1..N. Convention: rightmost (largest x) = -1 lightest."""
    sws_sorted = sorted(sws, key=lambda s: s[0])  # left→right by x
    n = len(sws_sorted)
    scale = {}
    for i, (x, y, hx) in enumerate(sws_sorted):
        lvl = n - i  # rightmost → 1
        scale[lvl] = hx
    return scale

def _roles_from_swatches(sws, txs):
    """Pair each swatch with the text label directly beneath it (x overlap). Returns {hex: role}."""
    pair = {}
    for x, y, w, txt in txs:
        if y < 0:  # skip titles that sit above; we want labels below swatches
            pass
        cand = [s for s in sws if abs(s[0] - x) < 30 and s[1] < y]
        cand.sort(key=lambda s: abs(s[0] - x))
        if cand:
            pair[cand[0][2]] = txt
    return pair

def find_canvases(file_key, token):
    """Locate Color / Shadow / Radius canvases by name (Arco/Volcengine convention)."""
    doc = get_file(file_key, token, depth=1).get("document", {})
    found = {}
    patterns = {
        "color": re.compile(r"颜色|/Color", re.I),
        "shadow": re.compile(r"投影|/Shadow", re.I),
        "radius": re.compile(r"圆角|/Radius", re.I),
    }
    for c in doc.get("children", []):
        nm = c.get("name", "")
        for key, pat in patterns.items():
            if key not in found and pat.search(nm):
                found[key] = c["id"]
    return found

def extract_colors(file_key, token, color_node=None):
    """
    Walk a Color canvas: Section → SubSection (color family) → Row → swatches.
    Returns [{"family", "scale": {level: hex}, "regular"=hex(level6 or darkest mid)}].
    """
    if not color_node:
        color_node = find_canvases(file_key, token).get("color")
    if not color_node:
        return []
    color_node = color_node.replace("-", ":")  # API keys nodes by colon form
    canvas = get_nodes(file_key, token, [color_node], depth=2).get(color_node, {}).get("document", {})

    # Collect every frame named "SubSection …" and dive into its "Row …" children.
    subsection_ids = [c["id"] for c in canvas.get("children", [])
                      if c.get("type") == "FRAME" and c.get("name", "").startswith("SubSection")]
    # Also accept Section frames that directly contain SubSections.
    section_ids = [c["id"] for c in canvas.get("children", [])
                   if c.get("type") == "FRAME" and c.get("name", "").startswith("Section")]
    target_ids = subsection_ids
    for sid in section_ids:
        sub = get_nodes(file_key, token, [sid], depth=2).get(sid, {}).get("document", {})
        target_ids += [c["id"] for c in sub.get("children", [])
                       if c.get("name", "").startswith("SubSection")]

    out = []
    seen = set()
    for sid in target_ids:
        sub = get_nodes(file_key, token, [sid], depth=6).get(sid, {}).get("document", {})
        family = re.sub(r"^SubSection\s*/\s*", "", sub.get("name", "")).strip()
        for row in sub.get("children", []):
            if not row.get("name", "").startswith("Row"):
                continue
            sws, _ = _collect_swatch_row(row)
            if not sws:
                continue
            scale = _scale_from_swatches(sws)
            key = (family, row["name"], tuple(sorted(scale.items())))
            if key in seen:
                continue
            seen.add(key)
            regular = scale.get(6) or scale.get(max(scale, key=lambda k: abs(k - 6)))
            out.append({"family": family, "row": row["name"], "scale": scale, "regular": regular})
    return out

def extract_radius(file_key, token, radius_node=None):
    """Read corner radius tokens from the Radius canvas (and any explicit radii on it)."""
    if not radius_node:
        radius_node = find_canvases(file_key, token).get("radius")
    if not radius_node:
        return []
    radius_node = radius_node.replace("-", ":")  # API keys nodes by colon form
    canvas = get_nodes(file_key, token, [radius_node], depth=4).get(radius_node, {}).get("document", {})

    # Collect radius values from two signals: explicit `cornerRadius` on shapes,
    # and standalone "Npx" text labels. Then pair each value with a nearby short
    # usage label (same row, not an Npx token, not a long sentence).
    values = set()
    npx_label = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*px\s*$", re.I)
    labels = []  # (x, y, w, px_int, text)

    def walk(n):
        t = n.get("type")
        bb = n.get("absoluteBoundingBox") or {}
        cr = n.get("cornerRadius")
        if cr is not None and abs(cr - round(cr)) < 0.1:  # skip fractional (scaled) noise like 4.88
            values.add(round(cr))
        if t == "TEXT" and n.get("characters"):
            m = npx_label.match(n["characters"])
            if m:
                px = round(float(m.group(1)))
                values.add(px)
                labels.append((bb.get("x", 0), bb.get("y", 0), bb.get("width", 0), px))
            else:
                txt = n["characters"].strip()
                if 1 < len(txt) <= 30:
                    labels.append((bb.get("x", 0), bb.get("y", 0), bb.get("width", 0), None, txt))
        for c in n.get("children", []) or []:
            walk(c)

    walk(canvas)

    radii = []
    for px in sorted(v for v in values if v >= 2):
        usage = ""
        # find an Npx label for this value, then a usage text beside/below it
        for x, y, w, p in [(l[0], l[1], l[2], l[3]) for l in labels if len(l) == 4 and l[3] == px]:
            for l in labels:
                if len(l) == 5 and abs(l[0] - x) < 80 and abs(l[1] - y) < 60:
                    usage = l[4]
                    break
            if usage:
                break
        radii.append({"value": px, "usage": usage})
    return radii

# ───────────────────────── output formatters ─────────────────────────

def _slug(s):
    s = re.sub(r"^Row\s*/?\s*", "", s)  # drop leading "Row /"
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s  # "" when the name is pure CJK / punctuation

def to_css(colors, shadows, radii):
    # Build a globally-unique CSS variable prefix per row.
    #  - family appearing in a single row  → just the family slug
    #  - otherwise                          → family + row qualifier
    #  - CJK-only row names fall back to r<index>; identical qualifiers get -2/-3
    from collections import Counter
    fam_count = Counter(_slug(c["family"]) for c in colors)
    used = Counter()
    fam_idx = Counter()
    L = [":root {"]
    for c in colors:
        if c.get("css_prefix"):
            prefix = c["css_prefix"]
        else:
            fam = _slug(c["family"]) or "color"
            if fam_count[fam] == 1:
                prefix = fam
            else:
                qual = _slug(c["row"])
                if not qual:
                    fam_idx[fam] += 1
                    qual = f"r{fam_idx[fam]}"
                prefix = f"{fam}-{qual}"
        used[prefix] += 1
        if used[prefix] > 1:
            prefix = f"{prefix}-{used[prefix]}"
        for lvl, hx in sorted(c["scale"].items()):
            L.append(f"  --{prefix}-{lvl}: {hx};")
    L.append("")
    L.append("  /* shadows */")
    seen_shadow = set()
    for s in shadows:
        var = "--shadow-" + _slug(re.sub(r"^[Ss]hadow\s*/?\s*", "", s["name"]))
        if var in seen_shadow:
            continue
        seen_shadow.add(var)
        L.append(f"  {var}: {s['css']};")
    L.append("")
    L.append("  /* radius */")
    for r in radii:
        L.append(f"  --radius-{r['value']}: {r['value']}px;")
    L.append("}")
    return "\n".join(L) + "\n"

def to_json(colors, shadows, radii):
    return json.dumps({"colors": colors, "shadows": shadows, "radius": radii},
                      ensure_ascii=False, indent=2) + "\n"

def to_md(colors, shadows, radii):
    L = ["# Figma Design Tokens\n"]
    L.append("## Color\n")
    for c in colors:
        reg = c["regular"] or "—"
        L.append(f"### {c['family']} — {c['row']}  (regular `{reg}`)")
        for lvl in sorted(c["scale"]):
            L.append(f"- level-{lvl} ({ROLE_BY_LEVEL.get(lvl, '')}): `{c['scale'][lvl]}`")
        L.append("")
    L.append("## Shadow\n")
    for s in shadows:
        L.append(f"- **{s['name']}** — `{s['css']}`")
    L.append("\n## Radius\n")
    for r in radii:
        L.append(f"- `{r['value']}px` — {r['usage'] or '(general)'}")
    return "\n".join(L) + "\n"

# ───────────────────────── main ─────────────────────────

def parse_target(arg):
    """Accept fileKey, URL, or 'fileKey/nodeId'."""
    if arg.startswith("http"):
        u = urllib.parse.urlparse(arg)
        qs = urllib.parse.parse_qs(u.query)
        nid = qs.get("node-id", [None])[0]
        m = re.search(r"/design/([^/]+)/", u.path) or re.search(r"/file/([^/]+)/", u.path)
        fk = m.group(1) if m else None
        return fk, nid
    if "/" in arg and ":" not in arg.split("/", 1)[1]:
        fk, nid = arg.split("/", 1)
        return fk, nid
    return arg, None

def main():
    ap = argparse.ArgumentParser(description="Extract Figma design tokens.")
    ap.add_argument("target", nargs="?", help="Figma fileKey/URL/fileKey+nodeId (省略并用 --builtin 则输出内置规范)")
    ap.add_argument("--builtin", action="store_true",
                    help="输出 skill 内置的规范 token（主色紫/中性/功能/分类/安全/阴影/圆角），无需 Figma")
    ap.add_argument("--format", choices=["css", "json", "md"], default="md")
    ap.add_argument("--radius-node", help="Override Radius canvas nodeId")
    ap.add_argument("--no-color", action="store_true", help="Skip color extraction")
    ap.add_argument("--no-shadow", action="store_true", help="Skip shadow extraction")
    ap.add_argument("--no-radius", action="store_true", help="Skip radius extraction")
    ap.add_argument("--token", help="Figma API token (figd_...); else $FIGMA_TOKEN or config")
    ap.add_argument("--no-brand-primary", action="store_true",
                    help="Keep the raw extracted primary (do NOT force Brand Purple)")
    ap.add_argument("--no-neutral-tokens", action="store_true",
                    help="Keep raw extracted neutrals (do NOT force Pixso Gray + Arco naming)")
    ap.add_argument("--no-pixso-colors", action="store_true",
                    help="Keep raw 功能色/分类色/安全色 (do NOT replace with Pixso hue scales)")
    args = ap.parse_args()

    # --builtin: output the curated tokens shipped with the skill (no Figma needed)
    if args.builtin:
        sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokens.json")
        data = json.load(open(sp, encoding="utf-8"))
        fmt = {"css": to_css, "json": to_json, "md": to_md}[args.format]
        sys.stdout.write(fmt(data["colors"], data["shadows"], data["radius"]))
        return

    if not args.target:
        sys.exit("需要一个 Figma 目标，或用 --builtin 输出内置规范 token。")
    file_key, node_id = parse_target(args.target)
    if not file_key:
        sys.exit("Could not parse a fileKey from the target.")
    token = load_token(args.token)

    shadows = []
    if not args.no_shadow:
        sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "react_shadows.json")
        shadows = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else extract_shadows(file_key, token)
    colors = [] if args.no_color else extract_colors(file_key, token, color_node=node_id)
    if colors and not args.no_brand_primary:
        colors = apply_brand_primary(colors)
    if colors and not args.no_neutral_tokens:
        colors = apply_neutral_tokens(colors)
    if colors and not args.no_pixso_colors:
        colors = apply_pixso_colors(colors)
    radii = [] if args.no_radius else extract_radius(file_key, token, radius_node=args.radius_node)

    fmt = {"css": to_css, "json": to_json, "md": to_md}[args.format]
    sys.stdout.write(fmt(colors, shadows, radii))

if __name__ == "__main__":
    main()
