"""
数据大屏API接口
提供全国地区热力数据、最新采集数据、AI分析等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date, timedelta
import random
import httpx

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings

router = APIRouter()


# ==================== 请求/响应模型 ====================

class ChartDataRequest(BaseModel):
    """图表数据请求"""
    chart_type: str  # pie, bar, line, map, globe
    data_source: Optional[str] = None
    industry: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None


class ChartDataResponse(BaseModel):
    """图表数据响应"""
    chart_type: str
    title: str
    data: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class MapDataResponse(BaseModel):
    """地图数据响应"""
    map_type: str  # 2d, 3d
    regions: List[Dict[str, Any]]
    center: Optional[List[float]] = None
    zoom: Optional[float] = None


class DashboardSummary(BaseModel):
    """仪表盘概览数据"""
    total_reports: int
    total_data_sources: int
    total_spiders: int
    total_users: int
    today_reports: int
    today_crawled_items: int
    active_spiders: int
    recent_activities: List[Dict[str, Any]]


class AIAnalysisRequest(BaseModel):
    """AI分析请求"""
    query: str
    chart_type: Optional[str] = None
    data_context: Optional[Dict[str, Any]] = None


class AIAnalysisResponse(BaseModel):
    """AI分析响应"""
    analysis: str
    chart_data: Optional[ChartDataResponse] = None
    suggestions: Optional[List[str]] = None


class LatestDataItem(BaseModel):
    """最新数据项"""
    id: int
    title: str
    source: Optional[str] = None
    time: str
    url: Optional[str] = None


class HeatMapData(BaseModel):
    """热力地图数据"""
    name: str  # 省份/城市名称
    value: int  # 热度值
    lng: Optional[float] = None  # 经度
    lat: Optional[float] = None  # 纬度


# ==================== 省份数据（含经纬度） ====================

PROVINCE_DATA = {
    "北京": {"lng": 116.405285, "lat": 39.904989},
    "天津": {"lng": 117.190182, "lat": 39.125596},
    "河北": {"lng": 114.502461, "lat": 38.045474},
    "山西": {"lng": 112.549248, "lat": 37.857014},
    "内蒙古": {"lng": 111.670801, "lat": 40.818311},
    "辽宁": {"lng": 123.429096, "lat": 41.796767},
    "吉林": {"lng": 125.3245, "lat": 43.886841},
    "黑龙江": {"lng": 126.642464, "lat": 45.756967},
    "上海": {"lng": 121.472644, "lat": 31.231706},
    "江苏": {"lng": 118.767413, "lat": 32.041544},
    "浙江": {"lng": 120.153576, "lat": 30.287459},
    "安徽": {"lng": 117.283042, "lat": 31.86119},
    "福建": {"lng": 119.306239, "lat": 26.075302},
    "江西": {"lng": 115.892151, "lat": 28.676493},
    "山东": {"lng": 117.000923, "lat": 36.675807},
    "河南": {"lng": 113.665412, "lat": 34.757975},
    "湖北": {"lng": 114.298572, "lat": 30.584355},
    "湖南": {"lng": 112.982279, "lat": 28.19409},
    "广东": {"lng": 113.280637, "lat": 23.125178},
    "广西": {"lng": 108.320004, "lat": 22.82402},
    "海南": {"lng": 110.33119, "lat": 20.031971},
    "重庆": {"lng": 106.504962, "lat": 29.533155},
    "四川": {"lng": 104.065735, "lat": 30.659462},
    "贵州": {"lng": 106.713478, "lat": 26.578343},
    "云南": {"lng": 102.712251, "lat": 25.040609},
    "西藏": {"lng": 91.132212, "lat": 29.660361},
    "陕西": {"lng": 108.948024, "lat": 34.263161},
    "甘肃": {"lng": 103.823557, "lat": 36.058039},
    "青海": {"lng": 101.778916, "lat": 36.623178},
    "宁夏": {"lng": 106.278179, "lat": 38.46637},
    "新疆": {"lng": 87.617733, "lat": 43.792818},
    "台湾": {"lng": 121.509062, "lat": 25.044332},
    "香港": {"lng": 114.173355, "lat": 22.320048},
    "澳门": {"lng": 113.54909, "lat": 22.198951},
}


# ==================== AI调用辅助函数 ====================

async def call_ai_api(prompt: str) -> str:
    """调用AI API进行分析"""
    try:
        if settings.AI_PROVIDER == "siliconflow" and settings.SILICONFLOW_API_KEY:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.SILICONFLOW_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.SILICONFLOW_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.SILICONFLOW_MODEL,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的数据分析师，擅长分析舆情数据和热点趋势。请用简洁专业的语言回答问题。"},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
        return "AI服务暂不可用，请检查API配置"
    except Exception as e:
        return f"AI分析出错: {str(e)}"


# ==================== API接口 ====================

@router.get("/summary", response_model=DashboardSummary, summary="获取仪表盘概览")
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """获取仪表盘概览数据（无需登录）"""
    # 模拟数据，实际应从数据库查询
    return DashboardSummary(
        total_reports=random.randint(100, 500),
        total_data_sources=random.randint(10, 50),
        total_spiders=random.randint(20, 100),
        total_users=random.randint(50, 200),
        today_reports=random.randint(5, 30),
        today_crawled_items=random.randint(1000, 5000),
        active_spiders=random.randint(5, 20),
        recent_activities=[
            {"time": "10:30", "text": "新增报告《2024年行业分析》"},
            {"time": "10:25", "text": "爬虫任务完成，获取数据1000条"},
            {"time": "10:20", "text": "用户张三登录系统"},
            {"time": "10:15", "text": "AI生成报告完成"},
            {"time": "10:10", "text": "新增数据源：新闻网站"}
        ]
    )


@router.get("/heatmap", summary="获取全国地区热力数据")
async def get_heatmap_data(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取全国地区热力数据（以省、市统计地区热词热度）
    返回JSON数据用于2D地图和3D地球展示
    """
    # 生成模拟热力数据，实际应从数据库统计
    heat_data = []
    for province, coords in PROVINCE_DATA.items():
        # 模拟热度值，北上广深等地区热度较高
        base_value = random.randint(100, 500)
        if province in ["北京", "上海", "广东", "浙江", "江苏"]:
            base_value = random.randint(800, 2000)
        elif province in ["四川", "山东", "河南", "湖北"]:
            base_value = random.randint(500, 1000)
        
        heat_data.append({
            "name": province,
            "value": base_value,
            "lng": coords["lng"],
            "lat": coords["lat"]
        })
    
    # 按热度排序
    heat_data.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "regions": heat_data,
            "max_value": max(item["value"] for item in heat_data),
            "min_value": min(item["value"] for item in heat_data),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/latest", summary="获取最新采集的20条数据")
async def get_latest_data(
    limit: int = 20,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取最新采集回来的20条数据
    不分类，按时间统计这排序最新的20条数据，用于列表显示
    """
    # 模拟最新数据，实际应从spider_data表查询
    news_titles = [
        "准备开抢！成都电影、餐饮、汽车消费券来了",
        "网络不给力，请稍后重试",
        "深耕域沃土 铸就金融标杆：银行业高质量发展纪实",
        "时尚WEEKLY | 迪桑特 精工极致 系列全新上市",
        "成都至阿拉木图航线开航 执飞机型为空客A320",
        "2024年度十大科技突破盘点",
        "人工智能赋能传统产业转型升级",
        "新能源汽车销量再创新高",
        "数字经济发展报告发布",
        "智慧城市建设加速推进",
        "5G应用场景持续拓展",
        "绿色低碳发展成效显著",
        "科技创新驱动高质量发展",
        "数据要素市场化配置改革深化",
        "产业链供应链韧性增强",
        "区块链技术应用落地加速",
        "元宇宙概念持续升温",
        "云计算市场规模快速增长",
        "网络安全形势依然严峻",
        "数字化转型成企业共识",
        "人才培养体系不断完善",
        "创新生态持续优化",
        "科技成果转化效率提升",
        "国际科技合作深入推进"
    ]
    
    sources = ["新浪新闻", "腾讯新闻", "网易新闻", "搜狐新闻", "凤凰网", "央视网", "人民网", "新华网"]
    
    latest_data = []
    now = datetime.now()
    
    for i in range(min(limit, len(news_titles))):
        # 生成随机时间（最近24小时内）
        random_minutes = random.randint(1, 1440)
        item_time = now - timedelta(minutes=random_minutes)
        
        latest_data.append({
            "id": i + 1,
            "title": news_titles[i],
            "source": random.choice(sources),
            "time": item_time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": f"https://example.com/news/{i + 1}"
        })
    
    # 按时间排序（最新的在前）
    latest_data.sort(key=lambda x: x["time"], reverse=True)
    
    return {
        "code": 200,
        "message": "success",
        "data": latest_data
    }


@router.get("/map/2d", response_model=MapDataResponse, summary="获取2D地图数据")
async def get_2d_map_data(
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取2D地图展示数据"""
    regions = []
    for province, coords in PROVINCE_DATA.items():
        base_value = random.randint(100, 500)
        if province in ["北京", "上海", "广东", "浙江", "江苏"]:
            base_value = random.randint(800, 2000)
        elif province in ["四川", "山东", "河南", "湖北"]:
            base_value = random.randint(500, 1000)
        
        regions.append({
            "name": province,
            "value": base_value,
            "lng": coords["lng"],
            "lat": coords["lat"]
        })
    
    return MapDataResponse(
        map_type="2d",
        regions=regions,
        center=[104.114129, 37.550339],
        zoom=5
    )


@router.get("/map/3d", summary="获取3D地球数据")
async def get_3d_globe_data(
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取3D地球展示数据，包含全球主要城市热点"""
    # 中国省份数据
    china_data = []
    for province, coords in PROVINCE_DATA.items():
        base_value = random.randint(100, 500)
        if province in ["北京", "上海", "广东", "浙江", "江苏"]:
            base_value = random.randint(800, 2000)
        elif province in ["四川", "山东", "河南", "湖北"]:
            base_value = random.randint(500, 1000)
        
        china_data.append({
            "name": province,
            "value": base_value,
            "lng": coords["lng"],
            "lat": coords["lat"],
            "country": "中国"
        })
    
    # 全球主要城市数据
    global_cities = [
        {"name": "纽约", "lng": -74.006, "lat": 40.7128, "country": "美国"},
        {"name": "洛杉矶", "lng": -118.2437, "lat": 34.0522, "country": "美国"},
        {"name": "伦敦", "lng": -0.1276, "lat": 51.5074, "country": "英国"},
        {"name": "巴黎", "lng": 2.3522, "lat": 48.8566, "country": "法国"},
        {"name": "东京", "lng": 139.6917, "lat": 35.6895, "country": "日本"},
        {"name": "首尔", "lng": 126.978, "lat": 37.5665, "country": "韩国"},
        {"name": "新加坡", "lng": 103.8198, "lat": 1.3521, "country": "新加坡"},
        {"name": "悉尼", "lng": 151.2093, "lat": -33.8688, "country": "澳大利亚"},
        {"name": "迪拜", "lng": 55.2708, "lat": 25.2048, "country": "阿联酋"},
        {"name": "莫斯科", "lng": 37.6173, "lat": 55.7558, "country": "俄罗斯"},
    ]
    
    for city in global_cities:
        city["value"] = random.randint(200, 800)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "china": china_data,
            "global": global_cities,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/realtime", summary="获取实时数据")
async def get_realtime_data(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取实时更新数据（用于大屏滚动展示）"""
    activities = [
        {"time": datetime.now().strftime("%H:%M:%S"), "text": "新增舆情数据 5 条", "type": "info"},
        {"time": (datetime.now() - timedelta(minutes=1)).strftime("%H:%M:%S"), "text": "AI分析完成：科技行业热度上升", "type": "success"},
        {"time": (datetime.now() - timedelta(minutes=2)).strftime("%H:%M:%S"), "text": "爬虫任务执行中...", "type": "warning"},
        {"time": (datetime.now() - timedelta(minutes=5)).strftime("%H:%M:%S"), "text": "数据同步完成", "type": "success"},
        {"time": (datetime.now() - timedelta(minutes=10)).strftime("%H:%M:%S"), "text": "新增报告《行业分析》", "type": "info"},
    ]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "activities": activities,
            "online_users": random.randint(10, 50),
            "today_visits": random.randint(100, 500),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/industry-distribution", response_model=ChartDataResponse, summary="获取行业分布")
async def get_industry_distribution(
    db: Session = Depends(get_db)
):
    """获取行业数据分布"""
    industries = [
        {"name": "科技", "value": random.randint(1000, 2000)},
        {"name": "金融", "value": random.randint(800, 1500)},
        {"name": "医疗", "value": random.randint(600, 1200)},
        {"name": "教育", "value": random.randint(500, 1000)},
        {"name": "制造", "value": random.randint(400, 900)},
        {"name": "能源", "value": random.randint(300, 700)},
        {"name": "消费", "value": random.randint(400, 800)},
        {"name": "其他", "value": random.randint(200, 500)},
    ]
    
    return ChartDataResponse(
        chart_type="pie",
        title="行业数据分布",
        data=industries
    )


@router.get("/trend", response_model=ChartDataResponse, summary="获取趋势数据")
async def get_trend_data(
    days: int = 7,
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取数据趋势"""
    trend_data = []
    now = datetime.now()
    
    for i in range(days, 0, -1):
        day = now - timedelta(days=i)
        trend_data.append({
            "date": day.strftime("%m-%d"),
            "value": random.randint(500, 2000)
        })
    
    return ChartDataResponse(
        chart_type="line",
        title="数据采集趋势",
        data=trend_data
    )


@router.post("/ai-analysis", summary="AI数据分析")
async def ai_data_analysis(
    request: AIAnalysisRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    AI驱动的数据分析
    通过自然语言查询获取数据分析结果和图表
    """
    # 构建分析提示词
    prompt = f"""
    请分析以下问题，并给出专业的数据分析结论：
    
    问题：{request.query}
    
    请从以下几个方面进行分析：
    1. 当前趋势分析
    2. 关键数据指标
    3. 建议和预测
    
    请用简洁专业的语言回答，控制在300字以内。
    """
    
    # 调用AI API
    analysis = await call_ai_api(prompt)
    
    # 生成建议
    suggestions = [
        "持续关注热点地区的舆情变化",
        "加强数据采集频率",
        "优化AI分析模型",
        "建立预警机制"
    ]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "analysis": analysis,
            "suggestions": suggestions,
            "query": request.query,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/ranking", summary="获取排行榜数据")
async def get_ranking_data(
    ranking_type: str = "region",  # region, industry, source
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取排行榜数据"""
    if ranking_type == "region":
        # 地区热度排行
        data = [
            {"name": "广东", "value": random.randint(1500, 2000)},
            {"name": "北京", "value": random.randint(1400, 1900)},
            {"name": "上海", "value": random.randint(1300, 1800)},
            {"name": "浙江", "value": random.randint(1200, 1700)},
            {"name": "江苏", "value": random.randint(1100, 1600)},
            {"name": "四川", "value": random.randint(900, 1400)},
            {"name": "山东", "value": random.randint(800, 1300)},
            {"name": "河南", "value": random.randint(700, 1200)},
            {"name": "湖北", "value": random.randint(600, 1100)},
            {"name": "福建", "value": random.randint(500, 1000)},
        ]
    elif ranking_type == "industry":
        # 行业热度排行
        data = [
            {"name": "科技", "value": random.randint(1500, 2000)},
            {"name": "金融", "value": random.randint(1200, 1700)},
            {"name": "医疗", "value": random.randint(1000, 1500)},
            {"name": "教育", "value": random.randint(800, 1300)},
            {"name": "制造", "value": random.randint(600, 1100)},
        ]
    else:
        # 数据源排行
        data = [
            {"name": "新浪新闻", "value": random.randint(500, 1000)},
            {"name": "腾讯新闻", "value": random.randint(400, 900)},
            {"name": "网易新闻", "value": random.randint(300, 800)},
            {"name": "搜狐新闻", "value": random.randint(200, 700)},
            {"name": "凤凰网", "value": random.randint(100, 600)},
        ]
    
    # 排序
    data.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "code": 200,
        "message": "success",
        "data": data[:limit]
    }


@router.post("/chart", response_model=ChartDataResponse, summary="获取图表数据")
async def get_chart_data(
    request: ChartDataRequest,
    db: Session = Depends(get_db)
):
    """
    获取图表数据
    
    支持的图表类型:
    - **pie**: 饼图
    - **bar**: 柱状图
    - **line**: 折线图
    - **scatter**: 散点图
    """
    if request.chart_type == "pie":
        data = [
            {"name": "科技", "value": random.randint(1000, 2000)},
            {"name": "金融", "value": random.randint(800, 1500)},
            {"name": "医疗", "value": random.randint(600, 1200)},
            {"name": "教育", "value": random.randint(500, 1000)},
            {"name": "其他", "value": random.randint(300, 700)},
        ]
        title = "行业分布"
    elif request.chart_type == "bar":
        data = [
            {"name": "周一", "value": random.randint(500, 1000)},
            {"name": "周二", "value": random.randint(500, 1000)},
            {"name": "周三", "value": random.randint(500, 1000)},
            {"name": "周四", "value": random.randint(500, 1000)},
            {"name": "周五", "value": random.randint(500, 1000)},
            {"name": "周六", "value": random.randint(300, 700)},
            {"name": "周日", "value": random.randint(300, 700)},
        ]
        title = "每日数据统计"
    else:
        # 默认折线图
        data = []
        now = datetime.now()
        for i in range(7, 0, -1):
            day = now - timedelta(days=i)
            data.append({
                "name": day.strftime("%m-%d"),
                "value": random.randint(500, 2000)
            })
        title = "数据趋势"
    
    return ChartDataResponse(
        chart_type=request.chart_type,
        title=title,
        data=data
    )
