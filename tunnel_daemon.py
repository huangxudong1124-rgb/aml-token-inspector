#!/usr/bin/env python3
"""把本机的分享服务通过匿名 SSH 隧道暴露到公网（无需任何账号）。

用法：
    python3 tunnel_daemon.py           # 建立隧道并打印公网地址
    python3 tunnel_daemon.py --status  # 查看当前公网地址
    python3 tunnel_daemon.py --stop    # 停止隧道

注意：免费隧道的域名每次重连都会变，重开后请重新复制地址。
"""
import os
import re
import signal
import subprocess
import sys
import time

LOG = "/tmp/aml_tunnel.log"
PIDFILE = "/tmp/aml_tunnel.pid"
PORT = int(os.environ.get("PORT", "8765"))
# 隧道地址形如 https://xxxxxxxxxxxx.lhr.life；
# 排除欢迎信息里的 admin.localhost.run / 文档链接等干扰项
URL_RE = re.compile(r"https://[a-z0-9-]{6,}\.(?:lhr\.life|localhost\.run)")


def running_pid():
    try:
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
    except Exception:
        return None
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    return pid


def current_url():
    try:
        with open(LOG, errors="ignore") as f:
            text = f.read()
    except FileNotFoundError:
        return None
    # 优先取「xxx tunneled with tls termination」那一行里的地址
    line = re.search(r"([a-z0-9.-]+) tunneled with tls termination", text)
    if line:
        return "https://" + line.group(1)
    found = [u for u in URL_RE.findall(text) if "admin." not in u]
    return found[-1] if found else None


def start():
    if running_pid():
        url = current_url()
        print("隧道已在运行（pid %d）" % running_pid())
        if url:
            print("  公网地址：%s" % url)
        return

    open(LOG, "w").close()
    log = open(LOG, "a")
    proc = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
         "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=3",
         "-o", "ExitOnForwardFailure=yes", "-n",
         "-R", "80:127.0.0.1:%d" % PORT, "nokey@localhost.run"],
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
    )
    with open(PIDFILE, "w") as f:
        f.write(str(proc.pid))

    url = None
    for _ in range(40):
        time.sleep(1)
        url = current_url()
        if url:
            break
    if url:
        print("公网隧道已建立（后台常驻）")
        print("")
        print("  发给同事的链接：%s" % url)
        print("")
        print("  一条命令安装：")
        print("    curl -fsSL %s/install.sh | bash -s -- %s" % (url, url))
        print("")
        print("提示：免费隧道域名每次重连都会变，重开后请重新复制。")
    else:
        print("隧道已启动但还没拿到地址，稍后再跑：python3 tunnel_daemon.py --status")
        print("日志：%s" % LOG)


def stop():
    pid = running_pid()
    if not pid:
        print("没有正在运行的隧道")
        return
    os.kill(pid, signal.SIGTERM)
    print("已停止隧道（pid %d）" % pid)
    try:
        os.remove(PIDFILE)
    except OSError:
        pass


def main():
    if "--stop" in sys.argv:
        stop()
    elif "--status" in sys.argv:
        pid = running_pid()
        url = current_url()
        if not pid:
            print("隧道未运行")
            return
        print("隧道运行中（pid %d）" % pid)
        print("  公网地址：%s" % (url or "(尚未分配)"))
        if url:
            print("  一条命令安装：")
            print("    curl -fsSL %s/install.sh | bash -s -- %s" % (url, url))
    else:
        start()


if __name__ == "__main__":
    main()
