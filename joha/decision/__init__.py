# 决策模块 - 回复决策、冷却管理、知识库、工具调用
from .reply_decision import MessageContext, should_reply, compute_reply_prob
from .cooldown import cooldown_manager
from .knowledge.base import KnowledgeBase, get_knowledge_base, search_knowledge_base
from .intent_classifier import IntentClassifier, get_intent_classifier, reload_intent_classifier, intent_classifier

# 工具模块已迁移至 joha/tools/（避免循环导入，使用惰性导入）
def __getattr__(name):
    import importlib
    _tool_names = {'SearchTool', 'WebpageTool', 'LinkPreviewTool',
                   'KnowledgeBaseSearchTool', 'get_kb_search_tool'}
    if name in _tool_names:
        return getattr(importlib.import_module('joha.tools'), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'MessageContext', 'should_reply', 'compute_reply_prob', 'cooldown_manager',
    'KnowledgeBase', 'get_knowledge_base', 'search_knowledge_base',
    'SearchTool', 'WebpageTool', 'LinkPreviewTool',
    'KnowledgeBaseSearchTool', 'get_kb_search_tool',
    'IntentClassifier', 'get_intent_classifier', 'reload_intent_classifier', 'intent_classifier',
]
