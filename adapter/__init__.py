"""
Joha Adapter —— 主入口模块
NapCat 适配层：连接、事件、API、配置管理
"""

from __future__ import annotations

from .message_client import MessageClient
from .config import Config, ConfigManager, config_manager, setup_logging, get_logger
from .kernel import (
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
    "ConfigManager",
    "config_manager",
    "setup_logging",
    "get_logger",
    "MessageClient",
    "__version__",
]
