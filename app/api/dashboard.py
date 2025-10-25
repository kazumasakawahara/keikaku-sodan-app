"""
ダッシュボードAPI

ダッシュボード統計データとアラート情報を提供します。
"""
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.database.connection import get_db
from app.models.user import User
from app.models.staff import Staff
from app.models.consultation import Consultation
from app.models.plan import Plan
from app.models.monitoring import Monitoring
from app.models.notebook import Notebook
from app.models.medication import Medication
from app.models.prescribing_doctor import PrescribingDoctor
from app.api.auth import get_current_staff

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
) -> Dict[str, Any]:
    """
    ダッシュボード統計データを取得

    Args:
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        Dict[str, Any]: 統計データ
    """
    # 利用者総数
    total_users = db.query(func.count(User.id)).filter(
        User.is_deleted == False
    ).scalar()

    # 実施中の計画数
    active_plans = db.query(func.count(Plan.id)).filter(
        Plan.is_deleted == False,
        Plan.approval_status == "実施中"
    ).scalar()

    # 承認待ち計画数
    pending_approvals = db.query(func.count(Plan.id)).filter(
        Plan.is_deleted == False,
        Plan.approval_status == "承認待ち"
    ).scalar()

    # 今月のモニタリング予定
    today = date.today()
    first_day = date(today.year, today.month, 1)
    if today.month == 12:
        last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)

    upcoming_monitorings = db.query(func.count(Monitoring.id)).filter(
        Monitoring.is_deleted == False,
        Monitoring.monitoring_date >= first_day,
        Monitoring.monitoring_date <= last_day
    ).scalar()

    # 相談記録の種別割合
    consultation_types = db.query(
        Consultation.consultation_type,
        func.count(Consultation.id).label('count')
    ).filter(
        Consultation.is_deleted == False
    ).group_by(Consultation.consultation_type).all()

    consultation_by_type = {ct[0]: ct[1] for ct in consultation_types}

    # 計画の承認状況
    plan_statuses = db.query(
        Plan.approval_status,
        func.count(Plan.id).label('count')
    ).filter(
        Plan.is_deleted == False
    ).group_by(Plan.approval_status).all()

    plan_status = {ps[0]: ps[1] for ps in plan_statuses}

    # 年齢層別利用者数
    users = db.query(User).filter(User.is_deleted == False).all()
    age_groups = {
        "0-17": 0,
        "18-39": 0,
        "40-64": 0,
        "65+": 0,
        "不明": 0
    }

    for user in users:
        age = user.age
        if age is None:
            age_groups["不明"] += 1
        elif age < 18:
            age_groups["0-17"] += 1
        elif age < 40:
            age_groups["18-39"] += 1
        elif age < 65:
            age_groups["40-64"] += 1
        else:
            age_groups["65+"] += 1

    # 月次相談件数（過去6ヶ月）
    monthly_consultations = []
    for i in range(5, -1, -1):
        target_month = today - timedelta(days=30 * i)
        count = db.query(func.count(Consultation.id)).filter(
            Consultation.is_deleted == False,
            extract('year', Consultation.consultation_date) == target_month.year,
            extract('month', Consultation.consultation_date) == target_month.month
        ).scalar()

        monthly_consultations.append({
            "month": target_month.strftime("%Y年%m月"),
            "count": count
        })

    # 服薬情報統計
    total_medications = db.query(func.count(Medication.id)).scalar()
    current_medications = db.query(func.count(Medication.id)).filter(
        Medication.is_current == True
    ).scalar()

    # 服薬中の利用者数
    users_with_medications = db.query(func.count(func.distinct(Medication.user_id))).filter(
        Medication.is_current == True
    ).scalar()

    # 処方医統計
    total_doctors = db.query(func.count(PrescribingDoctor.id)).scalar()

    # 処方医別利用者数（上位5件）
    doctors_with_patient_count = db.query(
        PrescribingDoctor.id,
        PrescribingDoctor.name,
        PrescribingDoctor.hospital_name,
        func.count(func.distinct(Medication.user_id)).label('patient_count')
    ).join(
        Medication, Medication.prescribing_doctor_id == PrescribingDoctor.id
    ).filter(
        Medication.is_current == True
    ).group_by(
        PrescribingDoctor.id
    ).order_by(
        func.count(func.distinct(Medication.user_id)).desc()
    ).limit(5).all()

    top_doctors = [
        {
            "doctor_id": doc.id,
            "doctor_name": doc.name,
            "hospital_name": doc.hospital_name or "",
            "patient_count": doc.patient_count
        }
        for doc in doctors_with_patient_count
    ]

    return {
        "total_users": total_users or 0,
        "active_plans": active_plans or 0,
        "pending_approvals": pending_approvals or 0,
        "upcoming_monitorings": upcoming_monitorings or 0,
        "consultation_by_type": consultation_by_type,
        "plan_status": plan_status,
        "users_by_age_group": age_groups,
        "monthly_consultations": monthly_consultations,
        "medication_stats": {
            "total_medications": total_medications or 0,
            "current_medications": current_medications or 0,
            "users_with_medications": users_with_medications or 0,
            "total_doctors": total_doctors or 0,
            "top_doctors": top_doctors
        }
    }


@router.get("/alerts")
async def get_alerts(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
) -> Dict[str, Any]:
    """
    アラート情報を取得

    Args:
        db: データベースセッション
        current_staff: 現在のスタッフ

    Returns:
        Dict[str, Any]: アラート一覧
    """
    today = date.today()
    three_months_later = today + timedelta(days=90)

    # 計画更新期限が近い（3ヶ月以内）
    plans_expiring_soon = db.query(Plan).join(User).filter(
        Plan.is_deleted == False,
        User.is_deleted == False,
        Plan.end_date.isnot(None),
        Plan.end_date <= three_months_later,
        Plan.end_date >= today
    ).all()

    plan_alerts = [
        {
            "plan_id": plan.id,
            "user_id": plan.user_id,
            "user_name": plan.user.name,
            "end_date": plan.end_date.isoformat(),
            "days_remaining": (plan.end_date - today).days,
            "type": "plan_expiring"
        }
        for plan in plans_expiring_soon
    ]

    # モニタリング期限超過
    monitorings_overdue = db.query(Monitoring).join(User).filter(
        Monitoring.is_deleted == False,
        User.is_deleted == False,
        Monitoring.monitoring_date < today
    ).all()

    monitoring_alerts = [
        {
            "monitoring_id": mon.id,
            "user_id": mon.user_id,
            "user_name": mon.user.name,
            "monitoring_date": mon.monitoring_date.isoformat(),
            "days_overdue": (today - mon.monitoring_date).days,
            "type": "monitoring_overdue"
        }
        for mon in monitorings_overdue
    ]

    # 手帳更新期限が近い（3ヶ月以内）
    notebooks_expiring = db.query(Notebook).join(User).filter(
        Notebook.is_deleted == False,
        User.is_deleted == False,
        Notebook.renewal_date.isnot(None),
        Notebook.renewal_date <= three_months_later,
        Notebook.renewal_date >= today
    ).all()

    notebook_alerts = [
        {
            "notebook_id": nb.id,
            "user_id": nb.user_id,
            "user_name": nb.user.name,
            "notebook_type": nb.notebook_type,
            "renewal_date": nb.renewal_date.isoformat(),
            "days_remaining": (nb.renewal_date - today).days,
            "type": "notebook_expiring"
        }
        for nb in notebooks_expiring
    ]

    return {
        "plan_expiring_soon": plan_alerts,
        "monitoring_overdue": monitoring_alerts,
        "notebook_expiring": notebook_alerts,
        "total_alerts": len(plan_alerts) + len(monitoring_alerts) + len(notebook_alerts)
    }
