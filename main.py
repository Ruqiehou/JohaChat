from ncatbot.core import BotClient, GroupMessage
from ncatbot.utils import config
import asyncio

from joha.core.handlers import message_handler
from joha.core.utils import runtime_context
from joha.core.builders import message_queue_manager

# ncatbot 配置（硬编码）
config.set_bot_uin(bot_uin="")
config.set_root(root="")
config.set_ws_uri(ws_uri="ws://localhost:3002")
config.set_ws_token(ws_token="")
config.set_webui_uri(webui_uri="http://localhost:6098")
config.set_webui_token(webui_token="")
runtime_context.bot_uin = 8888888888

bot = BotClient()


async def process_expired_queues():
    """定时处理过期的消息队列"""
    while True:
        try:
            await asyncio.sleep(10)  # 每10秒检查一次
            expired_messages = await message_queue_manager.process_expired()
            
            if expired_messages:
                from joha.config.infrastructure.logger import tprint
                tprint("info", f"[定时任务] 处理了 {len(expired_messages)} 个过期消息队列")
        except Exception as e:
            from joha.config.infrastructure.logger import tprint
            tprint("error", f"[定时任务] 处理过期队列失败: {e}")


@bot.on_group_message()
async def joha_agent(msg: GroupMessage):
    # 启动后台任务（只启动一次）
    if not hasattr(joha_agent, '_queue_task_started'):
        joha_agent._queue_task_started = True
        asyncio.create_task(process_expired_queues())
    
    await message_handler.process_group_message(msg, bot.api)


try:
    bot.run_frontend(debug=True)
finally:
    from joha.managers.style_learner import style_learner
    from joha.managers.user_profile import user_profile_manager
    from joha.decision.group_state import group_state_manager
    style_learner.save_all()
    user_profile_manager.save_all()
    # group_state 会自动保存，无需手动调用
    print("[Shutdown] 已保存所有状态")
