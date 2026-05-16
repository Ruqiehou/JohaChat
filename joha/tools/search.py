"""
搜索引擎工具
支持多种搜索引擎 API
"""
import requests
from typing import List, Dict, Optional


class SearchTool:
    """搜索引擎工具类"""

    def __init__(self, api_key: str = "", engine: str = "duckduckgo"):
        self.api_key = api_key
        self.engine = engine

    def search(self, query: str, num_results: int = 5) -> str:
        try:
            if self.engine == "duckduckgo":
                return self._duckduckgo_search(query, num_results)
            elif self.engine == "google":
                return self._google_search(query, num_results)
            elif self.engine == "bing":
                return self._bing_search(query, num_results)
            else:
                return f"不支持的搜索引擎: {self.engine}"
        except Exception as e:
            return f"搜索失败: {str(e)}"

    def _duckduckgo_search(self, query: str, num_results: int = 5) -> str:
        try:
            from ddgs import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', '')
                    })

            return self._format_results(results)
        except ImportError:
            return "请安装 ddgs: pip install ddgs"
        except Exception as e:
            return f"DuckDuckGo 搜索失败: {str(e)}"

    def _google_search(self, query: str, num_results: int = 5) -> str:
        if not self.api_key:
            return "Google 搜索需要 API Key"
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': 'YOUR_CUSTOM_SEARCH_ENGINE_ID',
                'q': query,
                'num': num_results
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            return self._format_results(results)
        except Exception as e:
            return f"Google 搜索失败: {str(e)}"

    def _bing_search(self, query: str, num_results: int = 5) -> str:
        if not self.api_key:
            return "Bing 搜索需要 API Key"
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            params = {'q': query, 'count': num_results}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', '')
                })
            return self._format_results(results)
        except Exception as e:
            return f"Bing 搜索失败: {str(e)}"

    def _format_results(self, results: List[Dict]) -> str:
        if not results:
            return "未找到相关结果"
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result['title']}\n"
                f"   链接: {result['url']}\n"
                f"   摘要: {result['snippet'][:200]}"
            )
        return "\n\n".join(formatted)


# ========== 新式函数+元信息模式（供 ToolRegistry 自动发现） ==========

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
