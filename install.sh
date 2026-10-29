#!/usr/bin/env bash
#
# AML Design Token Inspector — 一键安装脚本
#
# 用法 A（推荐，一条命令装好）：
#   curl -fsSL https://raw.githubusercontent.com/__OWNER__/aml-token-inspector/main/install.sh | bash
#
# 用法 B（已克隆仓库后本地执行）：
#   git clone https://github.com/__OWNER__/aml-token-inspector.git
#   cd aml-token-inspector && ./install.sh
#
# 可选环境变量：
#   REPO_URL  覆盖仓库地址（内网镜像 / fork）
#   BRANCH    覆盖分支名（默认 main）
#
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/__OWNER__/aml-token-inspector.git}"
BRANCH="${BRANCH:-main}"

# 1) 判断装到哪个客户端的 skills 目录
case "${__CFBundleIdentifier:-}" in
  *codebuddy*) SKILLS_DIR="$HOME/.codebuddy/skills" ;;
  *)           SKILLS_DIR="$HOME/.workbuddy/skills" ;;
esac

# 2) 定位仓库根目录（curl 管道执行时本地没有仓库 → 自动克隆）
SRC=""
if [ -n "${BASH_SOURCE[0]:-}" ]; then
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
if [ -z "$SRC" ] || [ ! -f "$SRC/install.sh" ]; then
  echo "→ 未检测到本地仓库，正在克隆 $REPO_URL ..."
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  git clone --depth 1 -b "$BRANCH" "$REPO_URL" "$TMP/repo" >/dev/null
  SRC="$TMP/repo"
fi

# 3) 逐个安装：凡是含 SKILL.md 的一级目录都当作一个 skill
mkdir -p "$SKILLS_DIR"
installed=0
for d in "$SRC"/*/; do
  name="$(basename "$d")"
  [ -f "$d/SKILL.md" ] || continue
  if [ -d "$SKILLS_DIR/$name" ]; then
    rm -rf "$SKILLS_DIR/$name"
    echo "  ↻ 已更新 skill: $name"
  else
    echo "  ✓ 已安装 skill: $name"
  fi
  cp -R "$d" "$SKILLS_DIR/$name"
  installed=$((installed + 1))
done

if [ "$installed" -eq 0 ]; then
  echo "✗ 仓库里没找到任何含 SKILL.md 的 skill 目录" >&2
  exit 1
fi

echo ""
echo "完成：$installed 个 skill 已装到 $SKILLS_DIR"
echo ""
echo "查看自检页："
echo "  open \"$SKILLS_DIR/aml-token-inspector/index.html\""
echo ""
echo "提示：WorkBuddy / CodeBuddy 需要重启会话（或刷新技能列表）后才会加载新 skill。"
