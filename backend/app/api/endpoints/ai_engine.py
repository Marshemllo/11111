"""
AI引擎管理API接口
提供AI引擎的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.db.models import AIEngine
from app.core.security import get_current_active_user

router = APIRouter()


# ==================== 请求/响应模型 ====================

class AIEngineCreate(BaseModel):
    """创建AI引擎请求"""
    name: str
    provider: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model_name: str
    description: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    is_active: bool = True
    is_default: bool = False


class AIEngineUpdate(BaseModel):
    """更新AI引擎请求"""
    name: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model_name: Optional[str] = None
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class AIEngineResponse(BaseModel):
    """AI引擎响应"""
    id: int
    name: str
    provider: str
    api_key: Optional[str] = None  # 返回时隐藏部分
    api_base_url: Optional[str] = None
    model_name: str
    description: Optional[str] = None
    max_tokens: int
    temperature: float
    timeout: int
    is_active: bool
    is_default: bool
    total_requests: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIEngineTestRequest(BaseModel):
    """测试AI引擎请求"""
    prompt: str = "你好，请简单介绍一下你自己"


class AIEngineTestResponse(BaseModel):
    """测试AI引擎响应"""
    success: bool
    message: str
    response: Optional[str] = None
    latency_ms: Optional[int] = None


# ==================== API接口 ====================

@router.get("/", response_model=List[AIEngineResponse], summary="获取AI引擎列表")
async def get_ai_engines(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取所有AI引擎配置
    
    - **skip**: 跳过记录数
    - **limit**: 返回记录数
    - **is_active**: 筛选是否启用
    """
    query = db.query(AIEngine)
    if is_active is not None:
        query = query.filter(AIEngine.is_active == is_active)
    
    engines = query.order_by(AIEngine.is_default.desc(), AIEngine.created_at.desc()).offset(skip).limit(limit).all()
    
    # 隐藏API密钥的部分内容
    for engine in engines:
        if engine.api_key:
            engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engines


@router.get("/default", response_model=AIEngineResponse, summary="获取默认AI引擎")
async def get_default_engine(db: Session = Depends(get_db)):
    """获取默认AI引擎配置"""
    engine = db.query(AIEngine).filter(AIEngine.is_default == True, AIEngine.is_active == True).first()
    if not engine:
        # 如果没有默认引擎，返回第一个启用的引擎
        engine = db.query(AIEngine).filter(AIEngine.is_active == True).first()
    
    if not engine:
        raise HTTPException(status_code=404, detail="没有可用的AI引擎")
    
    if engine.api_key:
        engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engine


@router.get("/{engine_id}", response_model=AIEngineResponse, summary="获取AI引擎详情")
async def get_ai_engine(engine_id: int, db: Session = Depends(get_db)):
    """获取指定AI引擎详情"""
    engine = db.query(AIEngine).filter(AIEngine.id == engine_id).first()
    if not engine:
        raise HTTPException(status_code=404, detail="AI引擎不存在")
    
    if engine.api_key:
        engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engine


@router.post("/", response_model=AIEngineResponse, summary="创建AI引擎")
async def create_ai_engine(
    engine_data: AIEngineCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的AI引擎配置
    
    - **name**: 引擎名称（唯一）
    - **provider**: 服务提供商 (openai/azure/siliconflow/deepseek/moonshot/qwen等)
    - **api_key**: API密钥
    - **api_base_url**: API基础URL
    - **model_name**: 模型名称
    """
    # 检查名称是否已存在
    existing = db.query(AIEngine).filter(AIEngine.name == engine_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="引擎名称已存在")
    
    # 如果设置为默认，取消其他默认
    if engine_data.is_default:
        db.query(AIEngine).filter(AIEngine.is_default == True).update({"is_default": False})
    
    engine = AIEngine(**engine_data.model_dump())
    db.add(engine)
    db.commit()
    db.refresh(engine)
    
    if engine.api_key:
        engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engine


@router.put("/{engine_id}", response_model=AIEngineResponse, summary="更新AI引擎")
async def update_ai_engine(
    engine_id: int,
    engine_data: AIEngineUpdate,
    db: Session = Depends(get_db)
):
    """更新AI引擎配置"""
    engine = db.query(AIEngine).filter(AIEngine.id == engine_id).first()
    if not engine:
        raise HTTPException(status_code=404, detail="AI引擎不存在")
    
    update_data = engine_data.model_dump(exclude_unset=True)
    
    # 如果名称变更，检查是否重复
    if "name" in update_data and update_data["name"] != engine.name:
        existing = db.query(AIEngine).filter(AIEngine.name == update_data["name"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="引擎名称已存在")
    
    # 如果设置为默认，取消其他默认
    if update_data.get("is_default"):
        db.query(AIEngine).filter(AIEngine.id != engine_id, AIEngine.is_default == True).update({"is_default": False})
    
    # 如果api_key为空字符串，保持原值
    if "api_key" in update_data and update_data["api_key"] == "":
        del update_data["api_key"]
    
    for key, value in update_data.items():
        setattr(engine, key, value)
    
    db.commit()
    db.refresh(engine)
    
    if engine.api_key:
        engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engine


@router.delete("/{engine_id}", summary="删除AI引擎")
async def delete_ai_engine(engine_id: int, db: Session = Depends(get_db)):
    """删除AI引擎配置"""
    engine = db.query(AIEngine).filter(AIEngine.id == engine_id).first()
    if not engine:
        raise HTTPException(status_code=404, detail="AI引擎不存在")
    
    db.delete(engine)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/{engine_id}/set-default", response_model=AIEngineResponse, summary="设置默认引擎")
async def set_default_engine(engine_id: int, db: Session = Depends(get_db)):
    """设置指定引擎为默认引擎"""
    engine = db.query(AIEngine).filter(AIEngine.id == engine_id).first()
    if not engine:
        raise HTTPException(status_code=404, detail="AI引擎不存在")
    
    # 取消其他默认
    db.query(AIEngine).filter(AIEngine.is_default == True).update({"is_default": False})
    
    engine.is_default = True
    db.commit()
    db.refresh(engine)
    
    if engine.api_key:
        engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engine


@router.post("/{engine_id}/toggle-status", response_model=AIEngineResponse, summary="切换引擎状态")
async def toggle_engine_status(engine_id: int, db: Session = Depends(get_db)):
    """启用/禁用AI引擎"""
    engine = db.query(AIEngine).filter(AIEngine.id == engine_id).first()
    if not engine:
        raise HTTPException(status_code=404, detail="AI引擎不存在")
    
    engine.is_active = not engine.is_active
    db.commit()
    db.refresh(engine)
    
    if engine.api_key:
        engine.api_key = engine.api_key[:8] + "****" + engine.api_key[-4:] if len(engine.api_key) > 12 else "****"
    
    return engine


@router.post("/{engine_id}/test", response_model=AIEngineTestResponse, summary="测试AI引擎")
async def test_ai_engine(
    engine_id: int,
    test_data: AIEngineTestRequest,
    db: Session = Depends(get_db)
):
    """
    测试AI引擎是否可用
    
    发送测试消息并返回响应
    """
    import httpx
    import time
    
    engine = db.query(AIEngine).filter(AIEngine.id == engine_id).first()
    if not engine:
        raise HTTPException(status_code=404, detail="AI引擎不存在")
    
    if not engine.api_key:
        return AIEngineTestResponse(
            success=False,
            message="未配置API密钥"
        )
    
    start_time = time.time()
    
    try:
        # 构建请求
        headers = {
            "Authorization": f"Bearer {engine.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": engine.model_name,
            "messages": [
                {"role": "user", "content": test_data.prompt}
            ],
            "max_tokens": min(engine.max_tokens, 500),
            "temperature": engine.temperature
        }
        
        api_url = f"{engine.api_base_url}/chat/completions"
        
        async with httpx.AsyncClient(timeout=engine.timeout) as client:
            response = await client.post(api_url, json=payload, headers=headers)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 更新统计
            engine.total_requests += 1
            usage = data.get("usage", {})
            engine.total_tokens += usage.get("total_tokens", 0)
            db.commit()
            
            return AIEngineTestResponse(
                success=True,
                message="测试成功",
                response=content,
                latency_ms=latency_ms
            )
        else:
            return AIEngineTestResponse(
                success=False,
                message=f"API返回错误: {response.status_code} - {response.text[:200]}",
                latency_ms=latency_ms
            )
            
    except httpx.TimeoutException:
        return AIEngineTestResponse(
            success=False,
            message="请求超时，请检查网络或增加超时时间"
        )
    except Exception as e:
        return AIEngineTestResponse(
            success=False,
            message=f"测试失败: {str(e)}"
        )


@router.get("/providers/list", summary="获取支持的服务商列表")
async def get_providers():
    """获取支持的AI服务商列表及其默认配置"""
    providers = [
        {
            "name": "openai",
            "label": "OpenAI",
            "icon": "🤖",
            "api_base_url": "https://api.openai.com/v1",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"],
            "description": "OpenAI官方API服务"
        },
        {
            "name": "siliconflow",
            "label": "SiliconFlow (硅基流动)",
            "icon": "🌊",
            "api_base_url": "https://api.siliconflow.cn/v1",
            "models": ["deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "Qwen/Qwen2.5-7B-Instruct", "THUDM/glm-4-9b-chat"],
            "description": "国内AI模型聚合平台"
        },
        {
            "name": "deepseek",
            "label": "DeepSeek (深度求索)",
            "icon": "🔍",
            "api_base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-coder"],
            "description": "DeepSeek官方API"
        },
        {
            "name": "moonshot",
            "label": "Moonshot (月之暗面)",
            "icon": "🌙",
            "api_base_url": "https://api.moonshot.cn/v1",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "description": "Kimi大模型API"
        },
        {
            "name": "qwen",
            "label": "通义千问",
            "icon": "🧠",
            "api_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "description": "阿里云通义千问API"
        },
        {
            "name": "zhipu",
            "label": "智谱AI",
            "icon": "📚",
            "api_base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4", "glm-4-flash", "glm-3-turbo"],
            "description": "智谱GLM系列模型"
        },
        {
            "name": "azure",
            "label": "Azure OpenAI",
            "icon": "☁️",
            "api_base_url": "https://your-resource.openai.azure.com/openai/deployments/your-deployment",
            "models": ["gpt-4", "gpt-35-turbo"],
            "description": "微软Azure托管的OpenAI服务"
        },
        {
            "name": "custom",
            "label": "自定义",
            "icon": "⚙️",
            "api_base_url": "",
            "models": [],
            "description": "自定义OpenAI兼容API"
        }
    ]
    return providers
