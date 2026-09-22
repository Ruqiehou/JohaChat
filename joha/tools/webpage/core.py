"""
网页抓取工具 - 核心实现
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
            
            # 检查协议
            if not all([result.scheme, result.netloc]) or result.scheme not in ['http', 'https']:
                return False
            
            # 获取主机名并检查是否为内网地址
            hostname = result.hostname
            if not hostname:
                return False
            
            # 禁止访问内网地址和回环地址
            import ipaddress
            try:
                # 尝试解析为 IP 地址
                ip = ipaddress.ip_address(hostname)
                # 检查是否为私有地址或回环地址
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
            except ValueError:
                # 不是 IP 地址，是域名
                # 禁止访问 localhost 相关域名
                if hostname.lower() in ['localhost', '127.0.0.1', '::1', '0.0.0.0']:
                    return False
            
            return True
        except Exception:
            return False
