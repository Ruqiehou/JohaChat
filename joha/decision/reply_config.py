"""
回复决策配置加载器
将 reply_decision 配置独立到 config/reply_decision.json，与主配置解耦
"""
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from joha.config.infrastructure.logger import tprint


CONFIG_FILE = Path(__file__).resolve().parent.parent / "config" / "reply_decision.json"


@dataclass(frozen=True)
class ReplyConfig:
    """回复决策配置（每次调用懒加载最新值）"""

    _data: Dict[str, Any] = None

    def _load(self) -> Dict[str, Any]:
        """懒加载配置文件"""
        if ReplyConfig._data is None:
            try:
                if CONFIG_FILE.exists():
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        ReplyConfig._data = json.load(f)
                else:
                    tprint("warning", f"[ReplyConfig] 配置文件不存在: {CONFIG_FILE}")
                    ReplyConfig._data = {}
            except Exception as e:
                tprint("warning", f"[ReplyConfig] 加载失败: {e}")
                ReplyConfig._data = {}
        return ReplyConfig._data

    def reload(self) -> None:
        """强制重新加载配置"""
        ReplyConfig._data = None

    @property
    def bot_nicknames(self) -> set:
        return set(self._load().get("bot_nicknames", ["bot", "机器人"]))

    @property
    def feedback_weights(self) -> Dict[str, float]:
        return self._load().get("feedback_weights", {})

    @property
    def thresholds(self) -> Dict[str, float]:
        return self._load().get("thresholds", {})

    @property
    def blend(self) -> Dict[str, float]:
        return self._load().get("blend", {})

    @property
    def ai_intent_trigger(self) -> Dict[str, Any]:
        return self._load().get("ai_intent_trigger", {})

    @property
    def group_dynamic(self) -> Dict[str, float]:
        return self._load().get("group_dynamic", {})

    @property
    def length_bonuses(self) -> Dict[str, float]:
        return self._load().get("length_bonuses", {})

    @property
    def spam_detection(self) -> Dict[str, float]:
        return self._load().get("spam_detection", {})

    @property
    def intent_feedback_mapping(self) -> Dict[str, str]:
        return self._load().get("intent_feedback_mapping", {})

    @property
    def threshold_adjustments(self) -> Dict[str, float]:
        return self._load().get("threshold_adjustments", {})

    def __getattr__(self, name):
        return self._load().get(name)


reply_cfg = ReplyConfig()
