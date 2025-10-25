"""処方医管理画面のルーター"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/doctors", response_class=HTMLResponse)
async def doctors_list(request: Request):
    """処方医一覧画面"""
    return templates.TemplateResponse(
        "doctors/list.html",
        {"request": request}
    )
