"""
Joha Adapter 入口
优先尝试连接已有 NapCat 实例，连接失败则自动启动 NapCat（配置启用时）
"""
import asyncio
import os
import socket
import subprocess
import time
from pathlib import Path

from joha.adapter import BotClient, GroupMessageEvent
from joha.core.handlers import message_handler
from joha.core.utils import runtime_context
from joha.core.builders import message_queue_manager
from joha.adapter.config import config_manager

# ---- 从配置读取参数 ----
WS_URL = config_manager.get("napcat.ws_url", "ws://localhost:3002")
ACCESS_TOKEN = config_manager.get("napcat.access_token", "")
AUTO_START = config_manager.get("napcat.auto_start", False)
NAPCAT_DIR = config_manager.get("napcat.napcat_dir", "napcat")
BOT_UIN = config_manager.get("napcat.bot_uin", "8888888888")
DEBUG = config_manager.get("settings.debug", True)

runtime_context.bot_uin = int(BOT_UIN) if BOT_UIN else 8888888888

# ---- 创建 BotClient ----
bot = BotClient(ws_url=WS_URL, access_token=ACCESS_TOKEN)


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


def _ensure_napcat():
    """确保 NapCat 可连接，必要时自动启动"""
    # 解析 host:port
    raw = WS_URL.replace("ws://", "").replace("wss://", "")
    host = raw.split(":")[0]
    port_str = raw.split(":")[1].split("/")[0] if ":" in raw else "3001"
    port = int(port_str)

    # 尝试连接已有实例
    if _try_tcp_probe(host, port):
        print(f"[NapCat] 检测到已有 NapCat 实例 ({WS_URL})，直接连接")
        return

    if not AUTO_START:
        print(f"[NapCat] 未检测到 NapCat 实例 ({WS_URL})，且 auto_start 未启用")
        print(f"[NapCat] 请手动启动 NapCat，或设置 napcat.auto_start=true")
        return

    # 查找启动脚本
    napcat_base = Path(NAPCAT_DIR)
    if not napcat_base.is_absolute():
        napcat_base = Path.cwd() / NAPCAT_DIR

    scripts = ["launcher.bat", "napcat.bat", "start.bat", "run.bat"]
    launcher = None
    for s in scripts:
        p = napcat_base / s
        if p.exists():
            launcher = p
            break

    if launcher is None:
        print(f"[NapCat] 未在 {napcat_base} 中找到启动脚本 ({', '.join(scripts)})")
        print(f"[NapCat] 请手动启动 NapCat")
        return

    print(f"[NapCat] 自动启动 NapCat: {launcher}")
    subprocess.Popen(
        [str(launcher)],
        cwd=str(napcat_base),
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    # 等待 NapCat 就绪（最多 30 秒）
    print("[NapCat] 等待 NapCat 就绪...", end="", flush=True)
    for i in range(30):
        time.sleep(1)
        if _try_tcp_probe(host, port):
            print(f" 已就绪（{i + 1}s）")
            return
        print(".", end="", flush=True)
    print(" 超时")
    print(f"[NapCat] NapCat 启动超时，请检查 {launcher}")


async def process_expired_queues():
    """定时处理过期的消息队列"""
    while True:
        try:
            await asyncio.sleep(10)
            expired_messages = await message_queue_manager.process_expired()

            if expired_messages:
                from joha.config.infrastructure.logger import tprint
                tprint("info", f"[定时任务] 处理了 {len(expired_messages)} 个过期消息队列")
        except Exception as e:
            from joha.config.infrastructure.logger import tprint
            tprint("error", f"[定时任务] 处理过期队列失败: {e}")


@bot.on_group_message()
async def joha_agent(event: GroupMessageEvent):
    if not hasattr(joha_agent, "_queue_task_started"):
        joha_agent._queue_task_started = True
        asyncio.create_task(process_expired_queues())

    await message_handler.process_group_message(event, bot.api)


if __name__ == "__main__":
    _ensure_napcat()
    try:
        bot.start(debug=DEBUG)
    finally:
        from joha.managers.style_learner import style_learner
        from joha.managers.user_profile import user_profile_manager
        style_learner.save_all()
        user_profile_manager.save_all()
        print("[Shutdown] 已保存所有状态")
