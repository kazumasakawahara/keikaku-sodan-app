"""
モニタリング記録管理API

モニタリング記録のCRUD操作を提供します。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.monitoring import Monitoring
from app.models.plan import Plan
from app.models.user import User
from app.models.staff import Staff
from app.schemas.monitoring import MonitoringCreate, MonitoringUpdate, MonitoringResponse
from app.api.auth import get_current_staff
from app.utils.kana_converter import hiragana_to_katakana
from app.services.pdf_service import PDFService

router = APIRouter()


@router.get("", response_model=List[MonitoringResponse])
def list_monitorings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="利用者名・モニタリング内容で検索"),
    plan_id: Optional[int] = Query(None, description="計画IDでフィルタ"),
    user_id: Optional[int] = Query(None, description="利用者IDでフィルタ"),
    staff_id: Optional[int] = Query(None, description="実施者スタッフIDでフィルタ"),
    monitoring_type: Optional[str] = Query(None, description="モニタリング種別でフィルタ"),
    include_deleted: bool = Query(False, description="削除済みを含む"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    モニタリング記録一覧を取得

    Args:
        skip: スキップ件数
        limit: 取得件数上限
        search: 検索キーワード（利用者名・モニタリング内容）
        plan_id: 計画ID
        user_id: 利用者ID
        staff_id: 実施者スタッフID
        monitoring_type: モニタリング種別
        include_deleted: 削除済みを含むか
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[MonitoringResponse]: モニタリング記録一覧
    """
    query = db.query(Monitoring)

    # 削除済みフィルタ
    if not include_deleted:
        query = query.filter(Monitoring.is_deleted == False)

    # 曖昧検索（利用者名・モニタリング内容 + ひらがな→カタカナ変換）
    if search:
        search_katakana = hiragana_to_katakana(search)
        search_pattern = f"%{search}%"
        search_katakana_pattern = f"%{search_katakana}%"
        query = query.join(User).filter(
            or_(
                User.name.like(search_pattern),
                User.name.like(search_katakana_pattern),
                User.name_kana.like(search_pattern),
                User.name_kana.like(search_katakana_pattern),
                Monitoring.service_usage_status.like(search_pattern),
                Monitoring.service_usage_status.like(search_katakana_pattern),
                Monitoring.goal_achievement.like(search_pattern),
                Monitoring.goal_achievement.like(search_katakana_pattern)
            )
        )

    # 計画でフィルタ
    if plan_id:
        query = query.filter(Monitoring.plan_id == plan_id)

    # 利用者でフィルタ
    if user_id:
        query = query.filter(Monitoring.user_id == user_id)

    # 実施者でフィルタ
    if staff_id:
        query = query.filter(Monitoring.staff_id == staff_id)

    # モニタリング種別でフィルタ
    if monitoring_type:
        query = query.filter(Monitoring.monitoring_type == monitoring_type)

    # 実施日降順でソート
    query = query.order_by(Monitoring.monitoring_date.desc())

    monitorings = query.offset(skip).limit(limit).all()
    return monitorings


@router.post("", response_model=MonitoringResponse, status_code=status.HTTP_201_CREATED)
def create_monitoring(
    monitoring_in: MonitoringCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    新しいモニタリング記録を作成

    Args:
        monitoring_in: モニタリング記録作成データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        MonitoringResponse: 作成されたモニタリング記録
    """
    # 計画の存在確認
    plan = db.query(Plan).filter(Plan.id == monitoring_in.plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    # 利用者の存在確認
    user = db.query(User).filter(User.id == monitoring_in.user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された利用者が見つかりません"
        )

    # モニタリング記録作成
    monitoring = Monitoring(**monitoring_in.dict())
    db.add(monitoring)
    db.commit()
    db.refresh(monitoring)

    return monitoring


@router.get("/{monitoring_id}", response_model=MonitoringResponse)
def get_monitoring(
    monitoring_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    モニタリング記録詳細を取得

    Args:
        monitoring_id: モニタリングID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        MonitoringResponse: モニタリング記録詳細
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

    return monitoring


@router.put("/{monitoring_id}", response_model=MonitoringResponse)
def update_monitoring(
    monitoring_id: int,
    monitoring_in: MonitoringUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    モニタリング記録を更新

    Args:
        monitoring_id: モニタリングID
        monitoring_in: 更新データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        MonitoringResponse: 更新されたモニタリング記録
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

    # 更新
    update_data = monitoring_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(monitoring, field, value)

    db.commit()
    db.refresh(monitoring)

    return monitoring


@router.delete("/{monitoring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitoring(
    monitoring_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    モニタリング記録を論理削除

    Args:
        monitoring_id: モニタリングID
        db: データベースセッション
        current_staff: 現在のスタッフ
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

    # 論理削除
    monitoring.is_deleted = True
    db.commit()


@router.get("/plans/{plan_id}/monitorings", response_model=List[MonitoringResponse])
def list_plan_monitorings(
    plan_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    特定計画のモニタリング記録一覧を取得

    Args:
        plan_id: 計画ID
        skip: スキップ件数
        limit: 取得件数上限
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[MonitoringResponse]: モニタリング記録一覧
    """
    # 計画の存在確認
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    monitorings = db.query(Monitoring).filter(
        Monitoring.plan_id == plan_id,
        Monitoring.is_deleted == False
    ).order_by(Monitoring.monitoring_date.desc()).offset(skip).limit(limit).all()

    return monitorings


@router.get("/users/{user_id}/monitorings", response_model=List[MonitoringResponse])
def list_user_monitorings(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    特定利用者のモニタリング記録一覧を取得

    Args:
        user_id: 利用者ID
        skip: スキップ件数
        limit: 取得件数上限
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[MonitoringResponse]: モニタリング記録一覧
    """
    # 利用者の存在確認
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された利用者が見つかりません"
        )

    monitorings = db.query(Monitoring).filter(
        Monitoring.user_id == user_id,
        Monitoring.is_deleted == False
    ).order_by(Monitoring.monitoring_date.desc()).offset(skip).limit(limit).all()

    return monitorings


@router.get("/{monitoring_id}/pdf")
def download_monitoring_pdf(
    monitoring_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    モニタリング記録をPDF形式でダウンロード

    Args:
        monitoring_id: モニタリングID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDF data

    Raises:
        HTTPException: モニタリング記録が見つからない
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

    # 利用者情報を取得してファイル名に使用
    user = db.query(User).filter(User.id == monitoring.user_id).first()
    user_name = user.name if user else f"利用者{monitoring.user_id}"

    # PDF生成サービスを使用してPDF作成
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_monitoring_pdf(monitoring)

    # ファイル名を生成（日本語対応）
    monitoring_date = monitoring.monitoring_date.strftime('%Y%m%d') if monitoring.monitoring_date else f"記録{monitoring_id}"
    filename = f"モニタリング記録_{user_name}_{monitoring_date}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )
