"""
工具模块 - 搜索、网页抓取、链接预览和知识库搜索
支持双模式：旧式类风格 + 新式函数+元信息风格
"""
from .search import SearchTool, TOOL_META as SEARCH_META, execute as search_execute
from .webpage import WebpageTool, TOOL_META as WEBPAGE_META, execute as webpage_execute
from .link_preview import LinkPreviewTool, TOOL_META as LINK_META, execute as link_execute
from .knowledge_search import (
    KnowledgeBaseSearchTool, get_kb_search_tool, kb_search_tool,
    TOOL_META as KB_META, execute as kb_execute,
)

# 全局工具实例（向后兼容）
search_tool = SearchTool()
webpage_tool = WebpageTool()
link_preview_tool = LinkPreviewTool()

# 新式工具元信息列表（供 ToolRegistry 自动发现）
__tool_metas__ = [SEARCH_META, WEBPAGE_META, LINK_META, KB_META]

__all__ = [
    # 类名
    'SearchTool', 'WebpageTool', 'LinkPreviewTool', 'KnowledgeBaseSearchTool',
    # 函数名
    'search_execute', 'webpage_execute', 'link_execute', 'kb_execute',
    # 元信息
    'SEARCH_META', 'WEBPAGE_META', 'LINK_META', 'KB_META',
    # 实例
    'search_tool', 'webpage_tool', 'link_preview_tool', 'kb_search_tool',
    'get_kb_search_tool',
]
