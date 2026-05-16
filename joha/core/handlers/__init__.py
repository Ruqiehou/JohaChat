# 消息处理器模块
from .message import message_processor, MessageProcessor
from .commands import command_handler, normalize_fallback_command
from .service import message_service, MessageService

__all__ = [
    'message_processor',
    'MessageProcessor',
    'command_handler',
    'normalize_fallback_command',
    'message_service',
    'MessageService',
]
