"""
情感分析模块
支持：
- SnowNLP（轻量级）
- Transformers BERT模型
- 自定义模型接口
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """情感标签"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """情感分析结果"""
    label: str
    score: float  # [-1, 1]，负数表示负面，正数表示正面
    confidence: float  # [0, 1]
    
    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "score": self.score,
            "confidence": self.confidence,
        }


class BaseSentimentAnalyzer:
    """情感分析基类"""
    
    def analyze(self, text: str) -> Dict:
        """
        分析文本情感
        
        Returns:
            {"label": "positive/negative/neutral", "score": float}
        """
        raise NotImplementedError
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """批量分析"""
        return [self.analyze(text) for text in texts]
    
    def _score_to_label(self, score: float, threshold: float = 0.2) -> str:
        """分数转标签"""
        if score > threshold:
            return SentimentLabel.POSITIVE.value
        elif score < -threshold:
            return SentimentLabel.NEGATIVE.value
        else:
            return SentimentLabel.NEUTRAL.value


class SnowNLPAnalyzer(BaseSentimentAnalyzer):
    """基于SnowNLP的情感分析"""
    
    def __init__(self):
        try:
            from snownlp import SnowNLP
            self.SnowNLP = SnowNLP
            self._available = True
        except ImportError:
            logger.warning("SnowNLP not installed, sentiment analysis disabled")
            self._available = False
    
    def analyze(self, text: str) -> Dict:
        if not self._available or not text:
            return {"label": "neutral", "score": 0.0}
        
        try:
            s = self.SnowNLP(text)
            # SnowNLP返回 [0, 1]，0为负面，1为正面
            raw_score = s.sentiments
            
            # 转换为 [-1, 1]
            score = (raw_score - 0.5) * 2
            label = self._score_to_label(score)
            
            return {
                "label": label,
                "score": round(score, 4),
            }
        except Exception as e:
            logger.error(f"SnowNLP analysis failed: {e}")
            return {"label": "neutral", "score": 0.0}


class BertAnalyzer(BaseSentimentAnalyzer):
    """基于BERT的情感分析"""
    
    # 中文情感分析模型
    DEFAULT_MODEL = "uer/roberta-base-finetuned-jd-binary-chinese"
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self._pipeline = None
        self._available = False
        
        self._init_model()
    
    def _init_model(self):
        """初始化模型"""
        try:
            from transformers import pipeline
            
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
            )
            self._available = True
            logger.info(f"Loaded BERT model: {self.model_name}")
        
        except ImportError:
            logger.warning("Transformers not installed")
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
    
    def analyze(self, text: str) -> Dict:
        if not self._available or not text:
            return {"label": "neutral", "score": 0.0}
        
        try:
            # 截断过长文本
            text = text[:512]
            
            result = self._pipeline(text)[0]
            
            # 转换标签和分数
            label_map = {
                "positive": 1,
                "negative": -1,
                "POSITIVE": 1,
                "NEGATIVE": -1,
                "LABEL_0": -1,  # 通常0是负面
                "LABEL_1": 1,   # 1是正面
            }
            
            raw_label = result["label"]
            confidence = result["score"]
            
            # 计算分数
            direction = label_map.get(raw_label, 0)
            score = direction * confidence
            
            label = self._score_to_label(score)
            
            return {
                "label": label,
                "score": round(score, 4),
            }
        
        except Exception as e:
            logger.error(f"BERT analysis failed: {e}")
            return {"label": "neutral", "score": 0.0}
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """批量分析（更高效）"""
        if not self._available or not texts:
            return [{"label": "neutral", "score": 0.0} for _ in texts]
        
        try:
            # 截断
            texts = [t[:512] for t in texts]
            
            results = self._pipeline(texts)
            
            return [self._convert_result(r) for r in results]
        
        except Exception as e:
            logger.error(f"BERT batch analysis failed: {e}")
            return [{"label": "neutral", "score": 0.0} for _ in texts]
    
    def _convert_result(self, result: Dict) -> Dict:
        """转换单个结果"""
        label_map = {
            "positive": 1, "negative": -1,
            "POSITIVE": 1, "NEGATIVE": -1,
            "LABEL_0": -1, "LABEL_1": 1,
        }
        
        raw_label = result["label"]
        confidence = result["score"]
        direction = label_map.get(raw_label, 0)
        score = direction * confidence
        
        return {
            "label": self._score_to_label(score),
            "score": round(score, 4),
        }


class SentimentAnalyzer:
    """情感分析器（统一接口）"""
    
    def __init__(self, model: str = "snownlp"):
        """
        初始化分析器
        
        Args:
            model: 模型类型，可选 "snownlp" 或 "bert"
        """
        self.model_type = model
        
        if model == "bert":
            self._analyzer = BertAnalyzer()
        else:
            self._analyzer = SnowNLPAnalyzer()
    
    def analyze(self, text: str) -> Dict:
        """分析单条文本"""
        return self._analyzer.analyze(text)
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """批量分析"""
        return self._analyzer.analyze_batch(texts)
    
    def analyze_with_keywords(self, text: str, keywords: List[str] = None) -> Dict:
        """
        带关键词权重的情感分析
        
        如果文本包含特定关键词，可以调整情感分数
        """
        result = self.analyze(text)
        
        if not keywords:
            return result
        
        # 负面关键词示例
        negative_keywords = ["投诉", "骗", "垃圾", "差评", "失望", "愤怒", "举报"]
        positive_keywords = ["好评", "推荐", "满意", "优秀", "点赞", "支持"]
        
        text_lower = text.lower()
        
        # 检查关键词
        neg_count = sum(1 for kw in negative_keywords if kw in text_lower)
        pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
        
        # 调整分数
        adjustment = (pos_count - neg_count) * 0.1
        new_score = max(-1, min(1, result["score"] + adjustment))
        
        result["score"] = round(new_score, 4)
        result["label"] = self._analyzer._score_to_label(new_score)
        
        return result


# 便捷函数
def analyze_sentiment(text: str, model: str = "snownlp") -> Dict:
    """快速情感分析"""
    analyzer = SentimentAnalyzer(model=model)
    return analyzer.analyze(text)


def analyze_sentiment_batch(texts: List[str], model: str = "snownlp") -> List[Dict]:
    """批量情感分析"""
    analyzer = SentimentAnalyzer(model=model)
    return analyzer.analyze_batch(texts)
