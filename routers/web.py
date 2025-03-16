from fastapi import APIRouter, Depends, Request, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated

from db import get_session
from routers.cars import get_all_cars


web_router = APIRouter(tags=["Web"])


templates = Jinja2Templates(directory="templates")


@web_router.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse("home.html", {"request": request})


@web_router.post("/search", response_class=HTMLResponse)
async def search(
    size: Annotated[str, Form()],
    doors: Annotated[int, Form()],
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):

    cars = await get_all_cars(size=size, doors=doors, session=session)
    return templates.TemplateResponse(
        "search_result.html", {"request": request, "cars": cars}
    )
