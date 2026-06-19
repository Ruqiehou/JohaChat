"""adapter.core.client → adapter.transport.client 兼容重导出"""

from adapter.transport.client import NapCatClient
from adapter.transport.interfaces import IClient, IConnectionEventListener, MessageSegmentType

__all__ = ["NapCatClient", "IClient", "IConnectionEventListener", "MessageSegmentType"]
