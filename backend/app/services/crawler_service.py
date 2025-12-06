"""
爬虫服务 - 数据采集核心逻辑
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import re
import urllib.parse


class CrawlerService:
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.timeout = 15
    
    async def search_bing(self, keyword: str, count: int = 20) -> List[Dict]:
        """Bing搜索采集"""
        results = []
        try:
            url = f"https://cn.bing.com/search?q={urllib.parse.quote(keyword)}&count={count}"
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    items = soup.select(".b_algo")
                    for item in items:
                        try:
                            title_elem = item.select_one("h2 a")
                            if not title_elem:
                                continue
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get("href", "")
                            summary_elem = item.select_one(".b_caption p")
                            summary = summary_elem.get_text(strip=True) if summary_elem else ""
                            results.append({
                                "title": title,
                                "source_url": link,
                                "summary": summary,
                                "source_name": "Bing",
                                "cover_url": None
                            })
                        except Exception:
                            continue
        except Exception as e:
            print(f"Bing search error: {e}")
        return results

    async def search_sogou(self, keyword: str, page: int = 1) -> List[Dict]:
        """搜狗搜索采集"""
        results = []
        try:
            url = f"https://www.sogou.com/web?query={urllib.parse.quote(keyword)}&page={page}"
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    items = soup.select(".vrwrap, .rb")
                    for item in items:
                        try:
                            title_elem = item.select_one("h3 a, .vr-title a")
                            if not title_elem:
                                continue
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get("href", "")
                            summary_elem = item.select_one(".str_info, .space-txt")
                            summary = summary_elem.get_text(strip=True) if summary_elem else ""
                            results.append({
                                "title": title,
                                "source_url": link,
                                "summary": summary,
                                "source_name": "Sogou",
                                "cover_url": None
                            })
                        except Exception:
                            continue
        except Exception as e:
            print(f"Sogou search error: {e}")
        return results

    async def crawl_all(self, keyword: str) -> List[Dict]:
        """综合采集 - 从多个来源采集数据"""
        all_results = []
        
        # 并发采集多个来源
        tasks = [
            self.search_bing(keyword, 15),
            self.search_sogou(keyword, 1),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
        
        # 去重
        seen_urls = set()
        unique_results = []
        for item in all_results:
            url = item.get("source_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(item)
        
        return unique_results

    async def deep_crawl(self, url: str) -> Dict:
        """深度采集 - 获取页面详细内容"""
        result = {"content": None, "cover_url": None, "success": False}
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # 提取正文内容
                    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                        tag.decompose()
                    
                    # 尝试获取文章主体
                    article = soup.select_one("article, .article, .content, .post, main")
                    if article:
                        content = article.get_text(separator="\n", strip=True)
                    else:
                        body = soup.find("body")
                        content = body.get_text(separator="\n", strip=True) if body else ""
                    
                    # 清理内容
                    lines = [line.strip() for line in content.split("\n") if line.strip()]
                    content = "\n".join(lines[:100])  # 限制行数
                    
                    # 提取封面图
                    og_image = soup.select_one('meta[property="og:image"]')
                    if og_image:
                        result["cover_url"] = og_image.get("content")
                    else:
                        first_img = soup.select_one("article img, .content img, main img")
                        if first_img:
                            result["cover_url"] = first_img.get("src")
                    
                    result["content"] = content[:5000]  # 限制长度
                    result["success"] = True
        except Exception as e:
            print(f"Deep crawl error: {e}")
        
        return result


# 全局实例
crawler_service = CrawlerService()
