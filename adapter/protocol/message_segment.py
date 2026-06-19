"""
消息段构建器
用于构建 NapCat / OneBot 数组格式的消息
"""

from __future__ import annotations

import json
from typing import Any, Dict, Union

from adapter.transport.interfaces import MessageSegmentType


class MessageSegment:
    """消息段构建器 —— 用于构建 NapCat 数组格式的消息

    NapCat 的 message 支持数组格式：
    ```python
    [
        {"type": "text", "data": {"text": "你好，"}},
        {"type": "image", "data": {"file": "https://example.com/pic.png"}},
        {"type": "text", "data": {"text": "这是图片！"}},
    ]
    ```
    """

    @staticmethod
    def text(content: str) -> MessageSegmentType:
        """文字消息段"""
        return {"type": "text", "data": {"text": content}}

    @staticmethod
    def image(file: str, summary: str = "") -> MessageSegmentType:
        """图片消息段
        Args:
            file: 图片路径（本地路径或 URL）
            summary: 图片简介（可选，用于加载失败时显示）
        """
        data: Dict[str, Any] = {"file": file}
        if summary:
            data["summary"] = summary
        return {"type": "image", "data": data}

    @staticmethod
    def at(qq: Union[int, str]) -> MessageSegmentType:
        """@某人消息段"""
        return {"type": "at", "data": {"qq": str(qq)}}

    @staticmethod
    def reply(message_id: int) -> MessageSegmentType:
        """回复消息段"""
        return {"type": "reply", "data": {"id": message_id}}

    @staticmethod
    def face(face_id: int) -> MessageSegmentType:
        """QQ 表情消息段 (face id)"""
        return {"type": "face", "data": {"id": face_id}}

    @staticmethod
    def dice() -> MessageSegmentType:
        """骰子消息段"""
        return {"type": "dice", "data": {}}

    @staticmethod
    def rps() -> MessageSegmentType:
        """猜拳消息段"""
        return {"type": "rps", "data": {}}

    @staticmethod
    def json_data(data: Union[Dict[str, Any], str]) -> MessageSegmentType:
        """JSON 卡片消息段"""
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        return {"type": "json", "data": {"data": data}}
