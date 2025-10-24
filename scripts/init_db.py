"""
データベース初期化スクリプト

SQLiteデータベースを作成し、全テーブルを初期化します。
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import Base, engine
from app.models import Staff, User, Notebook, Consultation, Organization, UserOrganization


def init_database():
    """データベースを初期化"""
    print("📊 データベースを初期化しています...")

    # 全テーブルを作成
    Base.metadata.create_all(bind=engine)

    print("✅ データベースの初期化が完了しました！")
    print(f"📂 データベースファイル: keikaku_sodan.db")
    print("\n作成されたテーブル:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    init_database()
