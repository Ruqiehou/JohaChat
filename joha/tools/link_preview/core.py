"""
链接预览工具 - 核心实现
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import urlparse


class LinkPreviewTool:
    """链接预览工具类"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def preview(self, url: str) -> Dict[str, Optional[str]]:
        try:
            if not self._is_valid_url(url):
                return {'error': f'无效的 URL: {url}'}

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            preview_data = {
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'image': self._extract_image(soup, url),
                'site_name': self._extract_site_name(soup),
                'url': url
            }
            return preview_data

        except requests.exceptions.Timeout:
            return {'error': f'请求超时: {url}'}
        except requests.exceptions.ConnectionError:
            return {'error': f'连接失败: {url}'}
        except Exception as e:
            return {'error': f'预览失败: {str(e)}'}

    def format_preview(self, url: str) -> str:
        data = self.preview(url)
        if 'error' in data:
            return data['error']

        lines = []
        if data.get('title'):
            lines.append(f"标题: {data['title']}")
        if data.get('description'):
            desc = data['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            lines.append(f"   {desc}")
        if data.get('site_name'):
            lines.append(f"  站点: {data['site_name']}")
        lines.append(f"  链接: {data['url']}")
        return "\n".join(lines)

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        return None

    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content'].strip()
            return self._resolve_url(image_url, base_url)
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            image_url = twitter_image['content'].strip()
            return self._resolve_url(image_url, base_url)
        return None

    def _extract_site_name(self, soup: BeautifulSoup) -> Optional[str]:
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            return og_site['content'].strip()
        try:
            parsed = urlparse(self._get_base_url(soup))
            return parsed.netloc
        except:
            return None

    def _resolve_url(self, image_url: str, base_url: str) -> str:
        if image_url.startswith('http'):
            return image_url
        from urllib.parse import urljoin
        return urljoin(base_url, image_url)

    def _get_base_url(self, soup: BeautifulSoup) -> str:
        base_tag = soup.find('base', href=True)
        if base_tag:
            return base_tag['href']
        return ''

    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
