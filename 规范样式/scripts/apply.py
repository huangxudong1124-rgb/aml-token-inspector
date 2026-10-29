#!/usr/bin/env python3
"""
apply.py — 把任意 HTML 页面刷成「规范样式」token（主色紫 #7B32DE / 中性纯灰 / 功能色 / 阴影 / 圆角）。

用法:
  python3 apply.py <html文件>              # 自动备份后改写
  python3 apply.py <html文件> --no-backup  # 不备份
  python3 apply.py path/to/index.html

它做两件事:
  1) 颜色重映射:常见蓝/青/靛 → 品牌紫,slate 灰 → 纯中性灰,功能红/绿/橙 → 规范功能色
     (含 hex 与 rgba 元组;不够可在下方 HEX_MAP / TUPLE_MAP 自行补充)
  2) 注入规范 :root token(--primary / --text-* / --border / --shadow-* / --radius 等)
"""
import argparse
import datetime
import os
import re
import shutil

# 默认 hex 映射 (大小写不敏感)
HEX_MAP = {
    # 主色:蓝/青/靛 → 品牌紫
    "#00d4ff": "#7B32DE", "#00a8cc": "#6512AD", "#00b4d8": "#7B32DE",
    "#1890ff": "#7B32DE", "#096dd9": "#6512AD", "#1677ff": "#7B32DE",
    "#2f54eb": "#7B32DE", "#1664ff": "#7B32DE", "#5252ff": "#7B32DE",
    "#4096ff": "#8E55F2", "#7c3aed": "#7B32DE", "#6200ee": "#7B32DE",
    # 中性:slate/灰 → 纯灰
    "#0f172a": "#0B0B0F", "#1e293b": "#0B0B0F", "#334155": "#3C3E43",
    "#475569": "#3C3E43", "#64748b": "#61646C", "#94a3b8": "#85888E",
    "#cbd5e1": "#B1B3BB", "#e2e8f0": "#E2E2E3", "#f1f5f9": "#ECECED",
    "#f5f7fa": "#F5F5F6", "#f8fafc": "#FAFAFA",
    # 功能色
    "#ef4444": "#E31B54", "#f5222d": "#E31B54", "#f5222e": "#E31B54",
    "#10b981": "#007878", "#52c41a": "#007878", "#16a34a": "#007878",
    "#f59e0b": "#F27000", "#fa8c16": "#F27000", "#faad14": "#F27000",
}

# rgb 元组映射 (用于 rgba(r,g,b,a))
TUPLE_MAP = {
    (0, 212, 255): (123, 50, 222), (0, 168, 204): (101, 18, 173),
    (24, 144, 255): (123, 50, 222), (47, 84, 235): (123, 50, 222),
    (22, 100, 255): (123, 50, 222), (82, 82, 255): (123, 50, 222),
    (124, 58, 237): (123, 50, 222),
    (15, 23, 42): (11, 11, 15), (30, 41, 59): (11, 11, 15),
    (51, 65, 85): (60, 62, 67), (71, 85, 105): (60, 62, 67),
    (100, 116, 139): (97, 100, 108), (148, 163, 184): (133, 136, 142),
    (203, 213, 225): (177, 179, 187), (226, 232, 240): (226, 226, 227),
    (241, 245, 249): (236, 236, 237),
    (239, 68, 68): (227, 27, 84), (16, 185, 129): (0, 120, 120),
    (245, 158, 11): (242, 112, 0),
}

SPEC_ROOT = """:root{
  /* 规范样式 token — 主色紫 / 中性灰 / 功能色 / 阴影 / 圆角 */
  --primary:#7B32DE; --primary-hover:#6512AD; --primary-soft:#F4F0FF;
  --ink:#0B0B0F; --text-2:#3C3E43; --text-3:#61646C; --text-4:#85888E;
  --border:#E2E2E3; --border-soft:#ECECED;
  --bg:#F5F5F6; --surface:#FFFFFF; --surface-2:#FAFAFA;
  --success:#007878; --warning:#F27000; --danger:#E31B54; --link:#7B32DE;
  --shadow-card:0 2px 6px 0 rgba(0,0,0,0.05);
  --shadow-float:0 5px 15px 0 rgba(0,0,0,0.05),0 15px 35px -2px rgba(0,0,0,0.05);
  --radius:12px; --radius-sm:8px; --radius-lg:20px;
}"""


def apply_to_html(html_path, backup=True):
    s = open(html_path, encoding="utf-8", errors="ignore").read()

    if backup:
        bk = html_path + ".bak" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(html_path, bk)
        print("backup ->", bk)

    # 1) hex 重映射
    n_hex = 0
    for old, new in HEX_MAP.items():
        s, n = re.subn(re.escape(old), new, s, flags=re.IGNORECASE)
        n_hex += n

    # 2) rgb 元组重映射
    for old, new in TUPLE_MAP.items():
        pat = r"(\b" + r"\s*,\s*".join(str(x) for x in old) + r"\b)"
        repl = ", ".join(str(x) for x in new)
        s = re.sub(pat, repl, s)

    # 3) 注入规范 :root (若尚未注入)
    injected = False
    if "--primary:#7B32DE" not in s:
        m = re.search(r"<style[^>]*>", s)
        if m:
            s = s[:m.end()] + SPEC_ROOT + s[m.end():]
        else:
            s = s.replace("</head>", "<style>" + SPEC_ROOT + "</style>\n</head>", 1)
        injected = True

    open(html_path, "w", encoding="utf-8").write(s)
    print(f"applied 规范样式 to {html_path}  (hex 替换 {n_hex} 处, token 注入 {'是' if injected else '否'})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="把 HTML 刷成「规范样式」token")
    ap.add_argument("html", help="要改写的 HTML 文件路径")
    ap.add_argument("--no-backup", action="store_true", help="不生成 .bak 备份")
    args = ap.parse_args()
    if not os.path.exists(args.html):
        raise SystemExit(f"文件不存在: {args.html}")
    apply_to_html(args.html, backup=not args.no_backup)
