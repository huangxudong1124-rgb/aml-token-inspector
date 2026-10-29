#!/usr/bin/env bash
#
# 生成可分享的静态站点目录 dist/
#   dist/index.html    安装页（自动按访问地址生成安装命令）
#   dist/install.sh    一键安装脚本
#   dist/skills.zip    两个 skill 的打包（UTF-8 文件名，跨平台不乱码）
#   dist/preview.html  自检页在线预览
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST="$ROOT/dist"
PY="$(command -v python3 || echo /usr/bin/python3)"

rm -rf "$DIST"
mkdir -p "$DIST"

# 1) 打包 skill（用 python 写 zip，保证中文目录名带 UTF-8 标记）
"$PY" - "$ROOT" "$DIST/skills.zip" <<'PY'
import os, sys, zipfile
root, out = sys.argv[1], sys.argv[2]
names = [n for n in ('aml-token-inspector', '规范样式') if os.path.isdir(os.path.join(root, n))]
n = 0
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for name in names:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, name)):
            dirnames[:] = [d for d in dirnames if d != '__pycache__']
            for f in filenames:
                if f == '.DS_Store':
                    continue
                full = os.path.join(dirpath, f)
                z.write(full, os.path.relpath(full, root))
                n += 1
print('  ✓ skills.zip（%d 个文件，含：%s）' % (n, '、'.join(names)))
PY

# 2) 拷贝静态文件
cp "$ROOT/install.sh" "$DIST/install.sh"
chmod +x "$DIST/install.sh"
cp "$ROOT/site/index.html" "$DIST/index.html"
cp "$ROOT/aml-token-inspector/index.html" "$DIST/preview.html"

echo "  ✓ dist/ 已生成"
echo ""
echo "下一步：分享给同事"
echo "  ./share.sh              # 局域网临时共享，输出可直接转发的安装命令"
echo "  open dist/index.html    # 本地预览安装页"
