"""
Joha Adapter —— 主入口模块
NapCat 适配层：连接、事件、API、配置管理
"""

from __future__ import annotations

from .bot_client import BotClient
from .config import Config, setup_logging
from .core import (
    BaseEvent,
    BotAPI,
    EventBus,
    FriendRecallNotice,
    FriendRequestEvent,
    GroupBanNotice,
    GroupDecreaseNotice,
    GroupIncreaseNotice,
    GroupMessageEvent,
    GroupRecallNotice,
    GroupRequestEvent,
    Message,
    NapCatClient,
    NoticeEvent,
    PokeNotice,
    PrivateMessageEvent,
    RequestEvent,
)

__version__: str = "3.5.0"

__all__: list[str] = [
    "NapCatClient",
    "BotAPI",
    "EventBus",
    "BaseEvent",
    "Message",
    "GroupMessageEvent",
    "PrivateMessageEvent",
    "NoticeEvent",
    "GroupIncreaseNotice",
    "GroupDecreaseNotice",
    "GroupBanNotice",
    "GroupRecallNotice",
    "FriendRecallNotice",
    "PokeNotice",
    "RequestEvent",
    "FriendRequestEvent",
    "GroupRequestEvent",
    "Config",
    "setup_logging",
    "BotClient",
    "__version__",
]
