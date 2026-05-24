"""
Joha 统一启动入口
通过 adapter/config/connection.yaml 读取 NapCat 连接配置
"""
import asyncio

from joha.adapter import MessageClient, GroupMessageEvent, ensure_napcat_running
from joha.adapter.config import config_manager
from joha.core.handlers import message_handler
from joha.core.utils import runtime_context
from joha.core.builders import message_queue_manager

_napcat_cfg = config_manager.get("napcat", {})
_bot_uin = _napcat_cfg.get("bot_uin", "8888888888")

runtime_context.bot_uin = int(_bot_uin) if _bot_uin else 8888888888

ensure_napcat_running()

client = MessageClient(
    ws_url=_napcat_cfg.get("ws_url", "ws://localhost:3002"),
    access_token=_napcat_cfg.get("access_token", ""),
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
