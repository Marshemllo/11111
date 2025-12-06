"""
Items模块测试
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from project.items import (
    BaseItem,
    WeiboItem,
    ZhihuItem,
    DouyinItem,
    CommentItem,
)


class TestBaseItem:
    """BaseItem测试"""
    
    def test_create_item(self):
        """测试创建Item"""
        item = BaseItem()
        
        item["platform"] = "test"
        item["content_id"] = "123"
        item["content"] = "测试内容"
        
        assert item["platform"] == "test"
        assert item["content_id"] == "123"
    
    def test_all_fields(self):
        """测试所有字段"""
        item = BaseItem()
        
        # 设置所有字段
        item["platform"] = "weibo"
        item["content_id"] = "123"
        item["url"] = "https://example.com"
        item["content"] = "内容"
        item["title"] = "标题"
        item["content_type"] = "post"
        item["images"] = ["img1.jpg"]
        item["videos"] = []
        item["author_id"] = "user1"
        item["author_name"] = "用户1"
        item["likes"] = 100
        item["comments"] = 50
        item["shares"] = 20
        item["sentiment"] = "positive"
        item["sentiment_score"] = 0.8
        item["matched_keywords"] = ["关键词1"]
        
        assert len(dict(item)) > 0


class TestWeiboItem:
    """WeiboItem测试"""
    
    def test_weibo_specific_fields(self):
        """测试微博特有字段"""
        item = WeiboItem()
        
        item["mid"] = "4900000000000000"
        item["bid"] = "Lxxxxxxx"
        item["reposts"] = 100
        item["attitudes"] = 200
        item["source"] = "iPhone客户端"
        item["is_retweet"] = False
        item["topics"] = ["话题1", "话题2"]
        item["at_users"] = ["用户1"]
        item["location"] = "北京"
        
        assert item["mid"] == "4900000000000000"
        assert item["topics"] == ["话题1", "话题2"]


class TestZhihuItem:
    """ZhihuItem测试"""
    
    def test_zhihu_specific_fields(self):
        """测试知乎特有字段"""
        item = ZhihuItem()
        
        item["question_id"] = "123456"
        item["question_title"] = "这是一个问题？"
        item["answer_id"] = "789"
        item["upvotes"] = 1000
        item["thanks"] = 50
        item["is_collapsed"] = False
        item["excerpt"] = "摘要内容"
        item["topics"] = ["科技", "互联网"]
        
        assert item["question_id"] == "123456"
        assert item["upvotes"] == 1000


class TestDouyinItem:
    """DouyinItem测试"""
    
    def test_douyin_specific_fields(self):
        """测试抖音特有字段"""
        item = DouyinItem()
        
        item["aweme_id"] = "7000000000000000000"
        item["desc"] = "视频描述 #话题"
        item["duration"] = 15000
        item["music_id"] = "music123"
        item["music_title"] = "背景音乐"
        item["digg_count"] = 10000
        item["collect_count"] = 500
        item["download_count"] = 100
        item["hashtags"] = ["话题1"]
        
        assert item["aweme_id"] == "7000000000000000000"
        assert item["duration"] == 15000


class TestCommentItem:
    """CommentItem测试"""
    
    def test_comment_fields(self):
        """测试评论字段"""
        item = CommentItem()
        
        item["platform"] = "weibo"
        item["content_id"] = "post123"
        item["comment_id"] = "comment456"
        item["parent_id"] = None
        item["content"] = "评论内容"
        item["author_id"] = "user1"
        item["author_name"] = "用户1"
        item["likes"] = 10
        item["replies"] = 2
        
        assert item["comment_id"] == "comment456"
        assert item["parent_id"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
