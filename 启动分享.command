#!/usr/bin/env bash
cd /Users/happy/Desktop/aml-token-inspector || exit 1
PY=/Users/happy/.workbuddy/binaries/python/versions/3.13.12/bin/python3

echo "1/2 启动本地分享服务…"
"$PY" serve_daemon.py
echo ""
echo "2/2 建立公网隧道（需要几秒）…"
echo ""
"$PY" tunnel_daemon.py
echo ""
echo "把上面的链接发给同事即可（任何网络都能打开）。"
echo ""
read -r -p "按回车键关闭本窗口…"
