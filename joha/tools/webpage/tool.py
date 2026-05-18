"""
网页抓取工具 - 元信息与函数式入口
"""
from .core import WebpageTool

TOOL_META = {
    "name": "webpage",
    "description": "抓取并提取网页内容，当用户提供URL或需要查看具体网页内容时使用",
    "category": "web",
    "aliases": ["wp", "fetch"],
    "parameters": {
        "url": {
            "type": "str",
            "description": "要抓取的网页URL",
            "required": True,
        },
    },
    "examples": ["/webpage https://example.com", "/wp https://baidu.com"],
}


def execute(url: str) -> str:
    """函数式入口：抓取网页内容"""
    return WebpageTool().fetch(url)
