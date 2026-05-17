# 决策模块 - 回复决策、冷却管理、意图分类
from .reply_decision import MessageContext, should_reply, compute_reply_prob
from .cooldown import cooldown_manager
from .intent_classifier import IntentClassifier, get_intent_classifier, reload_intent_classifier, intent_classifier

# 决策引擎（总分架构的"总"）
from .decision_engine import DecisionEngine, get_decision_engine, EngineResult

# 工具模块已迁移至 joha/tools/
def __getattr__(name):
    import importlib
    _tool_names = {'SearchTool', 'WebpageTool', 'LinkPreviewTool',
                   'KnowledgeBaseSearchTool', 'get_kb_search_tool'}
    if name in _tool_names:
        return getattr(importlib.import_module('joha.tools'), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'MessageContext', 'should_reply', 'compute_reply_prob', 'cooldown_manager',
    'DecisionEngine', 'get_decision_engine', 'EngineResult',
    'IntentClassifier', 'get_intent_classifier', 'reload_intent_classifier', 'intent_classifier',
]
