"""
知乎爬虫
支持：
- 关键词搜索
- 问题回答
- 热榜
- 话题
"""
import json
import logging
from typing import Iterator, Dict, Any
from urllib.parse import urlencode, quote

from scrapy.http import Request, Response

from project.items import ZhihuItem, CommentItem
from project.spiders.base_spider import BaseSpider

logger = logging.getLogger(__name__)


class ZhihuSpider(BaseSpider):
    """知乎爬虫"""
    
    name = "zhihu"
    platform = "zhihu"
    
    allowed_domains = ["zhihu.com", "www.zhihu.com"]
    
    # API端点
    SEARCH_API = "https://www.zhihu.com/api/v4/search_v3"
    QUESTION_API = "https://www.zhihu.com/api/v4/questions/{qid}/feeds"
    ANSWERS_API = "https://www.zhihu.com/api/v4/questions/{qid}/answers"
    HOT_LIST_API = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
    TOPIC_API = "https://www.zhihu.com/api/v4/topics/{tid}/feeds/essence"
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }
    
    # 请求头
    DEFAULT_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.zhihu.com/",
        "x-requested-with": "fetch",
    }
    
    def __init__(
        self,
        keywords: str = None,
        question_ids: str = None,
        topic_ids: str = None,
        hot_list: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(keywords=keywords, *args, **kwargs)
        
        self.question_ids = []
        if question_ids:
            self.question_ids = [qid.strip() for qid in question_ids.split(",") if qid.strip()]
        
        self.topic_ids = []
        if topic_ids:
            self.topic_ids = [tid.strip() for tid in topic_ids.split(",") if tid.strip()]
        
        self.hot_list = hot_list
    
    def start_requests(self) -> Iterator[Request]:
        """生成初始请求"""
        # 关键词搜索
        for keyword in self.keywords:
            yield self._make_search_request(keyword, offset=0)
        
        # 问题回答
        for qid in self.question_ids:
            yield self._make_answers_request(qid, offset=0)
        
        # 话题
        for tid in self.topic_ids:
            yield self._make_topic_request(tid, offset=0)
        
        # 热榜
        if self.hot_list:
            yield self._make_hot_list_request()
    
    def _make_search_request(self, keyword: str, offset: int = 0) -> Request:
        """构建搜索请求"""
        params = {
            "gk_version": "gz-gaokao",
            "t": "general",
            "q": keyword,
            "correction": 1,
            "offset": offset,
            "limit": 20,
            "filter_fields": "",
            "lc_idx": offset,
            "show_all_topics": 0,
            "search_source": "Normal",
        }
        
        url = f"{self.SEARCH_API}?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_search,
            headers=self.DEFAULT_HEADERS,
            meta={
                "keyword": keyword,
                "offset": offset,
            },
        )
    
    def _make_answers_request(self, question_id: str, offset: int = 0) -> Request:
        """构建问题回答请求"""
        params = {
            "include": "data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,"
                      "annotation_action,annotation_detail,collapse_reason,is_sticky,"
                      "collapsed_by,suggest_edit,comment_count,can_comment,content,"
                      "editable_content,attachment,voteup_count,reshipment_settings,"
                      "comment_permission,created_time,updated_time,review_info,"
                      "relevant_info,question,excerpt,is_labeled,paid_info,paid_info_content,"
                      "relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,"
                      "is_recognized;data[*].mark_infos[*].url;data[*].author.follower_count,"
                      "vip_info,badge[*].topics;data[*].settings.table_of_content.enabled",
            "offset": offset,
            "limit": 20,
            "sort_by": "default",
            "platform": "desktop",
        }
        
        url = self.ANSWERS_API.format(qid=question_id) + f"?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_answers,
            headers=self.DEFAULT_HEADERS,
            meta={
                "question_id": question_id,
                "offset": offset,
            },
        )
    
    def _make_topic_request(self, topic_id: str, offset: int = 0) -> Request:
        """构建话题请求"""
        params = {
            "include": "data[*].comment_count,suggest_edit,is_normal,thumbnail_extra_info,"
                      "thumbnail,can_comment,comment_permission,admin_closed_comment,"
                      "content,voteup_count,created,updated,upvoted_followees,voting,"
                      "review_info,is_labeled,label_info;data[*].author.badge[?(type=best_answerer)].topics",
            "offset": offset,
            "limit": 10,
        }
        
        url = self.TOPIC_API.format(tid=topic_id) + f"?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_topic,
            headers=self.DEFAULT_HEADERS,
            meta={
                "topic_id": topic_id,
                "offset": offset,
            },
        )
    
    def _make_hot_list_request(self) -> Request:
        """构建热榜请求"""
        params = {
            "limit": 50,
        }
        
        url = f"{self.HOT_LIST_API}?{urlencode(params)}"
        
        return self.make_request(
            url=url,
            callback=self.parse_hot_list,
            headers=self.DEFAULT_HEADERS,
        )
    
    def parse_search(self, response: Response) -> Iterator:
        """解析搜索结果"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response.url}")
            return
        
        keyword = response.meta["keyword"]
        offset = response.meta["offset"]
        
        results = data.get("data", [])
        
        for item in results:
            obj_type = item.get("type")
            obj = item.get("object", {})
            
            if obj_type == "search_result":
                # 搜索结果可能是回答、文章等
                yield from self._parse_search_object(obj, keyword)
        
        # 翻页
        paging = data.get("paging", {})
        if not paging.get("is_end", True) and offset < 200:
            yield self._make_search_request(keyword, offset + 20)
    
    def _parse_search_object(self, obj: Dict[str, Any], keyword: str) -> Iterator:
        """解析搜索对象"""
        obj_type = obj.get("type")
        
        if obj_type == "answer":
            yield from self._parse_answer(obj, keyword)
        elif obj_type == "article":
            yield from self._parse_article(obj, keyword)
        elif obj_type == "question":
            # 获取问题的回答
            qid = obj.get("id")
            if qid:
                yield self._make_answers_request(str(qid), offset=0)
    
    def parse_answers(self, response: Response) -> Iterator:
        """解析问题回答"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response.url}")
            return
        
        question_id = response.meta["question_id"]
        offset = response.meta["offset"]
        
        answers = data.get("data", [])
        
        for answer in answers:
            yield from self._parse_answer(answer)
        
        # 翻页
        paging = data.get("paging", {})
        if not paging.get("is_end", True) and offset < 100:
            yield self._make_answers_request(question_id, offset + 20)
    
    def parse_topic(self, response: Response) -> Iterator:
        """解析话题内容"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return
        
        topic_id = response.meta["topic_id"]
        offset = response.meta["offset"]
        
        items = data.get("data", [])
        
        for item in items:
            target = item.get("target", {})
            if target.get("type") == "answer":
                yield from self._parse_answer(target)
        
        # 翻页
        paging = data.get("paging", {})
        if not paging.get("is_end", True) and offset < 100:
            yield self._make_topic_request(topic_id, offset + 10)
    
    def parse_hot_list(self, response: Response) -> Iterator:
        """解析热榜"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return
        
        items = data.get("data", [])
        
        for item in items:
            target = item.get("target", {})
            qid = target.get("id")
            
            if qid:
                # 获取热榜问题的回答
                yield self._make_answers_request(str(qid), offset=0)
    
    def _parse_answer(self, answer: Dict[str, Any], keyword: str = None) -> Iterator:
        """解析单个回答"""
        answer_id = answer.get("id")
        if not answer_id:
            return
        
        # 问题信息
        question = answer.get("question", {})
        question_id = question.get("id", "")
        question_title = question.get("title", "")
        
        # 内容
        content = answer.get("content", "") or answer.get("excerpt", "")
        # 简单清理HTML
        import re
        content_clean = re.sub(r"<[^>]+>", "", content)
        
        # 关键词匹配
        text_to_match = f"{question_title} {content_clean}"
        matched = self.get_matched_keywords(text_to_match)
        if keyword and not matched:
            matched = [keyword] if keyword.lower() in text_to_match.lower() else []
        
        # 作者信息
        author = answer.get("author", {})
        
        # 话题
        topics = []
        if question.get("topics"):
            topics = [t.get("name", "") for t in question.get("topics", [])]
        
        item = ZhihuItem(
            platform="zhihu",
            content_id=str(answer_id),
            url=f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}",
            
            content=content_clean,
            title=question_title,
            content_type="answer",
            excerpt=answer.get("excerpt", ""),
            
            question_id=str(question_id),
            question_title=question_title,
            answer_id=str(answer_id),
            
            author_id=author.get("id", ""),
            author_name=author.get("name", ""),
            author_avatar=author.get("avatar_url", ""),
            author_followers=author.get("follower_count", 0),
            
            upvotes=answer.get("voteup_count", 0),
            likes=answer.get("voteup_count", 0),
            thanks=answer.get("thanks_count", 0),
            comments=answer.get("comment_count", 0),
            
            publish_time=self._timestamp_to_iso(answer.get("created_time")),
            
            is_collapsed=answer.get("is_collapsed", False),
            topics=topics,
            
            matched_keywords=matched,
        )
        
        yield item
    
    def _parse_article(self, article: Dict[str, Any], keyword: str = None) -> Iterator:
        """解析文章"""
        article_id = article.get("id")
        if not article_id:
            return
        
        title = article.get("title", "")
        content = article.get("content", "") or article.get("excerpt", "")
        
        import re
        content_clean = re.sub(r"<[^>]+>", "", content)
        
        text_to_match = f"{title} {content_clean}"
        matched = self.get_matched_keywords(text_to_match)
        if keyword and not matched:
            matched = [keyword] if keyword.lower() in text_to_match.lower() else []
        
        author = article.get("author", {})
        
        item = ZhihuItem(
            platform="zhihu",
            content_id=str(article_id),
            url=f"https://zhuanlan.zhihu.com/p/{article_id}",
            
            content=content_clean,
            title=title,
            content_type="article",
            excerpt=article.get("excerpt", ""),
            
            author_id=author.get("id", ""),
            author_name=author.get("name", ""),
            author_avatar=author.get("avatar_url", ""),
            author_followers=author.get("follower_count", 0),
            
            upvotes=article.get("voteup_count", 0),
            likes=article.get("voteup_count", 0),
            comments=article.get("comment_count", 0),
            
            publish_time=self._timestamp_to_iso(article.get("created")),
            
            matched_keywords=matched,
        )
        
        yield item
    
    def _timestamp_to_iso(self, timestamp) -> str:
        """时间戳转ISO格式"""
        if not timestamp:
            return None
        
        from datetime import datetime
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.isoformat()
        except (ValueError, TypeError, OSError):
            return None
