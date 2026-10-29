#!/usr/bin/env python3
"""脱离终端常驻的静态分享服务（double-fork daemon）。

用法：
    python3 serve_daemon.py          # 后台常驻，命令立即返回并打印链接
    python3 serve_daemon.py --stop   # 停止服务
"""
import os
import signal
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
PORT = int(os.environ.get("PORT", "8765"))
PIDFILE = "/tmp/aml_tokenshare.pid"
LOG = "/tmp/aml_share.log"


def local_ip():
    for iface in ("en0", "en1", "en2", "en3"):
        try:
            out = subprocess.check_output(["ipconfig", "getifaddr", iface], text=True).strip()
        except Exception:
            out = ""
        if out:
            return out
    return "127.0.0.1"


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


def stop():
    pid = running_pid()
    if not pid:
        print("没有正在运行的服务")
        return
    os.kill(pid, signal.SIGTERM)
    print("已停止服务（pid %d）" % pid)
    try:
        os.remove(PIDFILE)
    except OSError:
        pass


def serve():
    """子进程：脱离会话后常驻。"""
    os.setsid()
    if os.fork() > 0:
        os._exit(0)

    os.chdir(ROOT)
    log = open(LOG, "a")
    os.dup2(log.fileno(), sys.stdout.fileno())
    os.dup2(log.fileno(), sys.stderr.fileno())

    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    ThreadingHTTPServer.allow_reuse_address = True
    ThreadingHTTPServer(("0.0.0.0", PORT), Quiet).serve_forever()


def main():
    if "--stop" in sys.argv:
        stop()
        return

    ip = local_ip()
    if running_pid():
        print("服务已在运行（pid %d）" % running_pid())
        print("  安装页：http://%s:%d" % (ip, PORT))
        return

    if os.fork() > 0:          # 父进程：等一下，打印链接后退出
        time.sleep(1.2)
        print("服务已启动（后台常驻，重启电脑或执行 --stop 才会停）")
        print("")
        print("  发给同事的链接：http://%s:%d" % (ip, PORT))
        print("")
        return

    serve()                    # 子进程：进入常驻


if __name__ == "__main__":
    main()
