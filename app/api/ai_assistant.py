"""
AI計画作成支援APIエンドポイント

Ollama ローカルLLMを使用した計画作成支援機能のAPIを提供します。
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.ai_assistant_service import OllamaAIAssistantService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class PlanProposalRequest(BaseModel):
    """計画提案リクエスト"""
    user_id: int = Field(..., description="利用者ID")
    previous_plan_id: Optional[int] = Field(None, description="前回の計画ID(任意)")
    model: Optional[str] = Field("llama3", description="使用するOllamaモデル名")


class PlanProposalResponse(BaseModel):
    """計画提案レスポンス"""
    user_id: int
    generated_at: str
    model_used: str
    proposal: Dict[str, Any]
    data_sources: Dict[str, bool]


class ModelListResponse(BaseModel):
    """利用可能モデル一覧レスポンス"""
    models: List[Dict[str, Any]]


@router.post("/plans/propose", response_model=PlanProposalResponse)
async def generate_plan_proposal(
    request: PlanProposalRequest,
    db: Session = Depends(get_db)
):
    """
    AI計画提案を生成 (Ollama使用)

    利用者の基本情報、障害特性、服薬情報、相談記録、前回計画の評価などを
    総合的に分析し、新しいサービス利用計画を提案します。

    Args:
        request: 計画提案リクエスト
        db: データベースセッション

    Returns:
        生成された計画提案

    Raises:
        HTTPException: 利用者が見つからない、またはOllamaエラーの場合
    """
    try:
        ai_service = OllamaAIAssistantService(db, model=request.model)
        result = ai_service.generate_plan_proposal(
            user_id=request.user_id,
            previous_plan_id=request.previous_plan_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI計画提案生成エラー: {str(e)}")


@router.get("/models/available", response_model=ModelListResponse)
async def get_available_models(db: Session = Depends(get_db)):
    """
    利用可能なOllamaモデル一覧を取得

    Args:
        db: データベースセッション

    Returns:
        モデル情報のリスト

    Raises:
        HTTPException: Ollamaサーバーエラーの場合
    """
    try:
        ai_service = OllamaAIAssistantService(db)
        models = ai_service.get_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"モデル一覧取得エラー: {str(e)}")
