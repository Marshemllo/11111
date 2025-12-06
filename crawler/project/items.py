"""
统一数据字段定义
支持微博、知乎、抖音等多平台数据采集
"""
import scrapy
from scrapy import Field


class BaseItem(scrapy.Item):
    """基础Item - 所有平台共用字段"""
    # 平台标识
    platform = Field()          # weibo/zhihu/douyin/toutiao
    
    # 内容标识
    content_id = Field()        # 平台原始ID
    url = Field()               # 原始链接
    
    # 内容主体
    content = Field()           # 正文内容
    title = Field()             # 标题（如有）
    content_type = Field()      # post/comment/article/video
    
    # 媒体资源
    images = Field()            # 图片URL列表
    videos = Field()            # 视频URL列表
    
    # 作者信息
    author_id = Field()         # 作者ID
    author_name = Field()       # 作者昵称
    author_avatar = Field()     # 作者头像
    author_followers = Field()  # 粉丝数
    author_verified = Field()   # 是否认证
    
    # 互动数据
    likes = Field()             # 点赞数
    comments = Field()          # 评论数
    shares = Field()            # 转发/分享数
    views = Field()             # 阅读/播放量
    
    # 时间信息
    publish_time = Field()      # 发布时间
    crawl_time = Field()        # 采集时间
    
    # 情感分析
    sentiment = Field()         # positive/negative/neutral
    sentiment_score = Field()   # 情感分数 [-1, 1]
    
    # 关键词匹配
    matched_keywords = Field()  # 匹配到的关键词列表
    
    # 扩展字段
    extra = Field()             # 平台特有字段（JSON）


class WeiboItem(BaseItem):
    """微博Item"""
    # 微博特有字段
    mid = Field()               # 微博mid
    bid = Field()               # 微博bid
    reposts = Field()           # 转发数
    attitudes = Field()         # 态度数（赞）
    source = Field()            # 来源设备
    is_retweet = Field()        # 是否转发
    retweet_id = Field()        # 原微博ID
    topics = Field()            # 话题列表
    at_users = Field()          # @用户列表
    location = Field()          # 发布位置
    

class ZhihuItem(BaseItem):
    """知乎Item"""
    # 知乎特有字段
    question_id = Field()       # 问题ID
    question_title = Field()    # 问题标题
    answer_id = Field()         # 回答ID
    upvotes = Field()           # 赞同数
    thanks = Field()            # 感谢数
    is_collapsed = Field()      # 是否折叠
    excerpt = Field()           # 摘要
    topics = Field()            # 话题标签


class DouyinItem(BaseItem):
    """抖音Item"""
    # 抖音特有字段
    aweme_id = Field()          # 视频ID
    desc = Field()              # 视频描述
    duration = Field()          # 视频时长
    music_id = Field()          # 音乐ID
    music_title = Field()       # 音乐标题
    digg_count = Field()        # 点赞数
    collect_count = Field()     # 收藏数
    download_count = Field()    # 下载数
    hashtags = Field()          # 话题标签


class CommentItem(scrapy.Item):
    """评论Item - 通用"""
    platform = Field()
    content_id = Field()        # 所属内容ID
    comment_id = Field()        # 评论ID
    parent_id = Field()         # 父评论ID（回复）
    
    content = Field()           # 评论内容
    author_id = Field()
    author_name = Field()
    
    likes = Field()
    replies = Field()           # 回复数
    
    publish_time = Field()
    crawl_time = Field()
    
    sentiment = Field()
    sentiment_score = Field()
