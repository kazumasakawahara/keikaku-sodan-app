"""
関係機関管理API

関係機関のCRUD操作と利用者との紐付けを提供します。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.organization import Organization
from app.models.user_organization import UserOrganization
from app.models.user import User
from app.models.staff import Staff
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.schemas.user_organization import UserOrganizationCreate, UserOrganizationResponse
from app.api.auth import get_current_staff
from app.utils.kana_converter import hiragana_to_katakana

router = APIRouter()


@router.get("", response_model=List[OrganizationResponse])
def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="機関名・住所・電話番号で検索"),
    type: Optional[str] = Query(None, description="種別でフィルタ"),
    include_deleted: bool = Query(False, description="削除済みを含む"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    関係機関一覧を取得

    Args:
        skip: スキップ件数
        limit: 取得件数上限
        search: 検索キーワード（機関名・住所・電話番号）
        type: 種別フィルタ
        include_deleted: 削除済みを含むか
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[OrganizationResponse]: 関係機関一覧
    """
    query = db.query(Organization)

    # 削除済みフィルタ
    if not include_deleted:
        query = query.filter(Organization.is_deleted == False)

    # 曖昧検索（機関名・住所・電話番号 + ひらがな→カタカナ変換）
    if search:
        search_katakana = hiragana_to_katakana(search)
        search_pattern = f"%{search}%"
        search_katakana_pattern = f"%{search_katakana}%"
        query = query.filter(
            or_(
                Organization.name.like(search_pattern),
                Organization.name.like(search_katakana_pattern),
                Organization.address.like(search_pattern),
                Organization.address.like(search_katakana_pattern),
                Organization.phone.like(search_pattern),
                Organization.phone.like(search_katakana_pattern)
            )
        )

    # 種別フィルタ
    if type:
        query = query.filter(Organization.type == type)

    organizations = query.offset(skip).limit(limit).all()
    return organizations


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    関係機関を作成

    Args:
        organization_data: 関係機関作成データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        OrganizationResponse: 作成された関係機関
    """
    new_organization = Organization(**organization_data.model_dump())
    db.add(new_organization)
    db.commit()
    db.refresh(new_organization)

    return new_organization


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    関係機関詳細を取得

    Args:
        organization_id: 関係機関ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        OrganizationResponse: 関係機関情報

    Raises:
        HTTPException: 関係機関が見つからない
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="関係機関が見つかりません"
        )
    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: int,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    関係機関情報を更新

    Args:
        organization_id: 関係機関ID
        organization_data: 更新データ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        OrganizationResponse: 更新された関係機関情報

    Raises:
        HTTPException: 関係機関が見つからない
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="関係機関が見つかりません"
        )

    # データを更新
    update_data = organization_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    db.commit()
    db.refresh(organization)

    return organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    関係機関を論理削除

    Args:
        organization_id: 関係機関ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Raises:
        HTTPException: 関係機関が見つかりません
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="関係機関が見つかりません"
        )

    organization.is_deleted = True
    db.commit()


# 利用者と関係機関の紐付け

@router.get("/users/{user_id}/organizations", response_model=List[UserOrganizationResponse])
def get_user_organizations(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者に紐付けられた関係機関を取得

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[UserOrganizationResponse]: 利用者-関係機関一覧

    Raises:
        HTTPException: 利用者が見つからない
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    user_organizations = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.is_deleted == False
    ).all()

    return user_organizations


@router.post("/users/{user_id}/organizations", response_model=UserOrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_user_organization(
    user_id: int,
    user_org_data: UserOrganizationCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    利用者と関係機関を紐付ける

    Args:
        user_id: 利用者ID
        user_org_data: 紐付けデータ
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        UserOrganizationResponse: 作成された紐付け

    Raises:
        HTTPException: 利用者または関係機関が見つからない
    """
    # user_idの整合性チェック
    if user_org_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URLのユーザーIDとデータのユーザーIDが一致しません"
        )

    # 利用者の存在確認
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された利用者が見つかりません"
        )

    # 関係機関の存在確認
    organization = db.query(Organization).filter(Organization.id == user_org_data.organization_id).first()
    if not organization or organization.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された関係機関が見つかりません"
        )

    new_user_org = UserOrganization(**user_org_data.model_dump())
    db.add(new_user_org)
    db.commit()
    db.refresh(new_user_org)

    return new_user_org


@router.get("/{organization_id}/users", response_model=List[UserOrganizationResponse])
def get_organization_users(
    organization_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    関係機関に紐付けられた利用者を取得

    Args:
        organization_id: 関係機関ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        List[UserOrganizationResponse]: 利用者-関係機関一覧

    Raises:
        HTTPException: 関係機関が見つからない
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="関係機関が見つかりません"
        )

    user_organizations = db.query(UserOrganization).filter(
        UserOrganization.organization_id == organization_id,
        UserOrganization.is_deleted == False
    ).all()

    return user_organizations
