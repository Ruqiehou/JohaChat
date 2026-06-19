"""
传输层客户端
NapCatClient: WebSocket 连接管理、消息收发循环、通用 API 调用
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import time
import uuid
from typing import (
    Any, Awaitable, Callable, Dict, Final, List, Optional, Union,
)
from urllib.parse import urlparse
import websockets
from websockets.exceptions import ConnectionClosed

from adapter.config import Config, setup_logging
from adapter.transport.interfaces import IClient, IConnectionEventListener

# 设置日志系统
setup_logging()

logger = logging.getLogger(__name__)


class NapCatClient(IClient):
    """NapCat 传输层客户端 —— 专注于 WebSocket 连接管理
    
    职责：
    - WebSocket 连接/断开/重连
    - 原始消息收发
    - 通用 API 调用 (call_api)
    - 连接状态管理与事件监听
    
    不包含任何 OneBot 协议层的业务方法，协议封装由 protocol.api.BotAPI 负责。
    """

    # ---- 重连配置 ----
    MAX_RECONNECT_ATTEMPTS: Final[int] = 5
    RECONNECT_DELAY: Final[float] = 3.0       # 秒
    PING_INTERVAL: Final[float] = 25.0
    PING_TIMEOUT: Final[float] = 10.0
    CLOSE_TIMEOUT: Final[float] = 5.0

    def __init__(
        self,
        ws_url: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> None:
        self.ws_url: str = self._normalize_ws_url(ws_url or Config.NAPCAT_WS_URL)
        self.access_token: str = access_token or Config.NAPCAT_ACCESS_TOKEN
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._connected: bool = False
        self.echo_map: Dict[str, asyncio.Future[Any]] = {}

        # ---- 消息回调 ----
        self._message_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None

        # ---- 消息处理队列 ----
        self.msg_queue: Optional[asyncio.Queue[str]] = None
        self._processing_task: Optional[asyncio.Task[None]] = None
        self._listen_task: Optional[asyncio.Task[None]] = None

        # ---- 性能监控 ----
        self._perf_stats: Dict[str, Union[int, float]] = {
            "total_messages": 0,
            "total_processing_time": 0.0,
            "avg_latency": 0.0,
        }

        # ---- 重连控制 ----
        self._reconnect_attempts: int = 0
        self._reconnect_event: asyncio.Event = asyncio.Event()
        self._reconnect_event.set()  # 初始为可连接状态

        # ---- 连接事件监听器 ----
        self._connection_listeners: List[IConnectionEventListener] = []

    @staticmethod
    def _normalize_ws_url(url: str) -> str:
        """标准化 WebSocket URL，解决 localhost 的 IPv4/IPv6 解析问题
        
        将 localhost 替换为 127.0.0.1，避免在某些系统上解析为 IPv6 ::1 导致连接失败。
        
        Args:
            url: 原始 WebSocket URL
            
        Returns:
            标准化后的 URL
        """
        if "localhost" in url:
            url = url.replace("localhost", "127.0.0.1")
        return url

    @staticmethod
    def _parse_ws_endpoint(ws_url: str) -> tuple[str, int]:
        """解析 WebSocket URL 获取主机和端口
        
        Args:
            ws_url: WebSocket URL
            
        Returns:
            (host, port) 元组
        """
        parsed = urlparse(ws_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "wss" else 80)
        return host, port

    @staticmethod
    def _tcp_probe(host: str, port: int, timeout: float = 2.0) -> bool:
        """TCP 探测目标端口是否已开放
        
        Args:
            host: 主机地址
            port: 端口号
            timeout: 超时时间（秒）
            
        Returns:
            端口是否开放
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def check_connection(self) -> bool:
        """检测 NapCat 是否可连接
        
        Returns:
            是否可连接
        """
        host, port = self._parse_ws_endpoint(self.ws_url)
        return self._tcp_probe(host, port)

    @property
    def connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    def set_message_callback(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """设置消息回调函数
        
        Args:
            callback: 异步回调函数，接收消息数据字典
        """
        self._message_callback = callback
    
    async def connect(self, max_retries: Optional[int] = None) -> bool:
        """建立连接（支持重连）
        
        Args:
            max_retries: 最大重试次数，None使用默认配置
            
        Returns:
            是否连接成功
        """
        retries = 0
        max_retries = max_retries or self.MAX_RECONNECT_ATTEMPTS
        
        while retries < max_retries:
            try:
                if retries > 0:
                    self._reconnect_attempts = retries
                    logger.info(f"尝试重连 ({retries}/{max_retries})...")
                    for listener in self._connection_listeners:
                        try:
                            await listener.on_reconnecting(retries)
                        except Exception as e:
                            logger.error(f"重连监听器执行失败: {e}")
                
                headers = {}
                if self.access_token:
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    headers["access_token"] = self.access_token

                connect_kwargs = {
                    "ping_interval": self.PING_INTERVAL,
                    "ping_timeout": self.PING_TIMEOUT,
                    "close_timeout": self.CLOSE_TIMEOUT,
                    "additional_headers": headers if headers else {},
                }

                self.ws = await websockets.connect(
                    self.ws_url,
                    **connect_kwargs
                )
                
                # 初始化消息队列
                self.msg_queue = asyncio.Queue(maxsize=1000)
                
                self._connected = True

                # 启动接收任务
                self._listen_task = asyncio.create_task(self._listen_messages())
                
                # 启动处理任务
                self._processing_task = asyncio.create_task(self._process_messages())
                
                was_reconnect = self._reconnect_attempts > 0
                self._reconnect_attempts = 0

                logger.info(f"成功连接到NapCat服务器: {self.ws_url}")

                # 通知连接成功
                for listener in self._connection_listeners:
                    try:
                        if was_reconnect and hasattr(listener, 'on_reconnect_success'):
                            await listener.on_reconnect_success()
                        else:
                            await listener.on_connected()
                    except Exception as e:
                        logger.error(f"连接监听器执行失败: {e}")
                
                return True
                
            except Exception as e:
                retries += 1
                logger.error(f"连接失败 ({retries}/{max_retries}): {e}")
                
                if retries < max_retries:
                    wait_time = self.RECONNECT_DELAY * retries
                    logger.info(f"{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
        
        logger.error(f"连接失败，已达到最大重试次数 ({max_retries})")
        
        # 通知重连失败
        for listener in self._connection_listeners:
            try:
                await listener.on_reconnect_failed(
                    Exception(f"连接失败，已达到最大重试次数 ({max_retries})")
                )
            except Exception as e:
                logger.error(f"重连失败监听器执行失败: {e}")
        
        return False
    
    async def disconnect(self, force: bool = False) -> None:
        """断开连接
        
        Args:
            force: 是否强制断开
        """
        if not self._connected and not force:
            return
        
        self._connected = False
        
        # 关闭消息队列处理
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"关闭处理任务时出错: {e}")
            finally:
                self._processing_task = None
        
        # 关闭监听任务
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"关闭监听任务时出错: {e}")
            finally:
                self._listen_task = None
        
        # 关闭 WebSocket 连接
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"关闭WebSocket连接时出错: {e}")
            finally:
                self.ws = None
        
        logger.info("WebSocket 连接已关闭")
        
        # 通知断开连接
        for listener in self._connection_listeners:
            try:
                await listener.on_disconnected()
            except Exception as e:
                logger.error(f"断开连接监听器执行失败: {e}")
    
    def add_connection_listener(self, listener: IConnectionEventListener) -> None:
        """添加连接事件监听器

        Args:
            listener: IConnectionEventListener 实例
        """
        if listener not in self._connection_listeners:
            self._connection_listeners.append(listener)

    def remove_connection_listener(self, listener: IConnectionEventListener) -> None:
        """移除连接事件监听器

        Args:
            listener: IConnectionEventListener 实例
        """
        if listener in self._connection_listeners:
            self._connection_listeners.remove(listener)

    async def _listen_messages(self) -> None:
        """监听消息 —— 接收循环（非阻塞入队）"""
        try:
            async for message in self.ws:
                try:
                    if self.msg_queue:
                        self.msg_queue.put_nowait(message)
                except asyncio.QueueFull:
                    logger.warning("消息队列已满，丢弃消息")
                except Exception as e:
                    logger.error(f"消息入队失败: {e}")
        except ConnectionClosed:
            logger.warning("WebSocket连接已关闭")
            self._connected = False
        except Exception as e:
            logger.error(f"监听消息时发生错误: {e}")
            self._connected = False

    async def _process_messages(self) -> None:
        """消息处理循环 —— 与接收分离"""
        while self._connected:
            try:
                if not self.msg_queue:
                    await asyncio.sleep(0.1)
                    continue

                message = await self.msg_queue.get()
                
                # 性能监控 - 开始
                start_time = time.perf_counter()
                
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"消息解析失败: {e}")
                except Exception as e:
                    logger.error(f"处理消息时发生错误: {e}")
                finally:
                    # 性能监控 - 结束
                    processing_time = time.perf_counter() - start_time
                    self._perf_stats["total_messages"] += 1
                    self._perf_stats["total_processing_time"] += processing_time
                    self._perf_stats["avg_latency"] = (
                        self._perf_stats["total_processing_time"] / 
                        self._perf_stats["total_messages"]
                    )
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"处理循环错误: {e}")

    async def _handle_message(self, data: Dict[str, Any]) -> None:
        """处理消息"""
        # 处理 API 响应（echo）
        if "echo" in data:
            echo_id = data["echo"]
            if echo_id in self.echo_map:
                future = self.echo_map.pop(echo_id)
                if not future.done():
                    future.set_result(data)
                return
        
        # 调用消息回调函数
        if self._message_callback:
            try:
                await self._message_callback(data)
            except Exception as e:
                logger.error(f"消息回调执行失败: {e}", exc_info=True)

    async def call_api(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> Dict[str, Any]:
        """调用 API（支持重试）—— 传输层唯一对外暴露的调用入口
        
        Args:
            action: API 动作名称
            params: 参数字典
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            API 响应数据
            
        Raises:
            ConnectionError: 未连接
            TimeoutError: API 调用超时
            Exception: 其他错误
        """
        if not self.connected or not self.ws:
            raise ConnectionError("未连接到NapCat服务器")

        last_error = None
        
        for attempt in range(max_retries):
            echo_id = f"rqhbot-{uuid.uuid4().hex}"
            message = {
                "action": action,
                "params": params or {},
                "echo": echo_id
            }

            future = asyncio.Future()
            self.echo_map[echo_id] = future

            try:
                await self.ws.send(json.dumps(message))
                result = await asyncio.wait_for(future, timeout=30)
                
                if result.get("status") == "ok":
                    return result.get("data", {})
                else:
                    last_error = Exception(f"API调用失败: {result.get('msg', '未知错误')}")
                    
            except asyncio.TimeoutError:
                last_error = TimeoutError(f"API调用超时 (尝试 {attempt + 1}/{max_retries})")
            except Exception as e:
                last_error = e
            finally:
                self.echo_map.pop(echo_id, None)
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                logger.warning(f"API调用失败，{retry_delay}秒后重试 ({attempt + 1}/{max_retries}): {last_error}")
                await asyncio.sleep(retry_delay)
        
        # 所有重试都失败
        if last_error:
            raise last_error
        raise Exception(f"API调用失败: 未知错误 (action={action})")

    def get_performance_stats(self) -> Dict[str, Union[int, float, bool]]:
        """获取性能统计信息

        Returns:
            性能统计字典
        """
        stats: Dict[str, Union[int, float, bool]] = dict(self._perf_stats.copy())
        stats["reconnect_attempts"] = self._reconnect_attempts
        stats["is_connected"] = self._connected
        return stats
