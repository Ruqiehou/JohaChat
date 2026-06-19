"""
传输层接口定义
定义 WebSocket 客户端与连接事件监听器的抽象接口
"""

from __future__ import annotations

import logging
from typing import (
    Any, Awaitable, Callable, Dict, Optional, TypeAlias,
)
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)

# ---- 基础类型别名 ----
APIResponse: TypeAlias = Dict[str, Any]
EventHandler: TypeAlias = Callable[[Dict[str, Any]], Awaitable[None]]
MessageSegmentType = Dict[str, Any]


# ==================== 客户端接口 ====================

@runtime_checkable
class IClient(Protocol):
    """客户端 Protocol —— 定义所有客户端必须实现的方法签名"""

    # ---- 连接状态 ----
    @property
    def connected(self) -> bool:
        """是否已连接到服务端"""
        ...

    async def connect(self, max_retries: Optional[int] = None) -> bool:
        """建立连接（支持重试）

        Args:
            max_retries: 最大重试次数，None 使用默认值

        Returns:
            bool —— 是否连接成功
        """
        ...

    async def disconnect(self, force: bool = False) -> None:
        """断开连接

        Args:
            force: 是否强制断开
        """
        ...

    # ---- API 调用 ----
    async def call_api(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> APIResponse:
        """调用底层 API（带重试）

        Args:
            action: API 动作名称
            params: 参数
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）

        Returns:
            APIResponse —— API 返回的 data 字段

        Raises:
            ConnectionError: 未连接到服务端
            TimeoutError: 调用超时
        """
        ...


# ==================== 连接事件监听器接口 ====================

class IConnectionEventListener:
    """连接事件监听器接口 —— 观察 WebSocket 连接状态变化"""

    async def on_connected(self) -> None:
        """连接建立回调"""
        ...

    async def on_disconnected(self) -> None:
        """连接断开回调"""
        ...

    async def on_reconnecting(self, attempt: int) -> None:
        """开始重连回调

        Args:
            attempt: 当前重连尝试次数
        """
        ...

    async def on_reconnect_success(self) -> None:
        """重连成功回调"""
        ...

    async def on_reconnect_failed(self, error: Exception) -> None:
        """重连失败回调（已达最大次数）

        Args:
            error: 失败原因
        """
        ...
