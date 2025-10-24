"""
アプリケーション設定

環境変数から設定を読み込みます。
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """アプリケーション設定クラス"""

    # データベース設定
    database_url: str = "sqlite:///./keikaku_sodan.db"

    # セキュリティ設定
    secret_key: str = "your-secret-key-change-in-production"
    session_timeout_minutes: int = 30

    # アプリケーション設定
    app_name: str = "計画相談支援 利用者管理システム"
    app_version: str = "0.1.0"
    debug: bool = True

    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()
