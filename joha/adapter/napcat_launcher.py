"""
NapCat 启动辅助模块
"""
import socket
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

from joha.adapter.config import config_manager


def _try_tcp_probe(host: str, port: int, timeout: float = 2.0) -> bool:
    """TCP 探测 NapCat WebSocket 端口是否已开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _parse_ws_endpoint(ws_url: str) -> tuple[str, int]:
    parsed = urlparse(ws_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    return host, port


def ensure_napcat_running() -> None:
    """确保 NapCat 可连接，必要时自动启动"""
    ws_url = config_manager.get("napcat.ws_url", "ws://localhost:3002")
    auto_start = config_manager.get("napcat.auto_start", False)
    napcat_dir = config_manager.get("napcat.napcat_dir", "napcat")
    host, port = _parse_ws_endpoint(ws_url)

    if _try_tcp_probe(host, port):
        print(f"[NapCat] 检测到已有 NapCat 实例 ({ws_url})，直接连接")
        return

    if not auto_start:
        print(f"[NapCat] 未检测到 NapCat 实例 ({ws_url})，且 auto_start 未启用")
        print("[NapCat] 请手动启动 NapCat，或设置 napcat.auto_start=true")
        return

    napcat_base = Path(napcat_dir)
    if not napcat_base.is_absolute():
        napcat_base = Path.cwd() / napcat_base

    scripts = ["launcher.bat", "napcat.bat", "start.bat", "run.bat"]
    launcher = None
    for script in scripts:
        path = napcat_base / script
        if path.exists():
            launcher = path
            break

    if launcher is None:
        print(f"[NapCat] 未在 {napcat_base} 中找到启动脚本 ({', '.join(scripts)})")
        print("[NapCat] 请手动启动 NapCat")
        return

    print(f"[NapCat] 自动启动 NapCat: {launcher}")
    subprocess.Popen(
        [str(launcher)],
        cwd=str(napcat_base),
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print("[NapCat] 等待 NapCat 就绪...", end="", flush=True)
    for i in range(30):
        time.sleep(1)
        if _try_tcp_probe(host, port):
            print(f" 已就绪（{i + 1}s）")
            return
        print(".", end="", flush=True)
    print(" 超时")
    print(f"[NapCat] NapCat 启动超时，请检查 {launcher}")
