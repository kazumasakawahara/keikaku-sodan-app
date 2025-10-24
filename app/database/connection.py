"""
データベース接続管理

SQLAlchemyエンジンとセッションを管理します。
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# SQLAlchemyエンジン作成
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# セッションファクトリー
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db():
    """
    データベースセッションを取得する依存性

    FastAPIの依存性注入で使用します。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
