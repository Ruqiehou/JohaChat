"""adapter.core.interfaces → transport + protocol 接口兼容重导出"""

from adapter.transport.interfaces import (
    APIResponse,
    EventHandler,
    IClient,
    IConnectionEventListener,
    MessageSegmentType,
)
from adapter.protocol.interfaces import (
    IBotAPI,
    IEventDispatcher,
)

__all__ = [
    "APIResponse",
    "EventHandler",
    "IClient",
    "IConnectionEventListener",
    "MessageSegmentType",
    "IBotAPI",
    "IEventDispatcher",
]
