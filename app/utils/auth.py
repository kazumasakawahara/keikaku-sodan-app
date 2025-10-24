"""
認証ユーティリティ

パスワードハッシュ化、JWT生成などの認証関連機能を提供します。
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from app.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    プレーンパスワードとハッシュ化パスワードを照合する

    Args:
        plain_password: プレーンテキストのパスワード
        password_hash: ハッシュ化されたパスワード

    Returns:
        bool: パスワードが一致する場合True
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        password_hash.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する

    Args:
        password: プレーンテキストのパスワード

    Returns:
        str: ハッシュ化されたパスワード
    """
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWTアクセストークンを生成する

    Args:
        data: トークンに含めるデータ
        expires_delta: 有効期限（デフォルト: 30分）

    Returns:
        str: JWTトークン
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.session_timeout_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm="HS256"
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWTトークンをデコードする

    Args:
        token: JWTトークン

    Returns:
        Optional[dict]: デコードされたペイロード、無効な場合はNone
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None
