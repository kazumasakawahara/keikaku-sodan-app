"""
ネットワーク図API

利用者のネットワーク図データを提供します。
"""
from typing import List, Dict, Any
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.staff import Staff
from app.models.user_organization import UserOrganization
from app.models.organization import Organization
from app.api.auth import get_current_staff
from app.services.pdf_service import PDFService

router = APIRouter()


@router.get("/users/{user_id}/network")
async def get_user_network(
    user_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
) -> Dict[str, Any]:
    """
    利用者のネットワークデータを取得

    Args:
        user_id: 利用者ID
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        Dict[str, Any]: ノードとエッジのネットワークデータ

    Raises:
        HTTPException: 利用者が見つからない
    """
    # 利用者の存在確認
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    # 利用者ノード
    nodes = [
        {
            "id": f"user_{user.id}",
            "label": user.name,
            "type": "user",
            "data": {
                "age": user.age,
                "gender": user.gender,
                "support_level": user.disability_support_level
            }
        }
    ]

    edges = []

    # 関係機関を取得
    user_orgs = db.query(UserOrganization).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.is_deleted == False
    ).all()

    for user_org in user_orgs:
        org = db.query(Organization).filter(
            Organization.id == user_org.organization_id,
            Organization.is_deleted == False
        ).first()

        if org:
            # 組織ノードを追加
            node_id = f"org_{org.id}"

            # 関係種別に応じた色分け
            org_type = _get_org_node_type(user_org.relationship_type, org.type)

            nodes.append({
                "id": node_id,
                "label": org.name,
                "type": org_type,
                "data": {
                    "organization_type": org.type,
                    "relationship_type": user_org.relationship_type,
                    "contact": org.contact_person,
                    "phone": org.phone,
                    "frequency": user_org.frequency
                }
            })

            # エッジを追加
            edges.append({
                "from": f"user_{user.id}",
                "to": node_id,
                "relationship": user_org.relationship_type or "関連",
                "frequency": user_org.frequency,
                "start_date": user_org.start_date.isoformat() if user_org.start_date else None
            })

    # 担当スタッフを追加
    if user.assigned_staff:
        staff_id = f"staff_{user.assigned_staff.id}"
        nodes.append({
            "id": staff_id,
            "label": user.assigned_staff.name,
            "type": "staff",
            "data": {
                "role": user.assigned_staff.role,
                "email": user.assigned_staff.email
            }
        })

        edges.append({
            "from": f"user_{user.id}",
            "to": staff_id,
            "relationship": "担当",
            "frequency": None,
            "start_date": None
        })

    # 後見人情報がある場合
    if user.guardian_name:
        guardian_id = "guardian_1"
        nodes.append({
            "id": guardian_id,
            "label": user.guardian_name,
            "type": "guardian",
            "data": {
                "guardian_type": user.guardian_type,
                "contact": user.guardian_contact
            }
        })

        edges.append({
            "from": f"user_{user.id}",
            "to": guardian_id,
            "relationship": user.guardian_type or "後見人",
            "frequency": None,
            "start_date": None
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "user_id": user_id,
        "user_name": user.name
    }


def _get_org_node_type(relationship_type: str, organization_type: str) -> str:
    """
    関係種別と組織種別からノードタイプを決定

    Args:
        relationship_type: 関係種別
        organization_type: 組織種別

    Returns:
        str: ノードタイプ (service/medical/guardian/other)
    """
    if not relationship_type and not organization_type:
        return "other"

    # 関係種別での判定
    if relationship_type:
        rel = relationship_type.lower()
        if "通所" in rel or "サービス" in rel or "施設" in rel:
            return "service"
        elif "医療" in rel or "病院" in rel or "診療" in rel or "主治医" in rel:
            return "medical"
        elif "後見" in rel:
            return "guardian"

    # 組織種別での判定
    if organization_type:
        org = organization_type.lower()
        if "医療" in org or "病院" in org or "クリニック" in org:
            return "medical"
        elif "福祉" in org or "介護" in org or "障害" in org:
            return "service"

    return "other"


@router.post("/users/{user_id}/network/pdf")
async def download_network_pdf(
    user_id: int,
    image_data: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    ネットワーク図をPDF形式でダウンロード

    Args:
        user_id: 利用者ID
        image_data: Base64エンコードされた画像データ（PNG形式）
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        StreamingResponse: PDF data

    Raises:
        HTTPException: 利用者が見つからない
    """
    # 利用者の存在確認
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された利用者が見つかりません"
        )

    # PDF生成サービスを使用してPDF作成
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_network_pdf(image_data, user.name)

    # ファイル名を生成（日本語対応・URLエンコード）
    filename = f"ネットワーク図_{user.name}.pdf"
    encoded_filename = quote(filename.encode('utf-8'))

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
