"""
AI服务层
AI意图识别和功能调用逻辑
"""
from typing import Optional, Dict, Any, List
import json
import re
from enum import Enum

from app.core.config import settings


class AICommandType(Enum):
    """AI命令类型"""
    MUSIC = "music"
    MOVIE = "movie"
    WEATHER = "weather"
    CHART = "chart"
    REPORT = "report"
    UNKNOWN = "unknown"


class AIService:
    """AI服务类"""
    
    # 命令关键词映射
    COMMAND_KEYWORDS = {
        AICommandType.MUSIC: ["播放音乐", "放首歌", "来首歌", "听歌", "音乐"],
        AICommandType.MOVIE: ["播放电影", "看电影", "放电影", "视频"],
        AICommandType.WEATHER: ["天气", "气温", "下雨", "晴天", "温度"],
        AICommandType.CHART: ["饼图", "柱状图", "折线图", "图表", "数据", "报表", "统计"],
        AICommandType.REPORT: ["报告", "分析报告", "生成报告"],
    }
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    def parse_ai_command(self, message: str) -> Dict[str, Any]:
        """
        解析AI命令
        
        从用户消息中识别意图和参数
        
        Args:
            message: 用户消息内容（已去除@AI前缀）
        
        Returns:
            包含命令类型和参数的字典
        """
        message = message.strip()
        
        # 识别命令类型
        command_type = self._identify_command_type(message)
        
        # 根据命令类型提取参数
        params = self._extract_params(command_type, message)
        
        return {
            "command_type": command_type.value,
            "message": message,
            "params": params
        }
    
    def _identify_command_type(self, message: str) -> AICommandType:
        """识别命令类型"""
        for cmd_type, keywords in self.COMMAND_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message:
                    return cmd_type
        return AICommandType.UNKNOWN
    
    def _extract_params(self, command_type: AICommandType, message: str) -> Dict[str, Any]:
        """提取命令参数"""
        params = {}
        
        if command_type == AICommandType.MUSIC:
            # 尝试提取歌曲名或歌手
            params["query"] = self._extract_music_query(message)
        
        elif command_type == AICommandType.MOVIE:
            # 尝试提取电影名
            params["query"] = self._extract_movie_query(message)
        
        elif command_type == AICommandType.WEATHER:
            # 尝试提取城市
            params["city"] = self._extract_city(message)
        
        elif command_type == AICommandType.CHART:
            # 尝试提取图表类型和数据类型
            params["chart_type"] = self._extract_chart_type(message)
            params["data_type"] = self._extract_data_type(message)
        
        return params
    
    def _extract_music_query(self, message: str) -> Optional[str]:
        """提取音乐查询"""
        # 简单实现，后续可接入AI进行更精确的提取
        patterns = [
            r"播放[《"]?(.+?)[》"]?的?歌",
            r"来首(.+?)的歌",
            r"听(.+?)的歌",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return None
    
    def _extract_movie_query(self, message: str) -> Optional[str]:
        """提取电影查询"""
        patterns = [
            r"播放[《"]?(.+?)[》"]?电影",
            r"看[《"]?(.+?)[》"]?",
            r"电影[《"]?(.+?)[》"]?",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return None
    
    def _extract_city(self, message: str) -> str:
        """提取城市"""
        # 简单实现，默认返回北京
        cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
        for city in cities:
            if city in message:
                return city
        return "北京"
    
    def _extract_chart_type(self, message: str) -> str:
        """提取图表类型"""
        if "饼图" in message:
            return "pie"
        elif "柱状图" in message or "柱形图" in message:
            return "bar"
        elif "折线图" in message:
            return "line"
        elif "散点图" in message:
            return "scatter"
        return "bar"
    
    def _extract_data_type(self, message: str) -> Optional[str]:
        """提取数据类型"""
        data_types = ["销售", "用户", "订单", "收入", "访问", "报告"]
        for dt in data_types:
            if dt in message:
                return dt
        return None
    
    async def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行AI命令
        
        Args:
            command: 解析后的命令字典
        
        Returns:
            执行结果
        """
        command_type = AICommandType(command["command_type"])
        params = command.get("params", {})
        
        if command_type == AICommandType.MUSIC:
            return await self._handle_music(params)
        elif command_type == AICommandType.MOVIE:
            return await self._handle_movie(params)
        elif command_type == AICommandType.WEATHER:
            return await self._handle_weather(params)
        elif command_type == AICommandType.CHART:
            return await self._handle_chart(params)
        elif command_type == AICommandType.REPORT:
            return await self._handle_report(params)
        else:
            return await self._handle_unknown(command["message"])
    
    async def _handle_music(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理音乐播放"""
        query = params.get("query", "随机音乐")
        return {
            "success": True,
            "response_text": f"正在为您播放: {query}",
            "action": "play_music",
            "data": {
                "query": query,
                "type": "music"
            }
        }
    
    async def _handle_movie(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理电影播放"""
        query = params.get("query", "推荐电影")
        return {
            "success": True,
            "response_text": f"正在为您播放电影: {query}",
            "action": "play_movie",
            "data": {
                "query": query,
                "type": "movie"
            }
        }
    
    async def _handle_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理天气查询"""
        city = params.get("city", "北京")
        # TODO: 接入真实天气API
        return {
            "success": True,
            "response_text": f"{city}今日天气: 晴，温度 25°C，空气质量良好",
            "action": "show_weather",
            "data": {
                "city": city,
                "weather": "晴",
                "temperature": 25,
                "humidity": 60,
                "air_quality": "良"
            }
        }
    
    async def _handle_chart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理图表展示"""
        chart_type = params.get("chart_type", "bar")
        data_type = params.get("data_type", "数据")
        
        # TODO: 从数据库获取真实数据
        return {
            "success": True,
            "response_text": f"正在为您展示{data_type}{chart_type}图表",
            "action": "show_chart",
            "data": {
                "chart_type": chart_type,
                "data_type": data_type,
                "chart_data": {
                    "labels": ["一月", "二月", "三月", "四月", "五月"],
                    "values": [120, 200, 150, 80, 170]
                }
            }
        }
    
    async def _handle_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理报告生成"""
        return {
            "success": True,
            "response_text": "正在为您生成分析报告...",
            "action": "generate_report",
            "data": {}
        }
    
    async def _handle_unknown(self, message: str) -> Dict[str, Any]:
        """处理未知命令"""
        # TODO: 接入AI进行智能回复
        return {
            "success": True,
            "response_text": f"抱歉，我暂时无法理解您的请求: {message}。您可以尝试让我播放音乐、查询天气或展示数据图表。",
            "action": "chat",
            "data": {}
        }
    
    async def generate_report_content(
        self,
        topic: str,
        data: List[Dict[str, Any]],
        template: Optional[str] = None
    ) -> str:
        """
        使用AI生成报告内容
        
        Args:
            topic: 报告主题
            data: 相关数据
            template: 报告模板
        
        Returns:
            生成的报告内容（Markdown格式）
        """
        # TODO: 接入AI API生成报告
        return f"""
# {topic} 分析报告

## 概述
本报告基于收集的数据进行分析...

## 数据分析
...

## 结论与建议
...

---
*本报告由AI自动生成*
"""
