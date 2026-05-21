"""
搜索引擎工具 - 核心实现
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

    def _summarize_with_ai(self, query: str, content: str) -> str:
        """使用主 LLM 对搜索内容进行智能总结"""
        try:
            from joha.ai.generator import generator
            
            # 限制内容长度
            if len(content) > 2000:
                content = content[:2000] + "..."
            
            prompt = f"请对以下关于'{query}'的搜索结果进行简洁明了的总结:\n\n{content}\n\n总结:"
            
            # 调用LLM进行总结
            summary = generator.chat_sync(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return summary if summary else content
        except Exception as e:
            # 如果AI总结失败，返回原始内容
            return content

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

            # 获取原始结果
            raw_results = self._format_results(results)
            
            # 使用AI进行智能总结
            summarized_content = self._summarize_with_ai(query, raw_results)
            
            return f"🔍 搜索结果总结:\n{summarized_content}"
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
            
            # 获取原始结果
            raw_results = self._format_results(results)
            
            # 使用AI进行智能总结
            summarized_content = self._summarize_with_ai(query, raw_results)
            
            return f"🔍 搜索结果总结:\n{summarized_content}"
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
            
            # 获取原始结果
            raw_results = self._format_results(results)
            
            # 使用AI进行智能总结
            summarized_content = self._summarize_with_ai(query, raw_results)
            
            return f"🔍 搜索结果总结:\n{summarized_content}"
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
