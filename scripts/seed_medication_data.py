"""
服薬情報のテストデータ投入スクリプト
"""
import sys
from pathlib import Path
from datetime import date, timedelta

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_db
from app.models.prescribing_doctor import PrescribingDoctor
from app.models.medication import Medication
from app.models.user import User


def seed_medication_data():
    """服薬情報のテストデータを投入"""
    print("💊 服薬情報のテストデータを投入しています...")

    db = next(get_db())
    try:
        # 既存の利用者を取得
        users = db.query(User).limit(3).all()
        if not users:
            print("⚠️  利用者が見つかりません。先にseed_data.pyを実行してください。")
            return

        # 処方医のテストデータ
        doctors = [
            PrescribingDoctor(
                name="田中 太郎",
                hospital_name="北九州総合病院",
                department="精神科",
                phone="093-123-4567",
                address="福岡県北九州市小倉北区○○町1-2-3"
            ),
            PrescribingDoctor(
                name="山田 花子",
                hospital_name="小倉メンタルクリニック",
                department="心療内科",
                phone="093-234-5678",
                address="福岡県北九州市小倉南区△△町4-5-6"
            ),
            PrescribingDoctor(
                name="佐藤 次郎",
                hospital_name="八幡東病院",
                department="内科",
                phone="093-345-6789",
                address="福岡県北九州市八幡東区□□町7-8-9"
            ),
        ]

        for doctor in doctors:
            db.add(doctor)
        db.commit()
        print(f"✅ {len(doctors)}件の処方医を登録しました")

        # 処方医をリロード
        for doctor in doctors:
            db.refresh(doctor)

        # 服薬情報のテストデータ
        medications = [
            # 1人目の利用者（現在服用中）
            Medication(
                user_id=users[0].id,
                prescribing_doctor_id=doctors[0].id,
                medication_name="リスペリドン錠",
                generic_name="リスペリドン",
                dosage="2mg",
                frequency="1日2回",
                timing="朝・夕食後",
                start_date=date.today() - timedelta(days=180),
                is_current=True,
                purpose="統合失調症の治療"
            ),
            Medication(
                user_id=users[0].id,
                prescribing_doctor_id=doctors[0].id,
                medication_name="エチゾラム錠",
                generic_name="エチゾラム",
                dosage="0.5mg",
                frequency="1日1回",
                timing="就寝前",
                start_date=date.today() - timedelta(days=90),
                is_current=True,
                purpose="不眠症の改善",
                notes="必要時のみ服用"
            ),
            # 1人目の利用者（過去の薬）
            Medication(
                user_id=users[0].id,
                prescribing_doctor_id=doctors[0].id,
                medication_name="ハロペリドール錠",
                generic_name="ハロペリドール",
                dosage="1mg",
                frequency="1日3回",
                timing="毎食後",
                start_date=date.today() - timedelta(days=365),
                end_date=date.today() - timedelta(days=180),
                is_current=False,
                purpose="統合失調症の治療",
                notes="副作用のため変更"
            ),
        ]

        if len(users) > 1:
            # 2人目の利用者
            medications.extend([
                Medication(
                    user_id=users[1].id,
                    prescribing_doctor_id=doctors[1].id,
                    medication_name="セルトラリン錠",
                    generic_name="セルトラリン",
                    dosage="50mg",
                    frequency="1日1回",
                    timing="朝食後",
                    start_date=date.today() - timedelta(days=120),
                    is_current=True,
                    purpose="うつ病の治療"
                ),
                Medication(
                    user_id=users[1].id,
                    prescribing_doctor_id=doctors[2].id,
                    medication_name="アムロジピン錠",
                    generic_name="アムロジピン",
                    dosage="5mg",
                    frequency="1日1回",
                    timing="朝食後",
                    start_date=date.today() - timedelta(days=200),
                    is_current=True,
                    purpose="高血圧の治療"
                ),
            ])

        if len(users) > 2:
            # 3人目の利用者
            medications.extend([
                Medication(
                    user_id=users[2].id,
                    prescribing_doctor_id=doctors[1].id,
                    medication_name="アリピプラゾール錠",
                    generic_name="アリピプラゾール",
                    dosage="12mg",
                    frequency="1日1回",
                    timing="朝食後",
                    start_date=date.today() - timedelta(days=150),
                    is_current=True,
                    purpose="双極性障害の治療"
                ),
            ])

        for medication in medications:
            db.add(medication)
        db.commit()
        print(f"✅ {len(medications)}件の服薬情報を登録しました")

        # 登録したデータの確認
        print("\n📋 登録された服薬情報:")
        for user in users:
            user_meds = db.query(Medication).filter(Medication.user_id == user.id).all()
            if user_meds:
                print(f"\n  {user.name}:")
                for med in user_meds:
                    status = "現在服用中" if med.is_current else "服用終了"
                    print(f"    - {med.medication_name} ({status})")

        print("\n✅ テストデータの投入が完了しました！")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_medication_data()
