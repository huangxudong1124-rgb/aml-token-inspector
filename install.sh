#!/usr/bin/env bash
#
# AML Design Token Inspector — 一键安装脚本
#
# 用法 A（一条命令装好，SITE 换成安装页地址）：
#   curl -fsSL <SITE>/install.sh | bash -s -- <SITE>
#
# 用法 B（已克隆仓库后本地执行）：
#   git clone https://github.com/huangxudong1124-rgb/aml-token-inspector.git
#   cd aml-token-inspector && ./install.sh
#
# 环境变量：
#   SITE        安装页/静态站点地址（用法 A 时作为第一个参数传入即可）
#   REPO_URL    覆盖 Git 仓库地址（内网镜像 / fork）
#
set -euo pipefail

SITE="${1:-${SITE:-}}"
REPO_URL="${REPO_URL:-https://github.com/huangxudong1124-rgb/aml-token-inspector.git}"
ZIP_URL="${ZIP_URL:-https://codeload.github.com/huangxudong1124-rgb/aml-token-inspector/zip/refs/heads/main}"
# 现成的 skill 包（仓库里已提交），走 CDN 下载国内通常 1-3 秒，比拉整个仓库快得多
CDN_URL="${CDN_URL:-https://cdn.jsdelivr.net/gh/huangxudong1124-rgb/aml-token-inspector@main/skills.zip}"
CDN_URL_ALT="${CDN_URL_ALT:-https://fastly.jsdelivr.net/gh/huangxudong1124-rgb/aml-token-inspector@main/skills.zip}"

# 1) 判断装到哪个客户端的 skills 目录
case "${__CFBundleIdentifier:-}" in
  *codebuddy*) SKILLS_DIR="$HOME/.codebuddy/skills" ;;
  *)           SKILLS_DIR="$HOME/.workbuddy/skills" ;;
esac

TMP=""
cleanup() { [ -n "$TMP" ] && [ -d "$TMP" ] && rm -rf "$TMP"; }
trap cleanup EXIT

# 2) 定位 skill 源目录（本地仓库 → 站点 zip → git clone）
SRC=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.sh" ]; then
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ -z "$SRC" ]; then
  TMP="$(mktemp -d)"
  if [ -n "$SITE" ]; then
    echo "→ 正在从 $SITE 下载 skill 包 ..."
    curl -fsSL "$SITE/skills.zip" -o "$TMP/skills.zip"
    unzip -q "$TMP/skills.zip" -d "$TMP/unzipped"
    SRC="$TMP/unzipped"
  else
    got=""
    # 1) 优先走 CDN 上的现成 skill 包（国内最快）
    for CDN in "$CDN_URL" "$CDN_URL_ALT"; do
      rm -rf "$TMP/unzipped"
      curl -fsSL --max-time 30 "$CDN" -o "$TMP/skills.zip" 2>/dev/null || continue
      if command -v python3 >/dev/null 2>&1; then
        python3 -c 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' \
          "$TMP/skills.zip" "$TMP/unzipped" 2>/dev/null && { got=1; break; }
      fi
      unzip -q "$TMP/skills.zip" -d "$TMP/unzipped" 2>/dev/null && { got=1; break; }
    done

    # 2) CDN 拿不到（缓存未刷新 / 网络受限）就拉仓库压缩包（比 git clone 更容易穿透网络限制）
    if [ -z "$got" ]; then
    echo "→ 正在下载仓库压缩包 ..."
    # 第一次：按当前环境（可能走代理）；第二次：强制直连，绕开代理
    for mode in default direct; do
      rm -f "$TMP/repo.zip"
      rm -rf "$TMP/unzipped"
      if [ "$mode" = direct ]; then
        curl -fsSL --noproxy '*' --max-time 90 "$ZIP_URL" -o "$TMP/repo.zip" 2>/dev/null || continue
      else
        curl -fsSL --max-time 20 "$ZIP_URL" -o "$TMP/repo.zip" 2>/dev/null || continue
      fi
      # 用 python3 解压：GitHub 压缩包里的中文目录名，系统自带 unzip 会解成乱码
      if command -v python3 >/dev/null 2>&1; then
        python3 -c 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' \
          "$TMP/repo.zip" "$TMP/unzipped" 2>/dev/null && { got=1; break; }
      fi
      unzip -q "$TMP/repo.zip" -d "$TMP/unzipped" 2>/dev/null && { got=1; break; }
    done
    fi

    if [ -n "$got" ]; then
      SRC="$TMP/unzipped"
    else
      echo "→ 压缩包下载失败，改用 git clone ..."
      git clone --depth 1 "$REPO_URL" "$TMP/repo" >/dev/null 2>&1 \
        || git -c http.proxy= -c https.proxy= clone --depth 1 "$REPO_URL" "$TMP/repo" >/dev/null
      SRC="$TMP/repo"
    fi
  fi
fi

# 3) 找到含 SKILL.md 的目录（兼容多一层嵌套，例如 GitHub archive 的 -main 目录）
pick_dirs() {
  find "$1" -maxdepth 3 -name SKILL.md -type f -exec dirname {} \; 2>/dev/null | sort -u
}

DIRS="$(pick_dirs "$SRC")"
if [ -z "$DIRS" ]; then
  echo "✗ 没找到任何含 SKILL.md 的 skill 目录" >&2
  exit 1
fi

# 4) 逐个安装
mkdir -p "$SKILLS_DIR"
installed=0
while IFS= read -r d; do
  [ -n "$d" ] || continue
  name="$(basename "$d")"
  if [ -d "$SKILLS_DIR/$name" ]; then
    rm -rf "$SKILLS_DIR/$name"
    echo "  ↻ 已更新 skill: $name"
  else
    echo "  ✓ 已安装 skill: $name"
  fi
  cp -R "$d" "$SKILLS_DIR/$name"
  installed=$((installed + 1))
done <<< "$DIRS"

if [ "$installed" -eq 0 ]; then
  echo "✗ 没有安装任何 skill" >&2
  exit 1
fi

echo ""
echo "完成：$installed 个 skill 已装到 $SKILLS_DIR"
echo ""
echo "查看自检页："
echo "  open \"$SKILLS_DIR/aml-token-inspector/index.html\""
echo ""
echo "提示：WorkBuddy / CodeBuddy 需要重启会话（或刷新技能列表）后才会加载新 skill。"
