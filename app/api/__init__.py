"""
APIルーターモジュール

FastAPIのAPIエンドポイントを定義します。
"""
from fastapi import APIRouter
from app.api import auth, staffs, users, consultations, organizations, plans, monitorings, pdf, network, dashboard

api_router = APIRouter()

# 各エンドポイントを登録
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])
api_router.include_router(staffs.router, prefix="/staffs", tags=["スタッフ"])
api_router.include_router(users.router, prefix="/users", tags=["利用者"])
api_router.include_router(consultations.router, prefix="/consultations", tags=["相談記録"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["関係機関"])
api_router.include_router(plans.router, prefix="/plans", tags=["サービス利用計画"])
api_router.include_router(monitorings.router, prefix="/monitorings", tags=["モニタリング記録"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["PDF出力"])
api_router.include_router(network.router, prefix="/network", tags=["ネットワーク図"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["ダッシュボード"])

__all__ = ["api_router"]
