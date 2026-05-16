"""
网页抓取工具
支持提取网页内容
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse


class WebpageTool:
    """网页抓取工具类"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch(self, url: str, max_length: int = 3000) -> str:
        try:
            if not self._is_valid_url(url):
                return f"无效的 URL: {url}"

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            text = soup.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)

            if len(cleaned_text) > max_length:
                cleaned_text = cleaned_text[:max_length] + "\n\n[内容过长，已截断...]"

            return cleaned_text if cleaned_text else "未提取到有效内容"

        except requests.exceptions.Timeout:
            return f"请求超时: {url}"
        except requests.exceptions.ConnectionError:
            return f"连接失败: {url}"
        except Exception as e:
            return f"抓取失败: {str(e)}"

    def fetch_title(self, url: str) -> str:
        try:
            if not self._is_valid_url(url):
                return f"无效的 URL: {url}"

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "无标题"
            return title.strip()
        except Exception as e:
            return f"获取标题失败: {str(e)}"

    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False


# ========== 新式函数+元信息模式（供 ToolRegistry 自动发现） ==========

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
