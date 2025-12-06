# 智能数据分析平台

基于 FastAPI + Vue.js 3 + Element Plus 的智能数据分析平台，集成爬虫管理、AI分析、实时聊天等功能。

## 功能模块

1. **用户中心** - 用户注册/登录/管理
2. **菜单管理** - 动态菜单配置
3. **爬虫管理** - 多数据源、多爬虫管理，支持行业标签和效果测试
4. **报告管理** - AI生成报告，支持PDF下载
5. **数据大屏** - 炫酷可视化大屏，支持2D地图、3D地球、多种图表
6. **在线聊天** - 群聊/私聊，@AI智能助手

## 技术栈

- **后端**: FastAPI, SQLAlchemy, MySQL
- **前端**: Vue.js 3, Element Plus, Echarts
- **爬虫**: Scrapy
- **实时通讯**: WebSocket

## 项目结构

```
├── backend/                 # 后端项目
│   ├── app/                 # 应用代码
│   │   ├── api/             # API接口
│   │   ├── core/            # 核心配置
│   │   ├── db/              # 数据库
│   │   ├── services/        # 业务逻辑
│   │   └── websocket/       # WebSocket
│   ├── spiders/             # Scrapy爬虫
│   └── requirements.txt
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── api/             # API请求
│   │   ├── views/           # 页面组件
│   │   ├── stores/          # 状态管理
│   │   └── router/          # 路由配置
│   └── package.json
└── README.md
```

## 快速开始

### 后端

```bash
cd backend
# 配置虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 配置数据库和API密钥

# 启动服务
python run.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## API文档

启动后端后访问: http://localhost:8000/docs

## 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
