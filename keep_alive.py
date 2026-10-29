#!/usr/bin/env python3
"""分享服务守护：本地服务 + 公网隧道，任何一个断了就自动拉起，
地址变了自动更新桌面上的「发给同事.txt」和二维码。

用法：
    python3 keep_alive.py           # 常驻守护（后台）
    python3 keep_alive.py --once    # 只检查修复一次，然后退出
"""
import os
import re
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
PORT = int(os.environ.get("PORT", "8765"))
DESK = os.path.expanduser("~/Desktop")
TXT = os.path.join(DESK, "发给同事.txt")
QR = os.path.join(DESK, "分享二维码.png")
LOG = "/tmp/aml_keepalive.log"

# 本机 shell 配了 HTTP 代理，探测时必须绕开，否则会被误判成"隧道断了"
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

_last_url = None
_fail = 0


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def get(url, timeout):
    """绕开本机代理的探测"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return _opener.open(req, timeout=timeout)


def local_ok():
    try:
        get("http://127.0.0.1:%d/index.html" % PORT, 5)
        return True
    except Exception:
        return False


def start_local():
    log("本地分享服务没响应，正在拉起 ...")
    r = run([PY, "serve_daemon.py"])
    time.sleep(3)
    return local_ok()


def tunnel_alive():
    """返回当前可用的公网地址，不可用则返回 None"""
    r = run([PY, "tunnel_daemon.py", "--status"])
    out = r.stdout or ""
    if "隧道未运行" in out:
        return None
    m = re.search(r"https://\S+", out)   # 输出里的第一个 https 就是公网地址
    url = m.group(0).rstrip(".,)") if m else None
    if not url:
        return None
    # 真的能打开才算活着；网络抖一下不算死，连续 3 次失败才重连
    global _fail
    try:
        get(url + "/index.html", 25)
        _fail = 0
        return url
    except Exception:
        _fail += 1
        log("探测公网地址失败（%d/3）：%s" % (_fail, url))
        if _fail >= 3:
            return None
        return "pending"


def restart_tunnel():
    log("公网隧道断了，正在重连 ...")
    run([PY, "tunnel_daemon.py", "--stop"])
    time.sleep(2)
    r = run([PY, "tunnel_daemon.py"])
    log((r.stdout or r.stderr or "").strip().replace("\n", " | ")[:300])
    time.sleep(3)
    return tunnel_alive()


def write_files(url):
    txt = (
        "AML Design token 自检页，装一下（两步，一分钟）：\n"
        "\n"
        "第 1 步：打开这个链接\n"
        "%s\n"
        "\n"
        "第 2 步：点页面上那个蓝色的「复制一键安装命令」按钮，\n"
        "把复制到的那行粘到「终端」里，回车。\n"
        "\n"
        "装完退出 WorkBuddy 再重新打开，就生效了。\n"
        "\n"
        "\n"
        "——如果上面那条命令不会用，就打开链接后按页面里的说明手动装，\n"
        "或者直接找我要压缩包。\n"
        "\n"
        "（这个文件里的地址会自动更新，永远是最新的那条）\n"
    ) % url
    try:
        with open(TXT, "w", encoding="utf-8") as f:
            f.write(txt)
    except Exception as e:
        log("写文案失败: %s" % e)
    try:
        subprocess.run(
            ["/Users/happy/.workbuddy/binaries/python/envs/default/bin/python",
             "-c",
             "import qrcode; qrcode.make(%r).save(%r)" % (url, QR)],
            capture_output=True, timeout=60,
        )
    except Exception:
        pass


def check():
    global _last_url
    if not local_ok():
        if not start_local():
            log("本地服务起不来，跳过本轮")
            return
    url = tunnel_alive()
    if url == "pending":
        return  # 只是网络抖了一下，先不动，免得白白换地址
    if not url:
        url = restart_tunnel()
    if url and url not in ("pending", None) and url != _last_url:
        write_files(url)
        _last_url = url
        log("地址已更新到桌面：%s" % url)


def main():
    once = "--once" in sys.argv
    log("守护已启动（本地服务 + 公网隧道，断了自动重连）")
    while True:
        try:
            check()
        except Exception as e:
            log("本轮出错: %s" % e)
        if once:
            break
        time.sleep(30)


if __name__ == "__main__":
    main()
