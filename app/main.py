"""
FastAPIメインアプリケーション

計画相談支援 利用者管理システムのエントリーポイント
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import api_router
from app.database.connection import engine, Base

settings = get_settings()

# データベーステーブルの作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーション初期化
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="北九州市の計画相談支援事業所向け利用者管理システム",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルとテンプレート設定
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# APIルーター登録
app.include_router(api_router, prefix="/api")


# ルートエンドポイント
@app.get("/")
async def root():
    """ルートパス → ログインページにリダイレクト"""
    return RedirectResponse(url="/login")


# HTML画面のエンドポイント

@app.get("/login")
async def login_page(request: Request):
    """ログイン画面"""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@app.get("/dashboard")
async def dashboard_page(request: Request):
    """ダッシュボード画面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/users")
async def users_list_page(request: Request):
    """利用者一覧画面"""
    return templates.TemplateResponse("users/list.html", {"request": request})


# 重要: /users/new は /users/{user_id} より前に定義する必要があります
@app.get("/users/new")
async def user_create_page(request: Request):
    """利用者新規作成画面"""
    from app.database.connection import get_db
    from app.models.staff import Staff

    db = next(get_db())
    try:
        # スタッフ一覧を取得
        staffs = db.query(Staff).filter(Staff.is_active == True).all()

        return templates.TemplateResponse("users/create.html", {
            "request": request,
            "staffs": staffs
        })
    finally:
        db.close()


@app.get("/users/{user_id}")
async def user_detail_page(request: Request, user_id: int):
    """利用者詳細画面"""
    return templates.TemplateResponse("users/detail.html", {"request": request, "user_id": user_id})


@app.get("/users/{user_id}/edit")
async def user_edit_page(request: Request, user_id: int):
    """利用者編集画面"""
    return templates.TemplateResponse("users/edit.html", {"request": request, "user_id": user_id})


@app.get("/users/{user_id}/network")
async def user_network_page(request: Request, user_id: int):
    """利用者ネットワーク図画面"""
    return templates.TemplateResponse("users/network.html", {"request": request, "user_id": user_id})


@app.get("/consultations")
async def consultations_list_page(request: Request):
    """相談記録一覧画面"""
    return templates.TemplateResponse("consultations/list.html", {"request": request})


@app.get("/consultations/new")
async def consultation_create_page(request: Request):
    """相談記録新規作成画面"""
    from app.database.connection import get_db
    from app.models.user import User
    from app.models.staff import Staff

    db = next(get_db())
    try:
        # 利用者一覧を取得
        users = db.query(User).filter(User.is_deleted == False).all()
        # スタッフ一覧を取得
        staffs = db.query(Staff).filter(Staff.is_active == True).all()

        return templates.TemplateResponse("consultations/create.html", {
            "request": request,
            "users": users,
            "staffs": staffs
        })
    finally:
        db.close()


@app.get("/consultations/{consultation_id}/edit")
async def consultation_edit_page(request: Request, consultation_id: int):
    """相談記録編集画面"""
    return templates.TemplateResponse("consultations/edit.html", {"request": request, "consultation_id": consultation_id})


@app.get("/plans")
async def plans_list_page(request: Request):
    """計画一覧画面"""
    return templates.TemplateResponse("plans/list.html", {"request": request})


# 重要: /plans/new と /plans/create は /plans/{plan_id} より前に定義
@app.get("/plans/new")
@app.get("/plans/create")
async def plan_create_page(request: Request):
    """計画新規作成画面"""
    from app.database.connection import get_db
    from app.models.user import User
    from app.models.staff import Staff

    db = next(get_db())
    try:
        # 利用者一覧を取得
        users = db.query(User).filter(User.is_deleted == False).all()
        # スタッフ一覧を取得
        staffs = db.query(Staff).filter(Staff.is_active == True).all()

        return templates.TemplateResponse("plans/create.html", {
            "request": request,
            "users": users,
            "staffs": staffs
        })
    finally:
        db.close()


@app.get("/plans/{plan_id}")
async def plan_detail_page(request: Request, plan_id: int):
    """計画詳細画面"""
    return templates.TemplateResponse("plans/detail.html", {"request": request, "plan_id": plan_id})


@app.get("/plans/{plan_id}/edit")
async def plan_edit_page(request: Request, plan_id: int):
    """計画編集画面"""
    return templates.TemplateResponse("plans/edit.html", {"request": request, "plan_id": plan_id})


@app.get("/monitorings")
async def monitorings_list_page(request: Request):
    """モニタリング一覧画面"""
    return templates.TemplateResponse("monitorings/list.html", {"request": request})


# 重要: /monitorings/new は /monitorings/{monitoring_id} より前に定義
@app.get("/monitorings/new")
async def monitoring_create_page(request: Request):
    """モニタリング新規作成画面"""
    from app.database.connection import get_db
    from app.models.user import User
    from app.models.staff import Staff
    from app.models.plan import Plan

    db = next(get_db())
    try:
        # 利用者一覧を取得
        users = db.query(User).filter(User.is_deleted == False).all()
        # スタッフ一覧を取得
        staffs = db.query(Staff).filter(Staff.is_active == True).all()
        # 計画一覧を取得
        plans = db.query(Plan).filter(Plan.is_deleted == False).all()

        return templates.TemplateResponse("monitorings/create.html", {
            "request": request,
            "users": users,
            "staffs": staffs,
            "plans": plans
        })
    finally:
        db.close()


@app.get("/monitorings/{monitoring_id}")
async def monitoring_detail_page(request: Request, monitoring_id: int):
    """モニタリング詳細画面"""
    return templates.TemplateResponse("monitorings/detail.html", {"request": request, "monitoring_id": monitoring_id})


@app.get("/monitorings/{monitoring_id}/edit")
async def monitoring_edit_page(request: Request, monitoring_id: int):
    """モニタリング編集画面"""
    return templates.TemplateResponse("monitorings/edit.html", {"request": request, "monitoring_id": monitoring_id})


# 関係機関管理画面
@app.get("/organizations")
async def organizations_list_page(request: Request):
    """関係機関一覧画面"""
    return templates.TemplateResponse("organizations/list.html", {"request": request})


@app.get("/organizations/new")
async def organization_create_page(request: Request):
    """関係機関新規登録画面"""
    return templates.TemplateResponse("organizations/create.html", {"request": request})


@app.get("/organizations/{organization_id}")
async def organization_detail_page(request: Request, organization_id: int):
    """関係機関詳細画面"""
    return templates.TemplateResponse("organizations/detail.html", {"request": request, "organization_id": organization_id})


@app.get("/organizations/{organization_id}/edit")
async def organization_edit_page(request: Request, organization_id: int):
    """関係機関編集画面"""
    return templates.TemplateResponse("organizations/edit.html", {"request": request, "organization_id": organization_id})


# 処方医管理画面
@app.get("/doctors")
async def doctors_list_page(request: Request):
    """処方医一覧画面"""
    return templates.TemplateResponse("doctors/list.html", {"request": request})


# スタッフ管理画面
@app.get("/staffs")
async def staffs_list_page(request: Request):
    """スタッフ一覧画面（管理者のみ）"""
    return templates.TemplateResponse("staffs/list.html", {"request": request})


@app.get("/staffs/new")
async def staff_create_page(request: Request):
    """スタッフ新規登録画面（管理者のみ）"""
    return templates.TemplateResponse("staffs/create.html", {"request": request})


@app.get("/staffs/{staff_id}")
async def staff_detail_page(request: Request, staff_id: int):
    """スタッフ詳細画面"""
    return templates.TemplateResponse("staffs/detail.html", {"request": request, "staff_id": staff_id})


@app.get("/staffs/{staff_id}/edit")
async def staff_edit_page(request: Request, staff_id: int):
    """スタッフ編集画面（管理者のみ）"""
    return templates.TemplateResponse("staffs/edit.html", {"request": request, "staff_id": staff_id})


# ヘルスチェック
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
