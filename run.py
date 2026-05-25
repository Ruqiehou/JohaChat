"""
Joha 统一启动入口
支持从 connection.yaml 读取配置，也可在代码中自定义覆盖
"""
import asyncio

from joha.adapter import MessageClient, GroupMessageEvent
from joha.adapter.config import config_manager
from joha.core.handlers import message_handler
from joha.core.utils import runtime_context
from joha.core.builders import message_queue_manager

# ========================
# 连接配置（可自定义覆盖）
# ========================
# 优先级：代码中设置 > connection.yaml > 默认值

# 从 connection.yaml 读取配置
_napcat_cfg = config_manager.get("napcat", {})

# 可在此处自定义覆盖（取消注释并修改）
# WS_URL = "ws://127.0.0.1:3002"        # 自定义 WebSocket 地址
# ACCESS_TOKEN = "your_token"             # 自定义访问令牌
# BOT_UIN = "1234567890"                  # 自定义机器人 QQ 号

# 使用自定义配置或 YAML 配置
WS_URL = _napcat_cfg.get("ws_url", "ws://127.0.0.1:3002")
ACCESS_TOKEN = _napcat_cfg.get("access_token", "")
BOT_UIN = _napcat_cfg.get("bot_uin", "8888888888")

# 设置运行时上下文
runtime_context.bot_uin = int(BOT_UIN) if BOT_UIN else 8888888888

# 创建消息客户端
client = MessageClient(
    ws_url=WS_URL,
    access_token=ACCESS_TOKEN,
)


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


@client.on_group_message()
async def joha_agent(event: GroupMessageEvent):
    if not hasattr(joha_agent, "_queue_task_started"):
        joha_agent._queue_task_started = True
        asyncio.create_task(process_expired_queues())

    await message_handler.process_group_message(event, client.api)


def main() -> None:
    """启动机器人
    
    配置优先级：
    1. 代码中自定义的配置（WS_URL, ACCESS_TOKEN, BOT_UIN）
    2. adapter/connection.yaml 中的配置
    3. 默认值
    
    注意：如果配置不匹配，将无法连接到 NapCat
    请确保：
    1. NapCat 已启动
    2. WebSocket 地址和端口正确
    3. 机器人 QQ 号与 NapCat 配置一致
    """
    print("=" * 50)
    print("  Joha 智能群聊机器人")
    print("=" * 50)
    print(f"  WebSocket: {WS_URL}")
    print(f"  机器人 QQ: {BOT_UIN}")
    print("=" * 50)
    
    try:
        client.start(debug=config_manager.get("settings.debug", True))
    finally:
        from joha.managers.style_learner import style_learner
        from joha.managers.user_profile import user_profile_manager
        style_learner.save_all()
        user_profile_manager.save_all()
        print("[Shutdown] 已保存所有状态")


if __name__ == "__main__":
    main()
