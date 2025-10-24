"""
相談記録管理API

相談記録のCRUD操作を提供します。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.consultation import Consultation
from app.models.user import User
from app.models.staff import Staff
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate, ConsultationResponse
from app.api.auth import get_current_staff
from app.utils.kana_converter import hiragana_to_katakana
from app.services.pdf_service import PDFService

router = APIRouter()


@router.get("", response_model=List[ConsultationResponse])
def list_consultations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="相談内容・対応内容で検索"),
    user_id: Optional[int] = Query(None, description="利用者IDでフィルタ"),
    staff_id: Optional[int] = Query(None, description="スタッフIDでフィルタ"),
    include_deleted: bool = Query(False, description="削除済みを含む"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    相談記録一覧を取得

    Args:
        skip: スキップ件数
        limit: 取得件数上限
        search: 検索キーワード（相談内容・対応内容）
        user_id: 利用者ID
        staff_id: スタッフID
        include_deleted: 削除済みを含むか
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[ConsultationResponse]: 相談記録一覧
    """
    query = db.query(Consultation)

    # 削除済みフィルタ
    if not include_deleted:
        query = query.filter(Consultation.is_deleted == False)

    # 曖昧検索（相談内容・対応内容 + ひらがな→カタカナ変換）
    if search:
        search_katakana = hiragana_to_katakana(search)
        search_pattern = f"%{search}%"
        search_katakana_pattern = f"%{search_katakana}%"
        query = query.filter(
            or_(
                Consultation.content.like(search_pattern),
                Consultation.content.like(search_katakana_pattern),
                Consultation.response.like(search_pattern),
                Consultation.response.like(search_katakana_pattern)
            )
        )

    # 利用者フィルタ
    if user_id:
        query = query.filter(Consultation.user_id == user_id)

    # スタッフフィルタ
    if staff_id:
        query = query.filter(Consultation.staff_id == staff_id)

    # 日付の降順でソート
    query = query.order_by(Consultation.consultation_date.desc())

    consultations = query.offset(skip).limit(limit).all()
    return consultations


@router.post("", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(
    consultation_data: ConsultationCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    相談記録を作成

    Args:
        consultation_data: 相談記録作成データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        ConsultationResponse: 作成された相談記録

    Raises:
        HTTPException: 利用者またはスタッフが見つからない
    """
    # 利用者の存在確認
    user = db.query(User).filter(User.id == consultation_data.user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された利用者が見つかりません"
        )

    # スタッフの存在確認
    staff = db.query(Staff).filter(Staff.id == consultation_data.staff_id).first()
    if not staff or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定されたスタッフが見つかりません"
        )

    new_consultation = Consultation(**consultation_data.model_dump())
    db.add(new_consultation)
    db.commit()
    db.refresh(new_consultation)

    return new_consultation


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    相談記録詳細を取得

    Args:
        consultation_id: 相談記録ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        ConsultationResponse: 相談記録情報

    Raises:
        HTTPException: 相談記録が見つからない
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="相談記録が見つかりません"
        )
    return consultation


@router.put("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    consultation_data: ConsultationUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    相談記録を更新

    Args:
        consultation_id: 相談記録ID
        consultation_data: 更新データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        ConsultationResponse: 更新された相談記録

    Raises:
        HTTPException: 相談記録が見つからない
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="相談記録が見つかりません"
        )

    # データを更新
    update_data = consultation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consultation, field, value)

    db.commit()
    db.refresh(consultation)

    return consultation


@router.delete("/{consultation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    相談記録を論理削除

    Args:
        consultation_id: 相談記録ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Raises:
        HTTPException: 相談記録が見つかりません
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="相談記録が見つかりません"
        )

    consultation.is_deleted = True
    db.commit()


@router.get("/{consultation_id}/pdf")
def download_consultation_pdf(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    相談記録をPDF形式でダウンロード

    Args:
        consultation_id: 相談記録ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDF data

    Raises:
        HTTPException: 相談記録が見つからない
    """
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id,
        Consultation.is_deleted == False
    ).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された相談記録が見つかりません"
        )

    # 利用者情報を取得してファイル名に使用
    user = db.query(User).filter(User.id == consultation.user_id).first()
    user_name = user.name if user else f"利用者{consultation.user_id}"

    # PDF生成サービスを使用してPDF作成
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_consultation_pdf(consultation)

    # ファイル名を生成（日本語対応）
    consultation_date = consultation.consultation_date.strftime('%Y%m%d') if consultation.consultation_date else f"相談{consultation_id}"
    filename = f"相談記録_{user_name}_{consultation_date}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )
