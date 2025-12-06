"""
微博爬虫
支持：
- 关键词搜索
- 用户微博
- 话题微博
- 评论采集
"""
import json
import re
import logging
from typing import Iterator, Dict, Any
from urllib.parse import urlencode, quote

from scrapy.http import Request, Response

from project.items import WeiboItem, CommentItem
from project.spiders.base_spider import BaseSpider

logger = logging.getLogger(__name__)


class WeiboSpider(BaseSpider):
    """微博爬虫"""
    
    name = "weibo"
    platform = "weibo"
    
    allowed_domains = ["weibo.com", "weibo.cn", "m.weibo.cn"]
    
    # API端点
    SEARCH_API = "https://m.weibo.cn/api/container/getIndex"
    USER_API = "https://m.weibo.cn/api/container/getIndex"
    COMMENTS_API = "https://m.weibo.cn/comments/hotflow"
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }
    
    def __init__(self, keywords: str = None, user_ids: str = None, *args, **kwargs):
        super().__init__(keywords=keywords, *args, **kwargs)
        
        # 用户ID列表
        self.user_ids = []
        if user_ids:
            self.user_ids = [uid.strip() for uid in user_ids.split(",") if uid.strip()]
    
    def start_requests(self) -> Iterator[Request]:
        """生成初始请求"""
        # 关键词搜索
        for keyword in self.keywords:
            yield self._make_search_request(keyword, page=1)
        
        # 用户微博
        for user_id in self.user_ids:
            yield self._make_user_request(user_id, page=1)
    
    def _make_search_request(self, keyword: str, page: int = 1) -> Request:
        """构建搜索请求"""
        # containerid格式: 100103type=1&q=关键词
        containerid = f"100103type=1&q={quote(keyword)}"
        
        params = {
            "containerid": containerid,
            "page_type": "searchall",
            "page": page,
        }
        
        url = f"{self.SEARCH_API}?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_search,
            meta={
                "keyword": keyword,
                "page": page,
            },
        )
    
    def _make_user_request(self, user_id: str, page: int = 1) -> Request:
        """构建用户微博请求"""
        # containerid格式: 107603用户ID
        containerid = f"107603{user_id}"
        
        params = {
            "containerid": containerid,
            "page": page,
        }
        
        url = f"{self.USER_API}?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_user,
            meta={
                "user_id": user_id,
                "page": page,
            },
        )
    
    def parse_search(self, response: Response) -> Iterator:
        """解析搜索结果"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response.url}")
            return
        
        if data.get("ok") != 1:
            logger.warning(f"Search API error: {data.get('msg')}")
            return
        
        cards = data.get("data", {}).get("cards", [])
        keyword = response.meta["keyword"]
        page = response.meta["page"]
        
        for card in cards:
            # card_type 9 是微博卡片
            if card.get("card_type") == 9:
                mblog = card.get("mblog", {})
                yield from self._parse_mblog(mblog, keyword)
            
            # card_group 包含多条微博
            elif card.get("card_group"):
                for item in card["card_group"]:
                    if item.get("card_type") == 9:
                        mblog = item.get("mblog", {})
                        yield from self._parse_mblog(mblog, keyword)
        
        # 翻页
        if cards and page < 50:  # 最多50页
            yield self._make_search_request(keyword, page + 1)
    
    def parse_user(self, response: Response) -> Iterator:
        """解析用户微博"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response.url}")
            return
        
        if data.get("ok") != 1:
            return
        
        cards = data.get("data", {}).get("cards", [])
        user_id = response.meta["user_id"]
        page = response.meta["page"]
        
        for card in cards:
            if card.get("card_type") == 9:
                mblog = card.get("mblog", {})
                yield from self._parse_mblog(mblog)
        
        # 翻页
        if cards and page < 20:
            yield self._make_user_request(user_id, page + 1)
    
    def _parse_mblog(self, mblog: Dict[str, Any], keyword: str = None) -> Iterator:
        """解析单条微博"""
        if not mblog:
            return
        
        mid = mblog.get("mid") or mblog.get("id")
        if not mid:
            return
        
        # 提取文本内容
        text = mblog.get("text", "")
        # 清理HTML
        text_clean = re.sub(r"<[^>]+>", "", text)
        
        # 检查关键词匹配
        matched = self.get_matched_keywords(text_clean)
        if keyword and not matched:
            matched = [keyword] if keyword.lower() in text_clean.lower() else []
        
        # 用户信息
        user = mblog.get("user", {}) or {}
        
        # 图片
        pics = mblog.get("pics", []) or []
        images = [pic.get("large", {}).get("url") or pic.get("url") for pic in pics]
        
        # 话题
        topics = re.findall(r"#([^#]+)#", text_clean)
        
        # @用户
        at_users = re.findall(r"@([^\s:：]+)", text_clean)
        
        item = WeiboItem(
            platform="weibo",
            content_id=str(mid),
            mid=str(mid),
            bid=mblog.get("bid"),
            url=f"https://m.weibo.cn/detail/{mid}",
            
            content=text_clean,
            content_type="post",
            
            images=images,
            videos=[],
            
            author_id=str(user.get("id", "")),
            author_name=user.get("screen_name", ""),
            author_avatar=user.get("profile_image_url", ""),
            author_followers=user.get("followers_count", 0),
            author_verified=user.get("verified", False),
            
            likes=mblog.get("attitudes_count", 0),
            attitudes=mblog.get("attitudes_count", 0),
            comments=mblog.get("comments_count", 0),
            reposts=mblog.get("reposts_count", 0),
            shares=mblog.get("reposts_count", 0),
            
            publish_time=self.parse_time(mblog.get("created_at", "")),
            
            source=mblog.get("source", ""),
            is_retweet=bool(mblog.get("retweeted_status")),
            retweet_id=str(mblog.get("retweeted_status", {}).get("mid", "")) if mblog.get("retweeted_status") else None,
            
            topics=topics,
            at_users=at_users,
            location=mblog.get("region_name", ""),
            
            matched_keywords=matched,
        )
        
        yield item
        
        # 采集评论
        if mblog.get("comments_count", 0) > 0:
            yield self._make_comments_request(mid)
    
    def _make_comments_request(self, mid: str, max_id: str = None) -> Request:
        """构建评论请求"""
        params = {
            "id": mid,
            "mid": mid,
            "max_id_type": 0,
        }
        if max_id:
            params["max_id"] = max_id
        
        url = f"{self.COMMENTS_API}?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_comments,
            meta={"mid": mid},
        )
    
    def parse_comments(self, response: Response) -> Iterator:
        """解析评论"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return
        
        if data.get("ok") != 1:
            return
        
        mid = response.meta["mid"]
        comments_data = data.get("data", {})
        comments = comments_data.get("data", [])
        
        for comment in comments:
            comment_id = comment.get("id")
            if not comment_id:
                continue
            
            user = comment.get("user", {}) or {}
            text = re.sub(r"<[^>]+>", "", comment.get("text", ""))
            
            yield CommentItem(
                platform="weibo",
                content_id=str(mid),
                comment_id=str(comment_id),
                parent_id=str(comment.get("rootid", "")) if comment.get("rootid") else None,
                
                content=text,
                author_id=str(user.get("id", "")),
                author_name=user.get("screen_name", ""),
                
                likes=comment.get("like_count", 0),
                replies=comment.get("total_number", 0),
                
                publish_time=self.parse_time(comment.get("created_at", "")),
            )
        
        # 翻页
        max_id = comments_data.get("max_id")
        if max_id and max_id != 0:
            yield self._make_comments_request(mid, str(max_id))
