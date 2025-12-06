# 舆情监控爬虫系统

基于 Scrapy 的多平台舆情数据采集系统，支持微博、知乎等主流社交媒体平台。

## 功能特性

- **多平台支持**：微博、知乎（可扩展抖音、头条等）
- **关键词监控**：支持自定义关键词列表
- **情感分析**：集成 SnowNLP/BERT 情感分析
- **代理池**：支持代理池自动切换
- **Cookie池**：支持多账号Cookie轮换
- **分布式**：基于 scrapy-redis 支持分布式部署
- **数据存储**：MongoDB 持久化存储

## 项目结构

```
crawler/
├── project/                    # Scrapy项目
│   ├── spiders/               # 爬虫
│   │   ├── base_spider.py     # 基础爬虫类
│   │   ├── weibo_spider.py    # 微博爬虫
│   │   └── zhihu_spider.py    # 知乎爬虫
│   ├── items.py               # 数据模型
│   ├── pipelines.py           # 数据管道
│   ├── middlewares.py         # 中间件
│   └── settings.py            # 配置
├── libs/                       # 工具库
│   ├── proxy_pool.py          # 代理池
│   ├── cookie_pool.py         # Cookie池
│   ├── sign.py                # 签名生成
│   └── sentiment.py           # 情感分析
├── cfg/                        # 配置文件
│   ├── keywords.txt           # 关键词
│   └── sites.yml              # 站点配置
├── tests/                      # 测试
├── k8s/                        # K8s配置
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── scrapy.cfg
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `cfg/keywords.txt` 添加监控关键词：

```text
# 品牌关键词
华为
小米

# 事件关键词
双十一
```

### 3. 启动服务

使用 Docker Compose：

```bash
docker-compose up -d
```

或本地运行：

```bash
# 启动 MongoDB 和 Redis
# ...

# 运行爬虫
scrapy crawl weibo -a keywords="关键词1,关键词2"
scrapy crawl zhihu -a keywords="关键词1" -a hot_list=true
```

## 爬虫使用

### 微博爬虫

```bash
# 关键词搜索
scrapy crawl weibo -a keywords="华为,小米"

# 指定用户
scrapy crawl weibo -a user_ids="1234567890,0987654321"
```

### 知乎爬虫

```bash
# 关键词搜索
scrapy crawl zhihu -a keywords="人工智能"

# 热榜
scrapy crawl zhihu -a hot_list=true

# 指定问题
scrapy crawl zhihu -a question_ids="12345678"

# 指定话题
scrapy crawl zhihu -a topic_ids="19550517"
```

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MONGO_URI` | MongoDB连接URI | `mongodb://localhost:27017` |
| `MONGO_DATABASE` | 数据库名 | `crawler` |
| `REDIS_HOST` | Redis主机 | `localhost` |
| `REDIS_PORT` | Redis端口 | `6379` |
| `PROXY_POOL_URL` | 代理池API | `http://localhost:5010/get` |
| `PROXY_POOL_ENABLED` | 启用代理 | `true` |
| `SENTIMENT_ENABLED` | 启用情感分析 | `true` |
| `SENTIMENT_MODEL` | 情感模型 | `snownlp` |

### Cookie配置

#### 手动添加Cookie到Redis

```python
from libs.cookie_pool import CookiePool

pool = CookiePool()
pool.add_cookie("weibo", "username", "cookie_string")
```

#### 自动获取Cookie（推荐）

系统支持自动获取和刷新Cookie，当Cookie失效时会自动重新获取：

```python
import asyncio
from libs.cookie_manager import CookieManager, get_cookie

# 方式1：使用管理器
async def main():
    manager = CookieManager(auto_refresh=True)
    
    # 获取百度Cookie
    baidu_cookie = await manager.get_cookie("baidu")
    
    # 获取Bing Cookie
    bing_cookie = await manager.get_cookie("bing")
    
    # 获取微博访客Cookie
    weibo_cookie = await manager.get_cookie("weibo")
    
    # 获取知乎Cookie
    zhihu_cookie = await manager.get_cookie("zhihu")
    
    # 验证Cookie
    is_valid = await manager.validate_cookie("baidu", baidu_cookie)
    
    # 标记失效（会自动刷新）
    await manager.mark_invalid("baidu", baidu_cookie)
    
    # 刷新所有平台Cookie
    results = await manager.refresh_all()
    print(results)  # {"baidu": True, "bing": True, ...}

asyncio.run(main())

# 方式2：快捷函数
async def quick():
    from libs.cookie_manager import fetch_baidu_cookie, fetch_bing_cookie
    
    baidu = await fetch_baidu_cookie()
    bing = await fetch_bing_cookie()

# 方式3：同步调用
from libs.cookie_manager import get_cookie_sync
cookie = get_cookie_sync("baidu")
```

#### 支持的平台

| 平台 | 自动获取 | 说明 |
|------|----------|------|
| `baidu` | ✅ | 百度搜索Cookie |
| `bing` | ✅ | Bing搜索Cookie |
| `weibo` | ✅ | 微博访客Cookie（有效期较短） |
| `zhihu` | ✅ | 知乎访客Cookie |

#### 自定义Cookie获取器

```python
from libs.cookie_manager import BaseCookieFetcher, CookieManager, CookieInfo

class MyPlatformFetcher(BaseCookieFetcher):
    platform = "myplatform"
    
    async def fetch(self):
        # 实现获取逻辑
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://example.com")
            cookies = dict(resp.cookies)
            return CookieInfo(
                platform=self.platform,
                cookies=cookies,
                cookie_string=self._cookies_to_string(cookies),
            )
    
    async def validate(self, cookie_info):
        # 实现验证逻辑
        return True

# 注册到管理器
manager = CookieManager()
manager.register_fetcher("myplatform", MyPlatformFetcher)
```

## 数据格式

### 微博数据

```json
{
  "platform": "weibo",
  "content_id": "4900000000000000",
  "mid": "4900000000000000",
  "content": "微博正文内容",
  "author_name": "用户昵称",
  "likes": 100,
  "comments": 50,
  "reposts": 20,
  "publish_time": "2024-01-01T12:00:00",
  "sentiment": "positive",
  "sentiment_score": 0.85,
  "matched_keywords": ["关键词1"]
}
```

### 知乎数据

```json
{
  "platform": "zhihu",
  "content_id": "123456789",
  "question_title": "问题标题",
  "content": "回答内容",
  "author_name": "用户名",
  "upvotes": 1000,
  "comments": 50,
  "sentiment": "neutral",
  "sentiment_score": 0.1
}
```

## 扩展开发

### 添加新爬虫

1. 继承 `BaseSpider`
2. 实现 `start_requests()` 和解析方法
3. 在 `cfg/sites.yml` 添加配置

```python
from project.spiders.base_spider import BaseSpider

class NewSpider(BaseSpider):
    name = "new_platform"
    platform = "new_platform"
    
    def start_requests(self):
        for keyword in self.keywords:
            yield self.make_request(url, callback=self.parse)
    
    def parse(self, response):
        # 解析逻辑
        pass 
```

## 测试

```bash
pytest tests/ -v
```

## 注意事项

1. **遵守robots.txt**：请合理设置爬取频率
2. **Cookie有效期**：定期更新Cookie
3. **代理质量**：使用高质量代理避免封禁
4. **数据合规**：遵守相关法律法规

## License

MIT
