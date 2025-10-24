"""
利用者管理API

利用者のCRUD操作と検索機能を提供します。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.user import User
from app.models.staff import Staff
from app.models.notebook import Notebook
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.notebook import NotebookResponse
from app.api.auth import get_current_staff
from app.utils.kana_converter import hiragana_to_katakana
from app.services.pdf_service import PDFService

router = APIRouter()


@router.get("", response_model=List[UserListResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="氏名・カナで検索"),
    name: Optional[str] = Query(None, description="氏名で検索"),
    name_kana: Optional[str] = Query(None, description="カナで検索"),
    staff_id: Optional[int] = Query(None, description="担当スタッフIDでフィルタ"),
    min_age: Optional[int] = Query(None, ge=0, le=150, description="最低年齢"),
    max_age: Optional[int] = Query(None, ge=0, le=150, description="最高年齢"),
    disability_support_level: Optional[int] = Query(None, ge=1, le=6, description="障害支援区分"),
    has_guardian: Optional[bool] = Query(None, description="後見人有無"),
    gender: Optional[str] = Query(None, description="性別"),
    sort_by: str = Query("id", description="ソート項目 (id/name/age)"),
    order: str = Query("asc", description="ソート順 (asc/desc)"),
    include_deleted: bool = Query(False, description="削除済みを含む"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者一覧を取得（高度な検索対応）

    Args:
        skip: スキップ件数
        limit: 取得件数上限
        search: 検索キーワード（氏名・カナ）
        name: 氏名で検索
        name_kana: カナで検索
        staff_id: 担当スタッフID
        min_age: 最低年齢
        max_age: 最高年齢
        disability_support_level: 障害支援区分
        has_guardian: 後見人有無
        gender: 性別
        sort_by: ソート項目
        order: ソート順
        include_deleted: 削除済みを含むか
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[UserListResponse]: 利用者一覧
    """
    query = db.query(User)

    # 削除済みフィルタ
    if not include_deleted:
        query = query.filter(User.is_deleted == False)

    # 検索フィルタ（曖昧検索: 部分一致 + ひらがな→カタカナ変換）
    if search:
        # ひらがなをカタカナに変換して両方のパターンで検索
        search_katakana = hiragana_to_katakana(search)
        search_pattern = f"%{search}%"
        search_katakana_pattern = f"%{search_katakana}%"
        query = query.filter(
            or_(
                User.name.like(search_pattern),
                User.name.like(search_katakana_pattern),
                User.name_kana.like(search_pattern),
                User.name_kana.like(search_katakana_pattern)
            )
        )

    # 氏名フィルタ
    if name:
        query = query.filter(User.name.like(f"%{name}%"))

    # カナフィルタ
    if name_kana:
        query = query.filter(User.name_kana.like(f"%{name_kana}%"))

    # 担当スタッフフィルタ
    if staff_id:
        query = query.filter(User.assigned_staff_id == staff_id)

    # 障害支援区分フィルタ
    if disability_support_level:
        query = query.filter(User.disability_support_level == disability_support_level)

    # 後見人有無フィルタ
    if has_guardian is not None:
        if has_guardian:
            query = query.filter(User.guardian_name.isnot(None))
        else:
            query = query.filter(User.guardian_name.is_(None))

    # 性別フィルタ
    if gender:
        query = query.filter(User.gender == gender)

    # ソート
    if order.lower() == "desc":
        if sort_by == "name":
            query = query.order_by(User.name.desc())
        elif sort_by == "age":
            query = query.order_by(User.birth_date.asc())  # 生年月日の昇順=年齢の降順
        else:
            query = query.order_by(User.id.desc())
    else:
        if sort_by == "name":
            query = query.order_by(User.name.asc())
        elif sort_by == "age":
            query = query.order_by(User.birth_date.desc())  # 生年月日の降順=年齢の昇順
        else:
            query = query.order_by(User.id.asc())

    # 年齢フィルタは取得後に適用（計算プロパティのため）
    users = query.offset(skip).limit(limit * 2).all()  # 年齢フィルタのため多めに取得

    # 年齢フィルタリング
    if min_age is not None or max_age is not None:
        filtered_users = []
        for user in users:
            age = user.age
            if age is None:
                continue
            if min_age is not None and age < min_age:
                continue
            if max_age is not None and age > max_age:
                continue
            filtered_users.append(user)
        users = filtered_users[:limit]
    else:
        users = users[:limit]

    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者を作成

    Args:
        user_data: 利用者作成データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        UserResponse: 作成された利用者

    Raises:
        HTTPException: 担当スタッフが存在しない
    """
    # 担当スタッフの存在確認
    if user_data.assigned_staff_id:
        staff = db.query(Staff).filter(Staff.id == user_data.assigned_staff_id).first()
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定された担当スタッフが見つかりません"
            )

    new_user = User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者詳細を取得

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        UserResponse: 利用者情報

    Raises:
        HTTPException: 利用者が見つからない
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者情報を更新

    Args:
        user_id: 利用者ID
        user_data: 更新データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        UserResponse: 更新された利用者情報

    Raises:
        HTTPException: 利用者が見つからない、または担当スタッフが存在しない
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    # 担当スタッフの存在確認
    if user_data.assigned_staff_id is not None:
        staff = db.query(Staff).filter(Staff.id == user_data.assigned_staff_id).first()
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定された担当スタッフが見つかりません"
            )

    # データを更新
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者を論理削除

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Raises:
        HTTPException: 利用者が見つからない
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    user.is_deleted = True
    db.commit()


@router.get("/{user_id}/notebooks", response_model=List[NotebookResponse])
def get_user_notebooks(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者の手帳情報を取得

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[NotebookResponse]: 手帳一覧

    Raises:
        HTTPException: 利用者が見つからない
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    notebooks = db.query(Notebook).filter(
        Notebook.user_id == user_id,
        Notebook.is_deleted == False
    ).all()

    return notebooks


@router.get("/{user_id}/pdf")
def download_user_pdf(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者基本情報をPDF形式でダウンロード

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDF data

    Raises:
        HTTPException: 利用者が見つからない
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    # PDF生成サービスを使用してPDF作成
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_user_profile_pdf(user)

    # ファイル名を生成（日本語対応）
    filename = f"利用者情報_{user.name}_{user.id}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )
