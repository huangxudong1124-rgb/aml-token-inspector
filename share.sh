#!/usr/bin/env bash
#
# 局域网一键分享：起一个临时静态服务，打印可直接转发的链接与安装命令。
# 同一 WiFi / 内网下的同事打开链接或执行那条命令即可安装。
#
#   ./share.sh            # 默认 8765 端口
#   PORT=9000 ./share.sh  # 换端口
#   ./share.sh --public   # 顺便用 cloudstudio 部署一个公网链接（需客户端支持）
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-8765}"
PY="$(command -v python3 || echo /usr/bin/python3)"

"$ROOT/make_dist.sh"

# 取内网 IP
IP=""
for iface in en0 en1 en2 en3; do
  IP="$(ipconfig getifaddr "$iface" 2>/dev/null || true)"
  [ -n "$IP" ] && break
done
[ -z "$IP" ] && IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' || true)"
[ -z "$IP" ] && IP="127.0.0.1"

URL="http://$IP:$PORT"

cd "$ROOT/dist"
echo ""
echo "──────────────────────────────────────────────"
echo " 服务已启动（Ctrl+C 停止）"
echo ""
echo " 安装页：  $URL"
echo " 自检页：  $URL/preview.html"
echo ""
echo " 发给同事的一条命令安装："
echo "   curl -fsSL $URL/install.sh | bash -s -- $URL"
echo "──────────────────────────────────────────────"
echo ""

trap 'echo ""; echo "已停止共享。"; exit 0' INT TERM
"$PY" -m http.server "$PORT" --bind 0.0.0.0
