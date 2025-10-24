"""
サービス利用計画管理API

サービス利用計画のCRUD操作と承認機能を提供します。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.plan import Plan
from app.models.user import User
from app.models.staff import Staff
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse, PlanApprove
from app.api.auth import get_current_staff
from app.utils.kana_converter import hiragana_to_katakana
from app.services.pdf_service import PDFService

router = APIRouter()


@router.get("", response_model=List[PlanResponse])
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="利用者名・計画番号・目標で検索"),
    user_id: Optional[int] = Query(None, description="利用者IDでフィルタ"),
    staff_id: Optional[int] = Query(None, description="作成者スタッフIDでフィルタ"),
    approval_status: Optional[str] = Query(None, description="承認状況でフィルタ"),
    include_deleted: bool = Query(False, description="削除済みを含む"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    計画一覧を取得

    Args:
        skip: スキップ件数
        limit: 取得件数上限
        search: 検索キーワード（利用者名・計画番号・目標）
        user_id: 利用者ID
        staff_id: 作成者スタッフID
        approval_status: 承認状況
        include_deleted: 削除済みを含むか
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[PlanResponse]: 計画一覧
    """
    query = db.query(Plan)

    # 削除済みフィルタ
    if not include_deleted:
        query = query.filter(Plan.is_deleted == False)

    # 曖昧検索（利用者名・計画番号・目標 + ひらがな→カタカナ変換）
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
                Plan.plan_number.like(search_pattern),
                Plan.plan_number.like(search_katakana_pattern),
                Plan.long_term_goal.like(search_pattern),
                Plan.long_term_goal.like(search_katakana_pattern),
                Plan.short_term_goal.like(search_pattern),
                Plan.short_term_goal.like(search_katakana_pattern)
            )
        )

    # 利用者でフィルタ
    if user_id:
        query = query.filter(Plan.user_id == user_id)

    # 作成者でフィルタ
    if staff_id:
        query = query.filter(Plan.staff_id == staff_id)

    # 承認状況でフィルタ
    if approval_status:
        query = query.filter(Plan.approval_status == approval_status)

    # 作成日降順でソート
    query = query.order_by(Plan.created_date.desc())

    plans = query.offset(skip).limit(limit).all()
    return plans


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_in: PlanCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    新しい計画を作成

    Args:
        plan_in: 計画作成データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        PlanResponse: 作成された計画
    """
    # 利用者の存在確認
    user = db.query(User).filter(User.id == plan_in.user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された利用者が見つかりません"
        )

    # 計画番号の重複チェック
    existing_plan = db.query(Plan).filter(Plan.plan_number == plan_in.plan_number).first()
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この計画番号は既に使用されています"
        )

    # 計画作成
    plan = Plan(**plan_in.dict())
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    計画詳細を取得

    Args:
        plan_id: 計画ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        PlanResponse: 計画詳細
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_in: PlanUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    計画を更新

    Args:
        plan_id: 計画ID
        plan_in: 更新データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        PlanResponse: 更新された計画
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    # 承認済み/実施中の計画は編集不可
    if not plan.can_edit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="承認済みまたは実施中の計画は編集できません"
        )

    # 更新
    update_data = plan_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    計画を論理削除

    Args:
        plan_id: 計画ID
        db: データベースセッション
        current_staff: 現在のスタッフ
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    # 論理削除
    plan.is_deleted = True
    db.commit()


@router.get("/users/{user_id}/plans", response_model=List[PlanResponse])
def list_user_plans(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    特定利用者の計画一覧を取得

    Args:
        user_id: 利用者ID
        skip: スキップ件数
        limit: 取得件数上限
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[PlanResponse]: 計画一覧
    """
    # 利用者の存在確認
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された利用者が見つかりません"
        )

    plans = db.query(Plan).filter(
        Plan.user_id == user_id,
        Plan.is_deleted == False
    ).order_by(Plan.created_date.desc()).offset(skip).limit(limit).all()

    return plans


@router.put("/{plan_id}/approve", response_model=PlanResponse)
def approve_plan(
    plan_id: int,
    approve_in: PlanApprove,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    計画を承認

    Args:
        plan_id: 計画ID
        approve_in: 承認データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        PlanResponse: 承認された計画
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    # 承認
    plan.approval_status = approve_in.approval_status
    plan.approval_date = approve_in.approval_date

    db.commit()
    db.refresh(plan)

    return plan


@router.get("/{plan_id}/pdf")
def download_plan_pdf(
    plan_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    計画をPDF形式でダウンロード

    Args:
        plan_id: 計画ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDF data

    Raises:
        HTTPException: 計画が見つからない
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された計画が見つかりません"
        )

    # 利用者情報を取得してファイル名に使用
    user = db.query(User).filter(User.id == plan.user_id).first()
    user_name = user.name if user else f"利用者{plan.user_id}"

    # PDF生成サービスを使用してPDF作成
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_plan_pdf(plan)

    # ファイル名を生成（日本語対応）
    plan_number = plan.plan_number or f"計画{plan_id}"
    filename = f"サービス利用計画_{user_name}_{plan_number}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )
