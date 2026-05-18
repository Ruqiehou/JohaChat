"""
链接预览工具 - 元信息与函数式入口
"""
from .core import LinkPreviewTool

TOOL_META = {
    "name": "link_preview",
    "description": "提取网页的Open Graph元数据，生成链接预览卡片（标题、描述、图片）",
    "category": "web",
    "aliases": ["preview", "lp"],
    "parameters": {
        "url": {
            "type": "str",
            "description": "要预览的网页URL",
            "required": True,
        },
    },
    "examples": ["/preview https://github.com"],
}


def execute(url: str) -> str:
    """函数式入口：生成链接预览"""
    return LinkPreviewTool().format_preview(url)
