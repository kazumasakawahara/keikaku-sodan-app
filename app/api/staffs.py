"""
スタッフ管理API

スタッフのCRUD操作とパスワード変更のエンドポイントを提供します。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse, StaffPasswordChange
from app.utils.auth import get_password_hash, verify_password
from app.api.auth import get_current_staff
from app.utils.kana_converter import hiragana_to_katakana

router = APIRouter()


def require_admin(current_staff: Staff = Depends(get_current_staff)) -> Staff:
    """
    管理者権限を要求する依存性

    Args:
        current_staff: 現在のスタッフ

    Returns:
        Staff: 管理者スタッフ

    Raises:
        HTTPException: 権限不足
    """
    if current_staff.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作には管理者権限が必要です"
        )
    return current_staff


@router.get("", response_model=List[StaffResponse])
def list_staffs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="氏名・ユーザー名・メールアドレスで検索"),
    role: Optional[str] = Query(None, description="権限でフィルタ"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    スタッフ一覧を取得

    Args:
        skip: スキップ件数
        limit: 取得件数上限
        search: 検索キーワード（氏名・ユーザー名・メールアドレス）
        role: 権限
        db: データベースセッション
        current_staff: 現在のスタッフ（認証確認用）

    Returns:
        List[StaffResponse]: スタッフ一覧
    """
    query = db.query(Staff)

    # 曖昧検索（氏名・ユーザー名・メールアドレス + ひらがな→カタカナ変換）
    if search:
        search_katakana = hiragana_to_katakana(search)
        search_pattern = f"%{search}%"
        search_katakana_pattern = f"%{search_katakana}%"
        query = query.filter(
            or_(
                Staff.name.like(search_pattern),
                Staff.name.like(search_katakana_pattern),
                Staff.username.like(search_pattern),
                Staff.username.like(search_katakana_pattern),
                Staff.email.like(search_pattern),
                Staff.email.like(search_katakana_pattern)
            )
        )

    # 権限でフィルタ
    if role:
        query = query.filter(Staff.role == role)

    staffs = query.offset(skip).limit(limit).all()
    return staffs


@router.post("", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    admin: Staff = Depends(require_admin)
):
    """
    スタッフを作成（管理者のみ）

    Args:
        staff_data: スタッフ作成データ
        db: データベースセッション
        admin: 管理者スタッフ

    Returns:
        StaffResponse: 作成されたスタッフ

    Raises:
        HTTPException: ユーザー名重複エラー
    """
    # ユーザー名の重複チェック
    existing_staff = db.query(Staff).filter(Staff.username == staff_data.username).first()
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています"
        )

    # パスワードをハッシュ化
    password_hash = get_password_hash(staff_data.password)

    # 資格リストをカンマ区切り文字列に変換
    qualifications_str = None
    if staff_data.qualifications:
        qualifications_str = ','.join(staff_data.qualifications)

    # スタッフを作成
    new_staff = Staff(
        username=staff_data.username,
        password_hash=password_hash,
        name=staff_data.name,
        email=staff_data.email,
        role=staff_data.role,
        hire_date=staff_data.hire_date,
        qualifications=qualifications_str,
        resignation_date=staff_data.resignation_date
    )

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return new_staff


@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    スタッフ詳細を取得

    Args:
        staff_id: スタッフID
        db: データベースセッション
        current_staff: 現在のスタッフ（認証確認用）

    Returns:
        StaffResponse: スタッフ情報

    Raises:
        HTTPException: スタッフが見つからない
    """
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スタッフが見つかりません"
        )
    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    スタッフ情報を更新

    Args:
        staff_id: スタッフID
        staff_data: 更新データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StaffResponse: 更新されたスタッフ情報

    Raises:
        HTTPException: スタッフが見つからない、または権限不足
    """
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スタッフが見つかりません"
        )

    # 自分自身または管理者のみ更新可能
    if current_staff.id != staff_id and current_staff.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作を実行する権限がありません"
        )

    # 権限変更は管理者のみ可能
    if staff_data.role is not None and current_staff.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限の変更には管理者権限が必要です"
        )

    # データを更新
    update_data = staff_data.model_dump(exclude_unset=True)

    # 資格リストをカンマ区切り文字列に変換
    if 'qualifications' in update_data and update_data['qualifications'] is not None:
        update_data['qualifications'] = ','.join(update_data['qualifications'])

    # 退職日が設定された場合、ステータスを無効に
    if 'resignation_date' in update_data and update_data['resignation_date'] is not None:
        update_data['is_active'] = False

    for field, value in update_data.items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)

    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    admin: Staff = Depends(require_admin)
):
    """
    スタッフを削除（管理者のみ）

    Args:
        staff_id: スタッフID
        db: データベースセッション
        admin: 管理者スタッフ

    Raises:
        HTTPException: スタッフが見つからない、または自分自身を削除しようとした
    """
    if admin.id == staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自分自身を削除することはできません"
        )

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スタッフが見つかりません"
        )

    db.delete(staff)
    db.commit()


@router.post("/{staff_id}/change-password")
def change_password(
    staff_id: int,
    password_data: StaffPasswordChange,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    パスワードを変更

    Args:
        staff_id: スタッフID
        password_data: パスワード変更データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        dict: 成功メッセージ

    Raises:
        HTTPException: 現在のパスワードが正しくない、または権限不足
    """
    if current_staff.id != staff_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のスタッフのパスワードを変更することはできません"
        )

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スタッフが見つかりません"
        )

    # 現在のパスワードを検証
    if not verify_password(password_data.current_password, staff.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在のパスワードが正しくありません"
        )

    # 新しいパスワードをハッシュ化して保存
    staff.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "パスワードを変更しました"}
