#!/usr/bin/env bash
cd /Users/happy/Desktop/aml-token-inspector || exit 1
echo "正在启动分享服务…"
echo ""
/Users/happy/.workbuddy/binaries/python/versions/3.13.12/bin/python3 serve_daemon.py
echo ""
echo "把这个链接发给同事即可（同一 WiFi 下有效）："
echo ""
read -r -p "按回车键关闭本窗口…"
