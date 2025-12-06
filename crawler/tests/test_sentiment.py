"""
情感分析模块测试
"""
import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.sentiment import (
    SentimentAnalyzer,
    SnowNLPAnalyzer,
    analyze_sentiment,
)


class TestSnowNLPAnalyzer:
    """SnowNLP分析器测试"""
    
    def setup_method(self):
        self.analyzer = SnowNLPAnalyzer()
    
    def test_positive_text(self):
        """测试正面文本"""
        text = "这个产品非常好用，我很满意，强烈推荐！"
        result = self.analyzer.analyze(text)
        
        assert "label" in result
        assert "score" in result
        assert result["score"] > 0  # 正面应该是正分数
    
    def test_negative_text(self):
        """测试负面文本"""
        text = "太差了，完全是骗人的，垃圾产品，要求退款！"
        result = self.analyzer.analyze(text)
        
        assert result["score"] < 0  # 负面应该是负分数
    
    def test_neutral_text(self):
        """测试中性文本"""
        text = "今天天气不错"
        result = self.analyzer.analyze(text)
        
        assert "label" in result
        assert -1 <= result["score"] <= 1
    
    def test_empty_text(self):
        """测试空文本"""
        result = self.analyzer.analyze("")
        
        assert result["label"] == "neutral"
        assert result["score"] == 0.0
    
    def test_none_text(self):
        """测试None"""
        result = self.analyzer.analyze(None)
        
        assert result["label"] == "neutral"


class TestSentimentAnalyzer:
    """统一接口测试"""
    
    def test_default_model(self):
        """测试默认模型"""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("好评！非常满意")
        assert "label" in result
        assert "score" in result
    
    def test_batch_analyze(self):
        """测试批量分析"""
        analyzer = SentimentAnalyzer()
        
        texts = [
            "非常好",
            "太差了",
            "一般般",
        ]
        
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == 3
        for result in results:
            assert "label" in result
            assert "score" in result
    
    def test_analyze_with_keywords(self):
        """测试带关键词的分析"""
        analyzer = SentimentAnalyzer()
        
        text = "这个产品有问题，我要投诉"
        result = analyzer.analyze_with_keywords(text)
        
        assert result["score"] < 0


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_analyze_sentiment(self):
        """测试快速分析函数"""
        result = analyze_sentiment("很好很满意")
        
        assert "label" in result
        assert "score" in result


# 性能测试
class TestPerformance:
    """性能测试"""
    
    def test_batch_performance(self):
        """测试批量处理性能"""
        import time
        
        analyzer = SentimentAnalyzer()
        texts = ["测试文本" * 10] * 100
        
        start = time.time()
        results = analyzer.analyze_batch(texts)
        elapsed = time.time() - start
        
        assert len(results) == 100
        # 100条应该在合理时间内完成
        assert elapsed < 10  # 10秒内


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
