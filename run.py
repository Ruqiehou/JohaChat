"""
Joha 统一启动入口
"""

from joha.adapter import MessageClient, GroupMessageEvent, config_manager
from joha.core.handlers import message_handler
from joha.core.utils import runtime_context

NAPCAT_WS_URL = "ws://127.0.0.1:3002"
NAPCAT_ACCESS_TOKEN = ""
NAPCAT_BOT_UIN = "8888888888"
DEBUG = True

config_manager.set_ws_uri(NAPCAT_WS_URL)
config_manager.set_ws_token(NAPCAT_ACCESS_TOKEN)
config_manager.set_bot_uin(NAPCAT_BOT_UIN)
config_manager.set_debug(DEBUG)

runtime_context.bot_uin = int(config_manager.get("napcat.bot_uin", NAPCAT_BOT_UIN))

client = MessageClient(
    ws_url=config_manager.get("napcat.ws_url", NAPCAT_WS_URL),
    access_token=config_manager.get("napcat.access_token", NAPCAT_ACCESS_TOKEN),
)


@client.on_group_message()
async def joha_agent(event: GroupMessageEvent):
    await message_handler.process_group_message(event, client.api)


def main() -> None:
    client.start(debug=config_manager.get("settings.debug", DEBUG))


if __name__ == "__main__":
    main()
