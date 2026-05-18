# 知识库模块 - 核心引擎 + 搜索工具 + 函数式入口
from .core import KnowledgeBase, get_knowledge_base, search_knowledge_base
from .core import KnowledgeBaseSearchTool, get_kb_search_tool, kb_search_tool
from .tool import TOOL_META, execute

__all__ = [
    'KnowledgeBase', 'get_knowledge_base', 'search_knowledge_base',
    'KnowledgeBaseSearchTool', 'get_kb_search_tool', 'kb_search_tool',
    'TOOL_META', 'execute',
]
