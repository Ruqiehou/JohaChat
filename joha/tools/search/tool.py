"""
搜索工具 - 元信息与函数式入口
"""
from .core import SearchTool

TOOL_META = {
    "name": "search",
    "description": "搜索互联网获取实时信息，如新闻、天气、百科等",
    "category": "web",
    "aliases": ["s", "web_search"],
    "parameters": {
        "query": {
            "type": "str",
            "description": "搜索关键词",
            "required": True,
        },
        "num_results": {
            "type": "int",
            "description": "返回结果数量，默认5",
            "required": False,
        },
    },
    "examples": ["/search 今天天气", "/s Python教程"],
}


def execute(query: str, num_results: int = 5) -> str:
    """函数式入口：搜索互联网"""
    return SearchTool().search(query, num_results)
