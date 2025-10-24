"""
PDF出力API

各種PDF出力機能を提供します。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.plan import Plan
from app.models.monitoring import Monitoring
from app.models.staff import Staff
from app.services.pdf_service import PDFService
from app.api.auth import get_current_staff

router = APIRouter()
pdf_service = PDFService()


@router.get("/users/{user_id}")
def generate_user_pdf(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者情報PDFを生成

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDFファイル
    """
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された利用者が見つかりません"
        )

    pdf_buffer = pdf_service.generate_user_profile_pdf(user)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=user_{user_id}_profile.pdf"
        }
    )


@router.get("/plans/{plan_id}")
def generate_plan_pdf(
    plan_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    サービス利用計画PDFを生成

    Args:
        plan_id: 計画ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDFファイル
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    pdf_buffer = pdf_service.generate_plan_pdf(plan)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=plan_{plan_id}.pdf"
        }
    )


@router.get("/monitorings/{monitoring_id}")
def generate_monitoring_pdf(
    monitoring_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    モニタリング記録PDFを生成

    Args:
        monitoring_id: モニタリングID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDFファイル
    """
    monitoring = db.query(Monitoring).filter(
        Monitoring.id == monitoring_id,
        Monitoring.is_deleted == False
    ).first()
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたモニタリング記録が見つかりません"
        )

    pdf_buffer = pdf_service.generate_monitoring_pdf(monitoring)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=monitoring_{monitoring_id}.pdf"
        }
    )
