"""
認証API

ログイン・ログアウト・認証状態確認のエンドポイントを提供します。
"""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.staff import Staff
from app.schemas.staff import StaffLogin, StaffResponse
from app.utils.auth import verify_password, create_access_token, decode_access_token
from app.config import get_settings

router = APIRouter()
settings = get_settings()


def get_current_staff(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db)
) -> Staff:
    """
    現在のログイン中スタッフを取得する依存性

    Args:
        access_token: Cookieから取得したアクセストークン
        db: データベースセッション

    Returns:
        Staff: ログイン中のスタッフ

    Raises:
        HTTPException: 認証エラー
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        raise credentials_exception

    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    staff = db.query(Staff).filter(Staff.username == username).first()
    if staff is None or not staff.is_active:
        raise credentials_exception

    return staff


@router.post("/login", response_model=StaffResponse)
def login(
    credentials: StaffLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    ログイン

    Args:
        credentials: ログイン情報（ユーザー名・パスワード）
        response: レスポンスオブジェクト（Cookieを設定するため）
        db: データベースセッション

    Returns:
        StaffResponse: ログインしたスタッフ情報

    Raises:
        HTTPException: ログイン失敗
    """
    staff = db.query(Staff).filter(Staff.username == credentials.username).first()

    if not staff or not verify_password(credentials.password, staff.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )

    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています",
        )

    # JWTトークンを生成
    access_token = create_access_token(
        data={"sub": staff.username},
        expires_delta=timedelta(minutes=settings.session_timeout_minutes)
    )

    # Cookieにトークンを設定
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.session_timeout_minutes * 60,
        samesite="lax"
    )

    return staff


@router.post("/logout")
def logout(response: Response):
    """
    ログアウト

    Args:
        response: レスポンスオブジェクト（Cookieを削除するため）

    Returns:
        dict: ログアウト成功メッセージ
    """
    response.delete_cookie(key="access_token")
    return {"message": "ログアウトしました"}


@router.get("/me", response_model=StaffResponse)
def get_current_user(
    current_staff: Staff = Depends(get_current_staff)
):
    """
    現在のログインユーザー情報を取得

    Args:
        current_staff: 現在のスタッフ（依存性注入）

    Returns:
        StaffResponse: ログイン中のスタッフ情報
    """
    return current_staff
