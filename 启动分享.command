#!/bin/bash
cd "$(dirname "$0")"
PY=/Users/happy/.workbuddy/binaries/python/versions/3.13.12/bin/python3
REPO=/Users/happy/Desktop/aml-token-inspector

cd "$REPO" || exit 1

echo "正在启动分享服务，请稍等几秒 ..."
"$PY" keep_alive.py --once

# 后台常驻守护：服务或链接断了会自动重连，并更新桌面上的地址
pgrep -f "keep_alive.py" >/dev/null 2>&1 || \
  nohup "$PY" keep_alive.py > /tmp/aml_keepalive.out 2>&1 &

sleep 2
URL=$(grep -o "https://[^ ]*" "$HOME/Desktop/发给同事.txt" | head -1)

echo ""
echo "=========================================="
echo ""
echo "  发给同事的链接："
echo ""
echo "     $URL"
echo ""
echo "=========================================="
echo ""
echo "桌面上的「发给同事.txt」已经写好，双击就能整段复制。"
echo "这个窗口可以关掉，服务会在后台一直跑。"
echo ""
read -n 1 -s -r -p "按任意键关闭 ..."
