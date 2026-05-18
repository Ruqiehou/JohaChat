"""
知识库搜索工具 - 元信息与函数式入口
"""
from .core import get_kb_search_tool

TOOL_META = {
    "name": "knowledge",
    "description": "搜索本地知识库获取历史对话和知识，用于查找项目相关历史信息、过往讨论",
    "category": "knowledge",
    "aliases": ["kb", "mem", "记忆"],
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
    "examples": ["/knowledge 项目架构", "/kb 数据库设计"],
}


def execute(query: str, num_results: int = 5) -> str:
    """函数式入口：搜索知识库"""
    return get_kb_search_tool().search(query, num_results)
