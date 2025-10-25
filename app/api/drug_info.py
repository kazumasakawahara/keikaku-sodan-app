"""薬品情報検索API"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from pydantic import BaseModel

from app.models.staff import Staff
from app.api.auth import get_current_staff

router = APIRouter(prefix="/drug-info", tags=["drug-info"])


class DrugSearchResult(BaseModel):
    """薬品検索結果"""
    name: str
    generic_name: Optional[str] = None
    effects: Optional[str] = None
    side_effects: Optional[str] = None
    dosage_form: Optional[str] = None
    manufacturer: Optional[str] = None
    warnings: Optional[str] = None
    source: str


@router.get("/search", response_model=List[DrugSearchResult])
async def search_drug_info(
    query: str,
    current_staff: Staff = Depends(get_current_staff)
):
    """
    薬品情報を検索

    複数の情報源から薬品情報を検索します:
    1. 内部データベース(将来的な拡張)
    2. 一般的な医薬品情報(基本的な情報)

    注: 実際の医薬品情報APIは有料サービスが多いため、
    ここではデモ用の基本情報を返します。
    実運用時は、PMDA API、医薬品医療機器情報提供ホームページ等との連携を推奨します。
    """
    if not query or len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="検索キーワードは2文字以上で入力してください"
        )

    results = []

    # デモ用の薬品情報データベース(実際はAPIや外部DBから取得)
    demo_drugs = _get_demo_drug_database()

    # 検索キーワードでフィルタリング
    query_lower = query.lower()
    for drug in demo_drugs:
        if (query_lower in drug["name"].lower() or
            (drug.get("generic_name") and query_lower in drug["generic_name"].lower())):
            results.append(DrugSearchResult(**drug))

    if not results:
        # 検索結果がない場合は、基本情報のみ返す
        results.append(DrugSearchResult(
            name=query,
            generic_name=None,
            effects="※この薬品の詳細情報は登録されていません。薬剤師または医師にご確認ください。",
            side_effects=None,
            dosage_form=None,
            manufacturer=None,
            warnings="※必ず医師の指示に従って服用してください。",
            source="内部データベース"
        ))

    return results


def _get_demo_drug_database() -> List[Dict[str, Any]]:
    """デモ用の薬品情報データベース"""
    return [
        {
            "name": "リスペリドン錠",
            "generic_name": "リスペリドン",
            "effects": "統合失調症の治療に使用される抗精神病薬です。陽性症状(幻覚、妄想)や陰性症状(意欲低下、感情の平板化)を改善します。",
            "side_effects": "眠気、めまい、体重増加、口の渇き、便秘、不眠、震え、筋肉のこわばり等。重大な副作用として悪性症候群、遅発性ジスキネジアがあります。",
            "dosage_form": "錠剤、細粒、内用液",
            "manufacturer": "複数社",
            "warnings": "運転操作は避けてください。アルコールとの併用は避けてください。定期的な血液検査が必要です。",
            "source": "内部データベース"
        },
        {
            "name": "エチゾラム錠",
            "generic_name": "エチゾラム",
            "effects": "不安、緊張、抑うつ、睡眠障害の改善に使用されるベンゾジアゼピン系抗不安薬です。",
            "side_effects": "眠気、ふらつき、脱力感、倦怠感、口の渇き。長期服用で依存性が生じる可能性があります。",
            "dosage_form": "錠剤",
            "manufacturer": "複数社",
            "warnings": "運転操作は避けてください。アルコールとの併用は避けてください。急に中止すると離脱症状が出ることがあります。",
            "source": "内部データベース"
        },
        {
            "name": "ハロペリドール錠",
            "generic_name": "ハロペリドール",
            "effects": "統合失調症の治療に使用される定型抗精神病薬です。幻覚、妄想などの陽性症状を改善します。",
            "side_effects": "錐体外路症状(手足の震え、筋肉のこわばり)、眠気、口の渇き、便秘。重大な副作用として悪性症候群があります。",
            "dosage_form": "錠剤、細粒、注射液",
            "manufacturer": "複数社",
            "warnings": "運転操作は避けてください。定期的な血液検査が必要です。錐体外路症状が出やすいため注意が必要です。",
            "source": "内部データベース"
        },
        {
            "name": "セルトラリン錠",
            "generic_name": "セルトラリン",
            "effects": "うつ病、パニック障害、強迫性障害の治療に使用されるSSRI(選択的セロトニン再取り込み阻害薬)です。",
            "side_effects": "吐き気、食欲不振、下痢、眠気、不眠、性機能障害。まれにセロトニン症候群が起こることがあります。",
            "dosage_form": "錠剤、OD錠",
            "manufacturer": "複数社",
            "warnings": "効果が出るまで2-4週間かかります。急に中止すると離脱症状が出ることがあります。",
            "source": "内部データベース"
        },
        {
            "name": "アムロジピン錠",
            "generic_name": "アムロジピン",
            "effects": "高血圧、狭心症の治療に使用されるカルシウム拮抗薬です。血管を広げて血圧を下げます。",
            "side_effects": "顔のほてり、頭痛、動悸、めまい、むくみ、歯肉肥厚。",
            "dosage_form": "錠剤、OD錠",
            "manufacturer": "複数社",
            "warnings": "グレープフルーツジュースとの併用は避けてください。急に中止すると症状が悪化することがあります。",
            "source": "内部データベース"
        },
        {
            "name": "アリピプラゾール錠",
            "generic_name": "アリピプラゾール",
            "effects": "統合失調症、双極性障害の治療に使用される非定型抗精神病薬です。陽性症状と陰性症状の両方を改善します。",
            "side_effects": "不眠、アカシジア(じっとしていられない)、体重増加、吐き気、便秘。錐体外路症状は比較的少ないです。",
            "dosage_form": "錠剤、OD錠、散剤、内用液",
            "manufacturer": "複数社",
            "warnings": "運転操作は避けてください。定期的な血液検査が必要です。",
            "source": "内部データベース"
        },
        {
            "name": "ロラゼパム錠",
            "generic_name": "ロラゼパム",
            "effects": "不安、緊張、抑うつ、睡眠障害の改善に使用されるベンゾジアゼピン系抗不安薬です。",
            "side_effects": "眠気、ふらつき、脱力感、倦怠感。長期服用で依存性が生じる可能性があります。",
            "dosage_form": "錠剤",
            "manufacturer": "複数社",
            "warnings": "運転操作は避けてください。アルコールとの併用は避けてください。急に中止すると離脱症状が出ることがあります。",
            "source": "内部データベース"
        },
        {
            "name": "クエチアピン錠",
            "generic_name": "クエチアピン",
            "effects": "統合失調症、双極性障害のうつ状態の治療に使用される非定型抗精神病薬です。",
            "side_effects": "眠気、体重増加、口の渇き、便秘、血糖値上昇。",
            "dosage_form": "錠剤、細粒",
            "manufacturer": "複数社",
            "warnings": "運転操作は避けてください。糖尿病の方は注意が必要です。定期的な血液検査が必要です。",
            "source": "内部データベース"
        },
        {
            "name": "パロキセチン錠",
            "generic_name": "パロキセチン",
            "effects": "うつ病、パニック障害、強迫性障害、社交不安障害、PTSDの治療に使用されるSSRIです。",
            "side_effects": "吐き気、食欲不振、眠気、不眠、性機能障害、体重増加。",
            "dosage_form": "錠剤",
            "manufacturer": "複数社",
            "warnings": "効果が出るまで2-4週間かかります。急に中止すると離脱症状が強く出ることがあります。",
            "source": "内部データベース"
        },
        {
            "name": "レボドパ・カルビドパ配合錠",
            "generic_name": "レボドパ・カルビドパ",
            "effects": "パーキンソン病の治療に使用される薬です。脳内のドパミンを増やして症状を改善します。",
            "side_effects": "吐き気、食欲不振、不随意運動、幻覚、妄想、起立性低血圧。",
            "dosage_form": "錠剤",
            "manufacturer": "複数社",
            "warnings": "食事との関係で効果が変わることがあります。急に中止しないでください。",
            "source": "内部データベース"
        }
    ]


@router.get("/detail/{drug_name}")
async def get_drug_detail(
    drug_name: str,
    current_staff: Staff = Depends(get_current_staff)
):
    """
    特定の薬品の詳細情報を取得
    """
    demo_drugs = _get_demo_drug_database()

    for drug in demo_drugs:
        if drug["name"].lower() == drug_name.lower():
            return DrugSearchResult(**drug)

    # 見つからない場合は基本情報のみ返す
    return DrugSearchResult(
        name=drug_name,
        generic_name=None,
        effects="※この薬品の詳細情報は登録されていません。薬剤師または医師にご確認ください。",
        side_effects=None,
        dosage_form=None,
        manufacturer=None,
        warnings="※必ず医師の指示に従って服用してください。",
        source="内部データベース"
    )
