-- ============================================
-- 智能数据分析平台 - 数据库初始化脚本
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS data_platform 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE data_platform;

-- ============================================
-- 1. 用户管理相关表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    hashed_password VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(255) COMMENT '头像URL',
    phone VARCHAR(20) COMMENT '手机号',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user',
    permissions TEXT COMMENT '权限列表(JSON)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_superuser BOOLEAN DEFAULT FALSE COMMENT '是否超级管理员',
    last_login DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. AI引擎配置相关表
-- ============================================

-- AI引擎配置表
CREATE TABLE IF NOT EXISTS ai_engines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '引擎名称',
    provider VARCHAR(50) NOT NULL COMMENT '服务提供商: openai/azure/siliconflow/local',
    api_key VARCHAR(500) COMMENT 'API密钥(加密存储)',
    api_base_url VARCHAR(255) COMMENT 'API基础URL',
    model_name VARCHAR(100) NOT NULL COMMENT '模型名称',
    description TEXT COMMENT '引擎描述',
    max_tokens INT DEFAULT 2048 COMMENT '最大Token数',
    temperature FLOAT DEFAULT 0.7 COMMENT '温度参数',
    timeout INT DEFAULT 30 COMMENT '超时时间(秒)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认引擎',
    total_requests INT DEFAULT 0 COMMENT '总请求次数',
    total_tokens INT DEFAULT 0 COMMENT '总消耗Token',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_provider (provider),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI引擎配置表';

-- AI对话记录表
CREATE TABLE IF NOT EXISTS ai_conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    engine_id INT COMMENT '使用的AI引擎ID',
    session_id VARCHAR(100) COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色: user/assistant/system',
    content TEXT NOT NULL COMMENT '消息内容',
    prompt_tokens INT DEFAULT 0 COMMENT '输入Token数',
    completion_tokens INT DEFAULT 0 COMMENT '输出Token数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI对话记录表';

-- ============================================
-- 3. 信息仓库相关表
-- ============================================

-- 信息分类表
CREATE TABLE IF NOT EXISTS info_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '分类名称',
    parent_id INT DEFAULT 0 COMMENT '父分类ID, 0为顶级分类',
    icon VARCHAR(50) COMMENT '图标',
    sort_order INT DEFAULT 0 COMMENT '排序',
    description TEXT COMMENT '分类描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='信息分类表';

-- 信息文档表
CREATE TABLE IF NOT EXISTS info_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT COMMENT '分类ID',
    source_id INT COMMENT '数据源ID',
    title VARCHAR(500) NOT NULL COMMENT '标题',
    content LONGTEXT COMMENT '正文内容',
    summary TEXT COMMENT '摘要',
    author VARCHAR(100) COMMENT '作者',
    source_name VARCHAR(100) COMMENT '来源名称',
    source_url VARCHAR(1000) COMMENT '原文链接',
    cover_image VARCHAR(500) COMMENT '封面图片URL',
    images JSON COMMENT '图片列表(JSON)',
    attachments JSON COMMENT '附件列表(JSON)',
    tags JSON COMMENT '标签列表(JSON)',
    industry VARCHAR(50) COMMENT '行业分类',
    region VARCHAR(50) COMMENT '地区',
    sentiment VARCHAR(20) COMMENT '情感倾向: positive/negative/neutral',
    sentiment_score FLOAT COMMENT '情感分数 -1到1',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    share_count INT DEFAULT 0 COMMENT '分享数',
    status VARCHAR(20) DEFAULT 'published' COMMENT '状态: draft/published/archived',
    is_top BOOLEAN DEFAULT FALSE COMMENT '是否置顶',
    is_hot BOOLEAN DEFAULT FALSE COMMENT '是否热门',
    publish_time DATETIME COMMENT '发布时间',
    crawl_time DATETIME COMMENT '采集时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category_id (category_id),
    INDEX idx_title (title(100)),
    INDEX idx_industry (industry),
    INDEX idx_region (region),
    INDEX idx_sentiment (sentiment),
    INDEX idx_publish_time (publish_time),
    INDEX idx_status (status),
    FULLTEXT INDEX ft_title_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='信息文档表';

-- 关键词表
CREATE TABLE IF NOT EXISTS info_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL UNIQUE COMMENT '关键词',
    frequency INT DEFAULT 1 COMMENT '出现频次',
    category VARCHAR(50) COMMENT '关键词分类',
    is_hot BOOLEAN DEFAULT FALSE COMMENT '是否热词',
    trend VARCHAR(20) COMMENT '趋势: up/down/stable',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_keyword (keyword),
    INDEX idx_frequency (frequency),
    INDEX idx_is_hot (is_hot)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='关键词表';

-- 信息统计表
CREATE TABLE IF NOT EXISTS info_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL COMMENT '统计日期',
    category_id INT COMMENT '分类ID',
    total_count INT DEFAULT 0 COMMENT '总数量',
    positive_count INT DEFAULT 0 COMMENT '正面数量',
    negative_count INT DEFAULT 0 COMMENT '负面数量',
    neutral_count INT DEFAULT 0 COMMENT '中性数量',
    region_distribution JSON COMMENT '地区分布',
    industry_distribution JSON COMMENT '行业分布',
    hot_keywords JSON COMMENT '热词统计',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_stat_date (stat_date),
    INDEX idx_category_id (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='信息统计表';

-- ============================================
-- 4. 菜单管理表
-- ============================================

CREATE TABLE IF NOT EXISTS menus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '菜单名称',
    path VARCHAR(100) COMMENT '路由路径',
    component VARCHAR(100) COMMENT '组件路径',
    icon VARCHAR(50) COMMENT '图标',
    parent_id INT DEFAULT 0 COMMENT '父菜单ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_visible BOOLEAN DEFAULT TRUE COMMENT '是否可见',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    permissions VARCHAR(255) COMMENT '所需权限',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';

-- ============================================
-- 5. 爬虫管理相关表
-- ============================================

-- 数据源表
CREATE TABLE IF NOT EXISTS data_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '数据源名称',
    url VARCHAR(500) NOT NULL COMMENT '目标URL',
    source_type VARCHAR(50) DEFAULT 'website' COMMENT '类型: website/api/rss',
    industry VARCHAR(50) COMMENT '行业分类',
    description TEXT COMMENT '描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    crawl_frequency VARCHAR(20) DEFAULT 'daily' COMMENT '采集频率',
    last_crawl_time DATETIME COMMENT '最后采集时间',
    total_crawled INT DEFAULT 0 COMMENT '总采集数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_industry (industry),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据源表';

-- 爬虫规则表
CREATE TABLE IF NOT EXISTS spider_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_id INT NOT NULL COMMENT '数据源ID',
    name VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_type VARCHAR(50) DEFAULT 'xpath' COMMENT '规则类型: xpath/css/regex',
    title_rule VARCHAR(500) COMMENT '标题提取规则',
    content_rule VARCHAR(500) COMMENT '内容提取规则',
    author_rule VARCHAR(500) COMMENT '作者提取规则',
    time_rule VARCHAR(500) COMMENT '时间提取规则',
    image_rule VARCHAR(500) COMMENT '图片提取规则',
    list_rule VARCHAR(500) COMMENT '列表页规则',
    next_page_rule VARCHAR(500) COMMENT '下一页规则',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_source_id (source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爬虫规则表';

-- ============================================
-- 6. 报告管理表
-- ============================================

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '报告标题',
    content LONGTEXT COMMENT '报告内容(Markdown)',
    report_type VARCHAR(50) DEFAULT 'analysis' COMMENT '报告类型',
    user_id INT COMMENT '创建用户ID',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published',
    file_path VARCHAR(500) COMMENT 'PDF文件路径',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告表';

-- ============================================
-- 7. 聊天相关表
-- ============================================

-- 聊天室表
CREATE TABLE IF NOT EXISTS chat_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '聊天室名称',
    description TEXT COMMENT '描述',
    room_type VARCHAR(20) DEFAULT 'group' COMMENT '类型: group/private',
    owner_id INT COMMENT '创建者ID',
    member_count INT DEFAULT 0 COMMENT '成员数',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_owner_id (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天室表';

-- 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL COMMENT '聊天室ID',
    sender_id INT NOT NULL COMMENT '发送者ID',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型: text/image/file/ai_response',
    is_ai_message BOOLEAN DEFAULT FALSE COMMENT '是否AI消息',
    ai_command VARCHAR(50) COMMENT 'AI命令类型',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_room_id (room_id),
    INDEX idx_sender_id (sender_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天消息表';

-- ============================================
-- 8. 初始数据
-- ============================================

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, hashed_password, nickname, role, is_active, is_superuser) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYE.Fz3yQKGe', '系统管理员', 'admin', TRUE, TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- 插入默认AI引擎配置
INSERT INTO ai_engines (name, provider, api_base_url, model_name, description, is_default) VALUES
('成小理 (SiliconFlow)', 'siliconflow', 'https://api.siliconflow.cn/v1', 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B', '基于SiliconFlow的智能助手', TRUE),
('OpenAI GPT-3.5', 'openai', 'https://api.openai.com/v1', 'gpt-3.5-turbo', 'OpenAI GPT-3.5模型', FALSE),
('OpenAI GPT-4', 'openai', 'https://api.openai.com/v1', 'gpt-4', 'OpenAI GPT-4模型', FALSE)
ON DUPLICATE KEY UPDATE name=name;

-- 插入默认信息分类
INSERT INTO info_categories (name, parent_id, icon, sort_order, description) VALUES
('新闻资讯', 0, 'news', 1, '各类新闻资讯'),
('行业动态', 0, 'industry', 2, '行业相关动态'),
('政策法规', 0, 'policy', 3, '政策法规信息'),
('舆情监控', 0, 'monitor', 4, '舆情监控数据'),
('数据报告', 0, 'report', 5, '数据分析报告')
ON DUPLICATE KEY UPDATE name=name;

-- 插入默认菜单
INSERT INTO menus (name, path, component, icon, parent_id, sort_order) VALUES
('数据大屏', '/dashboard', 'dashboard/index', 'DataBoard', 0, 1),
('用户管理', '/users', 'users/index', 'User', 0, 2),
('菜单管理', '/menus', 'menus/index', 'Menu', 0, 3),
('爬虫管理', '/spiders', 'spiders/index', 'Connection', 0, 4),
('报告管理', '/reports', 'reports/index', 'Document', 0, 5),
('在线聊天', '/chat', 'chat/index', 'ChatDotRound', 0, 6)
ON DUPLICATE KEY UPDATE name=name;

-- 插入默认聊天室
INSERT INTO chat_rooms (name, description, room_type, member_count) VALUES
('公共聊天室', '欢迎来到公共聊天室，可以使用@成小理与AI助手对话', 'group', 0)
ON DUPLICATE KEY UPDATE name=name;

-- ============================================
-- 完成
-- ============================================
SELECT '数据库初始化完成!' AS message;
