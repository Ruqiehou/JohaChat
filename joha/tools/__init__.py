"""
工具模块 - 搜索、网页抓取
支持双模式：旧式类风格 + 新式函数+元信息风格
"""
from .search.core import SearchTool
from .search.tool import TOOL_META as SEARCH_META, execute as search_execute
from .webpage.core import WebpageTool
from .webpage.tool import TOOL_META as WEBPAGE_META, execute as webpage_execute

# 全局工具实例（向后兼容）
search_tool = SearchTool()
webpage_tool = WebpageTool()

# 新式工具元信息列表（供 ToolRegistry 自动发现）
__tool_metas__ = [SEARCH_META, WEBPAGE_META]

__all__ = [
    # 类名
    'SearchTool', 'WebpageTool',
    # 函数名
    'search_execute', 'webpage_execute',
    # 元信息
    'SEARCH_META', 'WEBPAGE_META',
    # 实例
    'search_tool', 'webpage_tool',
]
