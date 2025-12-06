"""
AI服务层
AI意图识别和功能调用逻辑
"""
from typing import Optional, Dict, Any, List
import json
import re
from enum import Enum
import httpx

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
    
    # 成小理 AI 助手触发词
    CHENGLI_TRIGGERS = ["@成小理", "@chengli", "@成理"]
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        # SiliconFlow 配置
        self.siliconflow_api_key = settings.SILICONFLOW_API_KEY
        self.siliconflow_base_url = settings.SILICONFLOW_BASE_URL
        self.siliconflow_model = settings.SILICONFLOW_MODEL
    
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
        # 尝试提取《》中的内容
        if "《" in message and "》" in message:
            start = message.find("《") + 1
            end = message.find("》")
            if start < end:
                return message[start:end]
        # 尝试提取"播放"后的内容
        if "播放" in message:
            idx = message.find("播放") + 2
            rest = message[idx:].strip()
            if rest:
                return rest.split()[0] if rest.split() else rest
        return None
    
    def _extract_movie_query(self, message: str) -> Optional[str]:
        """提取电影查询"""
        # 尝试提取《》中的内容
        if "《" in message and "》" in message:
            start = message.find("《") + 1
            end = message.find("》")
            if start < end:
                return message[start:end]
        # 尝试提取"电影"后的内容
        if "电影" in message:
            idx = message.find("电影") + 2
            rest = message[idx:].strip()
            if rest:
                return rest.split()[0] if rest.split() else rest
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
        """处理未知命令 - 使用成小理进行智能回复"""
        # 尝试使用成小理进行智能回复
        reply = await self.chengli_reply(message)
        return {
            "success": True,
            "response_text": reply,
            "action": "chat",
            "data": {}
        }
    
    def is_chengli_command(self, message: str) -> bool:
        """
        检查消息是否是@成小理命令
        
        Args:
            message: 用户消息
        
        Returns:
            是否是成小理命令
        """
        message_lower = message.lower().strip()
        for trigger in self.CHENGLI_TRIGGERS:
            if message_lower.startswith(trigger.lower()):
                return True
        return False
    
    def extract_chengli_query(self, message: str) -> str:
        """
        提取成小理命令中的查询内容
        
        Args:
            message: 用户消息
        
        Returns:
            查询内容
        """
        message_stripped = message.strip()
        for trigger in self.CHENGLI_TRIGGERS:
            if message_stripped.lower().startswith(trigger.lower()):
                return message_stripped[len(trigger):].strip()
        return message_stripped
    
    async def chengli_reply(self, prompt: str) -> str:
        """
        成小理 AI 助手回复
        
        使用 SiliconFlow API 进行智能对话
        
        Args:
            prompt: 用户问题
        
        Returns:
            AI 回复内容
        """
        if not self.siliconflow_api_key:
            return "成小理未配置，请设置环境变量 SILICONFLOW_API_KEY"
        
        try:
            payload = {
                "model": self.siliconflow_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是成小理，一个友好、专业的AI助手。用简洁的中文回答用户问题，语气亲切自然。"
                    },
                    {
                        "role": "user",
                        "content": prompt or "请用简洁中文回答"
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.siliconflow_api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.siliconflow_base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "成小理没有返回可用内容")
                else:
                    return f"成小理服务异常 (HTTP {response.status_code})"
                    
        except httpx.TimeoutException:
            return "成小理响应超时，请稍后重试"
        except Exception as e:
            return f"成小理服务异常: {str(e)}"
    
    def handle_music_request(self, query: str) -> str:
        """处理音乐请求"""
        import random
        if not query:
            songs = [
                "《晴天》 - 周杰伦",
                "《安静》 - 周杰伦",
                "《小幸运》 - 田馥甸",
                "《稻香》 - 周杰伦",
                "《夜曲》 - 周杰伦",
                "《爱在西元前》 - 周杰伦",
            ]
            song = random.choice(songs)
            return f"🎶 为您推荐: {song}\n\n点击播放: https://music.163.com/"
        else:
            return f"🎵 正在为您搜索: {query}\n\n点击前往网易云音乐搜索: https://music.163.com/#/search/m/?s={query}"
    
    def handle_movie_request(self, query: str) -> str:
        """处理电影请求"""
        import random
        if not query:
            movies = [
                "《肖申克的救赎》 - 豆瓣 9.7",
                "《阿甘正传》 - 豆瓣 9.6",
                "《泰坦尼克号》 - 豆瓣 9.5",
                "《这个杀手不太冷》 - 豆瓣 9.4",
                "《盗梦空间》 - 豆瓣 9.4",
                "《星际穿越》 - 豆瓣 9.4",
            ]
            movie = random.choice(movies)
            return f"🎬 为您推荐: {movie}\n\n点击查看: https://movie.douban.com/"
        else:
            return f"🎞️ 正在为您搜索电影: {query}\n\n点击前往豆瓣搜索: https://search.douban.com/movie/subject_search?search_text={query}"
    
    def handle_weather_request(self, city: str) -> str:
        """处理天气请求"""
        weather_data = {
            "北京": {"天气": "晴", "温度": "25°C", "湿度": "45%", "空气质量": "良"},
            "上海": {"天气": "多云", "温度": "28°C", "湿度": "65%", "空气质量": "优"},
            "广州": {"天气": "阴", "温度": "30°C", "湿度": "75%", "空气质量": "良"},
            "深圳": {"天气": "小雨", "温度": "29°C", "湿度": "80%", "空气质量": "优"},
            "成都": {"天气": "阴", "温度": "22°C", "湿度": "70%", "空气质量": "良"},
            "武汉": {"天气": "晴", "温度": "27°C", "湿度": "55%", "空气质量": "良"},
            "杭州": {"天气": "多云", "温度": "26°C", "湿度": "60%", "空气质量": "优"},
            "南京": {"天气": "晴", "温度": "24°C", "湿度": "50%", "空气质量": "良"},
        }
        
        if city in weather_data:
            w = weather_data[city]
            return f"☀️ {city}今日天气\n\n天气: {w['天气']}\n温度: {w['温度']}\n湿度: {w['湿度']}\n空气质量: {w['空气质量']}"
        else:
            return f"🌤️ {city}今日天气\n\n天气: 晴\n温度: 25°C\n湿度: 50%\n空气质量: 良\n\n(暂无该城市详细数据)"
    
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
