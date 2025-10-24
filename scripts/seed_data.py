"""
シードデータ投入スクリプト

北九州市内の計画相談支援事業所を想定したダミーデータを作成します。
すべてのデータは架空のものです。
"""
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import bcrypt

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import SessionLocal
from app.models import Staff, User, Notebook, Consultation, Organization, UserOrganization, Plan, Monitoring


def hash_password(password: str) -> str:
    """パスワードをハッシュ化（bcryptを直接使用）"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def seed_data():
    """シードデータを投入"""
    db = SessionLocal()

    try:
        print("🌱 シードデータを投入しています...")

        # 1. スタッフデータ（計画相談支援専門員）
        print("\n👔 スタッフを作成中...")
        staff_list = [
            Staff(
                username="admin",
                password_hash=hash_password("admin123"),
                name="管理者 太郎",
                role="admin",
                email="admin@keikaku-sodan-kitakyushu.jp",
                is_active=True
            ),
            Staff(
                username="yamada",
                password_hash=hash_password("yamada123"),
                name="山田 花子",
                role="staff",
                email="yamada@keikaku-sodan-kitakyushu.jp",
                is_active=True
            ),
            Staff(
                username="sato",
                password_hash=hash_password("sato123"),
                name="佐藤 次郎",
                role="staff",
                email="sato@keikaku-sodan-kitakyushu.jp",
                is_active=True
            ),
            Staff(
                username="tanaka",
                password_hash=hash_password("tanaka123"),
                name="田中 美咲",
                role="staff",
                email="tanaka@keikaku-sodan-kitakyushu.jp",
                is_active=True
            ),
        ]
        db.add_all(staff_list)
        db.commit()
        print(f"  ✅ {len(staff_list)}名のスタッフを作成しました")

        # 2. 関係機関データ（北九州市内の事業所）
        print("\n🏢 関係機関を作成中...")
        organizations = [
            # サービス事業所
            Organization(
                name="ワークセンター北九州",
                type="サービス事業所",
                postal_code="803-0814",
                address="福岡県北九州市小倉北区大手町12-3",
                phone="093-521-1234",
                fax="093-521-1235",
                email="info@work-center-kitakyushu.jp",
                contact_person="鈴木 一郎",
                contact_person_phone="093-521-1234",
                notes="就労継続支援B型事業所"
            ),
            Organization(
                name="生活支援センター門司",
                type="サービス事業所",
                postal_code="801-0841",
                address="福岡県北九州市門司区西海岸1-4-5",
                phone="093-321-5678",
                contact_person="高橋 美穂",
                contact_person_phone="093-321-5678",
                notes="生活介護事業所"
            ),
            Organization(
                name="グループホーム小倉南",
                type="サービス事業所",
                postal_code="802-0985",
                address="福岡県北九州市小倉南区志井2-3-4",
                phone="093-961-2345",
                contact_person="伊藤 健太",
                contact_person_phone="093-961-2345",
                notes="共同生活援助事業所"
            ),
            Organization(
                name="八幡西就労支援センター",
                type="サービス事業所",
                postal_code="806-0028",
                address="福岡県北九州市八幡西区熊手1-1-1",
                phone="093-641-3456",
                contact_person="渡辺 直子",
                contact_person_phone="093-641-3456",
                notes="就労継続支援A型事業所"
            ),
            # 医療機関
            Organization(
                name="北九州市立医療センター",
                type="医療機関",
                postal_code="802-0077",
                address="福岡県北九州市小倉北区馬借2-1-1",
                phone="093-541-1831",
                contact_person="精神科外来",
                contact_person_phone="093-541-1831",
                notes="総合病院・精神科あり"
            ),
            Organization(
                name="門司メンタルクリニック",
                type="医療機関",
                postal_code="800-0025",
                address="福岡県北九州市門司区柳町2-5-6",
                phone="093-381-4567",
                contact_person="木村 医師",
                contact_person_phone="093-381-4567",
                notes="精神科・心療内科専門"
            ),
            Organization(
                name="小倉南病院",
                type="医療機関",
                postal_code="802-0973",
                address="福岡県北九州市小倉南区守恒本町1-10-18",
                phone="093-961-5678",
                contact_person="医療相談室",
                contact_person_phone="093-961-5678",
                notes="療養型病院"
            ),
            # 後見人等
            Organization(
                name="法律事務所北九州",
                type="後見人",
                postal_code="803-0812",
                address="福岡県北九州市小倉北区室町1-1-1",
                phone="093-551-6789",
                contact_person="弁護士 小林 太郎",
                contact_person_phone="093-551-6789",
                notes="成年後見業務対応"
            ),
            Organization(
                name="司法書士事務所門司",
                type="後見人",
                postal_code="801-0863",
                address="福岡県北九州市門司区栄町3-2-1",
                phone="093-331-7890",
                contact_person="司法書士 中村 花子",
                contact_person_phone="093-331-7890",
                notes="成年後見・保佐・補助業務"
            ),
            # その他関係機関
            Organization(
                name="北九州市障害者基幹相談支援センター",
                type="その他",
                postal_code="802-0803",
                address="福岡県北九州市小倉南区春ケ丘10-2",
                phone="093-922-5596",
                contact_person="相談支援課",
                contact_person_phone="093-922-5596",
                notes="基幹相談支援センター"
            ),
        ]
        db.add_all(organizations)
        db.commit()
        print(f"  ✅ {len(organizations)}件の関係機関を作成しました")

        # 3. 利用者データ（北九州市在住）
        print("\n👥 利用者を作成中...")
        users = [
            User(
                name="鈴木 花子",
                name_kana="スズキ ハナコ",
                birth_date=date(1980, 5, 15),
                gender="女性",
                postal_code="802-0001",
                address="福岡県北九州市小倉北区浅野1-2-3 浅野マンション101",
                phone="093-123-4567",
                email="hanako@example.com",
                emergency_contact_name="鈴木 太郎（夫）",
                emergency_contact_phone="090-1234-5678",
                disability_support_level=4,
                disability_support_certified_date=date(2023, 4, 1),
                disability_support_expiry_date=date(2026, 3, 31),
                guardian_type=None,
                assigned_staff_id=2  # 山田スタッフ
            ),
            User(
                name="田中 一郎",
                name_kana="タナカ イチロウ",
                birth_date=date(1975, 11, 8),
                gender="男性",
                postal_code="801-0841",
                address="福岡県北九州市門司区西海岸2-5-6",
                phone="093-321-7890",
                emergency_contact_name="田中 春子（母）",
                emergency_contact_phone="090-2345-6789",
                disability_support_level=5,
                disability_support_certified_date=date(2022, 10, 1),
                disability_support_expiry_date=date(2025, 9, 30),
                guardian_type="後見",
                guardian_name="弁護士 小林 太郎",
                guardian_contact="093-551-6789",
                assigned_staff_id=3  # 佐藤スタッフ
            ),
            User(
                name="高橋 美咲",
                name_kana="タカハシ ミサキ",
                birth_date=date(1992, 3, 22),
                gender="女性",
                postal_code="802-0985",
                address="福岡県北九州市小倉南区志井3-4-5 グリーンハイツ202",
                phone="093-961-3456",
                emergency_contact_name="高橋 健一（父）",
                emergency_contact_phone="090-3456-7890",
                disability_support_level=3,
                disability_support_certified_date=date(2024, 1, 1),
                disability_support_expiry_date=date(2027, 12, 31),
                assigned_staff_id=2  # 山田スタッフ
            ),
            User(
                name="伊藤 健太",
                name_kana="イトウ ケンタ",
                birth_date=date(1988, 7, 30),
                gender="男性",
                postal_code="806-0028",
                address="福岡県北九州市八幡西区熊手2-2-2",
                phone="093-641-5678",
                emergency_contact_name="伊藤 由美（妻）",
                emergency_contact_phone="090-4567-8901",
                disability_support_level=2,
                disability_support_certified_date=date(2023, 7, 1),
                disability_support_expiry_date=date(2026, 6, 30),
                assigned_staff_id=4  # 田中スタッフ
            ),
            User(
                name="渡辺 直子",
                name_kana="ワタナベ ナオコ",
                birth_date=date(1995, 12, 5),
                gender="女性",
                postal_code="800-0025",
                address="福岡県北九州市門司区柳町3-6-7",
                phone="093-381-6789",
                emergency_contact_name="渡辺 正夫（父）",
                emergency_contact_phone="090-5678-9012",
                disability_support_level=3,
                disability_support_certified_date=date(2024, 4, 1),
                disability_support_expiry_date=date(2027, 3, 31),
                guardian_type="保佐",
                guardian_name="司法書士 中村 花子",
                guardian_contact="093-331-7890",
                assigned_staff_id=3  # 佐藤スタッフ
            ),
        ]
        db.add_all(users)
        db.commit()
        print(f"  ✅ {len(users)}名の利用者を作成しました")

        # 4. 手帳データ
        print("\n📓 手帳情報を作成中...")
        notebooks = [
            # 鈴木花子: 療育手帳 + 精神障害者保健福祉手帳（重複所持）
            Notebook(
                user_id=1,
                notebook_type="療育手帳",
                grade="B2",
                issue_date=date(2015, 4, 1),
                renewal_date=date(2025, 4, 1),
                notes="知的障害"
            ),
            Notebook(
                user_id=1,
                notebook_type="精神障害者保健福祉手帳",
                grade="2級",
                issue_date=date(2018, 6, 1),
                renewal_date=date(2024, 6, 1),
                notes="統合失調症"
            ),
            # 田中一郎: 療育手帳のみ
            Notebook(
                user_id=2,
                notebook_type="療育手帳",
                grade="A2",
                issue_date=date(2005, 8, 1),
                renewal_date=date(2025, 8, 1),
                notes="知的障害（重度）"
            ),
            # 高橋美咲: 精神障害者保健福祉手帳のみ
            Notebook(
                user_id=3,
                notebook_type="精神障害者保健福祉手帳",
                grade="3級",
                issue_date=date(2020, 3, 1),
                renewal_date=date(2026, 3, 1),
                notes="うつ病"
            ),
            # 伊藤健太: 精神障害者保健福祉手帳のみ
            Notebook(
                user_id=4,
                notebook_type="精神障害者保健福祉手帳",
                grade="2級",
                issue_date=date(2019, 9, 1),
                renewal_date=date(2025, 9, 1),
                notes="双極性障害"
            ),
            # 渡辺直子: 療育手帳のみ
            Notebook(
                user_id=5,
                notebook_type="療育手帳",
                grade="B1",
                issue_date=date(2016, 5, 1),
                renewal_date=date(2026, 5, 1),
                notes="知的障害"
            ),
        ]
        db.add_all(notebooks)
        db.commit()
        print(f"  ✅ {len(notebooks)}件の手帳情報を作成しました")

        # 5. 相談記録データ
        print("\n📝 相談記録を作成中...")
        base_date = datetime.now()
        consultations = [
            # 最近の相談記録
            Consultation(
                user_id=1,
                staff_id=2,
                consultation_date=base_date - timedelta(days=1),
                consultation_type="来所",
                content="就労支援の利用について相談。B型作業所からA型への移行を希望している。",
                response="近隣のA型事業所を3か所紹介。見学日程調整を次回実施予定。"
            ),
            Consultation(
                user_id=2,
                staff_id=3,
                consultation_date=base_date - timedelta(days=3),
                consultation_type="訪問",
                content="自宅での生活状況確認。最近の体調について聞き取り。",
                response="概ね安定。次回モニタリングは来月実施予定。"
            ),
            Consultation(
                user_id=3,
                staff_id=2,
                consultation_date=base_date - timedelta(days=5),
                consultation_type="電話",
                content="通所先の変更について相談。現在の事業所との相性が合わない様子。",
                response="他の事業所の情報を提供。見学調整を行う。"
            ),
            Consultation(
                user_id=4,
                staff_id=4,
                consultation_date=base_date - timedelta(days=7),
                consultation_type="来所",
                content="障害支援区分の更新について説明。必要書類の確認。",
                response="更新申請書類を準備。主治医意見書の依頼状を交付。"
            ),
            Consultation(
                user_id=5,
                staff_id=3,
                consultation_date=base_date - timedelta(days=10),
                consultation_type="訪問",
                content="グループホームの入居相談。現在の一人暮らしに不安がある。",
                response="市内のグループホーム3か所の情報を提供。見学を調整中。"
            ),
            # 過去の相談記録
            Consultation(
                user_id=1,
                staff_id=2,
                consultation_date=base_date - timedelta(days=30),
                consultation_type="来所",
                content="サービス利用計画の更新について。現在のサービスの満足度を確認。",
                response="概ね満足している様子。計画の大きな変更は不要。"
            ),
            Consultation(
                user_id=3,
                staff_id=2,
                consultation_date=base_date - timedelta(days=45),
                consultation_type="電話",
                content="体調不良による通所欠席の連絡。",
                response="事業所へ連絡済み。回復後、通所再開の支援を行う。"
            ),
        ]
        db.add_all(consultations)
        db.commit()
        print(f"  ✅ {len(consultations)}件の相談記録を作成しました")

        # 6. 利用者-関係機関の紐付け
        print("\n🔗 利用者と関係機関の紐付けを作成中...")
        user_orgs = [
            # 鈴木花子
            UserOrganization(
                user_id=1,
                organization_id=1,  # ワークセンター北九州
                relationship_type="通所先",
                start_date=date(2020, 4, 1),
                frequency="毎日",
                notes="就労継続支援B型を利用中"
            ),
            UserOrganization(
                user_id=1,
                organization_id=5,  # 北九州市立医療センター
                relationship_type="主治医",
                start_date=date(2018, 6, 1),
                frequency="月1回",
                notes="精神科通院中"
            ),
            # 田中一郎
            UserOrganization(
                user_id=2,
                organization_id=2,  # 生活支援センター門司
                relationship_type="通所先",
                start_date=date(2019, 5, 1),
                frequency="週5回",
                notes="生活介護を利用中"
            ),
            UserOrganization(
                user_id=2,
                organization_id=6,  # 門司メンタルクリニック
                relationship_type="主治医",
                start_date=date(2010, 3, 1),
                frequency="月1回"
            ),
            UserOrganization(
                user_id=2,
                organization_id=8,  # 法律事務所北九州
                relationship_type="後見人",
                start_date=date(2015, 7, 1),
                frequency="その他",
                notes="成年後見人として契約"
            ),
            # 高橋美咲
            UserOrganization(
                user_id=3,
                organization_id=3,  # グループホーム小倉南
                relationship_type="居住先",
                start_date=date(2022, 4, 1),
                frequency="毎日",
                notes="共同生活援助を利用中"
            ),
            UserOrganization(
                user_id=3,
                organization_id=7,  # 小倉南病院
                relationship_type="主治医",
                start_date=date(2020, 1, 1),
                frequency="月1回"
            ),
            # 伊藤健太
            UserOrganization(
                user_id=4,
                organization_id=4,  # 八幡西就労支援センター
                relationship_type="通所先",
                start_date=date(2021, 6, 1),
                frequency="週5回",
                notes="就労継続支援A型を利用中"
            ),
            # 渡辺直子
            UserOrganization(
                user_id=5,
                organization_id=2,  # 生活支援センター門司
                relationship_type="通所先",
                start_date=date(2023, 4, 1),
                frequency="週3回",
                notes="生活介護を利用中"
            ),
            UserOrganization(
                user_id=5,
                organization_id=9,  # 司法書士事務所門司
                relationship_type="後見人",
                start_date=date(2020, 2, 1),
                frequency="その他",
                notes="保佐人として契約"
            ),
        ]
        db.add_all(user_orgs)
        db.commit()
        print(f"  ✅ {len(user_orgs)}件の紐付けを作成しました")

        # 7. サービス利用計画データ
        print("\n📋 サービス利用計画を作成中...")
        plans = [
            # 鈴木花子の計画
            Plan(
                user_id=1,
                staff_id=2,
                plan_type="更新",
                plan_number="2024-001",
                created_date=date(2024, 3, 15),
                start_date=date(2024, 4, 1),
                end_date=date(2025, 3, 31),
                current_situation="就労継続支援B型事業所に通所中。作業に慣れてきており、A型への移行を希望している。",
                hopes_and_needs="将来的には一般就労を目指したい。まずはA型事業所で経験を積みたい。",
                support_policy="本人の希望を尊重しつつ、段階的にステップアップできるよう支援する。",
                long_term_goal="就労継続支援A型事業所での安定した就労",
                long_term_goal_period="12ヶ月",
                short_term_goal="A型事業所の見学と体験利用",
                short_term_goal_period="3ヶ月",
                services=[
                    {"service_type": "就労継続支援B型", "provider": "ワークセンター北九州", "frequency": "週5回", "hours": "6時間/日"},
                    {"service_type": "計画相談支援", "provider": "当事業所", "frequency": "月1回", "hours": "-"}
                ],
                approval_status="実施中",
                approval_date=date(2024, 3, 20)
            ),
            # 田中一郎の計画
            Plan(
                user_id=2,
                staff_id=3,
                plan_type="更新",
                plan_number="2024-002",
                created_date=date(2024, 9, 10),
                start_date=date(2024, 10, 1),
                end_date=date(2025, 9, 30),
                current_situation="生活介護事業所に通所中。日常生活全般に介助が必要。成年後見人が財産管理を行っている。",
                hopes_and_needs="現在の生活を継続したい。楽しく通所できる環境を維持してほしい。",
                support_policy="本人の生活リズムを大切にしながら、健康管理と社会参加の機会を確保する。",
                long_term_goal="健康を維持し、現在の通所を継続する",
                long_term_goal_period="12ヶ月",
                short_term_goal="季節の行事やイベントに参加し、楽しみを見つける",
                short_term_goal_period="6ヶ月",
                services=[
                    {"service_type": "生活介護", "provider": "生活支援センター門司", "frequency": "週5回", "hours": "5時間/日"},
                    {"service_type": "計画相談支援", "provider": "当事業所", "frequency": "3ヶ月に1回", "hours": "-"}
                ],
                approval_status="実施中",
                approval_date=date(2024, 9, 15)
            ),
            # 高橋美咲の計画
            Plan(
                user_id=3,
                staff_id=2,
                plan_type="初回",
                plan_number="2024-003",
                created_date=date(2024, 3, 1),
                start_date=date(2024, 4, 1),
                end_date=date(2025, 3, 31),
                current_situation="グループホームに入居中。うつ病の症状は安定している。",
                hopes_and_needs="グループホームでの生活を続けながら、就労を目指したい。",
                support_policy="居住の場を確保しつつ、就労に向けた準備を段階的に進める。",
                long_term_goal="就労継続支援事業所での就労",
                long_term_goal_period="12ヶ月",
                short_term_goal="生活リズムを整え、通所の準備をする",
                short_term_goal_period="6ヶ月",
                services=[
                    {"service_type": "共同生活援助", "provider": "グループホーム小倉南", "frequency": "毎日", "hours": "-"},
                    {"service_type": "計画相談支援", "provider": "当事業所", "frequency": "月1回", "hours": "-"}
                ],
                approval_status="実施中",
                approval_date=date(2024, 3, 5)
            ),
            # 伊藤健太の計画
            Plan(
                user_id=4,
                staff_id=4,
                plan_type="更新",
                plan_number="2024-004",
                created_date=date(2024, 5, 20),
                start_date=date(2024, 6, 1),
                end_date=date(2025, 5, 31),
                current_situation="就労継続支援A型事業所に通所中。双極性障害の症状は服薬でコントロールできている。",
                hopes_and_needs="現在の仕事を続けながら、スキルアップしたい。",
                support_policy="安定した就労を継続しつつ、本人の希望に応じた支援を行う。",
                long_term_goal="一般就労への移行",
                long_term_goal_period="24ヶ月",
                short_term_goal="現在の職場での役割を拡大し、自信をつける",
                short_term_goal_period="6ヶ月",
                services=[
                    {"service_type": "就労継続支援A型", "provider": "八幡西就労支援センター", "frequency": "週5回", "hours": "6時間/日"},
                    {"service_type": "計画相談支援", "provider": "当事業所", "frequency": "月1回", "hours": "-"}
                ],
                approval_status="実施中",
                approval_date=date(2024, 5, 25)
            ),
            # 渡辺直子の計画（作成中）
            Plan(
                user_id=5,
                staff_id=3,
                plan_type="更新",
                plan_number="2024-005",
                created_date=date(2024, 10, 20),
                start_date=date(2024, 11, 1),
                end_date=date(2025, 10, 31),
                current_situation="生活介護事業所に週3回通所中。一人暮らしに不安を感じており、グループホーム入居を検討している。",
                hopes_and_needs="安心して暮らせる場所がほしい。グループホームに入居したい。",
                support_policy="グループホームの見学と体験を通して、本人に合った居住の場を探す。",
                long_term_goal="グループホームでの安定した生活",
                long_term_goal_period="12ヶ月",
                short_term_goal="複数のグループホームを見学し、入居先を決定する",
                short_term_goal_period="3ヶ月",
                services=[
                    {"service_type": "生活介護", "provider": "生活支援センター門司", "frequency": "週3回", "hours": "4時間/日"},
                    {"service_type": "計画相談支援", "provider": "当事業所", "frequency": "月2回", "hours": "-"}
                ],
                approval_status="作成中",
                approval_date=None
            ),
        ]
        db.add_all(plans)
        db.commit()
        print(f"  ✅ {len(plans)}件のサービス利用計画を作成しました")

        # 8. モニタリング記録データ
        print("\n📊 モニタリング記録を作成中...")
        monitorings = [
            # 鈴木花子のモニタリング
            Monitoring(
                plan_id=1,
                user_id=1,
                staff_id=2,
                monitoring_date=date(2024, 7, 15),
                monitoring_type="定期",
                service_usage_status="B型事業所に安定して通所できている。作業内容にも慣れてきた。",
                goal_achievement="A型事業所3か所を見学済み。そのうち1か所で体験利用を開始した。",
                satisfaction="満足",
                changes_in_needs="体験利用先での手応えを感じており、移行への意欲が高まっている。",
                issues_and_concerns="体験利用と現在の通所の両立で疲れが見られる。",
                future_policy="体験利用の状況を見ながら、無理のないペースで移行を進める。",
                plan_revision_needed=False,
                next_monitoring_date=date(2024, 10, 15)
            ),
            Monitoring(
                plan_id=1,
                user_id=1,
                staff_id=2,
                monitoring_date=date(2024, 10, 15),
                monitoring_type="定期",
                service_usage_status="B型事業所とA型事業所の体験利用を並行して行っている。",
                goal_achievement="A型事業所での体験利用が順調。正式な移行時期を検討中。",
                satisfaction="やや満足",
                changes_in_needs="移行時期について具体的に決めたい。",
                issues_and_concerns="特になし。",
                future_policy="来年度からのA型移行を目標に、準備を進める。",
                plan_revision_needed=True,
                next_monitoring_date=date(2025, 1, 15)
            ),
            # 田中一郎のモニタリング
            Monitoring(
                plan_id=2,
                user_id=2,
                staff_id=3,
                monitoring_date=date(2024, 10, 20),
                monitoring_type="定期",
                service_usage_status="生活介護事業所に安定して通所できている。季節の行事を楽しみにしている様子。",
                goal_achievement="秋祭りや運動会などのイベントに積極的に参加した。",
                satisfaction="満足",
                changes_in_needs="特に変化なし。現在の生活を継続希望。",
                issues_and_concerns="高血圧の数値がやや高め。医療機関と連携して経過観察中。",
                future_policy="引き続き健康管理に留意しながら、現在のサービスを継続する。",
                plan_revision_needed=False,
                next_monitoring_date=date(2025, 1, 20)
            ),
            # 高橋美咲のモニタリング
            Monitoring(
                plan_id=3,
                user_id=3,
                staff_id=2,
                monitoring_date=date(2024, 7, 10),
                monitoring_type="定期",
                service_usage_status="グループホームでの生活は順調。他の入居者とも良好な関係を築いている。",
                goal_achievement="生活リズムが整ってきた。規則正しい生活ができている。",
                satisfaction="満足",
                changes_in_needs="就労に向けて、具体的な準備を始めたい。",
                issues_and_concerns="特になし。",
                future_policy="就労継続支援事業所の見学を開始する。",
                plan_revision_needed=False,
                next_monitoring_date=date(2024, 10, 10)
            ),
            Monitoring(
                plan_id=3,
                user_id=3,
                staff_id=2,
                monitoring_date=date(2024, 10, 10),
                monitoring_type="定期",
                service_usage_status="グループホームでの生活継続中。B型事業所2か所を見学した。",
                goal_achievement="就労への意欲が高まっている。見学先のうち1か所が気に入った様子。",
                satisfaction="満足",
                changes_in_needs="体験利用を経て、来年度から通所を開始したい。",
                issues_and_concerns="通所が始まると朝早い起床が必要になる。生活リズムの調整が課題。",
                future_policy="体験利用を実施し、計画の見直しを行う。",
                plan_revision_needed=True,
                next_monitoring_date=date(2025, 1, 10)
            ),
            # 伊藤健太のモニタリング
            Monitoring(
                plan_id=4,
                user_id=4,
                staff_id=4,
                monitoring_date=date(2024, 9, 15),
                monitoring_type="定期",
                service_usage_status="A型事業所に安定して通所中。新しい業務も任されるようになった。",
                goal_achievement="リーダー補佐の役割を担うようになり、自信がついてきた。",
                satisfaction="満足",
                changes_in_needs="一般就労に向けて、情報収集を始めたい。",
                issues_and_concerns="体調管理は良好。服薬も継続できている。",
                future_policy="ハローワークとの連携を検討する。就労移行支援の利用も視野に入れる。",
                plan_revision_needed=False,
                next_monitoring_date=date(2024, 12, 15)
            ),
        ]
        db.add_all(monitorings)
        db.commit()
        print(f"  ✅ {len(monitorings)}件のモニタリング記録を作成しました")

        print("\n✅ シードデータの投入が完了しました！")
        print("\n📊 作成されたデータ:")
        print(f"  - スタッフ: {len(staff_list)}名")
        print(f"  - 関係機関: {len(organizations)}件")
        print(f"  - 利用者: {len(users)}名")
        print(f"  - 手帳情報: {len(notebooks)}件")
        print(f"  - 相談記録: {len(consultations)}件")
        print(f"  - 利用者-関係機関紐付け: {len(user_orgs)}件")
        print(f"  - サービス利用計画: {len(plans)}件")
        print(f"  - モニタリング記録: {len(monitorings)}件")
        print("\n🔑 ログイン情報:")
        print("  管理者: username=admin, password=admin123")
        print("  スタッフ1: username=yamada, password=yamada123")
        print("  スタッフ2: username=sato, password=sato123")
        print("  スタッフ3: username=tanaka, password=tanaka123")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
